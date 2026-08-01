# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    bot
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  Target path:    plugins/bot.py
# =============================================================================

from telethon import TelegramClient, events, Button
from config.config import Config
from utils.decorators import rishabh_help
from utils import help_ui                      # ← shared terminal-theme helpers
import math
import importlib
from pathlib import Path
import asyncio
import random

# Initialize Bot Client
bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)

# Global Command Storage
CMD_LIST = {}

# Category Configuration
CATEGORIES = {
    "animations": {"icon": "🎭", "name": "Animations", "order": 1},
    "admin": {"icon": "👑", "name": "Admin", "order": 2},
    "developer": {"icon": "🛠", "name": "Developer", "order": 3},
    "media": {"icon": "🎬", "name": "Media", "order": 4},
    "utilities": {"icon": "⚙️", "name": "Utilities", "order": 5},
}

# Pagination Settings
PLUGINS_PER_PAGE = 9  # 3x3 grid
PLUGINS_PER_ROW = 3

# Random Emoji Pool (kept for the Update/Support button flair)
RANDOM_EMOJIS = [
    "🫶", "☠️", "❤️‍🔥", "🚬", "💀", "🔥", "✨", "⚡", "🌟", "💫",
    "🎯", "🎪", "🎨", "🎭", "🎬", "🎸", "🎹", "🎺", "🎻", "🥁",
    "🚀", "🛸", "🌌", "⭐", "🌠", "💥", "⚔️", "🗡️", "🏆", "👑",
    "💎", "🔱", "⚜️", "🎖️", "🏅", "🎁", "🎀", "🎊", "🎉", "🎈",
    "🌈", "☄️", "🌪️", "⛈️", "🌩️", "🔆", "🌞", "🌙", "💢", "💬",
]

# --- Global Tracker for Auto-Close Timers ---
HELP_TIMERS = {}


def get_random_emojis():
    """Two random emojis for button decoration."""
    return random.choice(RANDOM_EMOJIS), random.choice(RANDOM_EMOJIS)


def get_plugin_category(plugin_name):
    """Get category for a plugin by loading its module."""
    try:
        module = importlib.import_module(f"plugins.{plugin_name}")
        return getattr(module, "CATEGORY", "utilities")
    except:
        return "utilities"


def organize_by_category():
    """Organize plugins by category."""
    categorized = {}
    for plugin_name in CMD_LIST.keys():
        if plugin_name == "quickhelp":
            continue
        category = get_plugin_category(plugin_name)
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(plugin_name)
    return categorized


def get_help_media():
    """
    Video/Image for the help menu header.
    Returns the help_menu.mp4 video from resources/extras folder.
    """
    try:
        video_path = Path(__file__).parent.parent / "resources" / "extras" / "help_menu.mp4"
        if video_path.exists():
            return str(video_path)
    except Exception:
        pass
    return None


# =============================================================================
#  SHARED RENDER HELPERS  (used by inline query, reopen, page nav, plugin view)
# =============================================================================
def _sorted_plugin_names():
    names = list(CMD_LIST.keys())
    names.sort(key=lambda x: (x != 'quickhelp', x))   # quickhelp always first
    return names


def _total_commands():
    return sum(len(d['commands']) for d in CMD_LIST.values())


def _support_row():
    e1, e2 = get_random_emojis()
    return [
        Button.url(f"{e1} Update", "https://t.me/CipherElite_Userbot"),
        Button.url(f"Support {e2}", "https://t.me/cipherelite_support"),
    ]


def _menu_buttons(page):
    """Main menu with categories."""
    categorized = organize_by_category()
    sorted_categories = sorted(categorized.keys(), key=lambda x: CATEGORIES.get(x, {}).get("order", 99))
    
    buttons = []
    
    # Category buttons (2 per row)
    row = []
    for i, category in enumerate(sorted_categories):
        icon = CATEGORIES.get(category, {}).get("icon", "📦")
        name = CATEGORIES.get(category, {}).get("name", category.title())
        count = len(categorized[category])
        button_text = f"{icon} {name} ({count})"
        row.append(Button.inline(button_text, f"help_cat_{category}"))
        
        if (i + 1) % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append(_support_row())
    
    return buttons


def _category_buttons(category, page=0):
    """Buttons for plugins in a specific category."""
    categorized = organize_by_category()
    plugins = categorized.get(category, [])
    
    buttons = []
    row = []
    for i, plugin in enumerate(plugins):
        row.append(Button.inline(help_ui.button_label(plugin), f"help_plugin_{plugin}"))
        if (i + 1) % PLUGINS_PER_ROW == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    # Back button
    buttons.append([Button.inline("◀ Back to Categories", "help_reopen")])
    buttons.append(_support_row())
    
    return buttons


