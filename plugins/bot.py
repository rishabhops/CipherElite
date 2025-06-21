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
bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)
CMD_LIST = {}

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
            buttons = []
            row = []
            for plugin in CMD_LIST:
                row.append(Button.inline(plugin.title(), f"help_{plugin}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)

            result = builder.article(
                title="Help Menu",
                text=f"**🤖 Cipher Elite Help Menu**\n\n📂 **Loaded Plugins:** `{len(CMD_LIST)}`\nClick a button to see commands!",
                buttons=buttons
            )
            await event.answer([result])

    @bot.on(events.CallbackQuery(pattern=r"help_(.*)"))
    @rishabh_help()
    async def callback_handler(event):
        data = event.data_match.group(1).decode()
        
        if data == "back":
            buttons = []
            row = []
            for plugin in CMD_LIST:
                row.append(Button.inline(plugin.title(), f"help_{plugin}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
                
            text = f"**🤖 Cipher Elite Help Menu**\n\n📂 **Loaded Plugins:** `{len(CMD_LIST)}`\nClick a button to see commands!"
        else:
            plugin = data
            if plugin in CMD_LIST:
                text = f"**{plugin.title()} Plugin Commands:**\n\n"
                for cmd in CMD_LIST[plugin]["commands"]:
                    text += f"• `{cmd}`\n"
                if CMD_LIST[plugin]["description"]:
                    text += f"\n{CMD_LIST[plugin]['description']}"
                buttons = [[Button.inline("« Back", "help_back")]]
            
        await event.edit(text, buttons=buttons)
    
    return bot

async def register_commands():
    pass
    
