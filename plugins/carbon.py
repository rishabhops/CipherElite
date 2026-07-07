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
import random
import tempfile
import urllib.parse          # <-- the missing import that caused: name 'urllib' is not defined

import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# -----------------------------------------------------------------------------
#  Config
# -----------------------------------------------------------------------------
CARBON_API = "https://carbonara.solopov.dev/api/cook"
RAYSO_API = "https://ray.so/api/image"

# Total request timeout so a hung API call can't freeze the handler forever.
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=60)

DEFAULT_CARBON_THEME = "monokai"
DEFAULT_RAYSO_THEME = "breeze"

CARBON_THEMES = [
    "3024-night", "a11y-dark", "blackboard", "base16-dark",
    "base16-light", "cobalt", "dracula", "duotone-dark",
    "hopscotch", "lucario", "material", "monokai",
    "night-owl", "nord", "oceanic-next", "one-light",
    "one-dark", "panda-syntax", "paraiso-dark", "seti",
    "shades-of-purple", "solarized-dark", "solarized-light",
    "synthwave-84", "twilight", "verminal", "vscode",
    "yeti", "zenburn",
]

RAYSO_THEMES = [
    "breeze", "candy", "crimson", "falcon",
    "meadow", "midnight", "raindrop", "sunset",
]


def init(client_instance):
    commands = [
        ".carbon <reply/code> - Carbon image (monokai theme)",
        ".rcarbon <reply/code> - Carbon image with a random theme",
        ".tcarbon <theme> <reply/code> - Carbon image with a chosen theme",
        ".rayso <reply/code> - ray.so image (breeze theme)",
        ".rrayso <reply/code> - ray.so image with a random theme",
        ".themes - List all available carbon & ray.so themes",
    ]
    description = "Carbon / ray.so code beautifier — turn code into pretty screenshots"
    add_handler("carbon", commands, description)


# -----------------------------------------------------------------------------
#  Shared helpers
# -----------------------------------------------------------------------------
async def _get_reply_code(event):
    """Extract code from the replied-to message, if any."""
    reply = await event.get_reply_message()
    return (reply.text or reply.message) if reply else None


async def _resolve_code(event):
    """
    Return code either from a reply or from inline text after the command.
    Returns None if nothing usable was found.
    """
    if event.is_reply:
        return await _get_reply_code(event)
    parts = event.text.split(maxsplit=1)
    return parts[1] if len(parts) >= 2 else None


async def _resolve_theme_and_code(event, valid_themes):
    """
    For '.tcarbon <theme> ...' style commands.
    The first token after the command is treated as the theme.

    Returns (theme, code, error_message). If error_message is set, the caller
    should show it and stop.
    """
    parts = event.text.split(maxsplit=2)  # ['.tcarbon', '<theme>', '<rest?>']

    if len(parts) < 2:
        return None, None, "❌ Usage: `.tcarbon <theme> <code>` or reply to a message"

    theme = parts[1].lower()
    if theme not in valid_themes:
        return None, None, (
            f"❌ Unknown theme: `{theme}`\n"
            f"Use `.themes` to see the full list."
        )

    if event.is_reply:
        code = await _get_reply_code(event)
    else:
        code = parts[2] if len(parts) >= 3 else None

    return theme, code, None


def _carbon_payload(code, theme):
    return {
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
        "widthAdjustment": True,
    }


async def _fetch_carbon(code, theme):
    """POST to the carbon API and return raw PNG bytes (raises on failure)."""
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
        async with session.post(CARBON_API, json=_carbon_payload(code, theme)) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Carbon API returned status {resp.status}")
            return await resp.read()


async def _fetch_rayso(code, theme):
    """GET the ray.so image and return raw PNG bytes (raises on failure)."""
    params = {
        "code": code,          # urlencode handles escaping — no manual quote() needed
        "theme": theme,
        "darkMode": "true",
        "padding": "32",
        "language": "auto",
    }
    url = f"{RAYSO_API}?{urllib.parse.urlencode(params)}"
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"ray.so API returned status {resp.status}")
            return await resp.read()


