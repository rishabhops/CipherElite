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
PLUGINS_PER_PAGE = 9  # 3x3 grid (3 rows, 3 columns)
PLUGINS_PER_ROW = 3   # 3 columns per row

def init(client_instance):
    pass

def add_handler(plugin_name, commands, description=""):
    """Enhanced command handler with full syntax preservation"""
    if plugin_name not in CMD_LIST:
        # Ensure commands are stored exactly as provided
        CMD_LIST[plugin_name] = {
            "commands": commands.copy() if isinstance(commands, list) else [commands],
            "description": description
        }
        
        # Debug logging to check what's being stored
        print(f"🎭 Cipher Elite: Registered plugin '{plugin_name}' with {len(CMD_LIST[plugin_name]['commands'])} commands")
        for i, cmd in enumerate(CMD_LIST[plugin_name]['commands']):
            print(f"   Command {i+1}: {cmd}")

async def init_bot():
    await bot.start(bot_token=Config.BOT_TOKEN)
    
    @bot.on(events.InlineQuery)
    @rishabh_help()
    async def inline_handler(event):
        builder = event.builder
        if event.text == "help":
            # Precompute values before building the string
            total_plugins = len(CMD_LIST)
            total_commands = sum(len(data['commands']) for data in CMD_LIST.values())
            
            # Create beautiful help menu
            text = (
                "✨ <b>CIPHER ELITE USERBOT</b> ✨\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Loaded Plugins:</b> <code>{total_plugins}</code>\n"
                f"📂 <b>Commands:</b> <code>{total_commands}</code>\n\n"
                "<i>Select a plugin to view its commands</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
            
            # Create buttons in 3x3 grid
            buttons = []
            plugin_names = list(CMD_LIST.keys())
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            # First page buttons in 3x3 grid
            row = []
            for i, plugin in enumerate(plugin_names[:PLUGINS_PER_PAGE]):
                # Shorten long plugin names
                display_name = plugin.title()[:10] + ".." if len(plugin) > 12 else plugin.title()
                row.append(Button.inline(display_name, f"help_plugin_{plugin}"))
                # Start new row every 3 buttons
                if (i + 1) % PLUGINS_PER_ROW == 0:
                    buttons.append(row)
                    row = []
            # Add any remaining buttons in the last row
            if row:
                buttons.append(row)
            
            # Add navigation buttons if needed
            if total_pages > 1:
                buttons.append([Button.inline("Next Page →", f"help_page_1")])
            
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
                    f"🔹 <b>{plugin_name.title()} Plugin</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"<i>{CMD_LIST[plugin_name]['description']}</i>\n\n"
                    "<b>Available Commands:</b>\n"
                )
                
                # ENHANCED ROBUST COMMAND PARSING
                for cmd in CMD_LIST[plugin_name]["commands"]:
                    print(f"🔍 Debug - Processing command: '{cmd}'")  # Debug log
                    
                    if isinstance(cmd, str) and cmd.strip():
                        # Handle "command - description" format
                        if " - " in cmd:
                            cmd_part, desc_part = cmd.split(" - ", 1)
                            # Ensure we keep the FULL command syntax
                            full_command = cmd_part.strip()
                            description = desc_part.strip()
                            
                            print(f"🔍 Debug - Split into: '{full_command}' and '{description}'")  # Debug log
                            
                            text += f"• <code>{full_command}</code>\n"
                            text += f"  <i>{description}</i>\n\n"
                        else:
                            # Command without description separator
                            text += f"• <code>{cmd.strip()}</code>\n\n"
                    else:
                        # Fallback
                        text += f"• <code>{str(cmd)}</code>\n\n"
                
                # Add back button
                buttons = [[Button.inline("← Back to Menu", "help_page_0")]]
                await event.edit(text, buttons=buttons, parse_mode='html')
            return
        
        # Handle page navigation
        if data.startswith("page_"):
            page = int(data.replace("page_", ""))
            plugin_names = list(CMD_LIST.keys())
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            # Create beautiful main menu
            text = (
                "✨ <b>CIPHER ELITE USERBOT</b> ✨\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Loaded Plugins:</b> <code>{len(plugin_names)}</code>\n"
                f"📂 <b>Page:</b> <code>{page+1}/{total_pages}</code>\n\n"
                "<i>Select a plugin to view its commands</i>\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
            
            # Create buttons in 3x3 grid for current page
            buttons = []
            start_idx = page * PLUGINS_PER_PAGE
            end_idx = start_idx + PLUGINS_PER_PAGE
            current_plugins = plugin_names[start_idx:end_idx]
            
            row = []
            for i, plugin in enumerate(current_plugins):
                # Shorten long plugin names
                display_name = plugin.title()[:10] + ".." if len(plugin) > 12 else plugin.title()
                row.append(Button.inline(display_name, f"help_plugin_{plugin}"))
                # Start new row every 3 buttons
                if (i + 1) % PLUGINS_PER_ROW == 0:
                    buttons.append(row)
                    row = []
            # Add any remaining buttons in the last row
            if row:
                buttons.append(row)
            
            # Add navigation buttons
            nav_buttons = []
            if page > 0:
                nav_buttons.append(Button.inline("← Previous", f"help_page_{page-1}"))
            if end_idx < len(plugin_names):
                nav_buttons.append(Button.inline("Next →", f"help_page_{page+1}"))
            
            if nav_buttons:
                buttons.append(nav_buttons)
            
            await event.edit(text, buttons=buttons, parse_mode='html')
            return
    
    # Debug command to check stored commands
    @bot.on(events.NewMessage(pattern=r"\.debugcmds"))
    @rishabh_help()
    async def debug_commands(event):
        try:
            debug_msg = "🔍 **Debug: Stored Commands**\n\n"
            
            if not CMD_LIST:
                debug_msg += "❌ **No commands registered yet!**"
            else:
                for plugin_name, plugin_data in CMD_LIST.items():
                    debug_msg += f"**🎭 {plugin_name}:**\n"
                    debug_msg += f"📝 **Description:** {plugin_data.get('description', 'No description')}\n"
                    debug_msg += f"📊 **Commands ({len(plugin_data['commands'])}):**\n"
                    
                    for i, cmd in enumerate(plugin_data['commands']):
                        debug_msg += f"  `{i+1}.` {repr(cmd)}\n"
                    debug_msg += "\n"
            
            # Split message if too long
            if len(debug_msg) > 4000:
                parts = [debug_msg[i:i+4000] for i in range(0, len(debug_msg), 4000)]
                for part in parts:
                    await event.reply(part)
            else:
                await event.reply(debug_msg)
                
        except Exception as e:
            await event.reply(f"🔍 **Debug error:** {e}")
    
    return bot

async def register_commands():
    pass
