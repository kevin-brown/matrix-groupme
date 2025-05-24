from __future__ import annotations

from mautrix.bridge import BasePuppet, async_getter_lock
from mautrix.types import ContentURI, RoomID, SyncToken, UserID
from mautrix.util.simple_template import SimpleTemplate

from yarl import URL

from typing import AsyncIterable, Awaitable, cast, TYPE_CHECKING

from .config import Config
from .db import Puppet as DBPuppet
from .types import GroupMeID

if TYPE_CHECKING:
    from .__main__ import GroupMeBridge


class Puppet(DBPuppet, BasePuppet):
    bridge: GroupMeBridge
    config: Config
    hs_domain: str
    matrix_id_template: SimpleTemplate[GroupMeID]
    displayname_template: SimpleTemplate[str]

    by_groupme_id: dict[GroupMeID, Puppet] = {}
    by_custom_mxid: dict[UserID, Puppet] = {}

    def _add_to_cache(self) -> None:
        self.by_groupme_id[self.id] = self
        if self.custom_mxid:
            self.by_custom_mxid[self.custom_mxid] = self

    @classmethod
    def init_cls(cls, bridge: "GroupMeBridge") -> AsyncIterable[Awaitable[None]]:
        cls.bridge = bridge
        cls.config = bridge.config
        cls.loop = bridge.loop
        cls.mx = bridge.matrix
        cls.az = bridge.az
        cls.hs_domain = cls.config["homeserver.domain"]
        matrix_id_template = SimpleTemplate(
            cls.config["bridge.username_template"],
            "userid",
            prefix="@",
            suffix=f":{Puppet.hs_domain}",
            type=int,
        )
        cls.matrix_id_template = cast(SimpleTemplate[GroupMeID], matrix_id_template)
        cls.displayname_template = SimpleTemplate(
            cls.config["bridge.displayname_template"], "displayname"
        )
        cls.sync_with_custom_puppets = cls.config["bridge.sync_with_custom_puppets"]
        cls.login_device_name = "GroupMe Bridge"

        return []

    @classmethod
    @async_getter_lock
    async def get_by_groupme_id(
        cls, groupme_id: GroupMeID, /, *, create: bool = True, is_direct_chat: bool = False
    ) -> Puppet | None:
        if groupme_id is None:
            return None

        try:
            return cls.by_groupme_id[groupme_id]
        except KeyError:
            pass

        puppet = cast(Puppet, await super().get_by_groupme_id(groupme_id))
        if puppet:
            puppet._add_to_cache()
            return puppet

        if create:
            puppet = cls(groupme_id, is_direct_chat=is_direct_chat)
            await puppet.insert()
            puppet._add_to_cache()
            return puppet

        return None

    @classmethod
    def get_id_from_matrix_id(cls, mxid: UserID) -> GroupMeID | None:
        return cls.matrix_id_template.parse(mxid)

    @classmethod
    def get_by_matrix_id(cls, matrix_id: UserID, create: bool = True) -> Awaitable[Puppet | None]:
        return cls.get_by_groupme_id(cls.get_id_from_matrix_id(matrix_id), create=create)
