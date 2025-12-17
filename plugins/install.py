# ==============================================================================
#  🎭 Cipher Elite - Plugin Manager
#  Safe Install & Uninstall for Developers
# ==============================================================================

import os
import sys
import ast
import importlib
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# --- Configuration ---
PLUGIN_DIR = "plugins"

# --- Helper Functions ---

def validate_python_code(file_path):
    """
    Reads a file and checks for Syntax Errors using AST.
    Returns (True, None) if valid, (False, error_message) if invalid.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        # Parse the code to check for syntax errors without executing it
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".install - Reply to a .py file to install",
        ".uninstall <name> - Remove a plugin"
    ]
    description = "🎭 Developer - Manage & Install Plugins safely"
    add_handler("developer", commands, description)

async def register_commands():

    # -------------------------------------------------------------------------
    # 1. INSTALL PLUGIN
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.install$"))
    @rishabh()
    async def install_handler(event):
        reply = await event.get_reply_message()
        
        # 1. Validation: Did user reply to a file?
        if not reply or not reply.file or not reply.file.name.endswith('.py'):
            return await event.reply("💡 **Usage:** Reply to a `.py` file with `.install`")

        status = await event.reply("🔄 **Downloading & Verifying...**")
        
        file_name = reply.file.name
        file_path = Path(PLUGIN_DIR) / file_name

        try:
            # 2. Download File
            if os.path.exists(file_path):
                await status.edit(f"⚠️ **Warning:** `{file_name}` already exists. Overwriting...")
            
            await reply.download_media(file=file_path)

            # 3. SAFETY CHECK: Validate Code Structure
            is_valid, error_msg = validate_python_code(file_path)

            if not is_valid:
                # ❌ FAILED: Delete the file immediately
                os.remove(file_path)
                return await status.edit(
                    f"🎭 **Cipher Elite Security**\n\n"
                    f"❌ **Installation Failed!**\n"
                    f"The file `{file_name}` contains errors and was **NOT** installed.\n\n"
                    f"🔍 **Error:** `{error_msg}`"
                )

            # 4. Success: Try to load it (Optional Hot-Load)
            try:
                # We attempt to import it to catch Runtime Errors (like missing imports)
                module_name = f"plugins.{file_name[:-3]}"
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                    
                await status.edit(
                    f"🎭 **Cipher Elite Installer**\n\n"
                    f"✅ **Installed:** `{file_name}`\n"
                    f"📦 **Size:** `{reply.file.size} bytes`\n"
                    f"✨ **Status:** Loaded Successfully!"
                )
                
            except Exception as e:
                # If Runtime Import fails, we usually keep the file but warn the user,
                # OR we can be strict and delete it. Here we are STRICT as requested.
                os.remove(file_path)
                await status.edit(
                    f"🎭 **Cipher Elite Installer**\n\n"
                    f"❌ **Import Error!**\n"
                    f"The code syntax is fine, but it crashed while loading.\n"
                    f"🗑 **File Deleted.**\n\n"
                    f"🔍 **Error:** `{str(e)}`"
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
        
        # Add .py if user forgot it
        if not plugin_name.endswith(".py"):
            file_name = f"{plugin_name}.py"
        else:
            file_name = plugin_name

        file_path = Path(PLUGIN_DIR) / file_name

        if not os.path.exists(file_path):
            return await event.reply(f"❌ **Error:** Plugin `{file_name}` not found in `{PLUGIN_DIR}/`.")

        try:
            # Delete the file
            os.remove(file_path)
            
            await event.reply(
                f"🎭 **Cipher Elite Uninstaller**\n\n"
                f"🗑 **Removed:** `{file_name}`\n"
                f"✅ **Success!** Restart bot to fully clear memory."
            )
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
          
