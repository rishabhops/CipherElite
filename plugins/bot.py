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
            
            # Sort plugins: quickhelp first, then alphabetically
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x))
            
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            # First page buttons in 3x3 grid
            row = []
            for i, plugin in enumerate(plugin_names[:PLUGINS_PER_PAGE]):
                # Special formatting for quickhelp
                if plugin == 'quickhelp':
                    display_name = "⚡Help Guide"
                else:
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
                
                # Special handling for quickhelp plugin
                if plugin_name == "quickhelp":
                    # Show comprehensive help guide
                    text = (
                        f"⚡ <b>Cipher Elite Quick Help Guide</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🎯 <b>Basic Help Commands:</b>\n"
                        f"• <code>.help</code> - Full interactive help menu\n"
                        f"• <code>.help spam</code> - Direct help for spam plugin\n"
                        f"• <code>.help broadcast</code> - Direct help for broadcast plugin\n"
                        f"• <code>.help actions</code> - Direct help for actions plugin\n\n"
                        f"🔍 <b>Discovery Commands:</b>\n"
                        f"• <code>.plugins</code> - List all loaded plugins with stats\n"
                        f"• <code>.findplugin tool</code> - Find plugins containing 'tool'\n"
                        f"• <code>.helpstats</code> - Detailed help system statistics\n\n"
                        f"💡 <b>Pro Tips:</b>\n"
                        f"• Use <code>.help &lt;plugin&gt;</code> for instant access\n"
                        f"• Search partial names: <code>.findplugin spa</code> finds spam\n"
                        f"• All help commands work in any chat\n"
                        f"• Commands are case-insensitive\n"
                        f"• Direct access is 50% faster than menu navigation\n\n"
                        f"🎲 <b>Quick Examples:</b>\n"
                    )
                    
                    # Add examples from available plugins (excluding quickhelp)
                    available_plugins = [p for p in CMD_LIST.keys() if p != 'quickhelp']
                    if available_plugins:
                        import random
                        sample_plugins = random.sample(available_plugins, min(3, len(available_plugins)))
                        for plugin in sample_plugins:
                            text += f"• <code>.help {plugin}</code>\n"
                        text += "\n"
                    
                    text += f"📋 <b>Available in Both:</b>\n"
                    text += f"• Command: <code>.quickhelp</code>\n"
                    text += f"• Button: Click ⚡Help Guide in help menu\n\n"
                    text += f"🤖 <b>Powered by Cipher Elite</b>"
                    
                else:
                    # Regular plugin details view
                    text = (
                        f"🔹 <b>{plugin_name.title()} Plugin</b>\n"
                        "━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"<i>{CMD_LIST[plugin_name]['description']}</i>\n\n"
                        "<b>Available Commands:</b>\n"
                    )
                    
                    # ENHANCED ROBUST COMMAND PARSING WITH HTML ESCAPING
                    for cmd in CMD_LIST[plugin_name]["commands"]:
                        print(f"🔍 Debug - Processing command: '{cmd}'")  # Debug log
                        
                        if isinstance(cmd, str) and cmd.strip():
                            if " - " in cmd:
                                cmd_part, desc_part = cmd.split(" - ", 1)
                                full_command = cmd_part.strip()
                                description = desc_part.strip()
                                
                                print(f"🔍 Debug - Split into: '{full_command}' and '{description}'")  # Debug log
                                
                                # ESCAPE HTML CHARACTERS IN COMMAND SYNTAX
                                escaped_command = full_command.replace('<', '&lt;').replace('>', '&gt;')
                                
                                text += f"• <code>{escaped_command}</code>\n"
                                text += f"  <i>{description}</i>\n\n"
                            else:
                                escaped_cmd = cmd.strip().replace('<', '&lt;').replace('>', '&gt;')
                                text += f"• <code>{escaped_cmd}</code>\n\n"
                        else:
                            escaped_fallback = str(cmd).replace('<', '&lt;').replace('>', '&gt;')
                            text += f"• <code>{escaped_fallback}</code>\n\n"
                
                # Add back button
                buttons = [[Button.inline("← Back to Menu", "help_page_0")]]
                await event.edit(text, buttons=buttons, parse_mode='html')
            return
        
        # Handle page navigation
        if data.startswith("page_"):
            page = int(data.replace("page_", ""))
            plugin_names = list(CMD_LIST.keys())
            
            # Sort plugins: quickhelp first, then alphabetically
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x))
            
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
                # Special formatting for quickhelp
                if plugin == 'quickhelp':
                    display_name = "⚡Help Guide"
                else:
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
            debug_msg = "🔍 <b>Debug: Stored Commands</b>\n\n"
            
            if not CMD_LIST:
                debug_msg += "❌ <b>No commands registered yet!</b>"
            else:
                for plugin_name, plugin_data in CMD_LIST.items():
                    debug_msg += f"<b>🎭 {plugin_name}:</b>\n"
                    debug_msg += f"📝 <b>Description:</b> {plugin_data.get('description', 'No description')}\n"
                    debug_msg += f"📊 <b>Commands ({len(plugin_data['commands'])}):</b>\n"
                    
                    for i, cmd in enumerate(plugin_data['commands']):
                        debug_msg += f"  <code>{i+1}.</code> {repr(cmd)}\n"
                    debug_msg += "\n"
            
            # Split message if too long
            if len(debug_msg) > 4000:
                parts = [debug_msg[i:i+4000] for i in range(0, len(debug_msg), 4000)]
                for part in parts:
                    await event.reply(part, parse_mode='html')
            else:
                await event.reply(debug_msg, parse_mode='html')
                
        except Exception as e:
            await event.reply(f"🔍 <b>Debug error:</b> {e}", parse_mode='html')
    
    return bot

async def register_commands():
    pass
