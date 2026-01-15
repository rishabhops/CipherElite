# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    echo
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

DATA_FILE = Path(__file__).parent.parent / "data" / "echo.json"

def load_data():
    """Load echo data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save echo data to JSON file"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init(client_instance):
    commands = [
        ".echo <user> - Echo/repeat messages from user",
        ".unecho <user> - Stop echoing user",
        ".listecho - List echoed users"
    ]
    description = "Echo Plugin to repeat messages from specific users"
    add_handler("echo", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.echo"))
    @rishabh()
    async def echo(event):
        if not event.is_reply:
            text = event.text.split(maxsplit=1)
            if len(text) < 2:
                await event.reply("❌ Reply to a user or provide username to echo!")
                return
            
            try:
                user = await event.client.get_entity(text[1])
                user_id = user.id
                user_name = user.first_name or "User"
            except:
                await event.reply("❌ Invalid username or user not found!")
                return
        else:
            reply = await event.get_reply_message()
            user_id = reply.sender_id
            try:
                user = await event.client.get_entity(user_id)
                user_name = user.first_name or "User"
            except:
                user_name = "User"
        
        data = load_data()
        data[str(user_id)] = user_name
        save_data(data)
        
        await event.reply(f"🔊 Now echoing messages from {user_name} (`{user_id}`)")

    @CipherElite.on(events.NewMessage(pattern=r"\.unecho"))
    @rishabh()
    async def unecho(event):
        if not event.is_reply:
            text = event.text.split(maxsplit=1)
            if len(text) < 2:
                await event.reply("❌ Reply to a user or provide username to stop echoing!")
                return
            
            try:
                user = await event.client.get_entity(text[1])
                user_id = user.id
                user_name = user.first_name or "User"
            except:
                await event.reply("❌ Invalid username or user not found!")
                return
        else:
            reply = await event.get_reply_message()
            user_id = reply.sender_id
            try:
                user = await event.client.get_entity(user_id)
                user_name = user.first_name or "User"
            except:
                user_name = "User"
        
        data = load_data()
        
        if str(user_id) not in data:
            await event.reply(f"❌ {user_name} is not being echoed!")
            return
        
        del data[str(user_id)]
        save_data(data)
        
        await event.reply(f"🔇 Stopped echoing messages from {user_name} (`{user_id}`)")

    @CipherElite.on(events.NewMessage(pattern=r"\.listecho"))
    @rishabh()
    async def listecho(event):
        data = load_data()
        
        if not data:
            await event.reply("✅ No users are being echoed!")
            return
        
        msg = "📋 **Currently Echoing:**\n\n"
        for user_id, user_name in data.items():
            msg += f"👤 {user_name} (`{user_id}`)\n"
        
        await event.reply(msg)

    @CipherElite.on(events.NewMessage(incoming=True))
    async def echo_handler(event):
        # Skip if not a tracked user
        data = load_data()
        
        if str(event.sender_id) not in data:
            return
        
        # Skip if it's a command or our own message
        if event.text and event.text.startswith('.'):
            return
        
        try:
            # Echo the message
            if event.text:
                await event.reply(event.text)
            elif event.media:
                await event.reply(file=event.media)
        except Exception as e:
            print(f"Echo error: {e}")
