from mautrix.util.async_db import Connection

from . import upgrade_table


@upgrade_table.register(description="Initial revision for user")
async def upgrade_latest(conn: Connection) -> None:
    await conn.execute(
        """CREATE TABLE "user" (
            matrix_id   TEXT PRIMARY KEY,
            groupme_id  TEXT UNIQUE
        )"""
    )
