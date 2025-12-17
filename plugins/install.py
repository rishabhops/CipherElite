# ==============================================================================
#  🎭 Cipher Elite - Advanced Plugin Manager
# dev telegram @thanosceo
# ==============================================================================

import os
import sys
import ast
import asyncio
import importlib
import importlib.util
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# --- Configuration ---
PLUGIN_DIR = "plugins"

# 🧠 Smart Mapping: Import Name -> Pip Package Name
# Some libraries have different names on Pip. We fix them here.
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
    """
    Scans Python code and returns a list of all top-level imported module names.
    """
    tree = ast.parse(source_code)
    imports = set()
    
    for node in ast.walk(tree):
        # Handle 'import xyz'
        if isinstance(node, ast.Import):
            for alias in node.names:
                # We only care about the top level package (e.g., 'os' from 'os.path')
                name = alias.name.split('.')[0]
                imports.add(name)
        # Handle 'from xyz import abc'
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                name = node.module.split('.')[0]
                imports.add(name)
                
    return list(imports)

def is_installed(module_name):
    """Checks if a module is currently installed."""
    # check standard library or existing site-packages
    if module_name in sys.builtin_module_names:
        return True
    
    spec = importlib.util.find_spec(module_name)
    return spec is not None

async def install_package(package_name):
    """Runs pip install asynchronously."""
    # Check mapping (e.g., if code needs 'PIL', install 'Pillow')
    pip_name = PACKAGE_MAPPING.get(package_name, package_name)
    
    process = await asyncio.create_subprocess_shell(
        f"{sys.executable} -m pip install {pip_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    return process.returncode == 0, stderr.decode()

def validate_python_code(file_path):
    """Checks for Syntax Errors."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, None, source
    except SyntaxError as e:
        return False, f"Syntax Error at line {e.lineno}: {e.msg}", None
    except Exception as e:
        return False, str(e), None

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".install - Reply to .py file (Auto-Installs Libs)",
        ".uninstall <name> - Remove a plugin"
    ]
    description = "🎭 Developer - Smart Installer"
    add_handler("developer", commands, description)

async def register_commands():

    # -------------------------------------------------------------------------
    # 1. SMART INSTALLER
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.install$"))
    @rishabh()
    async def install_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.file or not reply.file.name.endswith('.py'):
            return await event.reply("💡 **Usage:** Reply to a `.py` file with `.install`")

        status = await event.reply("🔄 **Analyzing Plugin...**")
        
        file_name = reply.file.name
        file_path = Path(PLUGIN_DIR) / file_name
        module_name = f"plugins.{file_name[:-3]}"

        try:
            # 1. Download File
            if os.path.exists(file_path):
                try: os.remove(file_path)
                except: pass
            
            await reply.download_media(file=file_path)

            # 2. Syntax Check & Source Code Reading
            is_valid, error_msg, source_code = validate_python_code(file_path)
            
            if not is_valid:
                os.remove(file_path)
                return await status.edit(f"❌ **Install Failed:** Syntax Error.\n`{error_msg}`")

            # 3. 🧠 DEPENDENCY CHECKER
            await status.edit("🔄 **Checking Requirements...**")
            
            required_modules = get_imports(source_code)
            installed_count = 0
            
            for mod in required_modules:
                # Skip local plugins folder imports
                if mod == "plugins" or mod == "utils":
                    continue
                    
                if not is_installed(mod):
                    await status.edit(f"🛠 **Installing Requirement:** `{mod}`...\n\n_Please wait, this may take a moment._")
                    
                    success, error_log = await install_package(mod)
                    
                    if not success:
                        os.remove(file_path)
                        return await status.edit(
                            f"❌ **Dependency Error!**\n"
                            f"Failed to install library: `{mod}`\n"
                            f"**Pip Error:**\n`{error_log[:100]}...`\n\n"
                            f"🗑 **Plugin Deleted.**"
                        )
                    installed_count += 1

            # 4. Activation (Hot-Load)
            load_msg = "🔄 **Activating Plugin...**"
            if installed_count > 0:
                load_msg = f"✅ **Installed {installed_count} libraries.**\n" + load_msg
                
            await status.edit(load_msg)

            try:
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    module = importlib.import_module(module_name)

                # Auto-Run Init & Register
                if hasattr(module, "init"):
                    module.init(event.client)
                
                if hasattr(module, "register_commands"):
                    await module.register_commands()

                await status.edit(
                    f"🎭 **Cipher Elite Installer**\n\n"
                    f"✅ **Installed:** `{file_name}`\n"
                    f"📦 **Libs Added:** `{installed_count}`\n"
                    f"✨ **Status:** Active & Ready!"
                )
                
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                await status.edit(f"❌ **Activation Error:** `{str(e)}`\nPlugin deleted.")

        except Exception as e:
            await status.edit(f"❌ **Critical Error:** {str(e)}")

    # -------------------------------------------------------------------------
    # 2. UNINSTALLER
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
            if module_name in sys.modules:
                del sys.modules[module_name]

            await event.reply(
                f"🎭 **Cipher Elite Uninstaller**\n\n"
                f"🗑 **Deleted:** `{file_name}`\n"
                f"✅ **Success!**"
            )
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
            
