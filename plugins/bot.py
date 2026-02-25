# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    bot
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

from telethon import TelegramClient, events, Button
from config.config import Config
from utils.decorators import rishabh_help
import math
import importlib
from pathlib import Path
import asyncio

# Initialize Bot Client
bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)

# Global Command Storage
CMD_LIST = {}

# Pagination Settings
PLUGINS_PER_PAGE = 9  # 3x3 grid
PLUGINS_PER_ROW = 3

# --- Global Tracker for Auto-Close Timers ---
HELP_TIMERS = {}

async def reset_help_timer(event, message_id):
    """Resets the 60-second auto-close timer every time a button is clicked."""
    if message_id in HELP_TIMERS:
        HELP_TIMERS[message_id].cancel()
        
    async def close_menu():
        await asyncio.sleep(60)
        try:
            await event.edit("<i>⏳ Cipher Elite help session expired.</i>", buttons=None, parse_mode='html')
        except Exception:
            pass
            
    HELP_TIMERS[message_id] = asyncio.create_task(close_menu())

def init(client_instance):
    pass

def add_handler(plugin_name, commands, description=""):
    """Registers a plugin and its commands to the Help Menu."""
    if plugin_name not in CMD_LIST:
        CMD_LIST[plugin_name] = {
            "commands": commands.copy() if isinstance(commands, list) else [commands],
            "description": description
        }
        print(f"🎭 Cipher Elite: Registered '{plugin_name}' ({len(CMD_LIST[plugin_name]['commands'])} cmds)")

def remove_handler(plugin_name):
    """Removes a plugin from the Help Menu (Used by Uninstaller)."""
    try:
        if plugin_name in CMD_LIST:
            del CMD_LIST[plugin_name]
            print(f"🗑 Cipher Elite: Removed '{plugin_name}' from Help Menu.")
            return True
    except Exception as e:
        print(f"Error removing handler: {e}")
    return False

