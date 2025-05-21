from mautrix.util.async_db import Connection, Database, Scheme

from attr import dataclass

from typing import TYPE_CHECKING, ClassVar, Iterable

fake_db = Database.create("") if TYPE_CHECKING else None


@dataclass
class Portal:
    db: ClassVar[Database] = fake_db
