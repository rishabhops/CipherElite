# =============================================================================
#  CipherElite Roast Oracle (AI Auto-Pilot)
#  Author:         CipherElite Dev (@rishabhops)
# =============================================================================

import requests
import urllib.parse
import asyncio
from telethon import events
from telethon.utils import get_display_name

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# CONFIGURATION & STATE
# ==========================================
ROASTING_DATA = {}

# 🔥 THE NEW, HUMAN-LIKE SAVAGE PROMPT
ROAST_SYSTEM_PROMPT = """
You are a savage, witty friend roasting people in a Telegram chat.
RULES:
1. Roast them based EXACTLY on what they just said. No random metaphors. No robotic tech jokes.
2. Keep it under 25 words. Short, punchy, and brutally insulting.
3. Act like a real person, not an AI.
4. LANGUAGE IS CRITICAL:
   - If they speak Hindi/Hinglish (e.g., "kya kar raha hai", "dimag sahi hai?"), reply in pure, savage Hinglish street slang (e.g., "tere se matlab?", "apna dimaag check karle pehle").
   - If they speak English, use casual English slang.
5. End every reply with the 🔥 emoji.
"""

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".roast @username - Mark a user for automatic roasting",
        ".roast (reply) - Reply to someone to mark them",
        ".roast off - Stop auto-roasting in the current chat"
    ]
    description = (
        "🔥 **The Roast Oracle**\n"
        "🤖 AI-powered auto-replier.\n"
        "🎯 Mark a target and let the AI destroy them automatically.\n"
        "⚡ Uses Pollinations AI (No API Key required).\n\n"
    )
    add_handler("roast", commands, description)

# ==========================================
# AI GENERATOR FUNCTION
# ==========================================
def get_ai_roast(user_text):
    try:
        full_prompt = f"{ROAST_SYSTEM_PROMPT}\n\nTarget said: {user_text}"
        encoded = urllib.parse.quote(full_prompt)
        url = f"https://text.pollinations.ai/{encoded}?model=mistral" # Forcing Mistral model usually gives better/shorter text
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text.strip()
        return "You're so boring even my AI is lagging trying to roast you. 🔥"
    except Exception:
        return "I'd roast you, but I don't want to waste my server's RAM. 🔥"

# ==========================================
# COMMAND HANDLER
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"^\.roast(?: |$)(.*)", outgoing=True))
@rishabh
async def toggle_roast(event):
    args = event.pattern_match.group(1).strip().lower()
    chat_id = event.chat_id
    
    if args == "off":
        if chat_id in ROASTING_DATA:
            del ROASTING_DATA[chat_id]
            return await event.edit("✅ **Roast Oracle deactivated in this chat.**")
        return await event.edit("⚠️ **No roast target found in this chat.**")

    target_user = None
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        target_user = await reply_msg.get_sender()
    elif args:
        try:
            target_user = await event.client.get_entity(args)
        except Exception:
            return await event.edit("❌ **Error:** Could not find that user.")
    
    if not target_user:
        return await event.edit("❌ **Syntax:** `.roast @username` or reply to a message.")

    ROASTING_DATA[chat_id] = target_user.id
    target_name = get_display_name(target_user)
    
    await event.edit(f"🔥 **Target Locked:** `{target_name}`\n🤖 **Roast Oracle is now on Auto-Pilot.**")

# ==========================================
# THE AUTO-ROAST LISTENER
# ==========================================
@CipherElite.on(events.NewMessage(incoming=True))
async def auto_roaster(event):
    chat_id = event.chat_id
    
    if chat_id in ROASTING_DATA:
        target_id = ROASTING_DATA[chat_id]
        
        if event.sender_id == target_id:
            async with event.client.action(chat_id, 'typing'):
                roast_text = get_ai_roast(event.text or "...")
                await asyncio.sleep(2)
                await event.reply(roast_text)
