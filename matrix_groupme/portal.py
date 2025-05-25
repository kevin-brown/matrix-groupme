from __future__ import annotations

from mautrix.bridge import BasePortal, async_getter_lock
from mautrix.types import RoomID
from mautrix.util.simple_template import SimpleTemplate

from typing import TYPE_CHECKING, cast

from .db import Portal as DBPortal

if TYPE_CHECKING:
    from .__main__ import GroupMeBridge

class Portal(DBPortal, BasePortal):
    by_matrix_id: dict[RoomID, Portal] = {}
    by_chat_id: dict[tuple[str, str], Portal] = {}

    @classmethod
    def init_cls(cls, bridge: "GroupMeBridge") -> None:
        BasePortal.bridge = bridge
        cls.az = bridge.az
        cls.config = bridge.config
        cls.matrix = bridge.matrix

        cls.max_initial_member_sync = cls.config["bridge.max_initial_member_sync"]
        cls.sync_channel_members = cls.config["bridge.sync_channel_members"]
        cls.sync_matrix_state = cls.config["bridge.sync_matrix_state"]
        cls.public_portals = cls.config["bridge.public_portals"]
        cls.private_chat_portal_meta = cls.config["bridge.private_chat_portal_meta"]
        cls.filter_mode = cls.config["bridge.filter.mode"]
        cls.filter_list = cls.config["bridge.filter.list"]
        cls.filter_users = cls.config["bridge.filter.users"]
        cls.hs_domain = cls.config["homeserver.domain"]
        cls.backfill_enable = cls.config["bridge.backfill.enable"]
        cls.alias_template = SimpleTemplate(
            cls.config["bridge.alias_template"],
            "groupname",
            prefix="#",
            suffix=f":{cls.hs_domain}",
        )

    async def _post_init(self) -> None:
        self.by_chat_id[(self.groupme_chat_id, self.groupme_receiver)] = self
        if self.matrix_id:
            self.by_matrix_id[self.matrix_id] = self
        if self.is_direct_chat:
            puppet = await self.get_dm_puppet()
            self._main_intent = puppet.default_mxid_intent
        elif not self.is_direct_chat:
            self._main_intent = self.az.intent

    @classmethod
    @async_getter_lock
    async def get_by_matrix_id(cls, matrix_id: RoomID, /) -> Portal | None:
        try:
            return cls.by_matrix_id[matrix_id]
        except KeyError:
            pass

        portal = cast(Portal, await super().get_by_matrix_id(matrix_id))
        if portal is not None:
            await portal._post_init()
            return portal

        return None