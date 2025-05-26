from __future__ import annotations

from mautrix.bridge import BaseUser, async_getter_lock
from mautrix.types import UserID

from typing import AsyncIterable, AsyncGenerator, Awaitable, cast, TYPE_CHECKING

from .db import User as DBUser
from .groupme import GroupMeClient
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

    relay_whitelisted: bool
    is_whitelisted: bool
    is_admin: bool
    permission_level: str

    client: GroupMeClient | None = None
    connected: bool = False

    def __init__(self, matrix_id: UserID, groupme_id: GroupMeID = None, auth_token: str = None) -> None:
        super().__init__(matrix_id=matrix_id, groupme_id=groupme_id, auth_token=auth_token)
        BaseUser.__init__(self)

        perms = self.config.get_permissions(matrix_id)
        self.relay_whitelisted, self.is_whitelisted, self.is_admin, self.permission_level = perms


    def _add_to_cache(self) -> None:
        self.by_matrix_id[self.matrix_id] = self
        if self.groupme_id:
            self.by_groupme_id[self.groupme_id] = self

    @classmethod
    def init_cls(cls, bridge: "GroupMeBridge") -> AsyncIterable[Awaitable[None]]:
        cls.bridge = bridge
        cls.config = bridge.config

        return (user.connect() async for user in User.all_with_auth_tokens())

    @property
    def mxid(self) -> UserID:
        return self.matrix_id

    async def connect(self) -> None:
        if not self.client:
            self.client = GroupMeClient(self.auth_token)

        if not self.connected:
            await self.client.connect()
            self.connected = True

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

        user = cast(cls, await super().get_by_matrix_id(matrix_id))
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

    @classmethod
    async def all_with_auth_tokens(cls) -> AsyncGenerator[User, None]:
        async for user in super().all_with_auth_tokens():
            try:
                yield cls.by_matrix_id[user.matrix_id]
            except KeyError:
                user._add_to_cache()
                yield user

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
        return self.client and self.connected
