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
    by_custom_matrix_id: dict[UserID, Puppet] = {}

    def __init__(self, id: GroupMeID, display_name: str = "", display_name_set: bool = False,
                 groupme_avatar_url: str = "", matrix_avatar_url: ContentURI = "",
                 matrix_avatar_set: bool = False, custom_matrix_id: UserID = "",
                 access_token: str = "", is_registered: bool = False, next_batch: SyncToken = "") -> None:
        super().__init__(
            id=id,
            display_name=display_name,
            display_name_set=display_name_set,
            groupme_user_id=id,
            groupme_avatar_url=groupme_avatar_url,
            matrix_avatar_url=matrix_avatar_url,
            matrix_avatar_set=matrix_avatar_set,
            custom_matrix_id=custom_matrix_id,
            access_token=access_token,
            is_registered=is_registered,
            next_batch=next_batch
        )
        BasePuppet.__init__(self)

        self.default_mxid = self.get_matrix_id_from_id(self.id)
        self.default_mxid_intent = self.az.intent.user(self.default_mxid)
        self.intent = self._fresh_intent()

        self._add_to_cache()

    def _add_to_cache(self) -> None:
        self.by_groupme_id[self.id] = self
        if self.custom_matrix_id:
            self.by_custom_matrix_id[self.custom_matrix_id] = self

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
        cls.homeserver_url_map = {
            server: URL(url)
            for server, url in cls.config["bridge.double_puppet_server_map"].items()
        }
        cls.login_shared_secret_map = {
            server: secret.encode("utf-8")
            for server, secret in cls.config["bridge.login_shared_secret_map"].items()
        }
        cls.login_device_name = "GroupMe Bridge"

        return []

    @property
    def custom_mxid(self) -> UserID:
        return self.custom_matrix_id

    @custom_mxid.setter
    def custom_mxid(self, matrix_id: UserID) -> None:
        self.custom_matrix_id = matrix_id
        # self._add_to_cache()

    @classmethod
    @async_getter_lock
    async def get_by_groupme_id(
        cls, groupme_id: GroupMeID, /, *, create: bool = True
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
            puppet = cls(groupme_id)
            await puppet.insert()
            puppet._add_to_cache()
            return puppet

        return None

    @classmethod
    def get_id_from_matrix_id(cls, mxid: UserID) -> GroupMeID | None:
        return cls.matrix_id_template.parse(mxid)

    @classmethod
    def get_matrix_id_from_id(cls, groupme_id: GroupMeID) -> UserID:
        return UserID(cls.matrix_id_template.format_full(groupme_id))

    @classmethod
    def get_by_mxid(cls, matrix_id):
        return cls.get_by_matrix_id(matrix_id)

    @classmethod
    def get_by_matrix_id(cls, matrix_id: UserID, create: bool = True) -> Awaitable[Puppet | None]:
        return cls.get_by_groupme_id(cls.get_id_from_matrix_id(matrix_id), create=create)

    @classmethod
    async def get_by_custom_mxid(cls, matrix_id: UserID) -> Puppet | None:
        return await cls.get_by_custom_matrix_id(matrix_id)

    @classmethod
    @async_getter_lock
    async def get_by_custom_matrix_id(cls, matrix_id: UserID, /) -> Puppet | None:
        try:
            return cls.by_custom_matrix_id[matrix_id]
        except KeyError:
            pass

        puppet = cast(Puppet, await super().get_by_custom_matrix_id(matrix_id))
        if puppet:
            puppet._add_to_cache()
            return puppet

        return None

    async def switch_matrix_id(self, matrix_id: UserID) -> None:
        await self.switch_mxid(access_token="auto", mxid=matrix_id)
