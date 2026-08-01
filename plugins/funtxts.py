# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    funtxts
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .tcat
#                  .why
#                  .fact
# =============================================================================

from telethon import events
import aiohttp
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def init(client_instance):
    commands = [
        ".tcat - Random cat text art",
        ".why - Random funny question",
        ".fact - Random fact"
    ]
    description = "Fun text commands from CatPlugins"
    add_handler("funtxts", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.tcat$"))
    @rishabh()
    async def tcat(event):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/v2/cat") as resp:
                data = await resp.json()
        await event.reply(data.get("cat", "Meow?"))

    @CipherElite.on(events.NewMessage(pattern=r"\.why$"))
    @rishabh()
    async def why(event):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/v2/why") as resp:
                data = await resp.json()
        await event.reply(data.get("why", "Why not?"))

    @CipherElite.on(events.NewMessage(pattern=r"\.fact$"))
    @rishabh()
    async def fact(event):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/v2/fact") as resp:
                data = await resp.json()
        await event.reply(data.get("fact", "No fact today."))