def _render_menu(page):
    """Render main menu with categories."""
    total_plugins = len([p for p in CMD_LIST.keys() if p != "quickhelp"])
    total_commands = _total_commands()
    
    text = help_ui.build_menu_text(total_plugins, total_commands, 0, 1)
    return text, _menu_buttons(page)


def _render_category(category):
    """Render plugins in a specific category."""
    categorized = organize_by_category()
    plugins = categorized.get(category, [])
    
    icon = CATEGORIES.get(category, {}).get("icon", "📦")
    name = CATEGORIES.get(category, {}).get("name", category.title())
    
    text = (
        f"{icon} <b>{name}</b>\n\n"
        f"<blockquote>"
        f"📦 <b>{len(plugins)}</b> plugins available\n"
        f"</blockquote>\n"
        f"<i>Select a plugin below</i>"
    )
    
    return text, _category_buttons(category)


def _render_plugin(plugin_name):
    names = _sorted_plugin_names()
    try:
        page_number = names.index(plugin_name) // PLUGINS_PER_PAGE
    except ValueError:
        page_number = 0

    text = help_ui.build_plugin_text(plugin_name, CMD_LIST.get(plugin_name, {}))
    buttons = [
        [Button.inline("❮ Back to menu", f"help_page_{page_number}")],
        _support_row(),
    ]
    return text, buttons


