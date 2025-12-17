# ==============================================================================
#  🎭 Cipher Elite - Advanced Plugin Manager
# dev telegram @thanosceo
#  Features: Safe Update, Auto-Install Libs, Hot-Load, & Clean Uninstall
# ==============================================================================

import os
import sys
import ast
import asyncio
import importlib
import importlib.util
import shutil
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# ⚠️ Try to import remove_handler. If it fails, define a dummy one.
try:
    from plugins.bot import remove_handler
except ImportError:
    remove_handler = None

# --- Configuration ---
PLUGIN_DIR = "plugins"

# 🧠 Smart Mapping for Pip Install
PACKAGE_MAPPING = {
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "telegram": "Telethon",
    "dateutil": "python-dateutil",
    "qrcode": "qrcode[pil]"
}

# --- Helper Functions ---

def get_imports(source_code):
    """Scans code for required libraries."""
    tree = ast.parse(source_code)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return list(imports)

def get_plugin_key(source_code):
    """Scans code to find the 'add_handler' key for help menu cleanup."""
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id == 'add_handler':
                    if node.args:
                        if isinstance(node.args[0], ast.Constant):
                            return node.args[0].value
                        elif isinstance(node.args[0], ast.Str):
                            return node.args[0].s
    except: pass
    return None

def is_installed(module_name):
    if module_name in sys.builtin_module_names: return True
    return importlib.util.find_spec(module_name) is not None

async def install_package(package_name):
    pip_name = PACKAGE_MAPPING.get(package_name, package_name)
    process = await asyncio.create_subprocess_shell(
        f"{sys.executable} -m pip install {pip_name}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()
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

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".install - Safe Install/Update plugin",
        ".uninstall <name> - Remove plugin & clean help"
    ]
    description = "🎭 Developer - Safe Manager"
    add_handler("developer", commands, description)

async def register_commands():

    # -------------------------------------------------------------------------
    # 1. SMART INSTALLER (SAFE UPDATE)
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.install$"))
    @rishabh()
    async def install_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.file or not reply.file.name.endswith('.py'):
            return await event.reply("💡 **Usage:** Reply to a `.py` file with `.install`")

        status = await event.reply("🔄 **Analyzing...**")
        
        file_name = reply.file.name
        final_path = Path(PLUGIN_DIR) / file_name
        temp_path = Path(PLUGIN_DIR) / f"temp_{file_name}" # Download to temp first
        module_name = f"plugins.{file_name[:-3]}"
        
        is_update = os.path.exists(final_path)
        action_text = "Updated" if is_update else "Installed"

        try:
            # 1. Download to TEMP path first (Safe Mode)
            if os.path.exists(temp_path): os.remove(temp_path)
            await reply.download_media(file=temp_path)

            # 2. Validate Code in Temp File
            is_valid, error_msg, source_code = validate_python_code(temp_path)
            
            if not is_valid:
                os.remove(temp_path) # Delete bad update
                msg = f"❌ **{action_text} Failed:** Syntax Error.\n`{error_msg}`"
                if is_update:
                    msg += "\n\n🛡️ **Safe Mode:** Your old plugin was kept safe."
                return await status.edit(msg)

            # 3. Check Requirements
            await status.edit("🔄 **Checking Libs...**")
            required_modules = get_imports(source_code)
            installed_count = 0
            
            for mod in required_modules:
                if mod in ["plugins", "utils", "telethon", "config"]: continue
                if not is_installed(mod):
                    await status.edit(f"🛠 **Installing:** `{mod}`...")
                    success, err = await install_package(mod)
                    if not success:
                        os.remove(temp_path)
                        return await status.edit(f"❌ **Pip Failed:** `{mod}`\nError: {err[:100]}\n\n🛡️ Update cancelled.")
                    installed_count += 1

            # 4. Commit Changes (Swap Temp -> Final)
            if is_update:
                os.remove(final_path) # Delete old
            os.rename(temp_path, final_path) # Move new to final

            # 5. Hot-Load / Reload
            await status.edit("🔄 **Activating...**")
            try:
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    module = importlib.import_module(module_name)

                if hasattr(module, "init"): module.init(event.client)
                if hasattr(module, "register_commands"): await module.register_commands()

                # Success Message
                if is_update:
                    title = "✨ **Plugin Updated**"
                    note = "🔄 **Changes Applied:** Old code replaced."
                else:
                    title = "✅ **Plugin Installed**"
                    note = "✨ **Status:** Active & Ready!"

                await status.edit(
                    f"🎭 **Cipher Elite Manager**\n\n"
                    f"{title}\n"
                    f"📂 **File:** `{file_name}`\n"
                    f"📦 **Libs:** `{installed_count}`\n"
                    f"{note}"
                )
                
            except Exception as e:
                # If load fails, we are in trouble. 
                # Ideally we would rollback, but Python memory reload is tricky.
                # Use simple error for now.
                await status.edit(f"❌ **Activation Error:** `{str(e)}`\nPlugin code updated but crashed on load.")

        except Exception as e:
            if os.path.exists(temp_path): os.remove(temp_path)
            await status.edit(f"❌ **Critical Error:** {str(e)}")

    # -------------------------------------------------------------------------
    # 2. SMART UNINSTALLER
    # -------------------------------------------------------------------------
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
            # 1. Read file to find Help Menu Key
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            help_key = get_plugin_key(source)
            
            # 2. Delete File
            os.remove(file_path)
            
            # 3. Unload from Memory
            if module_name in sys.modules:
                del sys.modules[module_name]

            # 4. Remove from Help Menu
            help_msg = ""
            if help_key and remove_handler:
                if remove_handler(help_key):
                    help_msg = f"\n✅ **Removed from Help:** `{help_key}`"
                else:
                    help_msg = f"\n⚠️ **Help Remove Failed:** Key `{help_key}` not found."

            await event.reply(
                f"🎭 **Cipher Elite Uninstaller**\n\n"
                f"🗑 **Deleted:** `{file_name}`"
                f"{help_msg}"
            )
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
            
