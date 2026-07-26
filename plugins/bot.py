# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    bot
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  Update On: 26/07/2026
# =============================================================================

import os
import sys
import ast
import site
import math
import random
import asyncio
import importlib
import importlib.util
import requests
from io import BytesIO
from pathlib import Path

from telethon import TelegramClient, events, Button
from config.config import Config
from utils.decorators import rishabh_help, rishabh
from utils.utils import CipherElite

# Initialize Bot Client
bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)

# Global Command Storage
CMD_LIST = {}

# Pagination Settings
PLUGINS_PER_PAGE = 9  # 3x3 grid
PLUGINS_PER_ROW = 3

# Random Emoji Pool (50+)
RANDOM_EMOJIS = [
    "🫶", "☠️", "❤️‍🔥", "🚬", "💀", "🔥", "✨", "⚡", "🌟", "💫",
    "🎯", "🎪", "🎨", "🎭", "🎬", "🎸", "🎹", "🎺", "🎻", "🥁",
    "🚀", "🛸", "🌌", "⭐", "🌠", "💥", "⚔️", "🗡️", "🏆", "👑",
    "💎", "🔱", "⚜️", "🎖️", "🏅", "🎁", "🎀", "🎊", "🎉", "🎈",
    "🌈", "☄️", "🌪️", "⛈️", "🌩️", "🔆", "🌞", "🌙", "⭐", "🌟",
    "💥", "🔥", "⚡", "✨", "💫", "🎆", "🎇", "🌠", "💢", "💬"
]

# --- Global Tracker for Auto-Close Timers ---
HELP_TIMERS = {}

# ─────────────── SEND PLUGIN CONFIG (merged from send.py) ───────────────
SEND_LOGO_URL = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/cipher.jpg"
SEND_CHANNEL_LINK = "https://t.me/cipherelite_support"

# ─────────────── INSTALL/UNINSTALL CONFIG (merged from install.py) ───────────────
PLUGIN_DIR = "plugins"

# 🧠 SMART MAPPING: Import Name -> Real Pip Package Name
PACKAGE_MAPPING = {
    # Image Processing
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "skimage": "scikit-image",

    # AI & Google
    "google.generativeai": "google-generativeai",
    "google.genai": "google-generativeai",
    "genai": "google-generativeai",

    # Utilities
    "bs4": "beautifulsoup4",
    "yaml": "PyYAML",
    "dateutil": "python-dateutil",
    "qrcode": "qrcode[pil]",
    "requests": "requests",
    "numpy": "numpy",
    "pandas": "pandas",
    "youtube_dl": "youtube_dl",
    "yt_dlp": "yt-dlp",
    "pydub": "pydub",
    "ffmpeg": "ffmpeg-python",
    "gtts": "gTTS"
}


def get_random_emojis():
    """Get two random emojis from the pool for button decoration."""
    return random.choice(RANDOM_EMOJIS), random.choice(RANDOM_EMOJIS)


def get_help_media():
    """
    Returns the image to use for the help menu.
    Defaults to whatever the user has set as their alive_pic (auto-synced),
    so changing .setalivepic also updates the help menu image automatically.
    Falls back to None (text-only) if alive plugin isn't loaded or pic is disabled.
    """
    try:
        from plugins import alive as alive_module
        if alive_module.user_config.use_pic_for_alive and alive_module.user_config.alive_pic:
            return alive_module.user_config.alive_pic
    except Exception:
        pass
    return None


def get_send_thumb():
    """Download thumbnail image from GitHub for the .send command"""
    try:
        response = requests.get(SEND_LOGO_URL, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        print(f"Thumb download error: {e}")
    return None


# ─────────────── INSTALL/UNINSTALL HELPER FUNCTIONS (merged from install.py) ───────────────

def get_imports(source_code):
    """
    Scans code for imports.
    Returns BOTH top-level names ('os') and full sub-modules ('google.generativeai').
    """
    tree = ast.parse(source_code)
    imports = set()

    for node in ast.walk(tree):
        # Handle 'import xyz'
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)  # Full name: google.generativeai
                imports.add(alias.name.split('.')[0])  # Top level: google

        # Handle 'from xyz import abc'
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
                imports.add(node.module.split('.')[0])

    return list(imports)


def is_installed(module_name):
    """Checks if a library is installed."""
    if module_name in sys.builtin_module_names:
        return True

    try:
        if importlib.util.find_spec(module_name) is not None:
            return True
    except Exception:
        pass

    return False


