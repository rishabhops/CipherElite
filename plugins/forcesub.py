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
import asyncio
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
        ".fsub <@username/link> - Enable force subscribe (e.g., .fsub @THANOS_PRO or .fsub https://t.me/THANOS_PRO)",
        ".unforcesub - Disable force subscribe in this chat",
        ".fsub status - Check force subscribe status"
    ]
    description = "Force Subscribe - Users must join a specific channel to chat. Unsubscribed users' messages are deleted."
    add_handler("forcesub", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.fsub(?: |$)"))
    @rishabh()
    async def fsub(event):
        text = event.text.strip().split(maxsplit=1)
        
        if len(text) == 1:
            await event.reply("❌ **Usage:** `.fsub <channel_username_or_link>`\n💡 **Example:** `.fsub @THANOS_PRO`")
            return
        
        if text[1].lower() == "status":
            chat_id = str(event.chat_id)
            data = load_data()
            
            if chat_id not in data:
                await event.reply("❌ Force subscribe is not enabled in this chat!")
                return
            
            channel_id = data[chat_id]["channel_id"]
            channel_name = data[chat_id]["channel_name"]
            channel_link = data[chat_id].get("channel_link", "Link unavailable")
            
            await event.reply(f"✅ **Force Subscribe Status**\n\n📢 **Channel:** [{channel_name}]({channel_link})\n🆔 **ID:** `{channel_id}`\n\n✔️ **Status:** ENABLED")
            return
        
        # Enable force subscribe
        try:
            channel_input = text[1]
            channel = await event.client.get_entity(channel_input)
            
            # CRITICAL FIX: Ensure the ID is saved as a negative channel ID (-100...)
            channel_id = channel.id
            if not str(channel_id).startswith("-100"):
                channel_id = int(f"-100{channel_id}")
                
            channel_name = channel.title if hasattr(channel, 'title') else getattr(channel, 'username', 'Channel')
            
            # Determine the best link to save
            if getattr(channel, 'username', None):
                channel_link = f"https://t.me/{channel.username}"
            else:
                channel_link = channel_input 
            
            chat_id = str(event.chat_id)
            data = load_data()
            
            data[chat_id] = {
                "channel_id": channel_id,
                "channel_name": channel_name,
                "channel_link": channel_link
            }
            
            save_data(data)
            
            await event.reply(f"✅ **Force Subscribe Enabled**\n\n📢 **Channel:** [{channel_name}]({channel_link})\n🆔 **ID:** `{channel_id}`\n\n💡 Users must now join this channel to chat here!")
        except Exception as e:
            await event.reply(f"❌ **Invalid channel!** Make sure the bot/userbot has access to it.\n**Error:** `{str(e)}`")

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
        if not (event.is_group or event.is_channel) or event.out:
            return
        
        chat_id = str(event.chat_id)
        data = load_data()
        
        if chat_id not in data:
            return
            
        user_id = event.sender_id
        channel_id = data[chat_id]["channel_id"]
        
        # CRITICAL FIX: Retroactively fix old broken positive IDs from the JSON file
        if str(channel_id).isdigit():
            channel_id = int(f"-100{channel_id}")
            
        # 1. ADMIN BYPASS
        try:
            participant = await event.client.get_permissions(event.chat_id, user_id)
            if participant.is_admin or participant.is_creator:
                return
        except Exception:
            pass 
        
        user = await event.get_sender()
        if not user:
            return

        user_in_channel = False
        
        # 2. CHECK SUBSCRIPTION
        try:
            await event.client(GetParticipantRequest(
                channel=channel_id,
                participant=user
            ))
            user_in_channel = True
            
        except UserNotParticipantError:
            pass # User is definitely NOT in the channel
            
        except ValueError as ve:
            # 3. CACHE MISS FALLBACK: If Telethon still gets confused about the Channel ID,
            # we use the string link to fetch the entity dynamically.
            try:
                channel_link = data[chat_id].get("channel_link")
                if channel_link and channel_link != "Link unavailable":
                    channel_entity = await event.client.get_entity(channel_link)
                    await event.client(GetParticipantRequest(
                        channel=channel_entity,
                        participant=user
                    ))
                    user_in_channel = True
            except UserNotParticipantError:
                pass # Not in channel
            except Exception as e:
                print(f"Forcesub failed to resolve backup channel link: {e}")
                user_in_channel = True # Fail-safe: let message stay if bot breaks
                
        except Exception as e:
            print(f"Forcesub unexpected error: {e}")
            user_in_channel = True # Fail-safe
            
        # 4. DELETE AND WARN
        if not user_in_channel:
            try:
                await event.delete()
                
                channel_name = data[chat_id]["channel_name"]
                channel_link = data[chat_id].get("channel_link", "")
                
                user_first_name = user.first_name if hasattr(user, 'first_name') and user.first_name else "User"
                user_mention = f"[{user_first_name}](tg://user?id={user_id})"
                
                msg = await event.respond(
                    f"⚠️ **Force Subscribe Active**\n\n"
                    f"👤 Hello {user_mention}, you must join our channel to chat here!\n"
                    f"📢 **Channel:** [{channel_name}]({channel_link})\n\n"
                    f"Please join via the link above and try again!"
                )
                
                await asyncio.sleep(10)
                await msg.delete()
            except Exception as delete_err:
                print(f"Failed to delete/warn user: {delete_err}")
