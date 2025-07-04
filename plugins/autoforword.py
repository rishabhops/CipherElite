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
import asyncio
from pathlib import Path
from telethon import events
from telethon.types import Message, Channel
from telethon.errors import ChatAdminRequiredError
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
        "**Requirements:**\n"
        "- Bot must be admin in both channels\n"
        "- Bot needs 'Post Messages' permission\n\n"
        "**Examples:**\n" + "\n".join(examples)
    )
    add_handler("autoforword", commands, description)

def load_autopost_db():
    """Load autopost data from JSON file"""
    try:
        DB_FOLDER.mkdir(exist_ok=True, parents=True)
        if DB_FILE.exists():
            with open(DB_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Error loading autopost DB: {e}")
    return {}

def save_autopost_db(data):
    """Save autopost data to JSON file"""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"❌ Error saving autopost DB: {e}")
        return False

async def check_channel_permissions(client, chat_id):
    """Verify bot has admin rights in channel"""
    try:
        perms = await client.get_permissions(chat_id, 'me')
        return perms.is_admin and perms.post_messages
    except Exception as e:
        print(f"❌ Permission check failed for {chat_id}: {e}")
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
            if not isinstance(source_entity, Channel):
                return await event.reply("`Source must be a channel!`")
        except Exception as e:
            return await event.reply(f"`❌ Invalid source channel: {e}`")
        
        # Get target entity
        try:
            target_entity = await event.client.get_entity(target_chat)
            if not isinstance(target_entity, Channel):
                return await event.reply("`Target must be a channel!`")
        except Exception as e:
            return await event.reply(f"`❌ Invalid target channel: {e}`")
        
        # Check permissions in source channel
        if not await check_channel_permissions(event.client, source_entity.id):
            return await event.reply(
                f"`❌ Bot needs admin rights with post permission in source channel:`\n"
                f"{source_entity.title} ({source_entity.id})"
            )
        
        # Check permissions in target channel
        if not await check_channel_permissions(event.client, target_entity.id):
            return await event.reply(
                f"`❌ Bot needs admin rights with post permission in target channel:`\n"
                f"{target_entity.title} ({target_entity.id})"
            )
        
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
                f"From: `{source_entity.title}` ({source_entity.id})\n"
                f"To: `{target_entity.title}` ({target_entity.id})\n\n"
                f"**Note:** All new messages will be forwarded automatically!"
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
        except Exception as e:
            return await event.reply(f"`❌ Invalid source channel: {e}`")
        
        try:
            target_entity = await event.client.get_entity(target_chat)
        except Exception as e:
            return await event.reply(f"`❌ Invalid target channel: {e}`")
        
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

    @CipherElite.on(events.NewMessage(incoming=True))
    async def handle_autopost(event: Message):
        # Ignore private chats and messages from bots
        if event.is_private or event.sender.bot:
            return
        
        current_chat = event.chat_id
        
        # Find matching autoposts
        matches = []
        for key, data in autopost_db.items():
            if current_chat == data["source"]:
                matches.append(data)
        
        if not matches:
            return
        
        print(f"📨 Processing autopost from {current_chat}")
        
        # Process each match
        for data in matches:
            target_id = data["target"]
            try:
                # Forward the message
                await event.client.send_message(
                    entity=target_id,
                    message=event.message,
                    silent=True
                )
                print(f"✅ Forwarded to {target_id}")
            except ChatAdminRequiredError:
                print(f"❌ Bot not admin in target channel: {target_id}")
            except Exception as e:
                print(f"❌ Autopost error ({current_chat}→{target_id}): {e}")
