# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    carbon
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
# import urllib.parse moved to top
import aiohttp
import random
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".carbon <reply/code> - Create carbon code image",
        ".rcarbon <reply/code> - Random background carbon",
        ".rayso <reply/code> - Create rayso code image"
    ]
    description = "Carbon/Code Beautify for creating beautiful code screenshots"
    add_handler("carbon", commands, description)

# Carbon themes
CARBON_THEMES = [
    "3024-night", "a11y-dark", "blackboard", "base16-dark",
    "base16-light", "cobalt", "dracula", "duotone-dark",
    "hopscotch", "lucario", "material", "monokai",
    "night-owl", "nord", "oceanic-next", "one-light",
    "one-dark", "panda-syntax", "paraiso-dark", "seti",
    "shades-of-purple", "solarized-dark", "solarized-light",
    "synthwave-84", "twilight", "verminal", "vscode",
    "yeti", "zenburn"
]

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.carbon"))
    @rishabh()
    async def carbon(event):
        # Get code from reply or text
        if event.is_reply:
            reply = await event.get_reply_message()
            code = reply.text or reply.message
        else:
            text = event.text.split(maxsplit=1)
            if len(text) < 2:
                await event.reply("❌ Usage: `.carbon <code>` or reply to a message")
                return
            code = text[1]
        
        if not code:
            await event.reply("❌ No code provided!")
            return
        
        msg = await event.reply("🎨 Creating carbon image...")
        
        try:
            # Use Carbon API
            carbon_url = "https://carbonara.solopov.dev/api/cook"
            
            payload = {
                "code": code,
                "theme": "monokai",
                "backgroundColor": "rgba(171, 184, 195, 1)",
                "dropShadow": True,
                "dropShadowOffsetY": "20px",
                "dropShadowBlurRadius": "68px",
                "fontFamily": "Fira Code",
                "fontSize": "14px",
                "lineNumbers": True,
                "paddingVertical": "56px",
                "paddingHorizontal": "56px",
                "exportSize": "2x",
                "widthAdjustment": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(carbon_url, json=payload) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        
                        # Save to file
                        file_path = "/tmp/carbon.png"
                        with open(file_path, 'wb') as f:
                            f.write(image_data)
                        
                        # Send the image
                        await event.client.send_file(
                            event.chat_id,
                            file_path,
                            caption="✨ Created with Carbon"
                        )
                        
                        await msg.delete()
                        
                        # Clean up
                        import os
                        os.remove(file_path)
                    else:
                        await msg.edit(f"❌ Failed to create carbon image! Status: {resp.status}")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.rcarbon"))
    @rishabh()
    async def rcarbon(event):
        # Get code from reply or text
        if event.is_reply:
            reply = await event.get_reply_message()
            code = reply.text or reply.message
        else:
            text = event.text.split(maxsplit=1)
            if len(text) < 2:
                await event.reply("❌ Usage: `.rcarbon <code>` or reply to a message")
                return
            code = text[1]
        
        if not code:
            await event.reply("❌ No code provided!")
            return
        
        msg = await event.reply("🎨 Creating carbon image with random theme...")
        
        try:
            # Random theme
            theme = random.choice(CARBON_THEMES)
            
            carbon_url = "https://carbonara.solopov.dev/api/cook"
            
            payload = {
                "code": code,
                "theme": theme,
                "backgroundColor": "rgba(171, 184, 195, 1)",
                "dropShadow": True,
                "dropShadowOffsetY": "20px",
                "dropShadowBlurRadius": "68px",
                "fontFamily": "Fira Code",
                "fontSize": "14px",
                "lineNumbers": True,
                "paddingVertical": "56px",
                "paddingHorizontal": "56px",
                "exportSize": "2x",
                "widthAdjustment": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(carbon_url, json=payload) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        
                        # Save to file
                        file_path = "/tmp/carbon.png"
                        with open(file_path, 'wb') as f:
                            f.write(image_data)
                        
                        # Send the image
                        await event.client.send_file(
                            event.chat_id,
                            file_path,
                            caption=f"✨ Created with Carbon\n🎨 Theme: {theme}"
                        )
                        
                        await msg.delete()
                        
                        # Clean up
                        import os
                        os.remove(file_path)
                    else:
                        await msg.edit(f"❌ Failed to create carbon image! Status: {resp.status}")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.rayso"))
    @rishabh()
    async def rayso(event):
        # Get code from reply or text
        if event.is_reply:
            reply = await event.get_reply_message()
            code = reply.text or reply.message
        else:
            text = event.text.split(maxsplit=1)
            if len(text) < 2:
                await event.reply("❌ Usage: `.rayso <code>` or reply to a message")
                return
            code = text[1]
        
        if not code:
            await event.reply("❌ No code provided!")
            return
        
        msg = await event.reply("🎨 Creating rayso image...")
        
        try:
            # Use ray.so API
            # import urllib.parse moved to top
            encoded_code = urllib.parse.quote(code)
            
            rayso_url = f"https://ray.so/api/image?code={encoded_code}&theme=breeze&darkMode=true&padding=32&language=auto"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(rayso_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        
                        # Save to file
                        file_path = "/tmp/rayso.png"
                        with open(file_path, 'wb') as f:
                            f.write(image_data)
                        
                        # Send the image
                        await event.client.send_file(
                            event.chat_id,
                            file_path,
                            caption="✨ Created with ray.so"
                        )
                        
                        await msg.delete()
                        
                        # Clean up
                        import os
                        os.remove(file_path)
                    else:
                        await msg.edit(f"❌ Failed to create rayso image! Status: {resp.status}")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
