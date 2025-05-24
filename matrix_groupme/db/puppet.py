from __future__ import annotations

from mautrix.types import ContentURI, SyncToken, UserID
from mautrix.util.async_db import Connection, Database, Scheme

from attr import dataclass
from sqlite3 import Row
from yarl import URL

from typing import TYPE_CHECKING, ClassVar, Iterable, Awaitable

from ..types import GroupMeID

fake_db = Database.create("") if TYPE_CHECKING else None


@dataclass
class Puppet:
    db: ClassVar[Database] = fake_db

    id: GroupMeID

    is_registered: bool

    displayname: str | None
    displayname_source: GroupMeID | None
    displayname_contact: bool
    displayname_quality: int
    disable_updates: bool
    username: str | None
    phone: str | None
    photo_id: str | None
    avatar_url: ContentURI | None
    name_set: bool
    avatar_set: bool
    contact_info_set: bool
    is_bot: bool | None
    is_channel: bool
    is_premium: bool

    custom_mxid: UserID | None
    access_token: str | None
    next_batch: SyncToken | None
    base_url: URL | None

    @classmethod
    def _from_row(cls, row: Row | None) -> Puppet | None:
        if row is None:
            return None
        data = {**row}
        base_url = data.pop("base_url", None)
        return cls(**data, base_url=URL(base_url) if base_url else None)

    @classmethod
    async def get_by_groupme_id(cls, groupme_id: GroupMeID) -> Puppet | None:
        q = f"SELECT {cls.columns} FROM puppet WHERE id=$1"
        return cls._from_row(await cls.db.fetchrow(q, groupme_id))

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
