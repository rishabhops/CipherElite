# =============================================================================
#  CipherElite Ghost Vault (Anti-Delete & Edit Tracker)
#  Author:         CipherElite Dev (@rishabhops)
# =============================================================================

import os
import json
from pathlib import Path
from telethon import events
from telethon.utils import get_display_name, get_peer_id

from config.config import Config
from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh  

# ==========================================
# DATABASE & CACHE SETUP
# ==========================================
DB_DIR = Path("DB")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "vault_db.json"

# In-memory cache to remember recent messages (Max 5000 messages to save RAM)
MESSAGE_CACHE = {} 
MAX_CACHE_SIZE = 5000
cache_keys = []

def load_db():
    if DB_PATH.exists():
        try:
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"global_vault": False, "monitored_chats": []}

def save_db(db):
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=4)

def cache_message(chat_id, msg_id, message_obj):
    """Silently stores recent messages in memory to expose them if deleted later."""
    global cache_keys
    key = f"{chat_id}_{msg_id}"
    
    if key not in MESSAGE_CACHE:
        cache_keys.append(key)
        
    MESSAGE_CACHE[key] = message_obj
    
    # Prevent memory leaks by removing oldest messages
    if len(cache_keys) > MAX_CACHE_SIZE:
        oldest_key = cache_keys.pop(0)
        MESSAGE_CACHE.pop(oldest_key, None)

def get_cached_message(chat_id, msg_id):
    return MESSAGE_CACHE.get(f"{chat_id}_{msg_id}")

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".vault on/off - Turn Ghost Vault ON or OFF globally for ALL chats",
        ".vaultchat on/off - Turn Ghost Vault ON or OFF for the CURRENT chat",
        ".vaultlist - View all explicitly monitored chats"
    ]
    description = (
        "🕵️‍♂️ **Ghost Vault (Anti-Delete/Edit)**\n"
        "👁️ Silently caches messages to catch deletions\n"
        "📝 Exposes what people wrote before they edited\n"
        "📥 Forwards all exposed data to your LOG_CHAT_ID\n\n"
    )
    add_handler("ghostvault", commands, description)

# ==========================================
# COMMAND HANDLERS
# ==========================================

