from mautrix.bridge import Bridge
from mautrix.types import RoomID, UserID

from .config import Config
from .portal import Portal
from .puppet import Puppet
from .user import User
from .version import version, linkified_version


class GroupMeBridge(Bridge):
    module = "matrix_groupme"
    name = "matrix-groupme"
    beeper_service_name = "telegram"
    beeper_network_name = "telegram"
    command = "python -m matrix-groupme"
    description = "A Matrix-GroupMe puppeting bridge."
    repo_url = "https://github.com/kevin-brown/matrix-groupme"
    version = version
    markdown_version = linkified_version

    config_class = Config

    async def get_user(self, user_id: UserID, create: bool = True) -> User | None:
        user = await User.get_by_mxid(user_id, create=create)
        if user:
            await user.ensure_started()
        return user

    async def get_portal(self, room_id: RoomID) -> Portal | None:
        return await Portal.get_by_mxid(room_id)

    async def get_puppet(self, user_id: UserID, create: bool = False) -> Puppet | None:
        return await Puppet.get_by_mxid(user_id, create=create)

    async def get_double_puppet(self, user_id: UserID) -> Puppet | None:
        return await Puppet.get_by_custom_mxid(user_id)

    def is_bridge_ghost(self, user_id: UserID) -> bool:
        return bool(Puppet.get_id_from_mxid(user_id))

    async def count_logged_in_users(self) -> int:
        return len([user for user in User.by_groupme_id.values() if user.groupme_id])

GroupMeBridge().run()
