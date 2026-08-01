# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    status
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .offline, .online
# =============================================================================

from telethon import events
from telethon.tl import functions
import os
import aiohttp
import json
from pathlib import Path
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "utilities"

OFFLINE_TAG = "[OFFLINE]"
GVARS_FILE = Path(__file__).parent.parent / "DB" / "status_vars.json"
_gvars = {}

def _load_gvars():
    global _gvars
    if GVARS_FILE.exists():
        try:
            with open(GVARS_FILE, "r") as f:
                _gvars = json.load(f)
        except Exception:
            _gvars = {}
    else:
        _gvars = {}

def _save_gvars():
    GVARS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GVARS_FILE, "w") as f:
        json.dump(_gvars, f, indent=2)

def gvarstatus(key):
    _load_gvars()
    return _gvars.get(key)

def addgvar(key, value):
    _load_gvars()
    _gvars[key] = value
    _save_gvars()

def init(client_instance):
    commands = [
        ".offline - Set status to offline",
        ".online - Set status back to online"
    ]
    description = "Toggle online/offline status and profile"
    add_handler("status", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.offline$"))
    @rishabh()
    async def offline(event):
        user = await event.client.get_entity("me")
        if user.first_name.startswith(OFFLINE_TAG):
            await event.reply("**Already in Offline Mode.**")
            return
        status = await event.reply("**Changing Profile to Offline...**")
        temp_dir = Path("./temp")
        temp_dir.mkdir(exist_ok=True)
        photo = temp_dir / "donottouch.jpg"
        async with aiohttp.ClientSession() as session:
            async with session.get("https://telegra.ph/file/249f27d5b52a87babcb3f.jpg") as resp:
                with open(photo, "wb") as f:
                    f.write(await resp.read())
        try:
            file = await event.client.upload_file(str(photo))
            await event.client(functions.photos.UploadProfilePhotoRequest(file))
        except Exception as e:
            await status.edit(str(e))
            return
        finally:
            os.remove(photo)
        first_name = user.first_name
        addgvar("my_first_name", first_name)
        addgvar("my_last_name", user.last_name or "")
        await event.client(
            functions.account.UpdateProfileRequest(
                last_name=first_name, first_name=OFFLINE_TAG
            )
        )
        await status.edit(f"**`{OFFLINE_TAG} {first_name}`\nI am Offline now.**")

    @CipherElite.on(events.NewMessage(pattern=r"\.online$"))
    @rishabh()
    async def online(event):
        user = await event.client.get_entity("me")
        if not user.first_name.startswith(OFFLINE_TAG):
            await event.reply("**Already Online.**")
            return
        status = await event.reply("**Changing Profile to Online...**")
        try:
            await event.client(
                functions.photos.DeletePhotosRequest(
                    await event.client.get_profile_photos("me", limit=1)
                )
            )
        except Exception as e:
            await status.edit(str(e))
            return
        first_name = gvarstatus("my_first_name") or ""
        last_name = gvarstatus("my_last_name") or ""
        await event.client(
            functions.account.UpdateProfileRequest(
                last_name=last_name, first_name=first_name
            )
        )
        await status.edit(f"**`{first_name} {last_name}`\nI am Online!**")