async def reset_help_timer(event, message_id):
    """Resets the 60-second auto-close timer on every button click."""
    if message_id in HELP_TIMERS:
        HELP_TIMERS[message_id].cancel()

    async def close_menu():
        await asyncio.sleep(60)
        try:
            e1, e2 = get_random_emojis()
            text = (
                f"<i>⏳ Help session expired</i>\n"
                f"<i>Tap below to reopen</i>"
            )
            buttons = [
                [Button.inline(f"{e1} Reopen {e2}", "help_reopen")],
                _support_row(),
            ]
            await event.edit(text, buttons=buttons, parse_mode='html')
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
            "description": description,
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
                # Guard to avoid loading bot plugins twice if startup.py also loads them
                if not hasattr(bot, "_loaded_bot_plugins"):
                    bot._loaded_bot_plugins = set()

                for plugin_name in bot_plugins:
                    try:
                        if plugin_name in bot._loaded_bot_plugins:
                            continue
                        module = importlib.import_module(plugin_name)
                        if hasattr(module, "init_bot_plugin"):
                            module.init_bot_plugin(bot, owner_id, owner_name)
                            bot._loaded_bot_plugins.add(plugin_name)
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
        
        # Help menu
        if event.text == "help":
            text, buttons = _render_menu(0)

            media = get_help_media()
            result = None
            
            if media:
                try:
                    # Try to upload and use the media file
                    uploaded_file = await bot.upload_file(media)
                    
                    if media.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        # For videos, use document
                        result = builder.document(
                            uploaded_file,
                            text=text,
                            buttons=buttons,
                            parse_mode='html',
                            title="Cipher Elite Help Menu",
                            description="Video help menu"
                        )
                    else:
                        # For images, use photo
                        result = builder.photo(
                            uploaded_file,
                            text=text,
                            buttons=buttons,
                            parse_mode='html'
                        )
                except Exception as e:
                    print(f"⚠️ Failed to load help media: {e}")
                    result = None
            
            # Fallback to article if no media or upload failed
            if not result:
                result = builder.article(
                    title="Cipher Elite Help Menu",
                    text=text,
                    buttons=buttons,
                    parse_mode='html',
                )
            
            await event.answer([result])
        
        # Alive customization menu (via inline query, use "alivecustom" to avoid clash with .alive command)
        elif event.text == "alivecustom":
            try:
                from plugins.alive import user_config, ALIVE_STYLES, INLINE_DATA
                from config.config import Config
                from telethon import version
                from datetime import datetime
                
                # Generate preview text
                uptime = "0:00:00"
                quote = ""
                template = ALIVE_STYLES[user_config.alive_style_index]
                preview_text = template.format(
                    name="Preview",
                    telethon=version.__version__,
                    plugins=len(CMD_LIST),
                    uptime=uptime,
                    version=Config.VERSION,
                    branch=Config.BRANCH,
                    quote=quote,
                )
                
                buttons = [
                    [Button.inline("🖼 Change Alive Pic", "alive_changepic")],
                    [Button.inline(f"🎨 Style: {user_config.alive_style_index + 1}/5", "alive_nextstyle")],
                    [Button.inline(f"{'✅' if user_config.use_pic_for_alive else '❌'} Show Pic", "alive_togglepic")],
                    [Button.inline(f"{'✅' if user_config.show_quotes else '❌'} Show Quotes", "alive_togglequotes")],
                    [Button.inline("✏️ Custom Text", "alive_customtext")],
                    [Button.inline("🔄 Reset to Default", "alive_reset")],
                ]
                
                result = builder.article(
                    title="⚡ Alive Customization",
                    text=f"Current Style: {user_config.alive_style_index + 1}/5\n\n{preview_text}",
                    buttons=buttons,
                    parse_mode='html',
                )
                await event.answer([result])
            except Exception as e:
                result = builder.article(
                    title="❌ Error",
                    text=f"Failed to load alive config: {e}",
                )
                await event.answer([result])
        
        # Ping customization menu (via inline query, use "pingcustom" to avoid clash with .ping command)
        elif event.text == "pingcustom":
            try:
                from plugins.alive import user_config, PING_STYLES
                
                # Generate preview text
                uptime = "0:00:00"
                speed = "0"
                template = PING_STYLES[user_config.ping_style_index]
                preview_text = template.format(speed=speed, uptime=uptime)
                
                buttons = [
                    [Button.inline("🖼 Change Ping Pic", "ping_changepic")],
                    [Button.inline(f"🎨 Style: {user_config.ping_style_index + 1}/5", "ping_nextstyle")],
                    [Button.inline(f"{'✅' if user_config.use_pic_for_ping else '❌'} Show Pic", "ping_togglepic")],
                    [Button.inline("✏️ Custom Text", "ping_customtext")],
                    [Button.inline("🔄 Reset to Default", "ping_reset")],
                ]
                
                result = builder.article(
                    title="🏓 Ping Customization",
                    text=f"Current Style: {user_config.ping_style_index + 1}/5\n\n{preview_text}",
                    buttons=buttons,
                    parse_mode='html',
                )
                await event.answer([result])
            except Exception as e:
                result = builder.article(
                    title="❌ Error",
                    text=f"Failed to load ping config: {e}",
                )
                await event.answer([result])

    # -------------------------------------------------------------------------
    # 2. CALLBACK HANDLER (Button Clicks)
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"help_(.*)"))
    @rishabh_help()
    async def callback_handler(event):
        data = event.data_match.group(1).decode()

        # ⏱️ Reset the 60-second timer on every interaction
        await reset_help_timer(event, event.message_id)

        # --- REOPEN (from expired state) ---
        if data == "reopen":
            text, buttons = _render_menu(0)
            await event.edit(text, buttons=buttons, parse_mode='html')
            return

        # --- CATEGORY VIEW ---
        if data.startswith("cat_"):
            category = data.replace("cat_", "")
            text, buttons = _render_category(category)
            await event.edit(text, buttons=buttons, parse_mode='html')
            return

        # --- VIEW PLUGIN DETAILS ---
        if data.startswith("plugin_"):
            plugin_name = data.replace("plugin_", "")
            if plugin_name in CMD_LIST:
                text, buttons = _render_plugin(plugin_name)
                await event.edit(text, buttons=buttons, parse_mode='html')
            return

        # --- PAGE NAVIGATION ---
        if data.startswith("page_"):
            try:
                page = int(data.replace("page_", ""))
            except ValueError:
                page = 0
            text, buttons = _render_menu(page)
            await event.edit(text, buttons=buttons, parse_mode='html')
            return

    # -------------------------------------------------------------------------
    # 3. ALIVE CUSTOMIZATION CALLBACKS
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"alive_(.*)"))
    @rishabh_help()
    async def alive_callback(event):
        data = event.data_match.group(1).decode()
        
        try:
            from plugins.alive import user_config, save_config, ALIVE_STYLES, INLINE_DATA
            from config.config import Config
            from telethon import version
            
            if data == "nextstyle":
                user_config.alive_style_index = (user_config.alive_style_index + 1) % len(ALIVE_STYLES)
                save_config()
                await event.answer(f"✅ Style changed to {user_config.alive_style_index + 1}/5", alert=True)
            
            elif data == "togglepic":
                user_config.use_pic_for_alive = not user_config.use_pic_for_alive
                save_config()
                state = "ON" if user_config.use_pic_for_alive else "OFF"
                await event.answer(f"✅ Alive pic {state}", alert=True)
            
            elif data == "togglequotes":
                user_config.show_quotes = not user_config.show_quotes
                save_config()
                state = "ON" if user_config.show_quotes else "OFF"
                await event.answer(f"✅ Quotes {state}", alert=True)
            
            elif data == "reset":
                user_config.alive_style_index = 0
                user_config.custom_alive_text = None
                user_config.alive_pic = Config.DEFAULT_ALIVE_PIC
                user_config.use_pic_for_alive = True
                user_config.show_quotes = True
                save_config()
                await event.answer("✅ Reset to default!", alert=True)
            
            elif data == "changepic":
                await event.answer("📸 Reply to an image with .setalivepic command in userbot", alert=True)
                return
            
            elif data == "customtext":
                await event.answer("✏️ Use .setalivetext <text> command in userbot", alert=True)
                return
            
            # Refresh the menu
            uptime = "0:00:00"
            quote = ""
            template = ALIVE_STYLES[user_config.alive_style_index]
            preview_text = template.format(
                name="Preview",
                telethon=version.__version__,
                plugins=len(CMD_LIST),
                uptime=uptime,
                version=Config.VERSION,
                branch=Config.BRANCH,
                quote=quote,
            )
            
            buttons = [
                [Button.inline("🖼 Change Alive Pic", "alive_changepic")],
                [Button.inline(f"🎨 Style: {user_config.alive_style_index + 1}/5", "alive_nextstyle")],
                [Button.inline(f"{'✅' if user_config.use_pic_for_alive else '❌'} Show Pic", "alive_togglepic")],
                [Button.inline(f"{'✅' if user_config.show_quotes else '❌'} Show Quotes", "alive_togglequotes")],
                [Button.inline("✏️ Custom Text", "alive_customtext")],
                [Button.inline("🔄 Reset to Default", "alive_reset")],
            ]
            
            await event.edit(
                f"Current Style: {user_config.alive_style_index + 1}/5\n\n{preview_text}",
                buttons=buttons,
                parse_mode='html'
            )
            
        except Exception as e:
            await event.answer(f"❌ Error: {e}", alert=True)

    # -------------------------------------------------------------------------
    # 4. PING CUSTOMIZATION CALLBACKS
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"ping_(.*)"))
    @rishabh_help()
    async def ping_callback(event):
        data = event.data_match.group(1).decode()
        
        try:
            from plugins.alive import user_config, save_config, PING_STYLES
            from config.config import Config
            
            if data == "nextstyle":
                user_config.ping_style_index = (user_config.ping_style_index + 1) % len(PING_STYLES)
                save_config()
                await event.answer(f"✅ Style changed to {user_config.ping_style_index + 1}/5", alert=True)
            
            elif data == "togglepic":
                user_config.use_pic_for_ping = not user_config.use_pic_for_ping
                save_config()
                state = "ON" if user_config.use_pic_for_ping else "OFF"
                await event.answer(f"✅ Ping pic {state}", alert=True)
            
            elif data == "reset":
                user_config.ping_style_index = 0
                user_config.custom_ping_text = None
                user_config.ping_pic = Config.DEFAULT_PING_PIC
                user_config.use_pic_for_ping = True
                save_config()
                await event.answer("✅ Reset to default!", alert=True)
            
            elif data == "changepic":
                await event.answer("📸 Reply to an image with .setpingpic command in userbot", alert=True)
                return
            
            elif data == "customtext":
                await event.answer("✏️ Use .setpingtext <text> command in userbot", alert=True)
                return
            
            # Refresh the menu
            uptime = "0:00:00"
            speed = "0"
            template = PING_STYLES[user_config.ping_style_index]
            preview_text = template.format(speed=speed, uptime=uptime)
            
            buttons = [
                [Button.inline("🖼 Change Ping Pic", "ping_changepic")],
                [Button.inline(f"🎨 Style: {user_config.ping_style_index + 1}/5", "ping_nextstyle")],
                [Button.inline(f"{'✅' if user_config.use_pic_for_ping else '❌'} Show Pic", "ping_togglepic")],
                [Button.inline("✏️ Custom Text", "ping_customtext")],
                [Button.inline("🔄 Reset to Default", "ping_reset")],
            ]
            
            await event.edit(
                f"Current Style: {user_config.ping_style_index + 1}/5\n\n{preview_text}",
                buttons=buttons,
                parse_mode='html'
            )
            
        except Exception as e:
            await event.answer(f"❌ Error: {e}", alert=True)

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
                        msg += f"  <code>{i + 1}.</code> {help_ui.esc(str(cmd)[:50])}\n"
                    msg += "\n"

            if len(msg) > 4000:
                for x in range(0, len(msg), 4000):
                    await event.reply(msg[x:x + 4000], parse_mode='html')
            else:
                await event.reply(msg, parse_mode='html')
        except Exception as e:
            await event.reply(f"❌ Error: {e}")

    return bot


async def register_commands():
    pass