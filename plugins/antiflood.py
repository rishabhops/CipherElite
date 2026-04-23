# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    antiflood
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import json
import time
from pathlib import Path
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

DATA_FILE = Path(__file__).parent.parent / "data" / "antiflood.json"
user_floods = {}  # {chat_id: {user_id: [timestamps]}}

def load_data():
    """Load antiflood settings from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save antiflood settings to JSON file"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init(client_instance):
    commands = [
        ".setflood <number> - Set flood limit (messages before action)",
        ".antiflood off - Disable antiflood",
        ".antiflood - Check current flood settings"
    ]
    description = "Antiflood Protection to prevent spam"
    add_handler("antiflood", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.setflood"))
    @rishabh()
    async def setflood(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.setflood <number>`\n\nExample: `.setflood 5`")
            return
        
        try:
            limit = int(text[1])
            
            if limit < 2:
                await event.reply("❌ Flood limit must be at least 2!")
                return
            
            chat_id = str(event.chat_id)
            data = load_data()
            
            data[chat_id] = {
                "limit": limit,
                "action": "mute",
                "time_window": 10  # seconds
            }
            
            save_data(data)
            
            await event.reply(f"✅ **Antiflood Settings Updated**\n\n⚡ Limit: {limit} messages\n⏱️ Time Window: 10 seconds\n🎯 Action: MUTE")
        except ValueError:
            await event.reply("❌ Invalid number!")

    @CipherElite.on(events.NewMessage(pattern=r"\.antiflood"))
    @rishabh()
    async def antiflood(event):
        text = event.text.strip()
        
        if text == ".antiflood off":
            chat_id = str(event.chat_id)
            data = load_data()
            
            if chat_id in data:
                del data[chat_id]
                save_data(data)
                await event.reply("✅ Antiflood protection disabled for this chat!")
            else:
                await event.reply("❌ Antiflood is already disabled!")
            return
        
        # Show current settings
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data:
            await event.reply("❌ Antiflood is not enabled in this chat!\n\nUse `.setflood <number>` to enable it.")
            return
        
        settings = data[chat_id]
        msg = f"🛡️ **Antiflood Settings**\n\n"
        msg += f"⚡ Limit: {settings['limit']} messages\n"
        msg += f"⏱️ Time Window: {settings['time_window']} seconds\n"
        msg += f"🎯 Action: {settings['action'].upper()}\n\n"
        msg += f"✅ Status: ENABLED"
        
        await event.reply(msg)

    @CipherElite.on(events.NewMessage(incoming=True))
    async def check_flood(event):
        # Skip if not a group or if it's our own message
        if not (event.is_group or event.is_channel) or event.out:
            return
        
        chat_id = str(event.chat_id)
        data = load_data()
        
        # Skip if antiflood not enabled for this chat
        if chat_id not in data:
            return
        
        user_id = event.sender_id
        current_time = time.time()
        
        # Initialize flood tracking
        if chat_id not in user_floods:
            user_floods[chat_id] = {}
        
        if user_id not in user_floods[chat_id]:
            user_floods[chat_id][user_id] = []
        
        # Add current message timestamp
        user_floods[chat_id][user_id].append(current_time)
        
        # Remove old timestamps outside time window
        time_window = data[chat_id]["time_window"]
        user_floods[chat_id][user_id] = [
            ts for ts in user_floods[chat_id][user_id]
            if current_time - ts <= time_window
        ]
        
        # Check if limit exceeded
        limit = data[chat_id]["limit"]
        if len(user_floods[chat_id][user_id]) >= limit:
            try:
                # Get user info
                user = await event.client.get_entity(user_id)
                user_name = user.first_name or "User"
                
                # Mute the user
                await event.client(EditBannedRequest(
                    event.chat_id,
                    user_id,
                    ChatBannedRights(until_date=None, send_messages=True)
                ))
                
                # Send notification
                await event.reply(f"🛡️ **Antiflood Triggered**\n\n👤 {user_name} has been muted for flooding!\n⚡ Sent {len(user_floods[chat_id][user_id])} messages in {time_window} seconds")
                
                # Reset flood tracking for this user
                user_floods[chat_id][user_id] = []
            except Exception as e:
                print(f"Antiflood error: {e}")
