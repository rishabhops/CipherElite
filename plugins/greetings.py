# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    greetings
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

DATA_FILE = Path(__file__).parent.parent / "data" / "greetings.json"

def load_data():
    """Load greetings data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save greetings data to JSON file"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init(client_instance):
    commands = [
        ".setwelcome <text> - Set welcome message",
        ".setgoodbye <text> - Set goodbye message",
        ".delwelcome - Delete welcome message",
        ".delgoodbye - Delete goodbye message",
        ".getwelcome - View current welcome",
        ".getgoodbye - View current goodbye"
    ]
    description = "Welcome/Goodbye System for greeting members"
    add_handler("greetings", commands, description)

def format_message(text, user):
    """Format message with user placeholders"""
    if not text:
        return text
    
    text = text.replace("{mention}", f"[{user.first_name}](tg://user?id={user.id})")
    text = text.replace("{name}", user.first_name)
    text = text.replace("{username}", f"@{user.username}" if user.username else user.first_name)
    text = text.replace("{id}", str(user.id))
    
    return text

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.setwelcome"))
    @rishabh()
    async def setwelcome(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply(
                "❌ Usage: `.setwelcome <text>`\n\n"
                "**Placeholders:**\n"
                "• `{mention}` - Mention user\n"
                "• `{name}` - User's first name\n"
                "• `{username}` - User's username\n"
                "• `{id}` - User's ID"
            )
            return
        
        welcome_text = text[1]
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data:
            data[chat_id] = {}
        
        data[chat_id]["welcome"] = welcome_text
        save_data(data)
        
        await event.reply(f"✅ **Welcome Message Set!**\n\n{welcome_text}")

    @CipherElite.on(events.NewMessage(pattern=r"\.setgoodbye"))
    @rishabh()
    async def setgoodbye(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply(
                "❌ Usage: `.setgoodbye <text>`\n\n"
                "**Placeholders:**\n"
                "• `{mention}` - Mention user\n"
                "• `{name}` - User's first name\n"
                "• `{username}` - User's username\n"
                "• `{id}` - User's ID"
            )
            return
        
        goodbye_text = text[1]
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data:
            data[chat_id] = {}
        
        data[chat_id]["goodbye"] = goodbye_text
        save_data(data)
        
        await event.reply(f"✅ **Goodbye Message Set!**\n\n{goodbye_text}")

    @CipherElite.on(events.NewMessage(pattern=r"\.delwelcome"))
    @rishabh()
    async def delwelcome(event):
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data or "welcome" not in data[chat_id]:
            await event.reply("❌ No welcome message set for this chat!")
            return
        
        del data[chat_id]["welcome"]
        if not data[chat_id]:  # Remove chat entry if empty
            del data[chat_id]
        save_data(data)
        
        await event.reply("✅ Welcome message deleted!")

    @CipherElite.on(events.NewMessage(pattern=r"\.delgoodbye"))
    @rishabh()
    async def delgoodbye(event):
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data or "goodbye" not in data[chat_id]:
            await event.reply("❌ No goodbye message set for this chat!")
            return
        
        del data[chat_id]["goodbye"]
        if not data[chat_id]:  # Remove chat entry if empty
            del data[chat_id]
        save_data(data)
        
        await event.reply("✅ Goodbye message deleted!")

    @CipherElite.on(events.NewMessage(pattern=r"\.getwelcome"))
    @rishabh()
    async def getwelcome(event):
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data or "welcome" not in data[chat_id]:
            await event.reply("❌ No welcome message set for this chat!")
            return
        
        welcome_text = data[chat_id]["welcome"]
        await event.reply(f"📝 **Current Welcome Message:**\n\n{welcome_text}")

    @CipherElite.on(events.NewMessage(pattern=r"\.getgoodbye"))
    @rishabh()
    async def getgoodbye(event):
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data or "goodbye" not in data[chat_id]:
            await event.reply("❌ No goodbye message set for this chat!")
            return
        
        goodbye_text = data[chat_id]["goodbye"]
        await event.reply(f"📝 **Current Goodbye Message:**\n\n{goodbye_text}")

    @CipherElite.on(events.ChatAction)
    async def handle_greetings(event):
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data:
            return
        
        try:
            # Handle user join
            if event.user_joined or event.user_added:
                if "welcome" in data[chat_id]:
                    user = await event.get_user()
                    welcome_msg = format_message(data[chat_id]["welcome"], user)
                    await event.reply(welcome_msg)
            
            # Handle user leave
            elif event.user_left or event.user_kicked:
                if "goodbye" in data[chat_id]:
                    user = await event.get_user()
                    goodbye_msg = format_message(data[chat_id]["goodbye"], user)
                    await event.reply(goodbye_msg)
        except Exception as e:
            print(f"Greetings error: {e}")
