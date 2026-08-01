# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    catecho
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .addecho, .delecho, .rmecho
#  Note:           .listecho skipped (exists in echo.py)
# =============================================================================

from telethon import events
import json
from pathlib import Path
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "utilities"

DATA_FILE = Path(__file__).parent.parent / "DB" / "echo_db.json"

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

async def _resolve_user(event):
    if not event.is_reply:
        text = event.text.split(maxsplit=1)
        if len(text) < 2:
            return None, None
        try:
            user = await event.client.get_entity(text[1])
            return user.id, user.first_name or "User"
        except Exception:
            return None, None
    else:
        reply = await event.get_reply_message()
        try:
            user = await event.client.get_entity(reply.sender_id)
            return user.id, user.first_name or "User"
        except Exception:
            return reply.sender_id, "User"

def init(client_instance):
    commands = [
        ".addecho <user> - Add user to echo list",
        ".delecho <user> - Remove user from echo list",
        ".rmecho <user> - Remove user from echo list"
    ]
    description = "CatPlugins-style echo aliases (shares data with echo plugin)"
    add_handler("catecho", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.addecho"))
    @rishabh()
    async def addecho(event):
        user_id, user_name = await _resolve_user(event)
        if user_id is None:
            await event.reply("❌ Reply to a user or provide username to add echo.")
            return
        data = load_data()
        data[str(user_id)] = user_name
        save_data(data)
        await event.reply(f"🔊 Added {user_name} (`{user_id}`) to echo list.")

    @CipherElite.on(events.NewMessage(pattern=r"\.(delecho|rmecho)"))
    @rishabh()
    async def delecho(event):
        user_id, user_name = await _resolve_user(event)
        if user_id is None:
            await event.reply("❌ Reply to a user or provide username to remove echo.")
            return
        data = load_data()
        if str(user_id) not in data:
            await event.reply(f"❌ {user_name} is not in the echo list.")
            return
        del data[str(user_id)]
        save_data(data)
        await event.reply(f"🔇 Removed {user_name} (`{user_id}`) from echo list.")
