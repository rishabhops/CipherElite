import asyncio
import re
from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        "hii       — Big ‘HI’ in emojis",
        "thanks    — Big ‘THANKS’ in emojis",
        "ok        — Sparkling OK in emojis",
        "gn        — Sparkling GN in emojis"
    ]
    add_handler("greetings", commands, "Emoji Greetings Plugin")

async def edit_or_reply(event, text):
    """
    Try to edit the triggering message; if that fails, send a reply.
    """
    try:
        return await event.edit(text)
    except (MessageNotModifiedError, Exception):
        return await event.reply(text)

@CipherElite.on(events.NewMessage(pattern=r"^(?i)hii$", outgoing=True))
@rishabh()
async def hi(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        """
██╗░░██╗██╗
██║░░██║██║
███████║██║
██╔══██║██║
██║░░██║██║
╚═╝░░╚═╝╚═╝
🦋✨🄷🄴🄻🄻🄾✨🦋\n
"""
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"^(?i)thanks$", outgoing=True))
@rishabh()
async def thanks(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        "💖💖💖💖💖💖💖💖💖💖\n"
        "💖  THANKS  💖\n"
        "💖💖💖💖💖💖💖💖💖💖"
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"^(?i)ok$", outgoing=True))
@rishabh()
async def ok(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        "✨✨✨✨✨✨✨✨✨💙💙💙✨✨✨💙✨✨✨💙✨✨💙✨✨✨💙✨✨💙✨✨✨💙✨✨✨💙💙💙✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨💙✨✨✨💙✨✨💙✨✨💙✨✨✨💙💙💙✨✨✨✨💙✨✨💙✨✨✨💙✨✨✨💙✨✨✨✨✨✨✨✨"
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"^(?i)gn$", outgoing=True))
@rishabh()
async def good_night(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        "░██████╗░███╗░░██╗\n"
        "██╔════╝░████╗░██║\n"
        "██║░░██╗░██╔██╗██║\n"
        "╚██████╔╝██║░╚███║\n"
        "░╚═════╝░╚═╝░░╚══╝\n"
        "🦋✨🄶🄾🄾🄳 🄽🄸🄶🄷🅃✨🦋"
    )
    await edit_or_reply(event, art)
