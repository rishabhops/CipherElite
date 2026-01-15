# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    forcesub
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import json
from pathlib import Path
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

DATA_FILE = Path(__file__).parent.parent / "data" / "forcesub.json"

def load_data():
    """Load forcesub data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save forcesub data to JSON file"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init(client_instance):
    commands = [
        ".fsub <channel> - Enable force subscribe for a channel",
        ".unforcesub - Disable force subscribe",
        ".fsub status - Check force subscribe status"
    ]
    description = "Force Subscribe - Users must join a channel to chat"
    add_handler("forcesub", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.fsub"))
    @rishabh()
    async def fsub(event):
        text = event.text.strip().split(maxsplit=1)
        
        if len(text) == 1:
            await event.reply("❌ Usage: `.fsub <channel>` or `.fsub status`")
            return
        
        if text[1].lower() == "status":
            chat_id = str(event.chat_id)
            data = load_data()
            
            if chat_id not in data:
                await event.reply("❌ Force subscribe is not enabled in this chat!")
                return
            
            channel_id = data[chat_id]["channel_id"]
            channel_name = data[chat_id]["channel_name"]
            
            await event.reply(f"✅ **Force Subscribe Status**\n\n📢 Channel: {channel_name}\n🆔 ID: `{channel_id}`\n\n✔️ Status: ENABLED")
            return
        
        # Enable force subscribe
        try:
            channel = await event.client.get_entity(text[1])
            channel_id = channel.id
            channel_name = channel.title if hasattr(channel, 'title') else channel.username
            
            chat_id = str(event.chat_id)
            data = load_data()
            
            data[chat_id] = {
                "channel_id": channel_id,
                "channel_name": channel_name
            }
            
            save_data(data)
            
            await event.reply(f"✅ **Force Subscribe Enabled**\n\n📢 Channel: {channel_name}\n🆔 ID: `{channel_id}`\n\n💡 Users must join this channel to chat!")
        except Exception as e:
            await event.reply(f"❌ Invalid channel! Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.unforcesub"))
    @rishabh()
    async def unforcesub(event):
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data:
            await event.reply("❌ Force subscribe is not enabled in this chat!")
            return
        
        del data[chat_id]
        save_data(data)
        
        await event.reply("✅ Force subscribe disabled for this chat!")

    @CipherElite.on(events.NewMessage(incoming=True))
    async def check_forcesub(event):
        # Skip if not a group or if it's our own message
        if not (event.is_group or event.is_channel) or event.out:
            return
        
        chat_id = str(event.chat_id)
        data = load_data()
        
        # Skip if forcesub not enabled
        if chat_id not in data:
            return
        
        user_id = event.sender_id
        channel_id = data[chat_id]["channel_id"]
        
        try:
            # Check if user is in the required channel
            await event.client(GetParticipantRequest(
                channel=channel_id,
                participant=user_id
            ))
        except UserNotParticipantError:
            # User is not in channel, delete their message
            try:
                await event.delete()
                channel_name = data[chat_id]["channel_name"]
                
                # Send warning (will be auto-deleted)
                msg = await event.reply(
                    f"⚠️ **Force Subscribe Active**\n\n"
                    f"👤 You must join our channel to chat here!\n"
                    f"📢 Channel: {channel_name}\n\n"
                    f"Join and try again!"
                )
                
                # Delete warning after 10 seconds
                import asyncio
                await asyncio.sleep(10)
                await msg.delete()
            except:
                pass
        except Exception as e:
            print(f"Forcesub check error: {e}")
