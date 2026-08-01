# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    figlet
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Command:        .figlet <style> ; <text>
# =============================================================================

from telethon import events
import pyfiglet
import re
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

CMD_FIG = {
    "slant": "slant",
    "3D": "3-d",
    "5line": "5lineoblique",
    "alpha": "alphabet",
    "banner": "banner3-D",
    "doh": "doh",
    "basic": "basic",
    "binary": "binary",
    "iso": "isometric1",
    "letter": "letters",
    "allig": "alligator",
    "dotm": "dotmatrix",
    "bubble": "bubble",
    "bulb": "bulbhead",
    "digi": "digital",
}

def deEmojify(text):
    return text.encode("ascii", "ignore").decode("ascii")

def init(client_instance):
    commands = [
        ".figlet <style> ; <text> - Convert text to figlet style",
        ".figlet <text> - Default figlet style"
    ]
    description = "Make big ASCII art text with figlet"
    add_handler("figlet", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.figlet(?: |$)([\s\S]*)"))
    @rishabh()
    async def figlet_cmd(event):
        input_str = event.pattern_match.group(1).strip()
        if event.is_reply:
            input_str = (await event.get_reply_message()).text or input_str
        if not input_str:
            await event.reply("❌ Give some text to convert. Example: `.figlet digi ; hello`")
            return
        if ";" in input_str:
            cmd, text = input_str.split(";", maxsplit=1)
            style = cmd.strip()
            text = text.strip()
        else:
            style = None
            text = input_str.strip()
        if style:
            font = CMD_FIG.get(style)
            if not font:
                await event.reply("❌ Invalid style. Use: " + ", ".join(CMD_FIG.keys()))
                return
            result = pyfiglet.figlet_format(deEmojify(text), font=font)
        else:
            result = pyfiglet.figlet_format(deEmojify(text))
        if not result.strip():
            await event.reply("❌ Could not generate figlet text.")
            return
        await event.reply(f"```\n{result}\n```")
