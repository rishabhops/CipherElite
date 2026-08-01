# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    textformat
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .upper, .lower, .title, .camel, .rcamel
# =============================================================================

from telethon import events
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

async def _process(event, transform):
    if event.is_reply:
        text = (await event.get_reply_message()).text or ""
    else:
        text = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
    if not text:
        await event.reply("❌ Reply to text or give text as input.")
        return
    await event.reply(transform(text))

def init(client_instance):
    commands = [
        ".upper <text> - Convert to UPPERCASE",
        ".lower <text> - Convert to lowercase",
        ".title <text> - Convert to Title Case",
        ".camel <text> - Mixed case camel",
        ".rcamel <text> - Reverse camel"
    ]
    description = "Simple text formatting tools"
    add_handler("textformat", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.upper(?: |$)([\s\S]*)"))
    @rishabh()
    async def upper_cmd(event):
        await _process(event, str.upper)

    @CipherElite.on(events.NewMessage(pattern=r"\.lower(?: |$)([\s\S]*)"))
    @rishabh()
    async def lower_cmd(event):
        await _process(event, str.lower)

    @CipherElite.on(events.NewMessage(pattern=r"\.title(?: |$)([\s\S]*)"))
    @rishabh()
    async def title_cmd(event):
        await _process(event, str.title)

    @CipherElite.on(events.NewMessage(pattern=r"\.(r?)camel(?: |$)([\s\S]*)"))
    @rishabh()
    async def camel_cmd(event):
        reverse = event.pattern_match.group(1).lower() == "r"
        if event.is_reply:
            text = (await event.get_reply_message()).text or ""
        else:
            text = event.pattern_match.group(2).strip() if event.pattern_match.group(2) else ""
        if not text:
            await event.reply("❌ Reply to text or give text as input.")
            return
        if reverse:
            bad = list(text.lower())[::2]
            cat = list(text.upper())[1::2]
        else:
            bad = list(text.upper())[::2]
            cat = list(text.lower())[1::2]
        result = "".join(f"{i}{j}" for i, j in zip(bad, cat))
        await event.reply(result)
