from mautrix.bridge import BasePortal
from .db import Portal as DBPortal

class Portal(DBPortal, BasePortal):
    pass
