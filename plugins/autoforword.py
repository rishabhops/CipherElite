# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    autoforword
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

import os
import json
from pathlib import Path
from telethon import events
from telethon.types import Message
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Database configuration
DB_FOLDER = Path(__file__).parent.parent / "DB"
DB_FILE = DB_FOLDER / "autopost_db.json"

def init(client_instance):
    commands = [
        ".autopost <source> <target> - Start autoposting between channels",
        ".stopautopost <source> <target> - Stop autoposting",
        ".autoposts - List active autoposts"
    ]
    examples = [
        "• `.autopost @my_channel @backup_channel`",
        "• `.autopost -100123456789 -100987654321`",
        "• `.stopautopost @my_channel @backup_channel`",
        "• `.autoposts`"
    ]
    description = (
        "Auto-post content between Telegram channels\n\n"
        "**Examples:**\n" + "\n".join(examples)
    )
    add_handler("autopost", commands, description)

def load_autopost_db():
    """Load autopost data from JSON file"""
    try:
        DB_FOLDER.mkdir(exist_ok=True)
        if DB_FILE.exists():
            with open(DB_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading autopost DB: {e}")
    return {}

def save_autopost_db(data):
    """Save autopost data to JSON file"""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving autopost DB: {e}")
        return False

async def register_commands():
    autopost_db = load_autopost_db()

    @CipherElite.on(events.NewMessage(pattern=r"\.autopost\s+(\S+)\s+(\S+)"))
    @rishabh()
    async def autopost(event: Message):
        source_chat = event.pattern_match.group(1).strip()
        target_chat = event.pattern_match.group(2).strip()
        
        # Get source entity
        try:
            source_entity = await event.client.get_entity(source_chat)
            if not source_entity:
                return await event.reply("`Invalid source channel specified.`")
        except:
            return await event.reply("`Invalid source channel specified.`")
        
        # Get target entity
        try:
            target_entity = await event.client.get_entity(target_chat)
            if not target_entity:
                return await event.reply("`Invalid target channel specified.`")
        except:
            return await event.reply("`Invalid target channel specified.`")
        
        key = f"{source_entity.id}|{target_entity.id}"
        
        if key in autopost_db:
            return await event.reply(
                f"`Autopost already enabled:`\n"
                f"From: {source_entity.title}\n"
                f"To: {target_entity.title}"
            )
        
        autopost_db[key] = {
            "source": source_entity.id,
            "source_title": source_entity.title,
            "target": target_entity.id,
            "target_title": target_entity.title
        }
        
        if save_autopost_db(autopost_db):
            await event.reply(
                f"**✅ Autopost enabled!**\n"
                f"From: `{source_entity.title}`\n"
                f"To: `{target_entity.title}`\n\n"
                f"**Note:** Bot must be admin in both channels!"
            )
        else:
            await event.reply("`Failed to save autopost configuration. Please check logs.`")

    @CipherElite.on(events.NewMessage(pattern=r"\.stopautopost\s+(\S+)\s+(\S+)"))
    @rishabh()
    async def stop_autopost(event: Message):
        source_chat = event.pattern_match.group(1).strip()
        target_chat = event.pattern_match.group(2).strip()
        
        try:
            source_entity = await event.client.get_entity(source_chat)
            if not source_entity:
                return await event.reply("`Invalid source channel specified.`")
        except:
            return await event.reply("`Invalid source channel specified.`")
        
        try:
            target_entity = await event.client.get_entity(target_chat)
            if not target_entity:
                return await event.reply("`Invalid target channel specified.`")
        except:
            return await event.reply("`Invalid target channel specified.`")
        
        key = f"{source_entity.id}|{target_entity.id}"
        
        if key not in autopost_db:
            return await event.reply(
                f"`No active autopost found:`\n"
                f"From: {source_entity.title}\n"
                f"To: {target_entity.title}"
            )
        
        del autopost_db[key]
        if save_autopost_db(autopost_db):
            await event.reply(
                f"**✅ Autopost disabled!**\n"
                f"From: `{source_entity.title}`\n"
                f"To: `{target_entity.title}`"
            )
        else:
            await event.reply("`Failed to save autopost configuration. Please check logs.`")

    @CipherElite.on(events.NewMessage(pattern=r"\.autoposts"))
    @rishabh()
    async def list_autoposts(event: Message):
        if not autopost_db:
            return await event.reply("`No active autoposts found.`")
        
        message = "**📋 Active Autoposts:**\n\n"
        for key, data in autopost_db.items():
            message += (
                f"• **Source:** {data['source_title']} (`{data['source']}`)\n"
                f"• **Target:** {data['target_title']} (`{data['target']}`)\n\n"
            )
        
        await event.reply(message)

    @CipherElite.on(events.NewMessage())
    async def handle_autopost(event: Message):
        if event.is_private:
            return
        
        current_chat = event.chat_id
        for key, data in autopost_db.items():
            if current_chat == data["source"]:
                try:
                    await event.client.send_message(
                        data["target"],
                        event.message
                    )
                except Exception as e:
                    print(f"Autopost error from {data['source']} to {data['target']}: {e}")
