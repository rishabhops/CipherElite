# ==============================================================================
#  🎭 Cipher Elite - Plugin install Manager
# ==============================================================================

import os
import sys
import ast
import importlib
import asyncio
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# --- Configuration ---
PLUGIN_DIR = "plugins"

# --- Helper Functions ---

def validate_python_code(file_path):
    """Checks for Syntax Errors before running."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".install - Reply to .py file to install & activate",
        ".uninstall <name> - Remove a plugin"
    ]
    description = "🎭 Developer - Manage Plugins (Hot-Load)"
    add_handler("developer", commands, description)

async def register_commands():

    # -------------------------------------------------------------------------
    # 1. INSTALL & ACTIVATE PLUGIN
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.install$"))
    @rishabh()
    async def install_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.file or not reply.file.name.endswith('.py'):
            return await event.reply("💡 **Usage:** Reply to a `.py` file with `.install`")

        status = await event.reply("🔄 **Installing & Activating...**")
        
        file_name = reply.file.name
        file_path = Path(PLUGIN_DIR) / file_name
        module_name = f"plugins.{file_name[:-3]}"

        try:
            # 1. Download
            if os.path.exists(file_path):
                # If it exists, remove old compiled python files to ensure fresh load
                try:
                    os.remove(file_path)
                except: pass
            
            await reply.download_media(file=file_path)

            # 2. Syntax Check
            is_valid, error_msg = validate_python_code(file_path)
            if not is_valid:
                os.remove(file_path)
                return await status.edit(f"❌ **Install Failed:** Syntax Error.\n`{error_msg}`")

            # 3. Import & Hot-Load
            try:
                if module_name in sys.modules:
                    # Reload existing module
                    module = importlib.reload(sys.modules[module_name])
                else:
                    # Import new module
                    module = importlib.import_module(module_name)

                # --- ⚠️ CRITICAL FIX: MANUALLY RUN THE FUNCTIONS ---
                
                # A) Run init() to add to Help Menu
                if hasattr(module, "init"):
                    module.init(event.client)
                
                # B) Run register_commands() to start the Command Listener
                if hasattr(module, "register_commands"):
                    # We must await it because it's async
                    await module.register_commands()

                await status.edit(
                    f"🎭 **Cipher Elite Installer**\n\n"
                    f"✅ **Installed:** `{file_name}`\n"
                    f"🔄 **Activated:** Yes\n"
                    f"✨ **Status:** Ready to use!"
                )
                
            except Exception as e:
                # If activation fails, delete file so bot doesn't crash on restart
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                await status.edit(
                    f"❌ **Activation Error!**\n"
                    f"The code is valid Python, but it crashed during activation.\n"
                    f"**Error:** `{str(e)}`\n"
                    f"🗑 **Plugin Deleted.**"
                )

        except Exception as e:
            await status.edit(f"❌ **Critical Error:** {str(e)}")

    # -------------------------------------------------------------------------
    # 2. UNINSTALL PLUGIN
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.uninstall\s+(.+)"))
    @rishabh()
    async def uninstall_handler(event):
        plugin_name = event.pattern_match.group(1).strip()
        if not plugin_name.endswith(".py"):
            file_name = f"{plugin_name}.py"
        else:
            file_name = plugin_name

        file_path = Path(PLUGIN_DIR) / file_name
        module_name = f"plugins.{file_name[:-3]}"

        if not os.path.exists(file_path):
            return await event.reply(f"❌ **Error:** `{file_name}` not found.")

        try:
            os.remove(file_path)
            
            # Note: We can't easily "unload" the code from memory without restarting,
            # but deleting the file ensures it won't load next time.
            if module_name in sys.modules:
                del sys.modules[module_name]

            await event.reply(
                f"🎭 **Cipher Elite Uninstaller**\n\n"
                f"🗑 **Deleted:** `{file_name}`\n"
                f"⚠️ **Note:** Functionality stops fully after restart."
            )
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
            
