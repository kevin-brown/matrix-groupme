from typing import Any, Awaitable, Callable, TYPE_CHECKING

from mautrix.bridge.commands import CommandEvent, command_handler

if TYPE_CHECKING:
    from ..__main__ import GroupMeBridge

@command_handler(
    needs_auth=False,
    management_only=True,
    description="Log in to GroupMe with a GroupMe access token.",
)
async def login(evt: CommandEvent):
    print("login called")
