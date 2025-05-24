from mautrix.util.async_db import Connection

from . import upgrade_table


@upgrade_table.register(description="Initial revision for puppet")
async def upgrade_latest(conn: Connection) -> None:
    await conn.execute(
        """CREATE TABLE puppet (
            id                  BIGINT PRIMARY KEY,

            display_name        TEXT NOT NULL DEFAULT '',
            display_name_set    BOOLEAN NOT NULL DEFAULT false,

            groupme_user_id     TEXT NOT NULL DEFAULT '',
            groupme_avatar_url  TEXT NOT NULL DEFAULT '',

            matrix_avatar_url   TEXT NOT NULL DEFAULT '',
            matrix_avatar_set   BOOLEAN NOT NULL DEFAULT false,

            custom_matrix_id    TEXT NOT NULL DEFAULT '',
            access_token        TEXT,

            next_batch          TEXT,
        )"""
    )