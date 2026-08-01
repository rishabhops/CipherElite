# update on: 09/07/2026

from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import os
import requests
from io import BytesIO

VERSION = "1.0.0"
CATEGORY = "developer"

# ─────────────── CONFIG ───────────────
LOGO_URL = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/cipher.jpg"
CHANNEL_LINK = "https://t.me/cipherelite_support"

def init(client_instance):
    commands = [
        ".send <plugin_name> - Send a plugin file from server"
    ]
    description = "📦 Send Plugin - Send any installed plugin file"
    add_handler("send", commands, description)

def get_thumb():
    """Download thumbnail image from GitHub"""
    try:
        response = requests.get(LOGO_URL, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        print(f"Thumb download error: {e}")
    return None

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.send\s+(.+)"))
    @rishabh()
    async def send_plugin(event):
        try:
            # Get plugin name
            plugin_name = event.pattern_match.group(1).strip().lower()
            
            # Remove .py if user adds it
            if plugin_name.endswith('.py'):
                plugin_name = plugin_name[:-3]
            
            plugin_path = f"./plugins/{plugin_name}.py"

            # Check if plugin exists
            if not os.path.exists(plugin_path):
                await event.reply(
                    f"❌ **Plugin not found!**\n\n"
                    f"📄 `{plugin_name}.py` does not exist in plugins folder.\n\n"
                    f"💡 Use `.plugins` to see available plugins."
                )
                return

            # Get sender info
            sender = await event.get_sender()
            user_mention = f"[{sender.first_name}](tg://user?id={sender.id})"

            # Build caption
            caption = (
                "🎭 **Cipher Elite Plugin Sender**\n\n"
                f"📦 **• Plugin name ≈** `{plugin_name}.py`\n"
                f"👤 **• Uploaded by ≈** {user_mention}\n\n"
                f"⚡ **[Powered by Cipher Elite]({CHANNEL_LINK})** ⚡"
            )

            # Get thumbnail
            thumb = get_thumb()

            # Send the file
            await event.client.send_file(
                event.chat_id,
                plugin_path,
                thumb=thumb,
                caption=caption,
                force_document=True,
                allow_cache=False,
                reply_to=event.reply_to_msg_id or event.id
            )

            # Delete the command message
            await event.delete()

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
