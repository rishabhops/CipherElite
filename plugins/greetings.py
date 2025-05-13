import asyncio
from telethon import events

from utils.utils import CipherElite, edit_or_reply
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        ".hii       — Big ‘HI’ in emojis",
        ".thanks    — Big ‘THANKS’ in emojis",
        ".ok        — Big ‘OK’ in emojis",
        ".gn        — Big ‘GN’ in emojis"
    ]
    add_handler("greetings", commands, "Emoji Greetings Plugin")

@CipherElite.on(events.NewMessage(pattern=r"^\.hii$", outgoing=True))
@rishabh()
async def hi(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        "🌸   🌸   🌸🌸🌸\n"
        "🌸   🌸     🌸\n"
        "🌸🌸🌸     🌸\n"
        "🌸   🌸     🌸\n"
        "🌸   🌸   🌸🌸🌸"
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"^\.thanks$", outgoing=True))
@rishabh()
async def thanks(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        "🌟🌟🌟🌟🌟🌟🌟\n"
        "🌟 THANKS 🌟\n"
        "🌟🌟🌟🌟🌟🌟🌟"
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"^\.ok$", outgoing=True))
@rishabh()
async def ok(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        "⭕⭕⭕⭕⭕     K   \n"
        "⭕    ⭕    K  K \n"
        "⭕    ⭕   K K  \n"
        "⭕    ⭕    K  K \n"
        "⭕⭕⭕⭕⭕     K   "
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"^\.gn$", outgoing=True))
@rishabh()
async def good_night(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        "🌙🌙🌙🌙    🌙   🌙\n"
        "🌙        🌙🌙  🌙\n"
        "🌙🌙🌙🌙    🌙 🌙 🌙\n"
        "🌙    🌙    🌙  🌙🌙\n"
        "🌙🌙🌙🌙    🌙   🌙"
    )
    await edit_or_reply(event, art)
