# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    cipher_cmd
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
#        – Telegram:  @rishabhops
#
#  Thank you for respecting open-source software!
# =============================================================================

import asyncio
import json
import logging
import re
import os
from datetime import datetime, timedelta
from pathlib import Path
from openai import AsyncOpenAI, OpenAIError
from telethon import events, functions
from telethon.tl.types import ChatBannedRights, InputMediaUploadedPhoto
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from vars import ELITE_BOT_USERNAME

# DB setup for API key
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
API_KEY_FILE = DB_DIR / "api_key.txt"

# AI Configuration
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "mistralai/mistral-nemotron"

# AI System Prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Cipher AI, part of the CipherElite Userbot, created by @rishabhops. Parse natural language commands (e.g., 'ban karo isko', 'send sticker', 'pin this message') to identify the Telegram action and target. Return a JSON object with 'action' (e.g., 'ban', 'mute', 'send_message', 'pin'), 'target' (e.g., 'user', 'chat', 'message'), and 'details' (e.g., duration, content, media_type). Support a wide range of Telegram actions. Be concise, accurate, and avoid <think> blocks or markdown."
}

def load_api_key():
    """Load the API key from file"""
    try:
        if API_KEY_FILE.exists():
            with API_KEY_FILE.open("r", encoding="utf-8") as f:
                return f.read().strip()
        return None
    except Exception as e:
        logging.error(f"API key load error: {e}")
        return None

def save_api_key(api_key):
    """Save the API key to file"""
    try:
        with API_KEY_FILE.open("w", encoding="utf-8") as f:
            f.write(api_key)
        os.chmod(API_KEY_FILE, 0o600)
        return True
    except Exception as e:
        logging.error(f"API key save error: {e}")
        return False

# Initialize OpenAI client
api_key = load_api_key()
if not api_key:
    logging.warning("NVIDIA_API_KEY not found. AI features will fail.")
client = AsyncOpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=api_key or "dummy_key"
)

def init(client):
    """Initialize the cipher_cmd plugin"""
    commands = [
        f".cipher <instruction> — Issue a natural language command (e.g., ban karo isko, send sticker, pin this message)",
        f".cipher setkey <key> — Set the NVIDIA API key"
    ]
    description = "Execute any Telegram action with Cipher AI"
    add_handler("cipher_cmd", commands, description)
    print("🤖 Cipher Command Plugin initialized successfully")
    return True

async def parse_command(instruction):
    """Parse command using Cipher AI"""
    if not api_key:
        return None

    try:
        stream = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                SYSTEM_PROMPT,
                {"role": "user", "content": instruction}
            ],
            temperature=0.6,
            top_p=0.7,
            max_tokens=256,
            stream=True
        )
        response = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
        return json.loads(response) if response else None
    except Exception as e:
        logging.error(f"AI command parsing error: {e}")
        return None

