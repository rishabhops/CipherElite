# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    emoji_greetings
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "animations"

import asyncio
import re
from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        "hii       - Big ‘HI’ in emojis",
        "thanks    - Big ‘THANKS’ in emojis",
        "ok        - Sparkling OK in emojis",
        "gn        - Sparkling GN in emojis",
        "bye       - Waving ‘BYE’ in emojis",
        "welc      - Festive ‘WELCOME’ in emojis",
        "love      - Heartfelt ‘LOVE’ in emojis"
    ]
    add_handler("emoji_greetings", commands, "Emoji Greetings Plugin")
    
async def edit_or_reply(event, text):
    """
    Try to edit the triggering message; if that fails, send a reply.
    """
    try:
        return await event.edit(text)
    except (MessageNotModifiedError, Exception):
        return await event.reply(text)



@CipherElite.on(events.NewMessage(pattern=r"(?i)^bye$", outgoing=True))
@rishabh()
async def bye(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        """
██████╗░██╗░░░██╗███████╗
██╔══██╗╚██╗░██╔╝██╔════╝
██████╦╝░╚████╔╝░█████╗░░
██╔══██╗░░╚██╔╝░░██╔══╝░░
██║░░██║░░░██║░░░███████╗
╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
👋✨🄱🅈🄴✨👋
"""
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"(?i)^welc$", outgoing=True))
@rishabh()
async def welcome(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        """
██╗██╗██╗██╗██╗██╗██╗██╗██╗██╗
██║██║██║██║██║██║██║██║██║██║
██║██║██║██║██║██║██║██║██║██║
╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝
🎉✨🅆🄴🄻🄲🄾🄼🄴✨🎉
"""
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"(?i)^love$", outgoing=True))
@rishabh()
async def love(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        """
██╗░░░░░░█████╗░██╗░░░██╗███████╗
██║░░░░░██╔══██╗██║░░░██║██╔════╝
██║░░░░░██║░░██║██║░░░██║█████╗░░
██║░░░░░██║░░██║██║░░░██║██╔══╝░░
███████╗╚█████╔╝╚██████╔╝███████╗
╚══════╝░╚════╝░░╚═════╝░╚══════╝
💖✨🄻🄾🅅🄴✨💖
"""
    )
    await edit_or_reply(event, art)


@CipherElite.on(events.NewMessage(pattern=r"(?i)^hii$", outgoing=True))
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

@CipherElite.on(events.NewMessage(pattern=r"(?i)^thanks$", outgoing=True))
@rishabh()
async def thanks(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        """
▀█▀ █░█ ▄▀█ █▄░█ █▄▀ █▀
░█░ █▀█ █▀█ █░▀█ █░█ ▄█
"""
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"(?i)^ok$", outgoing=True))
@rishabh()
async def ok(event):
    if getattr(event.message, "fwd_from", None):
        return
    art = (
        """
░█████╗░██╗░░██╗
██╔══██╗██║░██╔╝
██║░░██║█████═╝░
██║░░██║██╔═██╗░
╚█████╔╝██║░╚██╗
░╚════╝░╚═╝░░╚═╝
🦋✨🄾🄺🄰🅈✨🦋
"""
    )
    await edit_or_reply(event, art)

@CipherElite.on(events.NewMessage(pattern=r"(?i)^gn$", outgoing=True))
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
