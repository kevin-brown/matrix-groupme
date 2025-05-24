from __future__ import annotations

from mautrix.types import ContentURI, SyncToken, UserID
from mautrix.util.async_db import Connection, Database, Scheme

from attr import dataclass
from sqlite3 import Row
from yarl import URL

from typing import TYPE_CHECKING, ClassVar

from ..types import GroupMeID

fake_db = Database.create("") if TYPE_CHECKING else None


@dataclass
class Puppet:
    db: ClassVar[Database] = fake_db

    id: GroupMeID

    display_name: str
    display_name_set: bool

    groupme_user_id: GroupMeID
    groupme_avatar_url: str

    matrix_avatar_url: ContentURI
    matrix_avatar_set: bool

    custom_matrix_id: UserID
    access_token: str

    next_batch: SyncToken

    columns: ClassVar[str] = (
        "id, "
        "display_name, display_name_set, "
        "groupme_avatar_url, matrix_avatar_url, matrix_avatar_set, "
        "custom_matrix_id, access_token, next_batch"
    )

    @classmethod
    def _from_row(cls, row: Row | None) -> Puppet | None:
        if row is None:
            return None

        return cls(**row)

    @classmethod
    async def get_by_groupme_id(cls, groupme_id: GroupMeID) -> Puppet | None:
        q = f"SELECT {cls.columns} FROM puppet WHERE groupme_user_id=$1"
        return cls._from_row(await cls.db.fetchrow(q, groupme_id))

    @classmethod
    async def get_by_custom_matrix_id(cls, matrix_id: UserID) -> Puppet | None:
        q = f"SELECT {cls.columns} FROM puppet WHERE custom_matrix_id=$1"
        return cls._from_row(await cls.db.fetchrow(q, matrix_id))

    async def insert(self) -> None:
        q = """
        INSERT INTO puppet (
            id, is_registered, displayname, displayname_source, displayname_contact,
            displayname_quality, disable_updates, username, phone, photo_id, avatar_url, name_set,
            avatar_set, contact_info_set, is_bot, is_channel, is_premium, custom_mxid,
            access_token, next_batch, base_url
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18,
                  $19, $20, $21)
        """
        await self.db.execute(q, *self._values)
