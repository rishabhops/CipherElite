# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    catmeme
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .oof, .type, .repeat, .give, .sadmin
#  Note:           .meme skipped because it conflicts with existing meme.py
# =============================================================================

from telethon import events
import asyncio
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def init(client_instance):
    commands = [
        ".oof - Oof animation",
        ".type <text> - Typewriter animation",
        ".repeat <count> <text> - Repeat text",
        ".give <text> - Give animation",
        ".sadmin - Admin shout animation"
    ]
    description = "CatPlugins meme and animation commands"
    add_handler("catmeme", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.oof$"))
    @rishabh()
    async def oof(event):
        status = await event.reply("Oof")
        t = "Oof"
        for _ in range(15):
            await asyncio.sleep(0.5)
            t = f"{t[:-1]}of"
            await status.edit(t)

    @CipherElite.on(events.NewMessage(pattern=r"\.type(?: |$)([\s\S]*)"))
    @rishabh()
    async def typewriter(event):
        message = event.pattern_match.group(1).strip()
        if event.is_reply:
            message = (await event.get_reply_message()).text or message
        if not message:
            await event.reply("❌ Give me some text to type.")
            return
        status = await event.reply("|")
        sleep_time = 0.2
        old_text = ""
        await asyncio.sleep(sleep_time)
        for character in message:
            old_text = f"{old_text}{character}"
            await status.edit(f"{old_text}|")
            await asyncio.sleep(sleep_time)
            await status.edit(old_text)
            await asyncio.sleep(sleep_time)

    @CipherElite.on(events.NewMessage(pattern=r"\.repeat(?: |$)(\d+)(?: |$)([\s\S]*)"))
    @rishabh()
    async def repeat(event):
        count = int(event.pattern_match.group(1))
        message = event.pattern_match.group(2).strip()
        if not message:
            await event.reply("❌ Usage: `.repeat <count> <text>`")
            return
        await event.reply((message + " ") * count)

    @CipherElite.on(events.NewMessage(pattern=r"\.give(?: |$)([\s\S]*)"))
    @rishabh()
    async def give(event):
        lp = event.pattern_match.group(1).strip()
        if not lp:
            lp = "🍭"
        status = await event.reply(f"{lp}        ")
        sleep_value = 0.5
        for i in range(1, 10):
            await asyncio.sleep(sleep_value)
            await status.edit(lp * i + " " * (9 - i))
        for i in range(1, 10):
            await asyncio.sleep(sleep_value)
            await status.edit(lp * i + " " * (9 - i))

    @CipherElite.on(events.NewMessage(pattern=r"\.sadmin$"))
    @rishabh()
    async def sadmin(event):
        status = await event.reply("sadmin")
        animation_chars = [
            "@aaaaaaaaaaaaadddddddddddddmmmmmmmmmmmmmiiiiiiiiiiiiinnnnnnnnnnnnn",
            "@aaaaaaaaaaaaddddddddddddmmmmmmmmmmmmiiiiiiiiiiiinnnnnnnnnnnn",
            "@aaaaaaaaaaadddddddddddmmmmmmmmmmmiiiiiiiiiiinnnnnnnnnnn",
            "@aaaaaaaaaaddddddddddmmmmmmmmmmiiiiiiiiiinnnnnnnnnn",
            "@aaaaaaaaadddddddddmmmmmmmmmiiiiiiiiinnnnnnnnn",
            "@aaaaaaaaddddddddmmmmmmmmiiiiiiiinnnnnnnn",
            "@aaaaaaadddddddmmmmmmmiiiiiiinnnnnnn",
            "@aaaaaaddddddmmmmmmiiiiiinnnnnn",
            "@aaaaadddddmmmmmiiiiinnnnn",
            "@aaaaddddmmmmiiiinnnn",
            "@aaadddmmmiiinnn",
            "@aaddmmiinn",
            "@admin",
        ]
        for i in range(13):
            await asyncio.sleep(1)
            await status.edit(animation_chars[i])