@CipherElite.on(events.NewMessage(pattern=r"^\.vault(?: |$)(.*)", outgoing=True))
@rishabh()
async def toggle_global_vault(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return await event.reply("❌ **Error:** Please set `LOG_CHAT_ID` in your config.py first!")
        
    args = event.pattern_match.group(1).strip().lower()
    db = load_db()
    
    if args == "on":
        db["global_vault"] = True
        save_db(db)
        await event.reply("🕵️‍♂️ **Global Ghost Vault ENABLED!**\n*I am now tracking deleted & edited messages in ALL chats.*")
    elif args == "off":
        db["global_vault"] = False
        save_db(db)
        await event.reply("💤 **Global Ghost Vault DISABLED!**")
    else:
        await event.reply("❌ **Syntax Error:** Use `.vault on` or `.vault off`")


@CipherElite.on(events.NewMessage(pattern=r"^\.vaultchat(?: |$)(.*)", outgoing=True))
@rishabh()
async def toggle_chat_vault(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return await event.reply("❌ **Error:** Please set `LOG_CHAT_ID` in your config.py first!")
        
    args = event.pattern_match.group(1).strip().lower()
    chat_id = str(get_peer_id(event.chat_id))
    db = load_db()
    
    if args == "on":
        if chat_id not in db["monitored_chats"]:
            db["monitored_chats"].append(chat_id)
            save_db(db)
        await event.reply("🕵️‍♂️ **Vault is now monitoring THIS chat!**")
    elif args == "off":
        if chat_id in db["monitored_chats"]:
            db["monitored_chats"].remove(chat_id)
            save_db(db)
        await event.reply("💤 **Vault stopped monitoring this chat.**")
    else:
        await event.reply("❌ **Syntax Error:** Use `.vaultchat on` or `.vaultchat off`")


@CipherElite.on(events.NewMessage(pattern=r"^\.vaultlist$", outgoing=True))
@rishabh()
async def list_vault_chats(event):
    db = load_db()
    
    text = "🕵️‍♂️ **Ghost Vault Status:**\n\n"
    text += f"🌍 **Global Vault:** `{'🟢 ON' if db['global_vault'] else '🔴 OFF'}`\n\n"
    text += "📍 **Specifically Monitored Chats:**\n"
    
    if not db["monitored_chats"]:
        text += "None."
    else:
        for chat in db["monitored_chats"]:
            text += f"• `{chat}`\n"
            
    await event.reply(text)

# ==========================================
# THE GHOST VAULT LISTENERS
# ==========================================

# 1. Silently memorize messages as they arrive
@CipherElite.on(events.NewMessage(incoming=True))
async def message_cacher(event):
    db = load_db()
    chat_id = str(get_peer_id(event.chat_id)) if event.chat_id else None
    
    # Only cache if Global is ON, or if this specific chat is monitored
    if db["global_vault"] or (chat_id and chat_id in db["monitored_chats"]):
        cache_message(chat_id, event.id, event.message)


# 2. Catch Deleted Messages
@CipherElite.on(events.MessageDeleted())
async def catch_deletions(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return
        
    db = load_db()
    chat_id = str(get_peer_id(event.chat_id)) if event.chat_id else None
    
    if not db["global_vault"] and (not chat_id or chat_id not in db["monitored_chats"]):
        return
        
    for msg_id in event.deleted_ids:
        cached_msg = get_cached_message(chat_id, msg_id)
        if cached_msg:
            try:
                # Get Chat Name
                chat_entity = await event.client.get_entity(int(chat_id))
                chat_title = get_display_name(chat_entity)
                
                # Get User Name
                sender_entity = await cached_msg.get_sender()
                sender_name = get_display_name(sender_entity) if sender_entity else "Unknown User"
                
                log_text = (
                    f"🗑 **DELETED MESSAGE EXPOSED**\n\n"
                    f"👤 **User:** {sender_name}\n"
                    f"💬 **Chat:** {chat_title}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{cached_msg.text or '[Media/No Text]'}"
                )
                
                # Send to Log Group
                await event.client.send_message(
                    Config.LOG_CHAT_ID, 
                    message=log_text, 
                    file=cached_msg.media
                )
            except Exception as e:
                print(f"Vault Deletion Error: {e}")


# 3. Catch Edited Messages
@CipherElite.on(events.MessageEdited())
async def catch_edits(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return
        
    db = load_db()
    chat_id = str(get_peer_id(event.chat_id)) if event.chat_id else None
    
    if not db["global_vault"] and (not chat_id or chat_id not in db["monitored_chats"]):
        return
        
    cached_msg = get_cached_message(chat_id, event.id)
    if cached_msg and cached_msg.text != event.text:
        try:
            # Get Chat Name
            chat_entity = await event.client.get_entity(int(chat_id))
            chat_title = get_display_name(chat_entity)
            
            # Get User Name
            sender_entity = await event.get_sender()
            sender_name = get_display_name(sender_entity) if sender_entity else "Unknown User"
            
            log_text = (
                f"✏️ **EDITED MESSAGE EXPOSED**\n\n"
                f"👤 **User:** {sender_name}\n"
                f"💬 **Chat:** {chat_title}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🛑 **ORIGINAL (Before Edit):**\n{cached_msg.text or '[Media]'}\n\n"
                f"✅ **NEW (After Edit):**\n{event.text}"
            )
            
            await event.client.send_message(Config.LOG_CHAT_ID, log_text)
            
            # Update cache with the new message so future edits are tracked properly
            cache_message(chat_id, event.id, event.message)
            
        except Exception as e:
            print(f"Vault Edit Error: {e}")
