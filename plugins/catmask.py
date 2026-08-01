# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    catmask
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .mask, .awooify, .lolice, .bun, .iphx
#  Status:         Requires external image APIs/templates.
#                  Placeholder replies for now.
# =============================================================================

from telethon import events
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def init(client_instance):
    commands = [
        ".mask - Hazmat suit (reply to image)",
        ".awooify - Awooify face",
        ".lolice - Lolice check",
        ".bun - Bun face",
        ".iphx - iPhone X wallpaper"
    ]
    description = "Image maskers (external APIs/templates pending)"
    add_handler("catmask", commands, description)

async def register_commands():

    async def _reply_to(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a media file.")
            return None
        return await event.get_reply_message()

    @CipherElite.on(events.NewMessage(pattern=r"\.mask$"))
    @rishabh()
    async def mask(event):
        reply = await _reply_to(event)
        if not reply:
            return
        await event.reply(
            "🦠 **Hazmat suit maker**\n\n"
            "Reply to an image and I will send it to @hazmat_suit_bot for processing.\n"
            "_(Image processing pipeline pending)_"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.(awooify|lolice|bun|iphx)$"))
    @rishabh()
    async def mask_cmd(event):
        reply = await _reply_to(event)
        if not reply:
            return
        cmd = event.pattern_match.group(1)
        await event.reply(
            f"🖼 **{cmd.title()}** image processing\n\n"
            "_(Requires external image template/API; pending)_"
        )
