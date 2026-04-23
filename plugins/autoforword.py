# =============================================================================
#  CipherElite Advanced Auto-Forwarder & Cloner
#  Author:         CipherElite Dev (@rishabhops)
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
        ".addfwd <source> <dest> - Start live auto-forwarding",
        ".delfwd <source> <dest> - Stop auto-forwarding",
        ".listfwd - View all active forwarding routes",
        ".batchfwd <source> <dest> <limit> - Clone X amount of recent messages"
    ]
    description = (
        "🔄 **Advanced Auto-Forwarder**\n"
        "⚡ Ghost Clones (No Forward Tag)\n"
        "🔓 **Private Channels:** Fully supported using -100 IDs\n"
        "🔗 **Smart Buttons:** Inline URL buttons are safely converted to text links\n"
        "🚦 Multi-Route Support Included\n\n"
    )
    add_handler("autoforward", commands, description)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
async def get_chat_id(client, chat_link):
    """Safely resolves usernames, invite links, or integer IDs to exact Telethon Peer IDs."""
    try:
        if chat_link.lstrip('-').isdigit():
            chat_link = int(chat_link)
        entity = await client.get_entity(chat_link)
        return str(get_peer_id(entity))
    except Exception as e:
        return None

async def safe_clone(client, dest_id, msg):
    """
    Surgically extracts text and media to bypass Userbot restrictions.
    Smartly converts inline URL buttons into clickable text links at the bottom!
    """
    text = msg.text or ""
    
    # Check if the message has buttons (reply_markup)
    if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
        button_links = []
        for row in msg.reply_markup.rows:
            for button in row.buttons:
                # We can only extract buttons that have actual URLs
                if hasattr(button, 'url') and button.url:
                    button_links.append(f"🔗 **[{button.text}]({button.url})**")
        
        # If we found links, attach them to the bottom of the text
        if button_links:
            text += "\n\n" + "\n".join(button_links)

    # Send the surgically cloned message using the Userbot
    await client.send_message(
        int(dest_id),
        message=text,
        file=msg.media,
        link_preview=False # Keeps it clean
    )

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
        return await status.edit("❌ **Error:** Could not resolve Source or Destination. Make sure you are joined to both!")
        
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
    args = event.pattern_match.group(1).split()
    if len(args) != 3:
        return await event.reply("❌ **Syntax Error:** `.batchfwd <source> <dest> <limit>`\n*Example:* `.batchfwd @source @dest 50`")
        
    source_arg, dest_arg, limit_arg = args[0], args[1], args[2]
    
    if not limit_arg.isdigit():
        return await event.reply("❌ **Limit must be a number!**")
        
    limit = int(limit_arg)
    status = await event.reply("🔍 **Resolving chats & starting Batch Forward...**")
    
    source = await get_chat_id(event.client, source_arg)
    dest = await get_chat_id(event.client, dest_arg)
    
    if not source or not dest:
        return await status.edit("❌ **Error:** Could not resolve chats. Ensure you are joined!")
        
    await status.edit(f"⏳ **Fetching the last {limit} messages...**\n*This may take time due to anti-ban delays.*")
    
    count = 0
    try:
        # Fetch the newest `limit` messages normally
        messages = await event.client.get_messages(int(source), limit=limit)
        
        # Reverse the list so we send them in chronological order
        messages.reverse()
        
        for msg in messages:
            if not msg.text and not msg.media:
                continue 
                
            while True:
                try:
                    await safe_clone(event.client, dest, msg)
                    count += 1
                    break
                except FloodWaitError as e:
                    if e.seconds > 60:
                        return await event.reply(f"🛑 **FloodWait over 60s! Stopping batch to protect account.**")
                    await asyncio.sleep(e.seconds + 2)
                except ChatWriteForbiddenError:
                    return await event.reply("🛑 **Error: I lack permission to write in the destination chat.**")
                except Exception as e:
                    print(f"⚠️ Skipped message {msg.id} due to error: {e}")
                    break 
            
            await asyncio.sleep(2.5) # Anti-Ban delay
            
    except Exception as e:
        return await event.reply(f"⚠️ **Batch Stopped with error:** `{str(e)}`")
        
    await status.edit(f"✅ **Batch Forward Completed!**\nSuccessfully cloned the last `{count}` messages.")


# ==========================================
# THE LIVE AUTO-FORWARD ENGINE
# ==========================================
@CipherElite.on(events.NewMessage())
async def live_forward_worker(event):
    db = load_db()
    if not db["routes"]:
        return
        
    chat_id = str(get_peer_id(event.chat_id)) if event.chat_id else None
    
    if chat_id and chat_id in db["routes"]:
        destinations = db["routes"][chat_id]
        
        for dest in destinations:
            try:
                await safe_clone(event.client, dest, event.message)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
                try:
                    await safe_clone(event.client, dest, event.message)
                except:
                    pass
            except Exception as e:
                print(f"Live forward error: {e}")
