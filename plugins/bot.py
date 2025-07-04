# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    bot
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

from telethon import TelegramClient, events, Button
from config.config import Config
from utils.decorators import rishabh_help
import math

bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)
CMD_LIST = {}
PLUGINS_PER_PAGE = 9  # Number of plugins per page

def init(client_instance):
    pass

def add_handler(plugin_name, commands, description=""):
    if plugin_name not in CMD_LIST:
        CMD_LIST[plugin_name] = {
            "commands": commands,
            "description": description
        }

async def init_bot():
    await bot.start(bot_token=Config.BOT_TOKEN)
    
    @bot.on(events.InlineQuery)
    @rishabh_help()
    async def inline_handler(event):
        builder = event.builder
        if event.text == "help":
            # Create beautiful help menu
            text = (
                "🌟 <b>CIPHER ELITE USERBOT</b> 🌟\n\n"
                "⚡ <i>Advanced Telegram Userbot</i>\n"
                f"📦 <b>Loaded Plugins:</b> <code>{len(CMD_LIST)}</code>\n\n"
                "🔍 <i>Select a plugin to see its commands</i>"
            )
            
            # Create buttons with pagination
            buttons = []
            plugin_names = list(CMD_LIST.keys())
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            # First page buttons
            for plugin in plugin_names[:PLUGINS_PER_PAGE]:
                buttons.append([Button.inline(f"🔹 {plugin.title()}", f"help_plugin_{plugin}")])
            
            # Add navigation buttons if needed
            nav_buttons = []
            if total_pages > 1:
                nav_buttons.append(Button.inline("➡️ Next", f"help_page_1"))
            
            if nav_buttons:
                buttons.append(nav_buttons)
            
            buttons.append([Button.url("📌 Support", "https://t.me/thanosprosss")])
            
            result = builder.article(
                title="Cipher Elite Help Menu",
                text=text,
                buttons=buttons,
                parse_mode='html'
            )
            await event.answer([result])

    @bot.on(events.CallbackQuery(pattern=r"help_(.*)"))
    @rishabh_help()
    async def callback_handler(event):
        data = event.data_match.group(1).decode()
        
        # Handle plugin details view
        if data.startswith("plugin_"):
            plugin_name = data.replace("plugin_", "")
            if plugin_name in CMD_LIST:
                # Create beautiful plugin details view
                text = (
                    f"✨ <b>{plugin_name.title()} Plugin</b> ✨\n\n"
                    f"📝 <i>{CMD_LIST[plugin_name]['description']}</i>\n\n"
                    "<b>Available Commands:</b>\n"
                )
                
                # Add commands with emojis
                for cmd in CMD_LIST[plugin_name]["commands"]:
                    text += f"• <code>{cmd}</code>\n"
                
                # Add back button
                buttons = [[Button.inline("🔙 Back to Main Menu", "help_main_0")]]
                await event.edit(text, buttons=buttons, parse_mode='html')
            return
        
        # Handle page navigation
        if data.startswith("page_"):
            page = int(data.replace("page_", ""))
            plugin_names = list(CMD_LIST.keys())
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            # Create beautiful main menu
            text = (
                "🌟 <b>CIPHER ELITE USERBOT</b> 🌟\n\n"
                "⚡ <i>Advanced Telegram Userbot</i>\n"
                f"📦 <b>Loaded Plugins:</b> <code>{len(CMD_LIST)}</code>\n"
                f"📑 <b>Page:</b> <code>{page+1}/{total_pages}</code>\n\n"
                "🔍 <i>Select a plugin to see its commands</i>"
            )
            
            # Create buttons for current page
            buttons = []
            start_idx = page * PLUGINS_PER_PAGE
            end_idx = start_idx + PLUGINS_PER_PAGE
            
            for plugin in plugin_names[start_idx:end_idx]:
                buttons.append([Button.inline(f"🔹 {plugin.title()}", f"help_plugin_{plugin}")])
            
            # Add navigation buttons
            nav_buttons = []
            if page > 0:
                nav_buttons.append(Button.inline("⬅️ Prev", f"help_page_{page-1}"))
            if end_idx < len(plugin_names):
                nav_buttons.append(Button.inline("➡️ Next", f"help_page_{page+1}"))
            
            if nav_buttons:
                buttons.append(nav_buttons)
            
            buttons.append([Button.url("📌 Support", "https://t.me/thanosprosss")])
            
            await event.edit(text, buttons=buttons, parse_mode='html')
            return
        
        # Handle main menu
        if data == "main_0":
            plugin_names = list(CMD_LIST.keys())
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            # Create beautiful main menu
            text = (
                "🌟 <b>CIPHER ELITE USERBOT</b> 🌟\n\n"
                "⚡ <i>Advanced Telegram Userbot</i>\n"
                f"📦 <b>Loaded Plugins:</b> <code>{len(CMD_LIST)}</code>\n"
                f"📑 <b>Page:</b> <code>1/{total_pages}</code>\n\n"
                "🔍 <i>Select a plugin to see its commands</i>"
            )
            
            # Create buttons for first page
            buttons = []
            for plugin in plugin_names[:PLUGINS_PER_PAGE]:
                buttons.append([Button.inline(f"🔹 {plugin.title()}", f"help_plugin_{plugin}")])
            
            # Add navigation buttons if needed
            nav_buttons = []
            if total_pages > 1:
                nav_buttons.append(Button.inline("➡️ Next", f"help_page_1"))
            
            if nav_buttons:
                buttons.append(nav_buttons)
            
            buttons.append([Button.url("📌 Support", "https://t.me/thanosprosss")])
            
            await event.edit(text, buttons=buttons, parse_mode='html')
    
    return bot

async def register_commands():
    pass
