import uuid
import asyncio
from telethon import events
from telethon.utils import get_display_name

from config.config import Config
from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# SHARED MEMORY DATABASE
# ==========================================
WHISPERS = {}

def init(client_instance):
    commands = [
        ".w @username <message> - Send a locked whisper to a specific user",
        ".w <message> - (Reply to someone) Send a locked whisper to them"
    ]
    description = (
        "🤫 **Inline Whisper (Dual-Client)**\n"
        "🔒 Sends a secret message hidden behind an inline button.\n"
        "🛑 Prevents anyone except the target from reading the popup.\n\n"
    )
    add_handler("whisper", commands, description)

@CipherElite.on(events.NewMessage(pattern=r"^\.w(?: |$)(.*)", outgoing=True))
@rishabh
async def send_whisper(event):
    # 1. INSTANTLY delete the message so nobody sees the secret text
    await event.delete()
    
    # 2. Send a temporary status message
    status = await event.respond("⏳ **Locking whisper...**")

    bot_username = getattr(Config, "TG_BOT_USERNAME", None)
    if not bot_username:
        return await status.edit("❌ **Error:** Please add `TG_BOT_USERNAME` to your config.py!")
        
    # Ensure it has the @ symbol
    if not bot_username.startswith("@"):
        bot_username = "@" + bot_username

    args = event.pattern_match.group(1).strip()
    target_entity = None
    secret_text = ""

    if event.is_reply:
        reply_msg = await event.get_reply_message()
        target_entity = await reply_msg.get_sender()
        secret_text = args
    else:
        parts = args.split(" ", 1)
        if len(parts) < 2:
            return await status.edit("❌ **Syntax Error:** Use `.w @username <message>` or reply to a user with `.w <message>`")
        try:
            target_entity = await event.client.get_entity(parts[0])
            secret_text = parts[1]
        except Exception:
            return await status.edit(f"❌ **Error:** Could not find user `{parts[0]}`. Make sure the username is correct.")

    if not target_entity or not secret_text:
        return await status.edit("❌ **Error:** Please provide a valid user and secret message.")

    # Generate unique ID and save to shared memory
    whisper_id = str(uuid.uuid4())[:8]
    WHISPERS[whisper_id] = {
        "sender": event.sender_id,
        "target": target_entity.id,
        "target_name": get_display_name(target_entity),
        "text": secret_text
    }

    # Query the Assistant Bot
    try:
        results = await event.client.inline_query(bot_username, f"w_{whisper_id}")
        if results:
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
            await status.delete() # Clean up status
        else:
            await status.edit("❌ **Error:** Assistant bot is not responding to inline queries.")
    except Exception as e:
        await status.edit(f"❌ **Inline Timeout/Error:** `{str(e)}`\n*Make sure whisper_bot.py is in your bot_plugins folder!*")
