from mautrix.bridge import BasePuppet
from .db import Puppet as DBPuppet

class Puppet(DBPuppet, BasePuppet):
    pass
