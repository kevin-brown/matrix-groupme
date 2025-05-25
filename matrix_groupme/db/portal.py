from __future__ import annotations

from mautrix.types import RoomID
from mautrix.util.async_db import Connection, Database, Scheme

from attr import dataclass
from sqlite3 import Row
from typing import TYPE_CHECKING, ClassVar

from ..types import GroupMeID

fake_db = Database.create("") if TYPE_CHECKING else None


@dataclass
class Portal:
    db: ClassVar[Database] = fake_db

    groupme_chat_id: str
    groupme_receiver: GroupMeID
    is_direct_chat: bool
    matrix_id: RoomID | None

    name: str
    topic: str
    avatar_url: str

    name_set: bool
    avatar_set: bool

    def __init__(self, groupme_chat_id: str, groupme_receiver: GroupMeID, is_direct_chat: bool = False,
                 matrix_id: RoomID | None = None, name: str = "", topic: str = "", avatar_url: str = "",
                 name_set: bool = False, avatar_set: bool = False) -> None:
        self.groupme_chat_id = groupme_chat_id
        self.groupme_receiver = groupme_receiver
        self.is_direct_chat = is_direct_chat
        self.matrix_id = matrix_id

        self.name = name
        self.topic = topic
        self.avatar_url = avatar_url

        self.name_set = name_set
        self.avatar_set = avatar_set

    @classmethod
    def _from_row(cls, row: Row | None) -> Portal | None:
        if row is None:
            return None

        return cls(**row)

    @classmethod
    async def get_by_matrix_id(cls, matrix_id: RoomID) -> Portal | None:
        q = f"SELECT groupme_chat_id, groupme_receiver, is_direct_chat, matrix_id, name, topic, avatar_url, name_set, avatar_set FROM portal WHERE matrix_id=$1"
        return cls._from_row(await cls.db.fetchrow(q, matrix_id))
