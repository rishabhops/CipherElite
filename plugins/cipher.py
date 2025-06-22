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
from cryptography.fernet import Fernet
from openai import AsyncOpenAI, OpenAIError
from telethon import events, functions
from telethon.tl.types import ChatBannedRights
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from vars import ELITE_BOT_USERNAME

# DB setup for encrypted API key
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
ENCRYPTED_KEY_FILE = DB_DIR / "api_key.enc"
FERNET_KEY_FILE = DB_DIR / "fernet.key"

# AI Configuration
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "mistralai/mistral-nemotron"

# AI System Prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Cipher AI, part of the CipherElite Userbot, created by @rishabhops. Parse natural language commands (e.g., 'ban karo isko', 'mute isko', 'message karo Hello') to identify the action (ban, mute, kick, message) and target (user or chat). Return a JSON object with 'action' (e.g., 'ban', 'mute', 'kick', 'message'), 'target' (e.g., 'user', 'chat'), and 'details' (e.g., duration for mute, message content). Be concise and accurate, avoiding <think> blocks or markdown."
}

def get_fernet_key():
    """Generate or load Fernet key for encryption/decryption"""
    if not FERNET_KEY_FILE.exists():
        key = Fernet.generate_key()
        with FERNET_KEY_FILE.open("wb") as f:
            f.write(key)
        os.chmod(FERNET_KEY_FILE, 0o600)
    with FERNET_KEY_FILE.open("rb") as f:
        return f.read()

def encrypt_api_key(api_key):
    """Encrypt and store the API key"""
    try:
        fernet = Fernet(get_fernet_key())
        encrypted_key = fernet.encrypt(api_key.encode())
        with ENCRYPTED_KEY_FILE.open("wb") as f:
            f.write(encrypted_key)
        os.chmod(ENCRYPTED_KEY_FILE, 0o600)
        return True
    except Exception as e:
        logging.error(f"API key encryption error: {e}")
        return False

def decrypt_api_key():
    """Decrypt the API key"""
    try:
        fernet = Fernet(get_fernet_key())
        with ENCRYPTED_KEY_FILE.open("rb") as f:
            encrypted_key = f.read()
        return fernet.decrypt(encrypted_key).decode()
    except Exception as e:
        logging.error(f"API key decryption error: {e}")
        return None

# Initialize OpenAI client
api_key = decrypt_api_key()
if not api_key:
    logging.warning("Failed to decrypt NVIDIA_API_KEY. AI features will fail.")
client = AsyncOpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=api_key or "dummy_key"
)

def init(client):
    """Initialize the cipher_cmd plugin"""
    commands = [
        f".cipher <instruction> — Issue a natural language command (e.g., ban karo isko, mute isko, message karo Hello)",
        f".cipher setkey <key> — Set the encrypted NVIDIA API key"
    ]
    description = "Execute natural language commands with Cipher AI"
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
        await event.reply(f"❓ **Usage:** `{ELITE_BOT_USERNAME} .cipher <instruction>`\n\n**Examples:**\n• `.cipher ban karo isko` (reply to user)\n• `.cipher mute isko 1 hour`\n• `.cipher message karo Hello`\n• `.cipher setkey <key>`")
        return

    if instruction.startswith("setkey"):
        key = instruction[6:].strip()
        if not key:
            await event.reply("❌ **Error:** Provide an API key with `.cipher setkey <key>`.")
            return
        if encrypt_api_key(key):
            await event.reply("✅ **API Key Set:** Encrypted and stored securely.")
            print("✅ API key encrypted and stored")
        else:
            await event.reply("❌ **Error:** Failed to encrypt API key.")
        return

    if not api_key:
        await event.reply("❌ **Error:** NVIDIA API key not set. Use `.cipher setkey <key>`.")
        return

    thinking_msg = await event.reply("🤔 **Cipher AI is processing your command...**")
    print(f"🤖 Processing command: {instruction[:50]}...")

    # Get replied-to user or chat
    reply = await event.get_reply_message()
    target_user = None
    chat_id = event.chat_id
    if reply:
        try:
            target_user = await reply.get_sender()
            target_user_id = target_user.id
        except Exception:
            target_user_id = None
    else:
        target_user_id = None

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
            try:
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
            except Exception as e:
                await thinking_msg.edit(f"❌ **Ban Error:** {str(e)}")
                print(f"❌ Ban error: {e}")

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
            try:
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
            except Exception as e:
                await thinking_msg.edit(f"❌ **Mute Error:** {str(e)}")
                print(f"❌ Mute error: {e}")

        elif action == "kick":
            if not target_user_id or target != "user":
                await thinking_msg.edit("❌ **Error:** Reply to a user to kick.")
                return
            try:
                await event.client(functions.channels.EditParticipantRequest(
                    channel=chat_id,
                    participant=target_user_id,
                    banned_rights=None
                ))
                await event.client.kick_participant(chat_id, target_user_id)
                await thinking_msg.edit(f"✅ **Kicked:** User `{target_user_id}` from chat `{chat_id}`.")
                print(f"✅ Kicked user {target_user_id} from chat {chat_id}")
            except Exception as e:
                await thinking_msg.edit(f"❌ **Kick Error:** {str(e)}")
                print(f"❌ Kick error: {e}")

        elif action == "message":
            message_content = details.get("content", "")
            if not message_content:
                await thinking_msg.edit("❌ **Error:** Specify a message to send (e.g., 'message karo Hello').")
                return
            target_id = target_user_id if target == "user" and target_user_id else chat_id
            try:
                await event.client.send_message(target_id, message_content)
                await thinking_msg.edit(f"✅ **Message Sent:** '{message_content}' to {'user' if target_user_id else 'chat'} `{target_id}`.")
                print(f"✅ Sent message to {target_id}: {message_content[:30]}...")
            except Exception as e:
                await thinking_msg.edit(f"❌ **Message Error:** {str(e)}")
                print(f"❌ Message error: {e}")

        else:
            await thinking_msg.edit(f"❌ **Unknown Action:** '{action}' not supported. Try 'ban', 'mute', 'kick', or 'message'.")
            print(f"❌ Unknown action: {action}")

    except Exception as e:
        await thinking_msg.edit(f"❌ **Error:** {str(e)}")
        print(f"❌ Command error: {e}")

print("✅ Cipher Command Plugin loaded successfully")
