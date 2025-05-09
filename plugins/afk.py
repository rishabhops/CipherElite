# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    afk
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
#
#  IMPORTANT:
#    • If you copy, fork or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • Give proper credit back to the CipherElite Userbot author:
#        – GitHub: https://github.com/rishabhops/CipherElite
#        – Telegram: @rishabhops
#
#  Thank you for respecting open‐source software!
# =============================================================================

import asyncio
from datetime import datetime, timedelta
import re

from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from config.config import Config

# ───────────────────────────────────────────────────────────────
# Global AFK state
USER_AFK      = False
AFK_REASON    = ""
AFK_START     = None      # datetime when AFK began
LAST_REPLIED  = {}        # chat_id -> datetime of last auto‐reply
THROTTLE_SEC  = 5 * 60    # throttle replies to same chat every 5m
LOG_CHAT_ID   = getattr(Config, "LOG_CHAT_ID", None)
# ───────────────────────────────────────────────────────────────

def human_timedelta(delta: timedelta) -> str:
    d = delta.days
    h, rem = divmod(delta.seconds, 3600)
    m, s   = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s: parts.append(f"{s}s")
    return " ".join(parts) or "0s"

def init(client):
    """
    Register AFK entries in your /help.
    """
    commands = [
        ".afk [reason]    — Go AFK with optional reason",
        ".unafk           — Return from AFK",
        ".afkstatus       — Show AFK status & uptime"
    ]
    description = "Auto‐reply to mentions/DMs while you're away"
    add_handler("afk", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?$", outgoing=True))
    @rishabh()
    async def set_afk(event):
        global USER_AFK, AFK_REASON, AFK_START
        AFK_REASON = (event.pattern_match.group(1) or "").strip()
        AFK_START = datetime.now().replace(microsecond=0)
        USER_AFK  = True

        text = "__You are now AFK!__"
        if AFK_REASON:
            text += f"\n**Reason:** {AFK_REASON}"
        await event.reply(text)
        # log if desired
        if LOG_CHAT_ID:
            await event.client.send_message(
                LOG_CHAT_ID,
                f"#AFK_ON\nReason: {AFK_REASON or '(none)'}\nSince: {AFK_START}"
            )

    @CipherElite.on(events.NewMessage(pattern=r"\.unafk$", outgoing=True))
    @rishabh()
    async def unset_afk_cmd(event):
        """
        Manually clear AFK.
        """
        await _clear_afk(event)

    @CipherElite.on(events.NewMessage(pattern=r"\.afkstatus$", outgoing=True))
    @rishabh()
    async def afk_status(event):
        """
        Show current AFK status.
        """
        if not USER_AFK:
            return await event.reply("✅ You are not AFK.")
        uptime = human_timedelta(datetime.now().replace(microsecond=0) - AFK_START)
        text = f"⏱ AFK for: {uptime}"
        if AFK_REASON:
            text += f"\n**Reason:** {AFK_REASON}"
        await event.reply(text)

    @CipherElite.on(events.NewMessage(outgoing=True))
    @rishabh()
    async def _any_outgoing(event):
        """
        Any outgoing (non‐.afk/.unafk/.afkstatus) clears AFK.
        """
        if not USER_AFK:
            return
        txt = event.raw_text or ""
        if txt.startswith((".afk", ".unafk", ".afkstatus")):
            return
        await _clear_afk(event)

    @CipherElite.on(
        events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private or e.mentioned
        )
    )
    @rishabh()
    async def auto_reply_afk(event):
        """
        Auto‐reply in DMs or when mentioned, throttled.
        """
        global LAST_REPLIED
        if not USER_AFK:
            return

        sender = await event.get_sender()
        if sender and getattr(sender, "bot", False):
            return  # skip bots

        now = datetime.now()
        last = LAST_REPLIED.get(event.chat_id)
        if last and (now - last).total_seconds() < THROTTLE_SEC:
            return  # too soon

        uptime = human_timedelta(now - AFK_START)
        text = (
            f"👀 Owner is AFK (for {uptime})\n"
            + (f"**Reason:** {AFK_REASON}" if AFK_REASON else "")
        )
        msg = await event.reply(text)
        LAST_REPLIED[event.chat_id] = now
        # auto-delete reply after 20s
        await asyncio.sleep(20)
        try:
            await msg.delete()
        except:
            pass

async def _clear_afk(event):
    """
    Clears AFK state, notifies chat & log‐group.
    """
    global USER_AFK, AFK_START, AFK_REASON, LAST_REPLIED
    if not USER_AFK:
        return

    back = datetime.now().replace(microsecond=0)
    uptime = human_timedelta(back - AFK_START)
    txt = f"✅ Welcome back! You were AFK for {uptime}."
    await event.reply(txt)

    if LOG_CHAT_ID:
        await event.client.send_message(
            LOG_CHAT_ID,
            f"#AFK_OFF\nUptime: {uptime}"
        )

    # reset state
    USER_AFK     = False
    AFK_REASON   = ""
    AFK_START    = None
    LAST_REPLIED.clear()
