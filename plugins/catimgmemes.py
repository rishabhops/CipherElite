# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    catimgmemes
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .fakegs, .trump, .modi, .cmm, .kanna
#  Note:           .tweet skipped because it conflicts with twitter.py
#  Status:         Image generation uses CatUserBot templates that are not
#                  publicly available. Commands are registered; placeholders
#                  below. Templates/URLs can be added later.
# =============================================================================

from telethon import events
import re
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def deEmojify(text):
    return text.encode("ascii", "ignore").decode("ascii") if text else ""

def init(client_instance):
    commands = [
        ".fakegs <search> ; <result> - Fake Google search meme",
        ".trump <text> - Trump tweet meme",
        ".modi <text> - Modi tweet meme",
        ".cmm <text> - Change my mind meme",
        ".kanna <text> - Kanna chan meme"
    ]
    description = "Image meme generators (templates pending)"
    add_handler("catimgmemes", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.fakegs(?:\s|$)([\s\S]*)"))
    @rishabh()
    async def fakegs(event):
        text = event.pattern_match.group(1).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        if not text or ";" not in text:
            await event.reply("❌ Usage: `.fakegs top text ; bottom text`")
            return
        search, result = text.split(";", 1)
        await event.reply(
            f"🔍 **Fake Google Search**\n\n"
            f"**Search:** `{deEmojify(search.strip())}`\n"
            f"**Result:** `{deEmojify(result.strip())}`\n\n"
            "_(Image generation requires templates; pending)_"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.(trump|modi)(?:\s|$)([\s\S]*)"))
    @rishabh()
    async def tweet_meme(event):
        cmd = event.pattern_match.group(1).lower()
        text = event.pattern_match.group(2).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        if not text:
            await event.reply(f"❌ {cmd.title()}: What should I tweet?")
            return
        await event.reply(
            f"🐦 **{cmd.title()} Tweet**\n\n"
            f"`{deEmojify(text)}`\n\n"
            "_(Image generation requires templates; pending)_"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.cmm(?:\s|$)([\s\S]*)"))
    @rishabh()
    async def cmm(event):
        text = event.pattern_match.group(1).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        if not text:
            await event.reply("❌ Give text to write on the banner.")
            return
        await event.reply(
            f"📝 **Change My Mind**\n\n"
            f"`{deEmojify(text)}`\n\n"
            "_(Image generation requires templates; pending)_"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.kanna(?:\s|$)([\s\S]*)"))
    @rishabh()
    async def kanna(event):
        text = event.pattern_match.group(1).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        if not text:
            await event.reply("❌ What should Kanna show?")
            return
        await event.reply(
            f"💜 **Kanna says:**\n\n"
            f"`{deEmojify(text)}`\n\n"
            "_(Image generation requires templates; pending)_"
        )
