from mautrix.util.async_db import UpgradeTable

upgrade_table = UpgradeTable()

from . import (
    v001_initial_portal,
    v002_initial_puppet,
    v003_initial_user,
    v004_user_auth_token,
    v005_puppet_is_registered
)