async def install_package(import_name):
    """Installs the pip package corresponding to the import name."""

    # 1. Check Mapping First (e.g. cv2 -> opencv-python)
    pip_name = PACKAGE_MAPPING.get(import_name, import_name)

    # Ignore common system modules that might flag false positives
    if pip_name in ["os", "sys", "math", "time", "datetime", "json", "asyncio", "telethon", "utils", "plugins", "config"]:
        return True, "Skipped system/local module"

    # 2. Run Pip Install
    process = await asyncio.create_subprocess_shell(
        f"{sys.executable} -m pip install {pip_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    # 3. Reload Site Packages so Python sees it immediately
    importlib.invalidate_caches()
    site.addsitedir(site.getsitepackages()[0])

    return process.returncode == 0, stderr.decode()


def validate_python_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, None, source
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}", None
    except Exception as e:
        return False, str(e), None


def get_plugin_key(source_code):
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == 'add_handler':
                if node.args:
                    if isinstance(node.args[0], ast.Constant):
                        return node.args[0].value
                    elif isinstance(node.args[0], ast.Str):
                        return node.args[0].s
    except Exception:
        pass
    return None


async def reset_help_timer(event, message_id):
    """Resets the 60-second auto-close timer every time a button is clicked."""
    if message_id in HELP_TIMERS:
        HELP_TIMERS[message_id].cancel()

    async def close_menu():
        await asyncio.sleep(60)
        try:
            emoji1, emoji2 = get_random_emojis()
            text = (
                f"<i>⏳ Cipher Elite help session expired.</i>\n\n"
                f"<b>Tap below to reopen or visit us:</b>"
            )
            buttons = [
                [
                    Button.inline(f"{emoji1} Reopen {emoji2}", "help_reopen"),
                ],
                [
                    Button.url(f"{emoji1} Update", "https://t.me/CipherElite_Userbot"),
                    Button.url(f"Support {emoji2}", "https://t.me/cipherelite_support"),
                ]
            ]
            await event.edit(text, buttons=buttons, parse_mode='html')
        except Exception:
            pass

    HELP_TIMERS[message_id] = asyncio.create_task(close_menu())


