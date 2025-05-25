from mautrix.util.async_db import Connection

from . import upgrade_table


@upgrade_table.register(description="Add auth_token to user table")
async def upgrade_latest(conn: Connection) -> None:
    await conn.execute(
        """ALTER TABLE user ADD COLUMN auth_token TEXT DEFAULT ''"""
    )
