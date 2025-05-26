from mautrix.util.async_db import Connection

from . import upgrade_table


@upgrade_table.register(description="Add is_registered to puppet table")
async def upgrade_latest(conn: Connection) -> None:
    await conn.execute(
        """ALTER TABLE puppet ADD COLUMN is_registered BOOLEAN NOT NULL DEFAULT false"""
    )
