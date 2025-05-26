from mautrix.bridge import Bridge
from mautrix.types import RoomID, UserID

from . import commands
from .config import Config
from .db import init as init_db, upgrade_table
from .matrix import MatrixHandler
from .portal import Portal
from .puppet import Puppet
from .user import User
from .version import version, linkified_version

class GroupMeBridge(Bridge):
    module = "matrix_groupme"
    name = "matrix-groupme"
    beeper_service_name = "groupme"
    beeper_network_name = "groupme"
    command = "python -m matrix-groupme"
    description = "A Matrix-GroupMe puppeting bridge."
    repo_url = "https://github.com/kevin-brown/matrix-groupme"
    version = version
    markdown_version = linkified_version

    config_class = Config

    upgrade_table = upgrade_table
    matrix_class = MatrixHandler

    def prepare_db(self) -> None:
        super().prepare_db()
        init_db(self.db)

    def prepare_bridge(self) -> None:
        self.matrix = MatrixHandler(bridge=self)
        Portal.init_cls(self)
        self.add_startup_actions(Puppet.init_cls(self))
        self.add_startup_actions(User.init_cls(self))
        self.add_startup_actions(Portal.restart_scheduled_disappearing())

        super().prepare_bridge()

    async def get_user(self, user_id: UserID, create: bool = True) -> User | None:
        return await User.get_by_matrix_id(user_id, create=create)

    async def get_portal(self, room_id: RoomID) -> Portal | None:
        return await Portal.get_by_matrix_id(room_id)

    async def get_puppet(self, user_id: UserID, create: bool = False) -> Puppet | None:
        return await Puppet.get_by_matrix_id(user_id, create=create)

    async def get_double_puppet(self, user_id: UserID) -> Puppet | None:
        return await Puppet.get_by_custom_matrix_id(user_id)

    def is_bridge_ghost(self, user_id: UserID) -> bool:
        return bool(Puppet.get_id_from_matrix_id(user_id))

    async def count_logged_in_users(self) -> int:
        return len([user for user in User.by_groupme_id.values() if user.groupme_id])

GroupMeBridge().run()