def init(client_instance):
    # Register this file's own commands (.send, .install, .uninstall)
    # to the help menu.
    add_handler(
        "send",
        [".send <plugin_name> - Send a plugin file from server"],
        "📦 Send Plugin - Send any installed plugin file"
    )
    add_handler(
        "developer",
        [
            ".install - Safe Update & Auto-Dependency Install",
            ".uninstall <name> - Remove plugin & clean help"
        ],
        "🎭 Developer - Smart Manager"
    )


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

            plugin_names_preview = list(CMD_LIST.keys())
            plugin_names_preview.sort(key=lambda x: (x != 'quickhelp', x))
            total_pages = math.ceil(len(plugin_names_preview) / PLUGINS_PER_PAGE)

            text = (
                "<code>root@cipher-elite:~$ help</code>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"[OK] System online\n"
                f"[OK] {total_plugins} plugins loaded\n"
                f"[OK] {total_commands} commands indexed\n\n"
                f"📦 <b>{total_plugins}</b>      ⚙️ <b>{total_commands}</b>      🟢 <b>Online</b>\n"
                f"Plugins    Commands    Status\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<i>Select a module below to view commands.</i>\n"
                f"[INFO] page 1 of {total_pages} — tap a module 👇"
            )

            buttons = []
            plugin_names = list(CMD_LIST.keys())
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x))  # quickhelp first

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
            if row:
                buttons.append(row)

            # Add permanent Update & Support buttons with random emojis
            emoji1, emoji2 = get_random_emojis()
            buttons.append([
                Button.url(f"{emoji1} Update", "https://t.me/CipherElite_Userbot"),
                Button.url(f"Support {emoji2}", "https://t.me/cipherelite_support"),
            ])

            if total_pages > 1:
                buttons.append([Button.inline("Next Page ❯", f"help_page_1")])

            media = get_help_media()
            if media:
                result = builder.photo(
                    media,
                    text=text,
                    buttons=buttons,
                    parse_mode='html'
                )
            else:
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

        # --- REOPEN (from expired state) ---
        if data == "reopen":
            total_plugins = len(CMD_LIST)
            total_commands = sum(len(cmd_data['commands']) for cmd_data in CMD_LIST.values())
            plugin_names = list(CMD_LIST.keys())
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x))
            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)

            text = (
                "<code>root@cipher-elite:~$ help</code>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"[OK] System online\n"
                f"[OK] {total_plugins} plugins loaded\n"
                f"[OK] {total_commands} commands indexed\n\n"
                f"📦 <b>{total_plugins}</b>      ⚙️ <b>{total_commands}</b>      🟢 <b>Online</b>\n"
                f"Plugins    Commands    Status\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<i>Select a module below to view commands.</i>\n"
                f"[INFO] page 1 of {total_pages} — tap a module 👇"
            )

            buttons = []
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
            if row:
                buttons.append(row)

            # Random emojis for Update & Support
            emoji1, emoji2 = get_random_emojis()
            buttons.append([
                Button.url(f"{emoji1} Update", "https://t.me/CipherElite_Userbot"),
                Button.url(f"Support {emoji2}", "https://t.me/cipherelite_support"),
            ])

            if total_pages > 1:
                buttons.append([Button.inline("Next Page ❯", f"help_page_1")])

            await event.edit(text, buttons=buttons, parse_mode='html')
            return

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

                # Random emojis for buttons
                emoji1, emoji2 = get_random_emojis()
                buttons = [
                    [Button.inline("❮ Back to Menu", f"help_page_{page_number}")],
                    [
                        Button.url(f"{emoji1} Update", "https://t.me/CipherElite_Userbot"),
                        Button.url(f"Support {emoji2}", "https://t.me/cipherelite_support"),
                    ]
                ]
                await event.edit(text, buttons=buttons, parse_mode='html')
            return

        # --- PAGE NAVIGATION ---
        if data.startswith("page_"):
            page = int(data.replace("page_", ""))
            plugin_names = list(CMD_LIST.keys())
            plugin_names.sort(key=lambda x: (x != 'quickhelp', x))

            total_pages = math.ceil(len(plugin_names) / PLUGINS_PER_PAGE)

            total_commands = sum(len(cmd_data['commands']) for cmd_data in CMD_LIST.values())

            text = (
                f"<code>root@cipher-elite:~$ help --page {page+1}</code>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"[OK] {len(plugin_names)} plugins loaded\n"
                f"[INFO] page {page+1} of {total_pages}\n\n"
                f"📦 <b>{len(plugin_names)}</b>      ⚙️ <b>{total_commands}</b>      📄 <b>{page+1}/{total_pages}</b>\n"
                f"Plugins    Commands    Page\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<i>Select a module below to view commands.</i>\n"
                f"[INFO] tap a module below 👇"
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
            if row:
                buttons.append(row)

            # Random emojis for permanent buttons
            emoji1, emoji2 = get_random_emojis()
            buttons.append([
                Button.url(f"{emoji1} Update", "https://t.me/CipherElite_Userbot"),
                Button.url(f"Support {emoji2}", "https://t.me/cipherelite_support"),
            ])

            nav = []
            if page > 0:
                nav.append(Button.inline("❮ Previous", f"help_page_{page-1}"))
            if end < len(plugin_names):
                nav.append(Button.inline("Next ❯", f"help_page_{page+1}"))
            if nav:
                buttons.append(nav)

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
    """
    Registers all the userbot-side (CipherElite client) commands owned by
    this file: .send, .install, .uninstall.
    """

    # =========================================================================
    #  .SEND — send a plugin file from the server (merged from send.py)
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.send\s+(.+)"))
    @rishabh()
    async def send_plugin(event):
        try:
            plugin_name = event.pattern_match.group(1).strip().lower()

            if plugin_name.endswith('.py'):
                plugin_name = plugin_name[:-3]

            plugin_path = f"./plugins/{plugin_name}.py"

            if not os.path.exists(plugin_path):
                await event.reply(
                    f"❌ **Plugin not found!**\n\n"
                    f"📄 `{plugin_name}.py` does not exist in plugins folder.\n\n"
                    f"💡 Use `.plugins` to see available plugins."
                )
                return

            sender = await event.get_sender()
            user_mention = f"[{sender.first_name}](tg://user?id={sender.id})"

            caption = (
                "🎭 **Cipher Elite Plugin Sender**\n\n"
                f"📦 **• Plugin name ≈** `{plugin_name}.py`\n"
                f"👤 **• Uploaded by ≈** {user_mention}\n\n"
                f"⚡ **[Powered by Cipher Elite]({SEND_CHANNEL_LINK})** ⚡"
            )

            thumb = get_send_thumb()

            await event.client.send_file(
                event.chat_id,
                plugin_path,
                thumb=thumb,
                caption=caption,
                force_document=True,
                allow_cache=False,
                reply_to=event.reply_to_msg_id or event.id
            )

            await event.delete()

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    # =========================================================================
    #  .INSTALL — Safe Update & Auto-Dependency Install (merged from install.py)
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.install$"))
    @rishabh()
    async def install_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.file or not reply.file.name.endswith('.py'):
            return await event.reply("💡 **Usage:** Reply to a `.py` file with `.install`")

        status = await event.reply("🔄 **Analyzing Code...**")

        file_name = reply.file.name
        final_path = Path(PLUGIN_DIR) / file_name
        temp_path = Path(PLUGIN_DIR) / f"temp_{file_name}"
        module_name = f"plugins.{file_name[:-3]}"

        is_update = os.path.exists(final_path)

        try:
            # 1. Download to Temp
            if os.path.exists(temp_path):
                os.remove(temp_path)
            await reply.download_media(file=temp_path)

            # 2. Validate Syntax
            is_valid, error_msg, source_code = validate_python_code(temp_path)
            if not is_valid:
                os.remove(temp_path)
                return await status.edit(f"❌ **Install Failed:** Syntax Error.\n`{error_msg}`")

            # 3. CHECK & INSTALL REQUIREMENTS
            await status.edit("🔄 **Checking Dependencies...**")

            imports_found = get_imports(source_code)
            installed_count = 0

            for mod in imports_found:
                if mod in sys.builtin_module_names:
                    continue
                if mod in ["telethon", "utils", "plugins", "config", "google"]:
                    continue

                if mod in PACKAGE_MAPPING:
                    if not is_installed(mod):
                        await status.edit(f"🛠 **Installing:** `{PACKAGE_MAPPING[mod]}`...")
                        success, err = await install_package(mod)
                        if not success:
                            os.remove(temp_path)
                            return await status.edit(f"❌ **Pip Failed:** `{PACKAGE_MAPPING[mod]}`\n\nError: `{err[:150]}...`")
                        installed_count += 1

                elif not is_installed(mod):
                    await status.edit(f"🛠 **Installing:** `{mod}`...")
                    success, err = await install_package(mod)
                    if success:
                        installed_count += 1

            # 4. Finalize File
            if is_update:
                os.remove(final_path)
            os.rename(temp_path, final_path)

            # 5. Hot-Load
            await status.edit("🔄 **Activating...**")

            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            if hasattr(module, "init"):
                module.init(event.client)
            if hasattr(module, "register_commands"):
                await module.register_commands()

            action = "Updated" if is_update else "Installed"
            libs_msg = f"\n📦 **Libs Added:** `{installed_count}`" if installed_count > 0 else ""

            # 6. Look up this plugin's registered commands and list them line-wise
            help_key = get_plugin_key(source_code)
            commands_msg = ""
            if help_key and help_key in CMD_LIST:
                cmd_list = CMD_LIST[help_key].get("commands", [])
                if cmd_list:
                    lines = "\n".join(f"  • `{c}`" for c in cmd_list)
                    commands_msg = f"\n\n📜 **Commands:**\n{lines}"

            await status.edit(
                f"🎭 **Cipher Elite Manager**\n\n"
                f"✅ **Plugin {action}:** `{file_name}`"
                f"{libs_msg}\n"
                f"✨ **Status:** Active!"
                f"{commands_msg}"
            )

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            await status.edit(f"❌ **Error:** {str(e)}")

    # =========================================================================
    #  .UNINSTALL — Remove plugin, clean help, auto-trigger self-update
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.uninstall\s+(.+)"))
    @rishabh()
    async def uninstall_handler(event):
        plugin_name = event.pattern_match.group(1).strip()
        file_name = f"{plugin_name}.py" if not plugin_name.endswith(".py") else plugin_name
        file_path = Path(PLUGIN_DIR) / file_name
        module_name = f"plugins.{file_name[:-3]}"

        if not os.path.exists(file_path):
            return await event.reply(f"❌ **Error:** `{file_name}` not found.")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            help_key = get_plugin_key(source)

            os.remove(file_path)
            if module_name in sys.modules:
                del sys.modules[module_name]

            help_msg = ""
            if help_key:
                remove_handler(help_key)
                help_msg = f"\n✅ **Removed from Help:** `{help_key}`"

            await event.reply(f"🗑 **Deleted:** `{file_name}`{help_msg}")

            # Auto-trigger a self-update after uninstalling, so the bot
            # refreshes/restarts cleanly instead of running with a plugin
            # missing from an otherwise-stale state.
            try:
                await event.client.send_message(event.chat_id, ".update")
            except Exception as e:
                await event.reply(f"⚠️ **Couldn't auto-trigger `.update`:** {str(e)}")

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
