from __future__ import annotations

from mautrix.bridge import BaseUser, async_getter_lock
from mautrix.types import UserID

from typing import AsyncIterable, Awaitable, cast, TYPE_CHECKING

from .db import User as DBUser
from .portal import Portal
from .puppet import Puppet
from .types import GroupMeID

if TYPE_CHECKING:
    from .__main__ import GroupMeBridge

class User(DBUser, BaseUser):
    """
    Represents a user in the GroupMe bridge.
    """

    by_matrix_id: dict[UserID, User] = {}
    by_groupme_id: dict[GroupMeID, User] = {}

    client: None

    def __init__(self, matrix_id: UserID, groupme_id: GroupMeID = None):
        self.matrix_id = matrix_id
        self.groupme_id = groupme_id

    def _add_to_cache(self) -> None:
        self.by_matrix_id[self.matrix_id] = self
        if self.groupme_id:
            self.by_groupme_id[self.groupme_id] = self

    @classmethod
    def init_cls(cls, bridge: "GroupMeBridge") -> AsyncIterable[Awaitable[None]]:
        return []

    @classmethod
    @async_getter_lock
    async def get_by_matrix_id(
        cls, matrix_id: UserID, /, *, check_db: bool = True, create: bool = True
    ) -> User | None:
        if not matrix_id or Puppet.get_id_from_matrix_id(matrix_id):
            return None
        try:
            return cls.by_matrix_id[matrix_id]
        except KeyError:
            pass

        if not check_db:
            return None

        user = cast(User, await super().get_by_matrix_id(matrix_id))
        if user is not None:
            user._add_to_cache()
            return user

        if create:
            cls.log.debug(f"Creating user instance for {matrix_id}")
            user = cls(matrix_id)
            await user.insert()
            user._add_to_cache()
            return user

        return None

    async def get_puppet(self) -> Puppet | None:
        if not self.groupme_id:
            return None
        return await Puppet.get_by_groupme_id(self.groupme_id)

    async def get_portal_with(self, puppet: Puppet, create: bool = True) -> Portal | None:
        if not self.groupme_id:
            return None
        return await Portal.get_by_groupme_id(
            puppet.groupme_id, groupme_receiver=self.groupme_id, is_direct_chat=True,
        )

    async def is_logged_in(self) -> bool:
        return (
            self.client and self.client.is_connected() and await self.client.is_user_authorized()
        )
