import os
import asyncio

from telethon import events
from snapchat_scraper import SnapchatScraper

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# where we store your Snapchat‐Scraper session
SESSIONS_DIR   = os.path.join("data", "sessions")
SNAP_SESSION   = os.path.join(SESSIONS_DIR, "snapchat_session.json")
TEMP_DIR       = os.path.join("temp", "snapchat")

os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

snap: SnapchatScraper = None
_registered = False

def init(client):
    """
    Called once on bot startup:
      • register help commands
      • try to load saved Snapchat session (cookies)
      • schedule event wiring
    """
    cmds = [
        ".snap <username>      — Download public Snapchat story",
        ".snaplogin <u> <p>    — Login to Snapchat (required for private stories)",
        ".snapstatus           — Check Snapchat login status",
        ".snapclear            — Clear saved Snapchat session"
    ]
    add_handler("snapchat", cmds, "Download Snapchat Stories")
    load_session()
    asyncio.get_event_loop().create_task(_register_handlers())


def load_session() -> bool:
    """Load saved cookies for SnapchatScraper."""
    global snap
    try:
        snap = SnapchatScraper()
        if os.path.exists(SNAP_SESSION):
            snap.load_session(SNAP_SESSION)
            return True
    except Exception as e:
        print(f"⚠️ Snapchat: could not load session: {e}")
    snap = None
    return False


def save_session() -> bool:
    """Dump cookies to disk."""
    global snap
    if not snap:
        return False
    try:
        snap.save_session(SNAP_SESSION)
        return True
    except Exception as e:
        print(f"❌ Snapchat: could not save session: {e}")
        return False


async def _register_handlers():
    global _registered
    if _registered:
        return
    _registered = True

    @CipherElite.on(events.NewMessage(pattern=r"\.snaplogin\s+(\S+)\s+(\S+)"))
    @rishabh()
    async def _snap_login(event):
        """Login to Snapchat so we can access private stories."""
        await event.delete()
        user, pw = event.pattern_match.group(1), event.pattern_match.group(2)
        msg = await event.respond("🔐 Logging in to Snapchat…")
        try:
            global snap
            snap = SnapchatScraper()
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: snap.login(user, pw)
            )
            save_session()
            await msg.edit("✅ Snapchat login successful & session saved!")
        except Exception as e:
            await msg.edit(f"❌ Snapchat login failed: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.snapstatus"))
    @rishabh()
    async def _snap_status(event):
        msg = await event.reply("🔍 Checking Snapchat status…")
        if not snap:
            return await msg.edit("❌ Not logged in. Use `.snaplogin <user> <pass>`")
        try:
            info = snap.whoami()  # returns your own username if logged in
            await msg.edit(f"✅ Logged in as @{info['username']}")
        except Exception as e:
            await msg.edit(f"❌ Session invalid: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.snap\s+(\w+)"))
    @rishabh()
    async def _snap_download(event):
        """Download a user’s public Snap story (requires login for private)."""
        username = event.pattern_match.group(1)
        if not snap:
            load_session()
        if not snap:
            return await event.reply("❌ Not logged in. Use `.snaplogin <user> <pass>`")

        # start spinner
        msg = await event.reply("🔄 Fetching story…")
        spinner = asyncio.create_task(_spin(msg, prefix="🔄 Downloading"))

        try:
            # download into TEMP_DIR/<username>/
            folder = os.path.join(TEMP_DIR, username)
            os.makedirs(folder, exist_ok=True)
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: snap.download_story(username, folder)
            )
            spinner.cancel()
            await spinner

            # find all files
            files = sorted(os.listdir(folder))
            if not files:
                return await msg.edit("❌ No story available or profile is private.")

            await msg.edit("✅ Download complete!")
            # send all media in one album
            paths = [os.path.join(folder, f) for f in files]
            await event.client.send_file(
                event.chat_id,
                paths,
                caption=(
                    f"📸 Snapchat story of @{username}\n"
                    "💪 Powered by Thanos"
                )
            )
        except Exception as e:
            spinner.cancel()
            await spinner
            await msg.edit(f"❌ Story download failed: {e}")
        finally:
            # cleanup
            for f in os.listdir(folder):
                try: os.remove(os.path.join(folder, f))
                except: pass

    @CipherElite.on(events.NewMessage(pattern=r"\.snapclear"))
    @rishabh()
    async def _snap_clear(event):
        """Clear saved Snapchat session (cookies)."""
        await event.delete()
        if os.path.exists(SNAP_SESSION):
            os.remove(SNAP_SESSION)
        global snap
        snap = None
        await event.respond("✅ Snapchat session cleared.")


async def _spin(msg, prefix="…", delay=0.1):
    """Simple spinner animation (cancellable)."""
    frames = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]
    i = 0
    try:
        while True:
            await asyncio.sleep(delay)
            await msg.edit(f"{prefix} {frames[i % len(frames)]}")
            i += 1
    except asyncio.CancelledError:
        return
