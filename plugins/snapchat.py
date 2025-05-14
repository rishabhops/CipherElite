import os
import re
import shutil
import asyncio
import requests

from telethon import events
from pyppeteer import launch

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

TEMP_DIR = "temp/snapchat"
os.makedirs(TEMP_DIR, exist_ok=True)

_browser = None
_registered = False

def init(client):
    """
    Called on bot startup:
      • register /help text
      • launch headless browser
      • wire up commands
    """
    cmds = [
        ".snap <username>   — Download public Snapchat Story",
        ".snapstatus        — Check Snapchat status",
        ".snapclear         — Clear any Snapchat cache"
    ]
    add_handler("snapchat", cmds, "Download public Snapchat Stories")

    # launch browser once
    asyncio.get_event_loop().create_task(_ensure_browser())
    # register commands
    asyncio.get_event_loop().create_task(_register_handlers())

async def _ensure_browser():
    global _browser
    if _browser:
        return
    _browser = await launch({
        "headless": True,
        "args": ["--no-sandbox", "--disable-setuid-sandbox"]
    })

async def _register_handlers():
    global _registered
    if _registered:
        return
    _registered = True

    async def _spin(msg, prefix="🔄", delay=0.1):
        frames = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]
        i = 0
        try:
            while True:
                await asyncio.sleep(delay)
                await msg.edit(f"{prefix} {frames[i % len(frames)]}")
                i += 1
        except asyncio.CancelledError:
            return

    @CipherElite.on(events.NewMessage(pattern=r"\.snapstatus"))
    @rishabh()
    async def _snap_status(event):
        # Snapchat has no persistent web session here.
        await event.reply("ℹ️ This plugin uses a headless browser for public Stories only.")

    @CipherElite.on(events.NewMessage(pattern=r"\.snapclear"))
    @rishabh()
    async def _snap_clear(event):
        await event.delete()
        # clear out temp folder
        if os.path.isdir(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)
            os.makedirs(TEMP_DIR, exist_ok=True)
        await event.respond("✅ Snapchat cache cleared.")

    @CipherElite.on(events.NewMessage(pattern=r"\.snap\s+(\w+)"))
    @rishabh()
    async def _snap_download(event):
        username = event.pattern_match.group(1)
        msg = await event.reply(f"🔄 Preparing to download @{username}’s story…")

        # spinner
        spin_task = asyncio.create_task(_spin(msg, prefix="🔄 Downloading"))

        try:
            await _ensure_browser()
            page = await _browser.newPage()
            url = f"https://story.snapchat.com/{username}"
            await page.goto(url, {"waitUntil": "networkidle2", "timeout": 60000})

            # collect all img/video src attributes
            # this selector may need tweaking if Snapchat changes their markup
            imgs = await page.evaluate("""
                Array.from(document.querySelectorAll('img')).map(i=>i.src)
            """)
            vids = await page.evaluate("""
                Array.from(document.querySelectorAll('video source')).map(v=>v.src)
            """)

            media = [u for u in imgs + vids if u.startswith("https://")]
            if not media:
                raise RuntimeError("No public story found or user has no public story.")

            # download each file
            user_temp = os.path.join(TEMP_DIR, username)
            os.makedirs(user_temp, exist_ok=True)
            paths = []
            for idx, murl in enumerate(media, 1):
                ext = ".mp4" if murl.endswith(".mp4") else ".jpg"
                fn = f"{username}_{idx}{ext}"
                fp = os.path.join(user_temp, fn)
                r = requests.get(murl, timeout=30)
                with open(fp, "wb") as f:
                    f.write(r.content)
                paths.append(fp)

            # stop spinner
            spin_task.cancel()
            await spin_task

            # edit to complete
            await msg.edit("✅ Download complete!")

            # send as album
            await event.client.send_file(
                event.chat_id,
                paths,
                caption=(
                    f"📸 Snapchat Story of @{username}\n"
                    "💪 Downloaded by Elite Userbot | Powered by Thanos"
                )
            )

        except Exception as e:
            spin_task.cancel()
            await spin_task
            await msg.edit(f"❌ Failed: {e}")

        finally:
            # cleanup this user's temp folder
            try:
                shutil.rmtree(os.path.join(TEMP_DIR, username), ignore_errors=True)
            except:
                pass