async def init_bot(user_client=None):
    """Initializes the Helper Bot and Event Listeners."""
    await bot.start(bot_token=Config.BOT_TOKEN)
    
    # -------------------------------------------------------------------------
    # LOAD BOT PLUGINS
    # -------------------------------------------------------------------------
    if user_client:
        try:
            owner = await user_client.get_me()
            owner_id = owner.id
            owner_name = owner.first_name
            
            print(f"\n🔌 Loading bot plugins for owner: {owner_name} (ID: {owner_id})")
            
            bot_plugins_path = Path(__file__).parent.parent / "bot_plugins"
            
            if not bot_plugins_path.exists():
                print(f"\033[1;33m⚠️ Bot plugins directory not found: {bot_plugins_path}\033[0m")
            else:
                bot_plugins = [
                    f"bot_plugins.{f.stem}"
                    for f in bot_plugins_path.glob("*.py")
                    if f.stem != "__init__"
                ]
                
                loaded_bot_plugins = []
                for plugin_name in bot_plugins:
                    try:
                        module = importlib.import_module(plugin_name)
                        if hasattr(module, "init_bot_plugin"):
                            module.init_bot_plugin(bot, owner_id, owner_name)
                            loaded_bot_plugins.append(plugin_name.split(".")[-1])
                            print(f"✅ Loaded bot plugin: {plugin_name.split('.')[-1]}")
                    except Exception as e:
                        print(f"\033[1;31m❌ Failed to load bot plugin {plugin_name}: {e}\033[0m")
                
                if loaded_bot_plugins:
                    print(f"🎉 Successfully loaded {len(loaded_bot_plugins)} bot plugin(s)\n")
        except Exception as e:
            print(f"\033[1;31m❌ Error loading bot plugins: {e}\033[0m")
    
    # -------------------------------------------------------------------------
    # 1. INLINE QUERY HANDLER (The Main Menu)
    # -------------------------------------------------------------------------
    @bot.on(events.InlineQuery)
    @rishabh_help()
    async def inline_handler(event):
        builder = event.builder
        if event.text == "help":
            total_plugins = len(CMD_LIST)
            total_commands = sum(len(data['commands']) for data in CMD_LIST.values())
            
            text = (
                "✦ <b>𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐋𝐈𝐓𝐄 𝐌𝐄𝐍𝐔</b> ✦\n"
                "⟡ ═════════════════ ⟡\n"
                f"❖ <b>Loaded Plugins:</b> <code>{total_plugins}</code>\n"
                f"❖ <b>Total Commands:</b> <code>{total_commands}</code>\n\n"
                "<i>Select a module below to view commands.</i>\n"
                "⟡ ═════════════════ ⟡"
            )
            
            buttons = []
            plugin_names = list(CMD_LIST.keys())
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x)) # quickhelp first
            
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            row = []
            for i, plugin in enumerate(plugin_names[:PLUGINS_PER_PAGE]):
                if plugin == 'quickhelp':
                    display_name = "⚡ Quick Guide"
                else:
                    display_name = plugin.title()[:10] + ".." if len(plugin) > 12 else plugin.title()
                
                row.append(Button.inline(display_name, f"help_plugin_{plugin}"))
                if (i + 1) % PLUGINS_PER_ROW == 0:
                    buttons.append(row)
                    row = []
            if row: buttons.append(row)
            
            if total_pages > 1:
                buttons.append([Button.inline("Next Page ❯", f"help_page_1")])
            
            result = builder.article(
                title="Cipher Elite Help Menu",
                text=text,
                buttons=buttons,
                parse_mode='html'
            )
            await event.answer([result])

    # -------------------------------------------------------------------------
    # 2. CALLBACK HANDLER (Button Clicks)
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"help_(.*)"))
    @rishabh_help()
    async def callback_handler(event):
        data = event.data_match.group(1).decode()
        
        # ⏱️ Reset the 60-second timer on user interaction
        await reset_help_timer(event, event.message_id)
        
        # --- VIEW PLUGIN DETAILS ---
        if data.startswith("plugin_"):
            plugin_name = data.replace("plugin_", "")
            
            # 🧮 Calculate which page this plugin belongs to for the back button
            plugin_names = list(CMD_LIST.keys())
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x))
            try:
                plugin_index = plugin_names.index(plugin_name)
                page_number = plugin_index // PLUGINS_PER_PAGE
            except ValueError:
                page_number = 0
            
            if plugin_name in CMD_LIST:
                if plugin_name == "quickhelp":
                    text = (
                        f"✦ <b>𝐐𝐔𝐈𝐂𝐊 𝐇𝐄𝐋𝐏 𝐆𝐔𝐈𝐃𝐄</b> ✦\n"
                        f"⟡ ═════════════════ ⟡\n\n"
                        f"🎯 <b>Basic Commands:</b>\n"
                        f" ├ <code>.help</code> - Show Menu\n"
                        f" ├ <code>.plugins</code> - View All\n"
                        f" ├ <code>.install</code> - Add Plugin\n"
                        f" └ <code>.uninstall</code> - Remove Plugin\n\n"
                        f"🤖 <i>Powered by Cipher Elite</i>"
                    )
                else:
                    desc = CMD_LIST[plugin_name]['description']
                    text = (
                        f"✦ <b>{plugin_name.upper()} 𝐌𝐎𝐃𝐔𝐋𝐄</b> ✦\n"
                        f"⟡ ═════════════════ ⟡\n"
                        f"<i>{desc}</i>\n\n"
                        f"❖ <b>Available Commands:</b>\n"
                    )
                    
                    for cmd in CMD_LIST[plugin_name]["commands"]:
                        if isinstance(cmd, str) and cmd.strip():
                            if " - " in cmd:
                                c, d = cmd.split(" - ", 1)
                                c = c.strip().replace('<', '&lt;').replace('>', '&gt;')
                                text += f" ├ <code>{c}</code>\n └ <i>{d.strip()}</i>\n\n"
                            else:
                                c = cmd.strip().replace('<', '&lt;').replace('>', '&gt;')
                                text += f" ├ <code>{c}</code>\n\n"
                
                buttons = [[Button.inline("❮ Back to Menu", f"help_page_{page_number}")]]
                await event.edit(text, buttons=buttons, parse_mode='html')
            return
        
        # --- PAGE NAVIGATION ---
        if data.startswith("page_"):
            page = int(data.replace("page_", ""))
            plugin_names = list(CMD_LIST.keys())
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x))
            
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)
            
            text = (
                "✦ <b>𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐋𝐈𝐓𝐄 𝐌𝐄𝐍𝐔</b> ✦\n"
                "⟡ ═════════════════ ⟡\n"
                f"❖ <b>Loaded Plugins:</b> <code>{len(plugin_names)}</code>\n"
                f"❖ <b>Page:</b> <code>{page+1} of {total_pages}</code>\n\n"
                "<i>Select a module below to view commands.</i>\n"
                "⟡ ═════════════════ ⟡"
            )
            
            buttons = []
            start = page * PLUGINS_PER_PAGE
            end = start + PLUGINS_PER_PAGE
            current_plugins = plugin_names[start:end]
            
            row = []
            for i, plugin in enumerate(current_plugins):
                if plugin == 'quickhelp':
                    display = "⚡ Quick Guide"
                else:
                    display = plugin.title()[:10] + ".." if len(plugin) > 12 else plugin.title()
                
                row.append(Button.inline(display, f"help_plugin_{plugin}"))
                if (i + 1) % PLUGINS_PER_ROW == 0:
                    buttons.append(row)
                    row = []
            if row: buttons.append(row)
            
            nav = []
            if page > 0:
                nav.append(Button.inline("❮ Previous", f"help_page_{page-1}"))
            if end < len(plugin_names):
                nav.append(Button.inline("Next ❯", f"help_page_{page+1}"))
            if nav: buttons.append(nav)
            
            await event.edit(text, buttons=buttons, parse_mode='html')
            return

    # -------------------------------------------------------------------------
    # 3. DEBUG COMMAND
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"\.debugcmds"))
    @rishabh_help()
    async def debug_commands(event):
        try:
            msg = "🔍 <b>Debug: Stored Commands</b>\n\n"
            if not CMD_LIST:
                msg += "❌ <b>No commands registered!</b>"
            else:
                for p_name, p_data in CMD_LIST.items():
                    msg += f"<b>🎭 {p_name}:</b> ({len(p_data['commands'])})\n"
                    for i, cmd in enumerate(p_data['commands']):
                        msg += f"  <code>{i+1}.</code> {str(cmd)[:50]}\n"
                    msg += "\n"
            
            if len(msg) > 4000:
                for x in range(0, len(msg), 4000):
                    await event.reply(msg[x:x+4000], parse_mode='html')
            else:
                await event.reply(msg, parse_mode='html')
        except Exception as e:
            await event.reply(f"❌ Error: {e}")

    return bot

async def register_commands():
    pass
