# =============================================================================
#  CipherElite Advanced Auto-Forwarder & Cloner
#  Author:         CipherElite Dev rishabh (@rishabhops)
#. telegram username - @thanosceo
# =============================================================================

import os
import json
import asyncio
from pathlib import Path
from telethon import events
from telethon.errors import FloodWaitError, ChatWriteForbiddenError
from telethon.utils import get_peer_id

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh  

# ==========================================
# DATABASE SETUP
# ==========================================
DB_DIR = Path("DB")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "autofwd_db.json"

def load_db():
    if DB_PATH.exists():
        try:
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"routes": {}} # Format: {"source_id": ["dest_id_1", "dest_id_2"]}

def save_db(db):
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=4)

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".addfwd <source> <dest> - Start live auto-forwarding from source to destination",
        ".delfwd <source> <dest> - Stop auto-forwarding between these chats",
        ".listfwd - View all active forwarding routes",
        ".batchfwd <source> <dest> <limit> - Clone X amount of old messages to destination"
    ]
    description = (
        "🔄 **Advanced Auto-Forwarder**\n"
        "⚡ Ghost Clones (No Forward Tag)\n"
        "🔓 Works on Private/Restricted Channels\n"
        "🚦 Multi-Route Support Included\n\n"
    )
    add_handler("autoforward", commands, description)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
async def get_chat_id(client, chat_link):
    """Safely resolves usernames, invite links, or integer IDs to exact Telethon Peer IDs."""
    try:
        # If it's a number string, convert to int
        if chat_link.lstrip('-').isdigit():
            chat_link = int(chat_link)
        
        entity = await client.get_entity(chat_link)
        return str(get_peer_id(entity))
    except Exception as e:
        return None

# ==========================================
# COMMAND HANDLERS
# ==========================================

@CipherElite.on(events.NewMessage(pattern=r"^\.addfwd(?: |$)(.*)", outgoing=True))
@rishabh()
async def add_forward(event):
    args = event.pattern_match.group(1).split()
    if len(args) != 2:
        return await event.reply("❌ **Syntax Error:** `.addfwd <source_id/username> <dest_id/username>`")
    
    status = await event.reply("🔍 **Resolving chats...**")
    
    source = await get_chat_id(event.client, args[0])
    dest = await get_chat_id(event.client, args[1])
    
    if not source or not dest:
        return await status.edit("❌ **Error:** Could not resolve Source or Destination. Make sure you have joined both chats!")
        
    db = load_db()
    if source not in db["routes"]:
        db["routes"][source] = []
        
    if dest in db["routes"][source]:
        return await status.edit("⚠️ **This route is already active!**")
        
    db["routes"][source].append(dest)
    save_db(db)
    
    await status.edit(f"✅ **Auto-Forward Link Created!**\n\n**Source:** `{source}`\n**Dest:** `{dest}`\n\n*Listening for new messages...*")


@CipherElite.on(events.NewMessage(pattern=r"^\.delfwd(?: |$)(.*)", outgoing=True))
@rishabh()
async def del_forward(event):
    args = event.pattern_match.group(1).split()
    if len(args) != 2:
        return await event.reply("❌ **Syntax Error:** `.delfwd <source_id/username> <dest_id/username>`")
        
    source = await get_chat_id(event.client, args[0])
    dest = await get_chat_id(event.client, args[1])
    
    db = load_db()
    
    if source in db["routes"] and dest in db["routes"][source]:
        db["routes"][source].remove(dest)
        # Cleanup empty source keys
        if not db["routes"][source]:
            del db["routes"][source]
            
        save_db(db)
        await event.reply(f"🗑️ **Forwarding route deleted successfully!**")
    else:
        await event.reply("⚠️ **Could not find this route in the database.**")


@CipherElite.on(events.NewMessage(pattern=r"^\.listfwd$", outgoing=True))
@rishabh()
async def list_forward(event):
    db = load_db()
    routes = db.get("routes", {})
    
    if not routes:
        return await event.reply("📭 **You have no active forwarding routes.**")
        
    text = "🔄 **Active Auto-Forward Routes:**\n\n"
    for source, destinations in routes.items():
        text += f"📡 **Source:** `{source}`\n"
        for dest in destinations:
            text += f"   ↳ 🎯 **Dest:** `{dest}`\n"
        text += "\n"
        
    await event.reply(text)


@CipherElite.on(events.NewMessage(pattern=r"^\.batchfwd(?: |$)(.*)", outgoing=True))
@rishabh()
async def batch_forward(event):
    """Clones historical messages from a chat."""
    args = event.pattern_match.group(1).split()
    if len(args) != 3:
        return await event.reply("❌ **Syntax Error:** `.batchfwd <source> <dest> <limit>`\n*Example:* `.batchfwd @source_channel @my_channel 50`")
        
    source_arg, dest_arg, limit_arg = args[0], args[1], args[2]
    
    if not limit_arg.isdigit():
        return await event.reply("❌ **Limit must be a number!**")
        
    limit = int(limit_arg)
    status = await event.reply("🔍 **Resolving chats & starting Batch Forward...**")
    
    source = await get_chat_id(event.client, source_arg)
    dest = await get_chat_id(event.client, dest_arg)
    
    if not source or not dest:
        return await status.edit("❌ **Error:** Could not resolve chats. Ensure you are joined!")
        
    await status.edit(f"⏳ **Batch Cloning {limit} messages...**\n*This may take time due to anti-ban delays.*")
    
    count = 0
    try:
        # reverse=True fetches the oldest messages first (chronological order)
        async for msg in event.client.iter_messages(int(source), limit=limit, reverse=True):
            if not msg.text and not msg.media:
                continue # Skip empty service messages
                
            while True:
                try:
                    # Using send_message with 'msg' object copies the message without Forward Tag
                    await event.client.send_message(int(dest), msg)
                    count += 1
                    break
                except FloodWaitError as e:
                    if e.seconds > 60:
                        return await event.reply(f"🛑 **FloodWait over 60s! Stopping batch to protect account.**")
                    await asyncio.sleep(e.seconds + 2)
                except ChatWriteForbiddenError:
                    return await event.reply("🛑 **Error: I lack permission to write in the destination chat.**")
            
            # Anti-Ban delay between each message
            await asyncio.sleep(2.5)
            
    except Exception as e:
        return await event.reply(f"⚠️ **Batch Stopped with error:** `{str(e)}`")
        
    await status.edit(f"✅ **Batch Forward Completed!**\nSuccessfully cloned `{count}` messages.")

# ==========================================
# THE LIVE AUTO-FORWARD ENGINE
# ==========================================

@CipherElite.on(events.NewMessage())
async def live_forward_worker(event):
    # Only process if we have active routes
    db = load_db()
    if not db["routes"]:
        return
        
    # Get the ID of the chat this message was sent in
    chat_id = str(get_peer_id(event.chat_id)) if event.chat_id else None
    
    # Check if this chat is registered as a source
    if chat_id and chat_id in db["routes"]:
        destinations = db["routes"][chat_id]
        
        for dest in destinations:
            try:
                # Ghost clone the message to destination (no forward tag)
                await event.client.send_message(int(dest), event.message)
            except FloodWaitError as e:
                # If we hit floodwait, we sleep in the background
                await asyncio.sleep(e.seconds)
                try:
                    await event.client.send_message(int(dest), event.message)
                except:
                    pass
            except Exception:
                pass # Silently pass to avoid crashing the worker
