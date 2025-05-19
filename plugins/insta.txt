import re
import os
import asyncio

from telethon import events
from instagrapi import Client

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# where we store the session dump
SESSIONS_DIR = os.path.join("data", "sessions")
SESSION_FILE = os.path.join(SESSIONS_DIR, "instagram_session.json")

os.makedirs(SESSIONS_DIR, exist_ok=True)

ig_client = None
_commands_registered = False

def init(client):
    global ig_client

    cmds = [
        ".insta <url>       — Download an Instagram post/reel",
        ".instalog <u> <p>  — Login to Instagram",
        ".instastatus       — Show login status",
        ".instaclear        — Clear saved session"
    ]
    add_handler("instagram", cmds, "Instagram download with session")

    if load_session():
        print("✔️ Instagram: Session loaded on startup")
    else:
        print("⚠️ Instagram: No valid session on startup")

    asyncio.get_event_loop().create_task(register_commands())


def load_session() -> bool:
    global ig_client
    client = Client()
    if not os.path.exists(SESSION_FILE):
        return False
    try:
        client.load_settings(SESSION_FILE)
        client.account_info()
        ig_client = client
        return True
    except Exception as e:
        print(f"⚠️ Instagram: failed to load session: {e}")
        return False


def save_session() -> bool:
    global ig_client
    if not ig_client:
        return False
    try:
        ig_client.dump_settings(SESSION_FILE)
        return True
    except Exception as e:
        print(f"❌ Instagram: could not save session: {e}")
        return False


def perform_login(username: str, password: str) -> bool:
    global ig_client
    ig_client = Client()
    try:
        ig_client.login(username, password)
        return True
    except Exception as e:
        print(f"❌ Instagram login failed: {e}")
        return False


async def register_commands():
    global _commands_registered
    if _commands_registered:
        return
    _commands_registered = True

    @CipherElite.on(events.NewMessage(pattern=r"\.instalog\s+(\S+)\s+(.+)"))
    @rishabh()
    async def _login(event):
        await event.delete()
        u, p = event.pattern_match.group(1), event.pattern_match.group(2)
        msg = await event.respond("🔐 Logging in…")
        ok = await asyncio.get_event_loop().run_in_executor(None, lambda: perform_login(u, p))
        if not ok:
            return await msg.edit("❌ Login failed: invalid credentials.")
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
        account = await asyncio.get_event_loop().run_in_executor(None, ig_client.account_info)
        data = account.dict() if hasattr(account, "dict") else account.__dict__

        usern   = data.get("username", "–")
        name    = data.get("full_name", "–")
        bio     = (data.get("biography") or "")[:50]
        bio     += "…" if len(data.get("biography","")) > 50 else ""
        foll    = data.get("follower_count", data.get("followers_count", "–"))
        folling = data.get("following_count", data.get("followed_by_count", "–"))

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
        url = event.pattern_match.group(1).strip()
        if not ig_client and not load_session():
            return await event.reply("❌ Not logged in. Use `.instalog <user> <pass>`")

        # send initial message
        msg = await event.reply("🔄 Preparing download…")

        # spinner coroutine
        async def spinner(m):
            frames = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]
            i = 0
            try:
                while True:
                    await asyncio.sleep(0.1)
                    await m.edit(f"🔄 Downloading {frames[i % len(frames)]}")
                    i += 1
            except asyncio.CancelledError:
                return

        spin_task = asyncio.create_task(spinner(msg))

        # extract shortcode
        m = re.search(r"(?:/p/|/reel/|/tv/)([^/?]+)", url)
        if not m:
            spin_task.cancel()
            await spin_task
            return await msg.edit("❌ Could not extract shortcode from URL.")
        code = m.group(1)

        try:
            # fetch media pk & info
            media_pk = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ig_client.media_pk_from_code(code)
            )
            info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ig_client.media_info(media_pk)
            )

            # perform download
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

            # stop spinner
            spin_task.cancel()
            await spin_task

            # edit to complete
            await msg.edit("✅ Download complete!")

            # send file with caption
            await event.client.send_file(
                event.chat_id,
                path,
                caption=(
                    "📥 Downloaded by Elite Userbot\n"
                    "💪 Powered by Thanos"
                )
            )

            # cleanup
            try: os.remove(path)
            except: pass

        except Exception as e:
            spin_task.cancel()
            await spin_task
            await msg.edit(f"❌ Download failed: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.instaclear"))
    @rishabh()
    async def _clear(event):
        await event.delete()
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        global ig_client
        ig_client = None
        await event.respond("✅ Instagram session cleared.")
