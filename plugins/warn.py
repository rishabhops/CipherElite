# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    warn
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import json
from pathlib import Path
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

DATA_FILE = Path(__file__).parent.parent / "data" / "warnings.json"

def load_data():
    """Load warnings data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save warnings data to JSON file"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init(client_instance):
    commands = [
        ".warn <reply> <reason> - Give warning to user",
        ".resetwarn <reply> - Reset all warnings",
        ".warns <reply> - Check user's warnings",
        ".setwarn <count> | <action> - Set warn limit and action (ban/mute/kick)"
    ]
    description = "Warning System for managing user behavior"
    add_handler("warn", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.warn"))
    @rishabh()
    async def warn(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a user to warn them!")
            return
        
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        chat_id = str(event.chat_id)
        
        try:
            user = await event.client.get_entity(user_id)
            user_name = user.first_name or "User"
        except:
            user_name = "User"
        
        # Get reason
        text_parts = event.text.split(maxsplit=1)
        reason = text_parts[1] if len(text_parts) > 1 else "No reason provided"
        
        data = load_data()
        
        # Initialize chat data if not exists
        if chat_id not in data:
            data[chat_id] = {
                "users": {},
                "limit": 3,
                "action": "ban"
            }
        
        # Initialize user warnings if not exists
        user_key = str(user_id)
        if user_key not in data[chat_id]["users"]:
            data[chat_id]["users"][user_key] = {
                "name": user_name,
                "warns": []
            }
        
        # Add warning
        data[chat_id]["users"][user_key]["warns"].append(reason)
        warn_count = len(data[chat_id]["users"][user_key]["warns"])
        limit = data[chat_id]["limit"]
        
        save_data(data)
        
        msg = f"⚠️ **Warning Issued**\n\n👤 User: {user_name} (`{user_id}`)\n📝 Reason: {reason}\n\n⚡ Warnings: {warn_count}/{limit}"
        
        # Check if limit reached
        if warn_count >= limit:
            action = data[chat_id]["action"]
            
            try:
                if action == "ban":
                    await event.client(EditBannedRequest(
                        event.chat_id,
                        user_id,
                        ChatBannedRights(until_date=None, view_messages=True)
                    ))
                    msg += f"\n\n🚫 **User has been banned!** (Limit reached)"
                elif action == "mute":
                    await event.client(EditBannedRequest(
                        event.chat_id,
                        user_id,
                        ChatBannedRights(until_date=None, send_messages=True)
                    ))
                    msg += f"\n\n🔇 **User has been muted!** (Limit reached)"
                elif action == "kick":
                    await event.client.kick_participant(event.chat_id, user_id)
                    msg += f"\n\n👢 **User has been kicked!** (Limit reached)"
                
                # Reset warnings after action
                data[chat_id]["users"][user_key]["warns"] = []
                save_data(data)
            except Exception as e:
                msg += f"\n\n❌ Failed to take action: {str(e)}"
        
        await event.reply(msg)

    @CipherElite.on(events.NewMessage(pattern=r"\.resetwarn"))
    @rishabh()
    async def resetwarn(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a user to reset their warnings!")
            return
        
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        chat_id = str(event.chat_id)
        
        try:
            user = await event.client.get_entity(user_id)
            user_name = user.first_name or "User"
        except:
            user_name = "User"
        
        data = load_data()
        
        if chat_id not in data or str(user_id) not in data[chat_id]["users"]:
            await event.reply(f"❌ {user_name} has no warnings!")
            return
        
        del data[chat_id]["users"][str(user_id)]
        save_data(data)
        
        await event.reply(f"✅ All warnings reset for {user_name}!")

    @CipherElite.on(events.NewMessage(pattern=r"\.warns"))
    @rishabh()
    async def warns(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a user to check their warnings!")
            return
        
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        chat_id = str(event.chat_id)
        
        try:
            user = await event.client.get_entity(user_id)
            user_name = user.first_name or "User"
        except:
            user_name = "User"
        
        data = load_data()
        
        if chat_id not in data or str(user_id) not in data[chat_id]["users"]:
            await event.reply(f"✅ {user_name} has no warnings!")
            return
        
        warns = data[chat_id]["users"][str(user_id)]["warns"]
        limit = data[chat_id]["limit"]
        
        msg = f"⚠️ **Warnings for {user_name}**\n\n"
        msg += f"📊 Total: {len(warns)}/{limit}\n\n"
        
        for i, reason in enumerate(warns, 1):
            msg += f"{i}. {reason}\n"
        
        await event.reply(msg)

    @CipherElite.on(events.NewMessage(pattern=r"\.setwarn"))
    @rishabh()
    async def setwarn(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2 or '|' not in text[1]:
            await event.reply("❌ Usage: `.setwarn <count> | <action>`\n\nExample: `.setwarn 3 | ban`\nActions: ban, mute, kick")
            return
        
        try:
            parts = text[1].split('|')
            count = int(parts[0].strip())
            action = parts[1].strip().lower()
            
            if action not in ['ban', 'mute', 'kick']:
                await event.reply("❌ Invalid action! Use: ban, mute, or kick")
                return
            
            if count < 1:
                await event.reply("❌ Warning count must be at least 1!")
                return
            
            chat_id = str(event.chat_id)
            data = load_data()
            
            if chat_id not in data:
                data[chat_id] = {
                    "users": {},
                    "limit": count,
                    "action": action
                }
            else:
                data[chat_id]["limit"] = count
                data[chat_id]["action"] = action
            
            save_data(data)
            
            await event.reply(f"✅ **Warning Settings Updated**\n\n⚡ Limit: {count} warnings\n🎯 Action: {action.upper()}")
        except ValueError:
            await event.reply("❌ Invalid format! Count must be a number.")