async def _send_image_bytes(event, image_data, caption):
    """
    Write bytes to a unique temp file, send it, then always clean up.
    Unique names avoid collisions if two renders run at once.
    """
    fd, path = tempfile.mkstemp(suffix=".png")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(image_data)
        await event.client.send_file(event.chat_id, path, caption=caption)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


# -----------------------------------------------------------------------------
#  Command handlers
# -----------------------------------------------------------------------------
async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.carbon(\s|$)"))
    @rishabh()
    async def carbon(event):
        code = await _resolve_code(event)
        if not code:
            await event.reply("❌ Usage: `.carbon <code>` or reply to a message")
            return

        msg = await event.reply("🎨 Creating carbon image...")
        try:
            image_data = await _fetch_carbon(code, DEFAULT_CARBON_THEME)
            await _send_image_bytes(event, image_data, "✨ Created with Carbon")
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ Error: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.rcarbon(\s|$)"))
    @rishabh()
    async def rcarbon(event):
        code = await _resolve_code(event)
        if not code:
            await event.reply("❌ Usage: `.rcarbon <code>` or reply to a message")
            return

        msg = await event.reply("🎨 Creating carbon image with a random theme...")
        try:
            theme = random.choice(CARBON_THEMES)
            image_data = await _fetch_carbon(code, theme)
            await _send_image_bytes(
                event, image_data, f"✨ Created with Carbon\n🎨 Theme: {theme}"
            )
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ Error: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.tcarbon(\s|$)"))
    @rishabh()
    async def tcarbon(event):
        theme, code, err = await _resolve_theme_and_code(event, CARBON_THEMES)
        if err:
            await event.reply(err)
            return
        if not code:
            await event.reply("❌ No code provided!")
            return

        msg = await event.reply(f"🎨 Creating carbon image with `{theme}`...")
        try:
            image_data = await _fetch_carbon(code, theme)
            await _send_image_bytes(
                event, image_data, f"✨ Created with Carbon\n🎨 Theme: {theme}"
            )
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ Error: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.rayso(\s|$)"))
    @rishabh()
    async def rayso(event):
        code = await _resolve_code(event)
        if not code:
            await event.reply("❌ Usage: `.rayso <code>` or reply to a message")
            return

        msg = await event.reply("🎨 Creating rayso image...")
        try:
            image_data = await _fetch_rayso(code, DEFAULT_RAYSO_THEME)
            await _send_image_bytes(event, image_data, "✨ Created with ray.so")
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ Error: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.rrayso(\s|$)"))
    @rishabh()
    async def rrayso(event):
        code = await _resolve_code(event)
        if not code:
            await event.reply("❌ Usage: `.rrayso <code>` or reply to a message")
            return

        msg = await event.reply("🎨 Creating rayso image with a random theme...")
        try:
            theme = random.choice(RAYSO_THEMES)
            image_data = await _fetch_rayso(code, theme)
            await _send_image_bytes(
                event, image_data, f"✨ Created with ray.so\n🎨 Theme: {theme}"
            )
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ Error: {e}")

    @CipherElite.on(events.NewMessage(pattern=r"\.themes(\s|$)"))
    @rishabh()
    async def themes(event):
        carbon_list = ", ".join(f"`{t}`" for t in CARBON_THEMES)
        rayso_list = ", ".join(f"`{t}`" for t in RAYSO_THEMES)
        await event.reply(
            f"🎨 **Carbon themes** ({len(CARBON_THEMES)}):\n{carbon_list}\n\n"
            f"🌈 **ray.so themes** ({len(RAYSO_THEMES)}):\n{rayso_list}\n\n"
            f"Use with `.tcarbon <theme> <code>`"
        )
