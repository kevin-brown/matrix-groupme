from __future__ import annotations

from mautrix.bridge import BasePortal
from mautrix.util.simple_template import SimpleTemplate

from typing import TYPE_CHECKING, AsyncIterable, Awaitable

from .db import Portal as DBPortal

if TYPE_CHECKING:
    from .__main__ import GroupMeBridge

class Portal(DBPortal, BasePortal):

    @classmethod
    def init_cls(cls, bridge: "GroupMeBridge") -> None:
        BasePortal.bridge = bridge
        cls.az = bridge.az
        cls.config = bridge.config
        cls.loop = bridge.loop
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

