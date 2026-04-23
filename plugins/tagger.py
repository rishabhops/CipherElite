import asyncio
import random
from collections import deque
from telethon import events
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError

from config.config import Config
from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh  

# ==========================================
# GLOBAL VARIABLES
# ==========================================
active_chats = set() 
processed_msgs = deque(maxlen=2000) 

# ==========================================
# PRESET MESSAGES
# ==========================================
GM_MESSAGES = [
    "Good Morning {mention}! Have a wonderful day 🌅",
    "Wakey wakey {mention}! It's a beautiful morning ☀️",
    "A very Good Morning to you, {mention}! ☕",
    "Rise and shine {mention}! ✨",
    "Good Morning {mention}! Sending good vibes your way 🌻"
]

GN_MESSAGES = [
    "Good Night {mention}! Sweet dreams 🌙",
    "Sleep tight {mention}! Don't let the bed bugs bite 😴",
    "Good Night {mention}! See you tomorrow 🌌",
    "Rest well {mention}! 🥱",
    "Nighty night {mention}! 🌃"
]

VC_MESSAGES = [
    "Hey {mention}, join the Voice Chat! We are waiting 🎤",
    "{mention} come to VC fast! 🎧",
    "Join the VC {mention}, let's talk! 🗣",
    "We need you in the VC {mention}! 🎵",
    "Hop in the VC {mention}, it's fun inside! 🎉"
]

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".btag <msg> - Bulk tag (5 users/msg) with custom message",
        ".utag <msg> - Tag every member individually with message",
        ".btaggm - Bulk tag all users with Good Morning",
        ".utaggm - Tag all users individually with Good Morning",
        ".btaggn - Bulk tag all users with Good Night",
        ".utaggn - Tag all users individually with Good Night",
        ".btagvc - Bulk tag all users to join Voice Chat",
        ".utagvc - Tag all users individually to join Voice Chat",
        ".cancel - Stop any ongoing tagging process in the current chat"
    ]

    description = (
        "🏷️ **Advanced Group Tagger**\n"
        "⚡ Safe Bulk & Individual Tagging\n"
        "📝 Custom & Random Messages\n"
        "🛑 Anti-Ban Humanized Delays Included\n\n"
    )

    add_handler("tagger", commands, description)

# ==========================================
# ANTI-BAN HELPER FUNCTIONS
# ==========================================
async def get_users(event):
    """Fetches all active users in the chat."""
    users = []
    chat_id = event.chat_id
    if not chat_id:
        return users
        
    async for user in event.client.iter_participants(chat_id):
        if not user.bot and not user.deleted:
            users.append(user)
    return users

async def human_delay(messages_sent):
    """Calculates safe, randomized sleep times to mimic humans and evade spam filters."""
    if messages_sent > 0 and messages_sent % 10 == 0:
        # Long break every 10 messages (10 to 15 seconds)
        await asyncio.sleep(random.uniform(10.0, 15.0))
    else:
        # Standard random break (2.5 to 4.5 seconds)
        await asyncio.sleep(random.uniform(2.5, 4.5))

# ==========================================
# CORE TAGGING FUNCTIONS
# ==========================================
async def handle_bulk_tag(event, msg_list=None, static_text=None):
    chat_id = event.chat_id
    if chat_id in active_chats:
        return await event.reply("⚠️ **Tagging is already running in this chat. Type `.cancel` to stop it.**")
    
    status = await event.reply("✅ **Starting Bulk Tag (Anti-Ban Mode)...**")
    active_chats.add(chat_id)
    users = await get_users(event)
    mentions, count, messages_sent = "", 0, 0
    
    try:
        for user in users:
            if chat_id not in active_chats: 
                break
                
            mentions += f"[{user.first_name}](tg://user?id={user.id}) "
            count += 1
            
            if count == 5:
                base_msg = random.choice(msg_list).replace("{mention}", "").strip() if msg_list else static_text
                
                while True:
                    try:
                        await event.client.send_message(chat_id, f"{base_msg}\n\n{mentions}")
                        messages_sent += 1
                        break 
                    except FloodWaitError as e:
                        if e.seconds > 60:
                            await event.reply(f"🛑 **FloodWait over 60s ({e.seconds}s)! Stopping to protect account.**")
                            active_chats.remove(chat_id)
                            return
                        await asyncio.sleep(e.seconds + 2) 
                    except (ChatWriteForbiddenError, UserBannedInChannelError):
                        await event.reply("🛑 **Error: I lack permission to send messages here or have been muted. Stopping.**")
                        active_chats.remove(chat_id)
                        return
                
                mentions, count = "", 0
                await human_delay(messages_sent)
                
        if mentions and chat_id in active_chats:
            base_msg = random.choice(msg_list).replace("{mention}", "").strip() if msg_list else static_text
            try:
                await event.client.send_message(chat_id, f"{base_msg}\n\n{mentions}")
            except Exception:
                pass
                    
    finally:
        if chat_id in active_chats:
            active_chats.remove(chat_id)
        await status.edit("✅ **Bulk tagging completed safely!**")


