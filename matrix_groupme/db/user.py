from __future__ import annotations

from mautrix.types import UserID
from mautrix.util.async_db import Connection, Database, Scheme

from attr import dataclass

from sqlite3 import Row
from typing import TYPE_CHECKING, ClassVar, AsyncGenerator

from ..types import GroupMeID

fake_db = Database.create("") if TYPE_CHECKING else None


@dataclass
class User:
    db: ClassVar[Database] = fake_db

    matrix_id: UserID
    groupme_id: GroupMeID | None

    auth_token: str | None

    @classmethod
    def _from_row(cls, row: Row | None) -> User | None:
        if row is None:
            return None

        return cls(**row)

    @classmethod
    async def get_by_matrix_id(cls, matrix_id: UserID) -> User | None:
        q = "SELECT matrix_id, groupme_id, auth_token FROM user WHERE matrix_id=$1"
        return cls._from_row(await cls.db.fetchrow(q, matrix_id))

    @classmethod
    async def all_with_auth_tokens(cls) -> AsyncGenerator[User, None]:
        q = "SELECT matrix_id, groupme_id, auth_token FROM user WHERE auth_token IS NOT NULL"
        for row in await cls.db.fetch(q):
            yield cls._from_row(row)

    async def insert(self) -> None:
        q = """
        INSERT INTO "user" (matrix_id, groupme_id, auth_token)
        VALUES ($1, $2, $3)
        """
        await self.db.execute(q, self.matrix_id, self.groupme_id, self.auth_token)

    async def update(self) -> None:
        q = """
        UPDATE "user" SET groupme_id=$1, auth_token=$2
        WHERE matrix_id=$3
        """
        await self.db.execute(q, self.groupme_id, self.auth_token, self.matrix_id)
