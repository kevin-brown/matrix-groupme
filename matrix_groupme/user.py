from mautrix.bridge import BaseUser

from typing import AsyncIterable, Awaitable, TYPE_CHECKING

from .db import User as DBUser

if TYPE_CHECKING:
    from .__main__ import GroupMeBridge

class User(DBUser, BaseUser):
    """
    Represents a user in the GroupMe bridge.
    """

    groupme_id: str
    groupme_name: str
    groupme_avatar_url: str
    groupme_access_token: str
    groupme_email: str
    groupme_phone_number: str

    def __init__(self, groupme_id: str, groupme_name: str, groupme_avatar_url: str,
                 groupme_access_token: str, groupme_email: str, groupme_phone_number: str):
        self.groupme_id = groupme_id
        self.groupme_name = groupme_name
        self.groupme_avatar_url = groupme_avatar_url
        self.groupme_access_token = groupme_access_token
        self.groupme_email = groupme_email
        self.groupme_phone_number = groupme_phone_number

    @classmethod
    def init_cls(cls, bridge: "GroupMeBridge") -> AsyncIterable[Awaitable[None]]:
        return []