async def handle_user_tag(event, msg_list=None, static_text=None):
    chat_id = event.chat_id
    if chat_id in active_chats:
        return await event.reply("⚠️ **Tagging is already running in this chat. Type `.cancel` to stop it.**")
        
    status = await event.reply("✅ **Starting Per User Tag (Anti-Ban Mode)...**")
    active_chats.add(chat_id)
    messages_sent = 0
    
    try:
        for user in await get_users(event):
            if chat_id not in active_chats: 
                break
                
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            text = random.choice(msg_list).format(mention=mention) if msg_list else f"{mention} {static_text}"
            
            while True:
                try:
                    await event.client.send_message(chat_id, text)
                    messages_sent += 1
                    break
                except FloodWaitError as e:
                    if e.seconds > 60:
                        await event.reply(f"🛑 **FloodWait over 60s ({e.seconds}s)! Stopping to protect account.**")
                        active_chats.remove(chat_id)
                        return
                    await asyncio.sleep(e.seconds + 2)
                except (ChatWriteForbiddenError, UserBannedInChannelError):
                    await event.reply("🛑 **Error: I lack permission to send messages here or have been muted. Stopping.**")
                    active_chats.remove(chat_id)
                    return
                    
            await human_delay(messages_sent)
            
    finally:
        if chat_id in active_chats:
            active_chats.remove(chat_id)
        await status.edit("✅ **Per user tag completed safely!**")

# ==========================================
# COMMAND HANDLERS
# ==========================================

@CipherElite.on(events.NewMessage(pattern=r"^\.btag(?: |$)(.*)", outgoing=True))
@rishabh()
async def bulk_tag(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    
    custom_msg = event.pattern_match.group(1).strip()
    if not custom_msg:
        return await event.reply("❌ **Please provide a message. Example:** `.btag Hello everyone!`")
    
    await handle_bulk_tag(event, static_text=custom_msg)

@CipherElite.on(events.NewMessage(pattern=r"^\.utag(?: |$)(.*)", outgoing=True))
@rishabh()
async def user_tag(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    
    custom_msg = event.pattern_match.group(1).strip()
    if not custom_msg:
        return await event.reply("❌ **Please provide a message. Example:** `.utag Hello!`")
        
    await handle_user_tag(event, static_text=custom_msg)

@CipherElite.on(events.NewMessage(pattern=r"^\.btaggm$", outgoing=True))
@rishabh()
async def btag_gm(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    await handle_bulk_tag(event, msg_list=GM_MESSAGES)

@CipherElite.on(events.NewMessage(pattern=r"^\.utaggm$", outgoing=True))
@rishabh()
async def utag_gm(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    await handle_user_tag(event, msg_list=GM_MESSAGES)

@CipherElite.on(events.NewMessage(pattern=r"^\.btaggn$", outgoing=True))
@rishabh()
async def btag_gn(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    await handle_bulk_tag(event, msg_list=GN_MESSAGES)

@CipherElite.on(events.NewMessage(pattern=r"^\.utaggn$", outgoing=True))
@rishabh()
async def utag_gn(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    await handle_user_tag(event, msg_list=GN_MESSAGES)

@CipherElite.on(events.NewMessage(pattern=r"^\.btagvc$", outgoing=True))
@rishabh()
async def btag_vc(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    await handle_bulk_tag(event, msg_list=VC_MESSAGES)

@CipherElite.on(events.NewMessage(pattern=r"^\.utagvc$", outgoing=True))
@rishabh()
async def utag_vc(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    await handle_user_tag(event, msg_list=VC_MESSAGES)

@CipherElite.on(events.NewMessage(pattern=r"^\.cancel$", outgoing=True))
@rishabh()
async def cancel_tagging(event):
    if event.id in processed_msgs: return
    processed_msgs.append(event.id)
    
    chat_id = event.chat_id
    if chat_id in active_chats:
        active_chats.remove(chat_id)
        await event.reply("🛑 **Tagging process has been successfully canceled in this chat!**")
    else:
        await event.reply("⚠️ **No tagging process is currently running in this chat.**")
