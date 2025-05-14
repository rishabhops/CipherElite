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

# where we store session + cookies
SESSIONS_DIR  = os.path.join("data", "sessions")
SESSION_FILE  = os.path.join(SESSIONS_DIR, "instagram_session.json")
COOKIE_FILE   = os.path.join(SESSIONS_DIR, "instagram_cookies.json")

os.makedirs(SESSIONS_DIR, exist_ok=True)

ig_client = None
_commands_registered = False

def init(client):
    """
    Called on bot startup:
     1) register help text
     2) pre-load any saved session
     3) schedule our event-handler registration
    """
    global ig_client

    commands = [
        ".insta <url>       — Download an Instagram post (image, video or reel)",
        ".instalog <u> <p>  — Login to Instagram for accessing private content",
        ".instastatus       — Check Instagram login status",
        ".instaclear        — Clear saved Instagram session"
    ]
    add_handler("instagram", commands, "Download Instagram media with authentication")

    # Try loading an existing session so it survives restarts
    if load_session():
        print("✔️ Instagram: Loaded saved session on startup")
    else:
        print("⚠️ Instagram: No valid session on startup")

    # defer the event wiring
    asyncio.get_event_loop().create_task(register_commands())


def load_session() -> bool:
    """Try to load a saved Insta session (settings+cookies)."""
    global ig_client
    client = Client()
    if not os.path.exists(SESSION_FILE):
        return False

    try:
        with open(SESSION_FILE, "r") as f:
            client.load_settings(json.load(f))
        # verify it’s still good
        client.account_info()
        ig_client = client
        return True
    except Exception as e:
        print(f"⚠️ Instagram: session load/verify failed: {e}")
        return False


def save_session() -> bool:
    """Dump client settings+cookies to disk."""
    global ig_client
    if not ig_client:
        return False
    try:
        data = ig_client.get_settings()
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"❌ Instagram: could not save session: {e}")
        return False


def perform_login(username: str, password: str) -> bool:
    """Blocking login call for executors."""
    global ig_client
    ig_client = Client()
    try:
        # clear any old ephemeral
        ig_client.set_settings({})
    except:
        pass

    try:
        ig_client.login(username, password)
        # quick verify
        ig_client.account_info()
        return True
    except Exception as e:
        print(f"❌ Instagram login failed: {e}")
        return False


async def register_commands():
    """Wires up all the .insta / .instalog / .instastatus / .instaclear handlers."""
    global _commands_registered
    if _commands_registered:
        return
    _commands_registered = True

    @CipherElite.on(events.NewMessage(pattern=r"\.instalog\s+(\S+)\s+(.+)"))
    @rishabh()
    async def _login(event):
        await event.delete()
        u, p = event.pattern_match.group(1), event.pattern_match.group(2)
        msg = await event.respond("🔐 Logging in to Instagram…")
        ok = await asyncio.get_event_loop().run_in_executor(None, lambda: perform_login(u, p))
        if not ok:
            return await msg.edit("❌ Login failed: bad credentials.")
        if save_session():
            await msg.edit("✅ Logged in & session saved.")
        else:
            await msg.edit("⚠️ Logged in but could not save session.")

    @CipherElite.on(events.NewMessage(pattern=r"\.instastatus"))
    @rishabh()
    async def _status(event):
        msg = await event.reply("🔍 Checking Instagram status…")
        if not ig_client and not load_session():
            return await msg.edit("❌ Not logged in. Use `.instalog <user> <pass>`")
        # fetch the account model in executor
        account = await asyncio.get_event_loop().run_in_executor(None, ig_client.account_info)
        data = account.dict() if hasattr(account, "dict") else account.__dict__

        # tolerant lookups
        usern    = data.get("username", "–")
        name     = data.get("full_name", "–")
        bio      = data.get("biography", "") or ""
        foll     = data.get("follower_count", data.get("followers_count", "–"))
        folling  = data.get("following_count", data.get("followed_by_count", "–"))

        bio = bio[:50] + ("…" if len(bio) > 50 else "")
        text = (
            f"✅ Logged in as @{usern}\n"
            f"👤 Name: {name}\n"
            f"👥 {foll} followers | {folling} following\n"
            f"📝 Bio: {bio}"
        )
        await msg.edit(text)

    @CipherElite.on(events.NewMessage(pattern=r"\.insta\s+(https?://\S+)"))
    @rishabh()
    async def _download(event):
        url = event.pattern_match.group(1)
        if not ig_client and not load_session():
            return await event.reply("❌ Not logged in. Use `.instalog <user> <pass>`")

        m = await event.reply("📥 Downloading media…")
        match = re.search(r"(?:/p/|/reel/|/tv/)([^/?]+)", url)
        if not match:
            return await m.edit("❌ Could not extract shortcode from URL.")

        code = match.group(1)
        try:
            # get PK
            media_pk = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ig_client.media_pk_from_code(code)
            )
            info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ig_client.media_info(media_pk)
            )

            tmp = "temp"
            os.makedirs(tmp, exist_ok=True)

            if info.media_type == 1:
                path = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ig_client.photo_download(media_pk, folder=tmp)
                )
            elif info.media_type == 2:
                path = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ig_client.video_download(media_pk, folder=tmp)
                )
            else:
                raise RuntimeError(f"Unsupported media type {info.media_type}")

            await event.client.send_file(event.chat_id, path)
            try: os.remove(path)
            except: pass
            await m.delete()

        except Exception as e:
            await m.edit(f"❌ Download failed: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.instaclear"))
    @rishabh()
    async def _clear(event):
        await event.delete()
        for f in (SESSION_FILE, COOKIE_FILE):
            if os.path.exists(f):
                os.remove(f)
        global ig_client
        ig_client = None
        await event.respond("✅ Instagram session cleared.")
