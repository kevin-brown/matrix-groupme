from mautrix.util.async_db import Database

from .upgrade import upgrade_table

from .portal import Portal
from .puppet import Puppet
from .user import User

def init(db: Database) -> None:
    for table in (
        Portal,
        User,
        Puppet,
    ):
        table.db = db
