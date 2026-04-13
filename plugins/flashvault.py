# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    flashvault.py (Anti-View-Once Media Saver)
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
from telethon.utils import get_display_name, get_peer_id

from config.config import Config
from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# DATABASE SETUP
# ==========================================
DB_DIR = Path("DB")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "flashvault_db.json"

def load_db():
    if DB_PATH.exists():
        try:
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"global_flash": False, "monitored_chats": []}

def save_db(db):
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=4)

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".flash on/off - Turn Auto-Save ON/OFF globally for all incoming View-Once media",
        ".flashchat on/off - Turn Auto-Save ON/OFF for the current chat only",
        ".flashlist - View your active FlashVault monitoring settings",
        ".saveflash - Reply to ANY media (view-once or normal) to manually save it to your Log Group"
    ]
    description = (
        "📸 **FlashVault (Anti-View-Once)**\n"
        "⚡ Automatically detects self-destructing photos & videos.\n"
        "📥 Secretly downloads and forwards them to your Log Group.\n"
        "🧹 Auto-cleans server storage to prevent lag.\n\n"
    )
    add_handler("flashvault", commands, description)

# ==========================================
# COMMAND HANDLERS
# ==========================================

@CipherElite.on(events.NewMessage(pattern=r"^\.flash(?: |$)(.*)", outgoing=True))
@rishabh()
async def toggle_global_flash(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return await event.reply("❌ **Error:** Please set `LOG_CHAT_ID` in your config.py first!")
        
    args = event.pattern_match.group(1).strip().lower()
    db = load_db()
    
    if args == "on":
        db["global_flash"] = True
        save_db(db)
        await event.reply("📸 **Global FlashVault ENABLED!**\n*I will secretly save all View-Once media to your Log Group.*")
    elif args == "off":
        db["global_flash"] = False
        save_db(db)
        await event.reply("💤 **Global FlashVault DISABLED!**")
    else:
        await event.reply("❌ **Syntax Error:** Use `.flash on` or `.flash off`")


@CipherElite.on(events.NewMessage(pattern=r"^\.flashchat(?: |$)(.*)", outgoing=True))
@rishabh()
async def toggle_chat_flash(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return await event.reply("❌ **Error:** Please set `LOG_CHAT_ID` in your config.py first!")
        
    args = event.pattern_match.group(1).strip().lower()
    chat_id = str(get_peer_id(event.chat_id))
    db = load_db()
    
    if args == "on":
        if chat_id not in db["monitored_chats"]:
            db["monitored_chats"].append(chat_id)
            save_db(db)
        await event.reply("📸 **FlashVault is now monitoring THIS chat for View-Once media!**")
    elif args == "off":
        if chat_id in db["monitored_chats"]:
            db["monitored_chats"].remove(chat_id)
            save_db(db)
        await event.reply("💤 **FlashVault stopped monitoring this chat.**")
    else:
        await event.reply("❌ **Syntax Error:** Use `.flashchat on` or `.flashchat off`")


@CipherElite.on(events.NewMessage(pattern=r"^\.flashlist$", outgoing=True))
@rishabh()
async def list_flash_chats(event):
    db = load_db()
    
    text = "📸 **FlashVault Status:**\n\n"
    text += f"🌍 **Global Auto-Save:** `{'🟢 ON' if db['global_flash'] else '🔴 OFF'}`\n\n"
    text += "📍 **Specifically Monitored Chats:**\n"
    
    if not db["monitored_chats"]:
        text += "None."
    else:
        for chat in db["monitored_chats"]:
            text += f"• `{chat}`\n"
            
    await event.reply(text)


@CipherElite.on(events.NewMessage(pattern=r"^\.saveflash$", outgoing=True))
@rishabh()
async def manual_flash_download(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return await event.reply("❌ **Error:** Please set `LOG_CHAT_ID` in your config.py first!")

    reply_msg = await event.get_reply_message()
    if not reply_msg or not reply_msg.media:
        return await event.reply("❌ **Please reply to a photo or video to save it!**")

    status = await event.reply("📥 **Downloading media...**")
    try:
        downloaded_file = await reply_msg.download_media()
        if downloaded_file:
            await event.client.send_file(
                Config.LOG_CHAT_ID,
                downloaded_file,
                caption="📸 **Manually Saved Media**\n*Source:* Triggered via `.saveflash`"
            )
            os.remove(downloaded_file) # Cleanup!
            await status.edit("✅ **Media successfully saved to your Log Group!**")
        else:
            await status.edit("❌ **Failed to download media.**")
    except Exception as e:
        await status.edit(f"❌ **Error:** `{str(e)}`")


# ==========================================
# THE FLASHVAULT AUTO-LISTENER
# ==========================================
# Note: No @rishabh decorator here because it must listen to incoming messages!
@CipherElite.on(events.NewMessage(incoming=True))
async def auto_media_downloader(event):
    if not getattr(Config, "LOG_CHAT_ID", None):
        return

    # Check if the message contains media
    if not event.media:
        return

    # Check if it's a self-destructing/view-once media
    # Telegram flags these either via media_unread or a ttl_seconds attribute
    is_view_once = getattr(event, 'media_unread', False) or getattr(event.media, 'ttl_seconds', None) is not None

    if not is_view_once:
        return

    db = load_db()
    chat_id = str(get_peer_id(event.chat_id)) if event.chat_id else None
    
    # Only process if Global is ON, or if this specific chat is monitored
    if db["global_flash"] or (chat_id and chat_id in db["monitored_chats"]):
        try:
            # Download the secret media
            downloaded_file = await event.download_media()
            
            if downloaded_file:
                # Get sender info for context
                sender = await event.get_sender()
                sender_name = get_display_name(sender) if sender else "Unknown User"
                
                caption = (
                    f"📸 **INTERCEPTED VIEW-ONCE MEDIA**\n\n"
                    f"👤 **From:** {sender_name}\n"
                    f"💬 **Chat ID:** `{chat_id}`"
                )
                
                # Secretly send to Log Chat
                await event.client.send_file(
                    Config.LOG_CHAT_ID,
                    downloaded_file,
                    caption=caption
                )
                
                # Delete the physical file from the bot's server to save space
                os.remove(downloaded_file)
                
        except Exception as e:
            print(f"FlashVault Auto-Save Error: {e}")
