# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    carbon
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

import asyncio
import os
import requests
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    """
    Initialize the plugin with command descriptions.
    """
    commands = [
        ".carbon <code snippet> - Make a carbon image of the code with a fixed style.",
        ".karbon <code snippet> - Make a carbon image of the code with a random style."
    ]
    description = "Plugin to create carbonized code images using carbon.now.sh."
    add_handler("carbon", commands, description)

async def generate_carbon(code, random_style=False):
    """
    Generate a carbon image for the given code using carbon.now.sh.
    Returns the path to the downloaded image file.
    """
    # Note: carbon.now.sh doesn't have a public API, so we simulate form submission.
    # Using a hypothetical API endpoint or alternative service like api.carbonsh.dev.
    CARBON_API = "https://api.carbonsh.dev"  # Placeholder; replace with actual endpoint if available
    payload = {
        "code": code,
        "backgroundColor": "rgba(171, 184, 195, 1)",  # Default carbon style
        "theme": "seti" if not random_style else "random",
        "fontFamily": "Hack",
        "fontSize": "14px",
        "lineNumbers": True,
        "windowControls": True,
        "widthAdjustment": True,
        "dropShadow": True,
        "dropShadowBlurRadius": "20px",
        "exportSize": "2x",
        "format": "png"
    }

    try:
        response = requests.post(CARBON_API, json=payload, stream=True)
        if response.status_code != 200:
            return None, f"API error: {response.status_code}"

        # Save the image temporarily
        image_path = f"carbon_{'random' if random_style else 'fixed'}_{hash(code)}.png"
        with open(image_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return image_path, None
    except Exception as e:
        return None, str(e)

async def register_commands():
    """
    Register all commands for the plugin.
    """
    @CipherElite.on(events.NewMessage(pattern=r"\.carbon(?:\s+(.+))?"))
    @rishabh()
    async def carbon_handler(event):
        """
        Make a carbon image of the given code snippet with a fixed style.
        """
        try:
            code = event.pattern_match.group(1)
            if not code:
                await event.reply("No code snippet provided!")
                return

            reply_to = event.reply_to_msg_id or event.message.id
            elite = await event.reply("**[ 50% ]** __Making carbon...__")

            # Optional: Add permission check if rishabh() doesn't handle it
            # if event.sender_id not in ALLOWED_USER_IDS:
            #     await event.reply("Unauthorized: You cannot use this command.")
            #     return

            await elite.edit("**[ 75% ]** __Making carbon...__")
            image_path, error = await generate_carbon(code, random_style=False)
            if error:
                await elite.edit(f"**Error:** `{error}`")
                return

            await asyncio.sleep(4)  # Simulate processing delay, as in original
            await elite.edit("**[ 100% ]** __Uploading carbon...__")

            await event.client.send_file(
                event.chat_id,
                image_path,
                caption=f"**𝖢𝖺𝗋𝖻𝗈𝗇𝖾𝖽 (@CipherElite):**\n`{code}`",
                reply_to=reply_to
            )

            await elite.delete()
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.karbon(?:\s+(.+))?"))
    @rishabh()
    async def karbon_handler(event):
        """
        Make a carbon image of the given code snippet with a random style.
        """
        try:
            code = event.pattern_match.group(1)
            if not code:
                await event.reply("No code snippet provided!")
                return

            reply_to = event.reply_to_msg_id or event.message.id
            elite = await event.reply("**[ 50% ]** __Making karbon...__")

            # Optional: Add permission check if rishabh() doesn't handle it
            # if event.sender_id not in ALLOWED_USER_IDS:
            #     await event.reply("Unauthorized: You cannot use this command.")
            #     return

            await elite.edit("**[ 75% ]** __Making karbon...__")
            image_path, error = await generate_carbon(code, random_style=True)
            if error:
                await elite.edit(f"**Error:** `{error}`")
                return

            await asyncio.sleep(4)  # Simulate processing delay, as in original
            await elite.edit("**[ 100% ]** __Uploading karbon...__")

            await event.client.send_file(
                event.chat_id,
                image_path,
                caption=f"**𝖪𝖺𝗋𝖻𝗈𝗇𝖾𝖽 (@CipherElite):**\n`{code}`",
                reply_to=reply_to
            )

            await elite.delete()
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            await event.reply(f"Error: {str(e)}")
