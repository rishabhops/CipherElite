# python:plugins/instagram.py
import re
import os
import json
import asyncio

from telethon import events
from instagrapi import Client

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Path to store Instagram session data
SESSIONS_DIR = os.path.join("data", "sessions")
SESSION_FILE = os.path.join(SESSIONS_DIR, "instagram_session.json")
COOKIE_FILE  = os.path.join(SESSIONS_DIR, "instagram_cookies.json")

os.makedirs(SESSIONS_DIR, exist_ok=True)

ig_client = None

def init(client):
    """
    Called by your bot loader.  We:
      1) register the help text
      2) schedule our register_commands coroutine
    """
    commands = [
        ".insta <url>       — Download an Instagram post (image, video or reel)",
        ".instalog <u> <p>  — Login to Instagram for accessing private content",
        ".instastatus       — Check Instagram login status",
        ".instaclear        — Clear saved Instagram session"
    ]
    add_handler("instagram", commands, "Download Instagram media with authentication")

    # ensure our event handlers are registered
    # cipherElite may already be running, so schedule this right away
    asyncio.get_event_loop().create_task(register_commands())

def load_session():
    global ig_client
    ig_client = Client()
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                ig_client.load_settings(json.load(f))
            # quick check
            ig_client.account_info()
            return True
        except Exception:
            return False
    return False

def save_session():
    global ig_client
    if not ig_client:
        return False
    try:
        settings = ig_client.get_settings()
        with open(SESSION_FILE, "w") as f:
            json.dump(settings, f)
        return True
    except Exception:
        return False

def perform_login(username, password):
    global ig_client
    ig_client = Client()
    try:
        ig_client.set_settings({})
    except:
        pass
    try:
        ig_client.login(username, password)
        # verify
        ig_client.account_info()
        return True
    except Exception:
        return False

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.instalog\s+(\S+)\s+(.+)"))
    @rishabh()
    async def instagram_login(event):
        await event.delete()
        user = event.pattern_match.group(1)
        pw   = event.pattern_match.group(2)
        m = await event.respond("🔐 Logging in…")
        ok = await asyncio.get_event_loop().run_in_executor(
            None, lambda: perform_login(user, pw)
        )
        if not ok:
            return await m.edit("❌ Login failed: invalid credentials.")
        if save_session():
            await m.edit("✅ Logged in & session saved.")
        else:
            await m.edit("⚠️ Logged in but could not save session.")

    @CipherElite.on(events.NewMessage(pattern=r"\.instastatus"))
    @rishabh()
    async def instagram_status(event):
        m = await event.reply("🔍 Checking Instagram status…")
        if not ig_client and not load_session():
            return await m.edit("❌ Not logged in. Use `.instalog <user> <pass>`")
        # now we have a client
        info = await asyncio.get_event_loop().run_in_executor(
            None, ig_client.account_info
        )
        txt = (
            f"✅ Logged in as @{info.username}\n"
            f"👤 Name: {info.full_name or '–'}\n"
            f"👥 {info.follower_count} followers | {info.following_count} following\n"
            f"📝 Bio: {info.biography[:50]}{'…' if len(info.biography)>50 else ''}"
        )
        await m.edit(txt)

    @CipherElite.on(events.NewMessage(pattern=r"\.insta\s+(https?://\S+)"))
    @rishabh()
    async def instagram_dl(event):
        url = event.pattern_match.group(1)
        if not ig_client and not load_session():
            return await event.reply("❌ Not logged in. Use `.instalog <user> <pass>`")
        m = await event.reply("📥 Downloading…")
        # extract shortcode
        match = re.search(r"(?:/p/|/reel/)([^/]+)", url)
        if not match:
            return await m.edit("❌ Unable to extract media code.")
        shortcode = match.group(1)
        try:
            # get pk & info
            media_pk = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ig_client.media_pk_from_code(shortcode)
            )
            info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ig_client.media_info(media_pk)
            )
            folder = "temp"
            os.makedirs(folder, exist_ok=True)
            if info.media_type == 1:
                path = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ig_client.photo_download(media_pk, folder=folder)
                )
            elif info.media_type == 2:
                path = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ig_client.video_download(media_pk, folder=folder)
                )
            else:
                raise RuntimeError("Unsupported media type")
            await event.client.send_file(event.chat_id, path)
            os.remove(path)
            await m.delete()
        except Exception as e:
            await m.edit(f"❌ Download failed: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.instaclear"))
    @rishabh()
    async def instagram_clear(event):
        await event.delete()
        for f in (SESSION_FILE, COOKIE_FILE):
            if os.path.exists(f):
                os.remove(f)
        global ig_client
        ig_client = None
        await event.respond("✅ Instagram session & cookies cleared.")