@CipherElite.on(events.NewMessage(pattern=r"\.cipher(?:\s+(.*))?"))
@rishabh()
async def cipher_handler(event):
    """Handle .cipher commands"""
    instruction = event.pattern_match.group(1)
    if not instruction:
        await event.reply(f"❓ **Usage:** `{ELITE_BOT_USERNAME} .cipher <instruction>`\n\n**Examples:**\n• `.cipher ban karo isko` (reply to user)\n• `.cipher mute isko 1 hour`\n• `.cipher send message Hello`\n• `.cipher pin this message` (reply to message)\n• `.cipher setkey <key>`")
        return

    if instruction.startswith("setkey"):
        key = instruction[6:].strip()
        if not key:
            await event.reply("❌ **Error:** Provide an API key with `.cipher setkey <key>`.")
            return
        if save_api_key(key):
            global api_key, client
            api_key = key
            client = AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)
            await event.reply("✅ **API Key Set:** Stored securely.")
            print("✅ API key stored")
        else:
            await event.reply("❌ **Error:** Failed to store API key.")
        return

    if not api_key:
        await event.reply("❌ **Error:** NVIDIA API key not set. Use `.cipher setkey <key>`.")
        return

    thinking_msg = await event.reply("🤔 **Cipher AI is processing your command...**")
    print(f"🤖 Processing command: {instruction[:50]}...")

    # Get context: replied-to user or message
    reply = await event.get_reply_message()
    target_user = None
    target_user_id = None
    target_message_id = None
    chat_id = event.chat_id
    if reply:
        try:
            target_user = await reply.get_sender()
            target_user_id = target_user.id if target_user else None
            target_message_id = reply.id
        except Exception:
            target_user_id = None
            target_message_id = reply.id if reply else None

    # Parse command with AI
    parsed = await parse_command(instruction)
    if not parsed:
        await thinking_msg.edit("❌ **Error:** Could not parse command. Try a clearer instruction (e.g., 'ban karo isko').")
        return

    action = parsed.get("action")
    target = parsed.get("target")
    details = parsed.get("details", {})

    try:
        if action == "ban":
            if not target_user_id or target != "user":
                await thinking_msg.edit("❌ **Error:** Reply to a user to ban.")
                return
            await event.client(functions.channels.EditBannedRequest(
                channel=chat_id,
                participant=target_user_id,
                banned_rights=ChatBannedRights(
                    until_date=None,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_inline=True,
                    embed_links=True
                )
            ))
            await thinking_msg.edit(f"✅ **Banned:** User `{target_user_id}` in chat `{chat_id}`.")
            print(f"✅ Banned user {target_user_id} in chat {chat_id}")

        elif action == "mute":
            if not target_user_id or target != "user":
                await thinking_msg.edit("❌ **Error:** Reply to a user to mute.")
                return
            duration = details.get("duration", None)
            until_date = None
            if duration:
                try:
                    if "hour" in duration.lower():
                        hours = int(re.search(r'\d+', duration).group())
                        until_date = datetime.now() + timedelta(hours=hours)
                    elif "minute" in duration.lower():
                        minutes = int(re.search(r'\d+', duration).group())
                        until_date = datetime.now() + timedelta(minutes=minutes)
                except:
                    until_date = None
            await event.client(functions.channels.EditBannedRequest(
                channel=chat_id,
                participant=target_user_id,
                banned_rights=ChatBannedRights(
                    until_date=until_date,
                    send_messages=True
                )
            ))
            duration_text = f"for {duration}" if duration else "indefinitely"
            await thinking_msg.edit(f"✅ **Muted:** User `{target_user_id}` {duration_text} in chat `{chat_id}`.")
            print(f"✅ Muted user {target_user_id} {duration_text} in chat {chat_id}")

        elif action == "kick":
            if not target_user_id or target != "user":
                await thinking_msg.edit("❌ **Error:** Reply to a user to kick.")
                return
            await event.client(functions.channels.EditParticipantRequest(
                channel=chat_id,
                participant=target_user_id,
                banned_rights=None
            ))
            await event.client.kick_participant(chat_id, target_user_id)
            await thinking_msg.edit(f"✅ **Kicked:** User `{target_user_id}` from chat `{chat_id}`.")
            print(f"✅ Kicked user {target_user_id} from chat {chat_id}")

        elif action == "send_message":
            message_content = details.get("content", "")
            if not message_content:
                await thinking_msg.edit("❌ **Error:** Specify a message to send (e.g., 'send message Hello').")
                return
            target_id = target_user_id if target == "user" and target_user_id else chat_id
            await event.client.send_message(target_id, message_content)
            await thinking_msg.edit(f"✅ **Message Sent:** '{message_content}' to {'user' if target_user_id else 'chat'} `{target_id}`.")
            print(f"✅ Sent message to {target_id}: {message_content[:30]}...")

        elif action == "send_sticker":
            sticker = details.get("sticker_id", None) or "CAACAgIAAxkBAAIBJ2cB8yY1l0Z5z3Xz7x0AAf7Z6YqFAAIAAAM7YCQU1c6A4pL2t0A4BA"  # Default sticker
            target_id = target_user_id if target == "user" and target_user_id else chat_id
            await event.client.send_file(target_id, file=sticker, force_document=False)
            await thinking_msg.edit(f"✅ **Sticker Sent:** To {'user' if target_user_id else 'chat'} `{target_id}`.")
            print(f"✅ Sent sticker to {target_id}")

        elif action == "send_photo":
            photo_url = details.get("photo_url", None)
            if not photo_url:
                await thinking_msg.edit("❌ **Error:** Specify a photo URL (e.g., 'send photo <url>').")
                return
            target_id = target_user_id if target == "user" and target_user_id else chat_id
            try:
                await event.client.send_file(target_id, file=photo_url, force_document=False)
                await thinking_msg.edit(f"✅ **Photo Sent:** To {'user' if target_user_id else 'chat'} `{target_id}`.")
                print(f"✅ Sent photo to {target_id}")
            except Exception as e:
                await thinking_msg.edit(f"❌ **Photo Error:** Invalid URL or access issue.")
                print(f"❌ Photo error: {e}")

        elif action == "pin":
            if not target_message_id or target != "message":
                await thinking_msg.edit("❌ **Error:** Reply to a message to pin.")
                return
            await event.client(functions.messages.UpdatePinnedMessageRequest(
                peer=chat_id,
                id=target_message_id,
                unpin=False
            ))
            await thinking_msg.edit(f"✅ **Pinned:** Message `{target_message_id}` in chat `{chat_id}`.")
            print(f"✅ Pinned message {target_message_id} in chat {chat_id}")

        elif action == "unpin":
            if not target_message_id or target != "message":
                await thinking_msg.edit("❌ **Error:** Reply to a message to unpin.")
                return
            await event.client(functions.messages.UpdatePinnedMessageRequest(
                peer=chat_id,
                id=target_message_id,
                unpin=True
            ))
            await thinking_msg.edit(f"✅ **Unpinned:** Message `{target_message_id}` in chat `{chat_id}`.")
            print(f"✅ Unpinned message {target_message_id} in chat {chat_id}")

        elif action == "delete":
            if not target_message_id or target != "message":
                await thinking_msg.edit("❌ **Error:** Reply to a message to delete.")
                return
            await event.client.delete_messages(chat_id, [target_message_id])
            await thinking_msg.edit(f"✅ **Deleted:** Message `{target_message_id}` in chat `{chat_id}`.")
            print(f"✅ Deleted message {target_message_id} in chat {chat_id}")

        elif action == "invite":
            if not target_user_id or target != "user":
                await thinking_msg.edit("❌ **Error:** Reply to a user to invite.")
                return
            await event.client(functions.channels.InviteToChannelRequest(
                channel=chat_id,
                users=[target_user_id]
            ))
            await thinking_msg.edit(f"✅ **Invited:** User `{target_user_id}` to chat `{chat_id}`.")
            print(f"✅ Invited user {target_user_id} to chat {chat_id}")

        else:
            await thinking_msg.edit(f"❌ **Unknown Action:** '{action}' not supported. Try 'ban', 'mute', 'send message', 'pin', etc.")
            print(f"❌ Unknown action: {action}")

    except Exception as e:
        await thinking_msg.edit(f"❌ **Error:** {str(e)}")
        print(f"❌ Command error: {e}")

print("✅ Cipher Command Plugin loaded successfully")
