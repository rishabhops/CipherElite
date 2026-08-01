# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    catart
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .hello, .killer
#  Note:           Other art commands skipped because they conflict with arts.py
# =============================================================================

from telethon import events
from config.config import Config
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

ALIVE_NAME = getattr(Config, "ALIVE_NAME", "CipherElite")

F = "╔┓┏╦━╦┓╔┓╔━━╗\n║┗┛║┗╣┃║┃║X X║\n║┏┓║┏╣┗╣┗╣╰╯║\n╚┛┗╩━╩━╩━╩━━╝\n"

def init(client_instance):
    commands = [
        ".hello - Hello art",
        ".killer <text> - Commando art"
    ]
    description = "ASCII art commands from CatPlugins"
    add_handler("catart", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.hello$"))
    @rishabh()
    async def hello(event):
        await event.reply(F)

    @CipherElite.on(events.NewMessage(pattern=r"\.killer(?: |$)([\s\S]*)"))
    @rishabh()
    async def killer(event):
        name = event.pattern_match.group(1).strip()
        if not name:
            name = "Target"
        await event.reply(
            f"__**Commando **__{ALIVE_NAME}\n\n"
            "_/﹋\\_\n"
            "(҂`_´)\n"
            f"<,︻╦╤─ ҉ - - - {name}\n"
            "_/﹋\\_\n"
        )
