# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    autokick
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import json
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

DATA_FILE = Path(__file__).parent.parent / "data" / "autokick.json"

def load_data():
    """Load autokick data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"autokick": {}, "dnd": {}}

def save_data(data):
    """Save autokick data to JSON file"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init(client_instance):
    commands = [
        ".autokick on - Enable auto-kick for new members",
        ".autokick off - Disable auto-kick",
        ".dnd on/off - Do not disturb mode for chat"
    ]
    description = "Auto Kick & DND Mode for chat management"
    add_handler("autokick", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.autokick"))
    @rishabh()
    async def autokick(event):
        text = event.text.strip().split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.autokick on` or `.autokick off`")
            return
        
        chat_id = str(event.chat_id)
        data = load_data()
        
        if text[1].lower() == "on":
            data["autokick"][chat_id] = True
            save_data(data)
            await event.reply("✅ **Auto-Kick Enabled**\n\n👢 New members will be automatically kicked from this chat!")
        elif text[1].lower() == "off":
            if chat_id in data["autokick"]:
                del data["autokick"][chat_id]
                save_data(data)
            await event.reply("✅ Auto-kick disabled for this chat!")
        else:
            await event.reply("❌ Invalid option! Use: `on` or `off`")

    @CipherElite.on(events.NewMessage(pattern=r"\.dnd"))
    @rishabh()
    async def dnd(event):
        text = event.text.strip().split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.dnd on` or `.dnd off`")
            return
        
        chat_id = str(event.chat_id)
        data = load_data()
        
        if text[1].lower() == "on":
            data["dnd"][chat_id] = True
            save_data(data)
            await event.reply("🔕 **Do Not Disturb Mode Enabled**\n\nYou will not receive notifications from this chat!")
        elif text[1].lower() == "off":
            if chat_id in data["dnd"]:
                del data["dnd"][chat_id]
                save_data(data)
            await event.reply("🔔 DND mode disabled for this chat!")
        else:
            await event.reply("❌ Invalid option! Use: `on` or `off`")

    @CipherElite.on(events.ChatAction)
    async def handle_new_member(event):
        # Check if someone joined
        if not event.user_joined and not event.user_added:
            return
        
        chat_id = str(event.chat_id)
        data = load_data()
        
        # Check if autokick is enabled
        if chat_id not in data["autokick"]:
            return
        
        try:
            # Get the user who joined
            user = await event.get_user()
            
            # Don't kick ourselves
            me = await event.client.get_me()
            if user.id == me.id:
                return
            
            # Kick the user
            await event.client.kick_participant(event.chat_id, user.id)
            
            # Send notification
            await event.reply(f"👢 {user.first_name} was automatically kicked! (Auto-kick is enabled)")
        except Exception as e:
            print(f"Auto-kick error: {e}")
