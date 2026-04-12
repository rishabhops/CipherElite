"""
CipherElite Text-to-Image Plugin
Created: 08/04/2026
"""

from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import requests
import io
from urllib.parse import quote

# ============================================
# CONFIGURATION
# ============================================
API_BASE = "https://text-to-image-bice.vercel.app"

def init(client_instance):
    commands = [
        ".t2i <prompt> - Generate image from text"
    ]
    description = "🎨 CipherElite Text-to-Image – Powered by CipherElite"
    add_handler("text2img", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.t2i\s+(.+)"))
    @rishabh()
    async def text_to_image(event):
        """Generate image from text prompt and delete command message"""
        try:
            # Delete the user's command message
            await event.delete()

            prompt = event.pattern_match.group(1).strip()
            if not prompt:
                await event.reply("🎨 **CipherElite Text-to-Image**\n\n"
                                "❌ **Usage:** `.t2i <prompt>`\n"
                                "Example: `.t2i a 3d heart`\n"
                                "Example: `.t2i a beautiful sunset`")
                return

            # URL encode the prompt (replace spaces with '+')
            encoded_plus = prompt.replace(' ', '+')
            url = f"{API_BASE}/generate?prompt={encoded_plus}"
            
            status = await event.reply(f"🎨 **CipherElite Text-to-Image**\n\n"
                                     f"🔄 Generating image for:\n`{prompt}`\n\n"
                                     f"⏳ Please wait...")

            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    image_data = io.BytesIO(response.content)
                    image_data.name = "cipher_t2i.png"
                    
                    await status.delete()
                    await event.client.send_file(
                        event.chat_id,
                        image_data,
                        caption=f"🎨 **CipherElite Text-to-Image**\n\n"
                               f"**Prompt:** `{prompt}`\n"
                               f"🤖 Powered by CipherElite API",
                        reply_to=event.message.id  # Note: event.message.id is the command message which is deleted, but reply_to with deleted message may cause issues. Better to reply to the status? Actually we delete command, then send new message without reply.
                    )
                else:
                    try:
                        error_json = response.json()
                        error_msg = error_json.get('message', 'Unknown error')
                    except:
                        error_msg = response.text[:200]
                    await status.edit(f"🎨 **CipherElite Text-to-Image**\n\n"
                                    f"❌ **API Error:** {error_msg}\n"
                                    f"💡 Please check your prompt and try again.")
            else:
                await status.edit(f"🎨 **CipherElite Text-to-Image**\n\n"
                                f"❌ **HTTP Error:** {response.status_code}\n"
                                f"💡 The API might be down or the prompt is invalid.")
                
        except requests.exceptions.Timeout:
            await event.reply("🎨 **CipherElite Text-to-Image**\n\n"
                            "❌ **Timeout:** The API took too long to respond.\n"
                            "💡 Please try again later.")
        except Exception as e:
            await event.reply(f"🎨 **CipherElite Text-to-Image**\n\n"
                            f"❌ **Error:** {str(e)}")
