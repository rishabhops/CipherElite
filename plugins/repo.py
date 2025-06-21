# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    inline_info
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • Give proper credit back to the CipherElite Userbot author:
#        – GitHub: https://github.com/rishabhops/CipherElite
#        – Telegram: @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

from telethon import events, Button
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from vars import ELITE_BOT_USERNAME

# Bot name for display
BOT_NAME = "CipherElite"

def init(client):
    """Initialize the inline_info plugin"""
    commands = [
        f"{ELITE_BOT_USERNAME} repo — Show bot info and links inline"
    ]
    description = "Inline query to display CipherElite bot information and links"
    add_handler("inline_info", commands, description)

@CipherElite.on(events.InlineQuery(pattern=r"repo"))
@rishabh()
async def inline_info_handler(event: events.InlineQuery.Event):
    """Handle inline query for bot info"""
    builder = event.builder
    buttons = [[Button.inline("🌟 Get Info 🌟", data="cipher_info")]]
    result = builder.article(
        title="CipherElite Info",
        text=f"Discover {BOT_NAME} - The Ultimate Userbot! 🚀",
        buttons=buttons,
        link_preview=False
    )
    await event.answer([result])

@CipherElite.on(events.CallbackQuery(data=re.compile(b"cipher_info")))
@rishabh()
async def callback_info_handler(event):
    """Handle callback query for bot info"""
    repo_url = "https://github.com/rishabhops/CipherElite"  # Replace with your actual repo URL
    support_url = "https://t.me/thanosprosss"  # Replace with your actual support group URL
    buttons = [
        [Button.url(f"🚀 {BOT_NAME} Repo", url=repo_url)],
        [Button.url(f"⚡ Support Group", url=support_url)],
        [Button.inline("ℹ️ About", data="cipher_about")]
    ]
    await event.edit(
        text=f"{BOT_NAME} - Power Up Your Telegram Experience! 🔥\n\n"
             "Explore the source code and join our community for updates and support.",
        buttons=buttons
    )

@CipherElite.on(events.CallbackQuery(data=re.compile(b"cipher_about")))
@rishabh()
async def callback_about_handler(event):
    """Handle callback query for about info"""
    buttons = [[Button.inline("🔙 Back", data="cipher_info")]]
    await event.edit(
        text=f"About {BOT_NAME} 🤖\n\n"
             "Built by CipherElite Dev (@rishabhops) to enhance your Telegram chats with "
             "powerful commands, animations, and utilities. Open-source under MIT license. "
             "Join the community to contribute or get help! 🌐",
        buttons=buttons
    )
