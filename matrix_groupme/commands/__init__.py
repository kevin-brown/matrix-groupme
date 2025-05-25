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
    if not evt.args:
        await evt.reply("**Usage:** `$cmdprefix+sp login <access_token>`")
        return

    evt.sender.auth_token = evt.args[0]

    await evt.sender.connect()
    await evt.sender.update()
