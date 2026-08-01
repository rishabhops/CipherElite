# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    catamongus
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .amongus, .imposter, .imp, .impn
#  Status:         Requires CatUserBot image resources and PIL templates.
#                  Placeholder replies for now.
# =============================================================================

from telethon import events
import random
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

COLORS = {
    1: "red", 2: "lime", 3: "green", 4: "blue", 5: "cyan",
    6: "brown", 7: "purple", 8: "pink", 9: "orange", 10: "yellow",
    11: "white", 12: "black"
}

def init(client_instance):
    commands = [
        ".amongus <text> - Among Us sticker",
        ".imposter <user> - Imposter check",
        ".imp <name> - Imposter animation",
        ".impn <name> - Not imposter animation"
    ]
    description = "Among Us image fun (templates pending)"
    add_handler("catamongus", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.amongus(?: |$)([\s\S]*)"))
    @rishabh()
    async def amongus(event):
        text = event.pattern_match.group(1).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        color = random.choice(list(COLORS.values()))
        await event.reply(
            f"🔴 **Among Us sticker**\n\n"
            f"Color: `{color}`\n"
            f"Text: `{text or 'No text'}`\n\n"
            "_(Image generation requires Among Us templates; pending)_"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.imposter(?: |$)([\s\S]*)"))
    @rishabh()
    async def imposter(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a user.")
            return
        reply = await event.get_reply_message()
        try:
            user = await event.client.get_entity(reply.sender_id)
        except Exception:
            await event.reply("❌ Could not resolve user.")
            return
        result = random.choice(["was the impostor", "wasn't the impostor"])
        await event.reply(
            f"🎮 **{user.first_name} {result}.**\n\n"
            "_(Image generation requires templates; pending)_"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.imp(|n)(?: |$)([\s\S]*)"))
    @rishabh()
    async def imp(event):
        name = event.pattern_match.group(2).strip()
        is_not = event.pattern_match.group(1) == "n"
        if not name:
            name = "Unknown"
        await event.reply(
            f"🎮 **{name}** was {'not ' if is_not else ''}an Imposter.\n"
            f"_{1 if is_not else 0} Impostor(s) remain._\n\n"
            "_(Image animation requires templates; pending)_"
        )
