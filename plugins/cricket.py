# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    cricket
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .score, .cric <command>
# =============================================================================

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def init(client_instance):
    commands = [
        ".score - Ongoing match score via @cricbuzz_bot",
        ".cric <command> - Scoreboard/commentary via @cricbuzz_bot"
    ]
    description = "Cricket score updates via Cricbuzz bot"
    add_handler("cricket", commands, description)

async def register_commands():

    async def _cric_query(event, details=None):
        chat = "@cricbuzz_bot"
        reply_to = None
        if event.is_reply:
            reply_to = (await event.get_reply_message()).id
        status = await event.reply("```Gathering info...```")
        try:
            async with event.client.conversation(chat) as conv:
                await conv.send_message("/start")
                response = await conv.get_response()
                await conv.send_message(details if details else "/score")
                respond = await conv.get_response()
                await event.client.send_read_acknowledge(conv.chat_id)
                if respond.text.startswith("I can't find that"):
                    await status.edit("Sorry, I can't find it.")
                else:
                    await status.delete()
                    await event.client.send_message(event.chat_id, respond.message, reply_to=reply_to)
                await event.client.delete_messages(conv.chat_id, [response.id, respond.id])
        except YouBlockedUserError:
            await status.edit("Unblock @cricbuzz_bot and try again.")
        except Exception as e:
            await status.edit(f"⚠️ Error: `{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.score$"))
    @rishabh()
    async def score(event):
        await _cric_query(event)

    @CipherElite.on(events.NewMessage(pattern=r"\.cric(?: |$)([\s\S]*)"))
    @rishabh()
    async def cric(event):
        details = event.pattern_match.group(1).strip()
        if not details:
            await event.reply("❌ Provide a command from `.score` output.")
            return
        await _cric_query(event, details)
