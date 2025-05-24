from mautrix.util.async_db import Connection

from . import upgrade_table


@upgrade_table.register(description="Initial revision for portal")
async def upgrade_latest(conn: Connection) -> None:
    await conn.execute(
        """CREATE TABLE portal (
            groupme_chat_id         TEXT NOT NULL,
            groupme_receiver        TEXT NOT NULL,
            is_direct_chat          BOOLEAN NOT NULL DEFAULT false,
            matrix_id               TEXT UNIQUE,

            name                    TEXT NOT NULL DEFAULT '',
            topic                   TEXT NOT NULL DEFAULT '',
            avatar_url              TEXT NOT NULL DEFAULT '',

            name_set                BOOLEAN NOT NULL DEFAULT false,
            avatar_set              BOOLEAN NOT NULL DEFAULT false,

            PRIMARY KEY (groupme_chat_id, groupme_receiver, is_direct_chat)
        )"""
    )