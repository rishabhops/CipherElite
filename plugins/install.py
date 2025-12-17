# ==============================================================================
#  🎭 Cipher Elite - Advanced Plugin Manager (Fixed)
#  Features: Smart Dependency Mapping & Auto-Install
# ==============================================================================

import os
import sys
import ast
import asyncio
import importlib
import importlib.util
import site
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

# 🧠 SMART MAPPING: Import Name -> Real Pip Package Name
# This fixes the issue where "google" installs the wrong thing.
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

# --- Helper Functions ---

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
                imports.add(alias.name) # Full name: google.generativeai
                imports.add(alias.name.split('.')[0]) # Top level: google
                
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
    
    # 1. Try finding spec
    try:
        if importlib.util.find_spec(module_name) is not None:
            return True
    except:
        pass
        
    # 2. Check mapping (Maybe the package name is different from import name)
    # We assume if the import scan got here, we strictly need to check installation.
    # But usually, find_spec works for the *import name*.
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
                    if isinstance(node.args[0], ast.Constant): return node.args[0].value
                    elif isinstance(node.args[0], ast.Str): return node.args[0].s
    except: pass
    return None

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".install - Safe Update & Auto-Dependency Install",
        ".uninstall <name> - Remove plugin & clean help"
    ]
    description = "🎭 Developer - Smart Manager"
    add_handler("developer", commands, description)

async def register_commands():

    # -------------------------------------------------------------------------
    # 1. INSTALL / UPDATE
    # -------------------------------------------------------------------------
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
            if os.path.exists(temp_path): os.remove(temp_path)
            await reply.download_media(file=temp_path)

            # 2. Validate Syntax
            is_valid, error_msg, source_code = validate_python_code(temp_path)
            if not is_valid:
                os.remove(temp_path)
                return await status.edit(f"❌ **Install Failed:** Syntax Error.\n`{error_msg}`")

            # 3. CHECK & INSTALL REQUIREMENTS
            await status.edit("🔄 **Checking Dependencies...**")
            
            # Scan imports
            imports_found = get_imports(source_code)
            installed_count = 0
            
            for mod in imports_found:
                # Filter out standard libraries and local folders
                if mod in sys.builtin_module_names: continue
                if mod in ["telethon", "utils", "plugins", "config", "google"]: continue 
                # Note: We skip 'google' generally, but 'google.generativeai' will be caught below because we scan submodules now.

                # If it's a known mapping key (like google.generativeai), check it specifically
                if mod in PACKAGE_MAPPING:
                    if not is_installed(mod):
                        await status.edit(f"🛠 **Installing:** `{PACKAGE_MAPPING[mod]}`...")
                        success, err = await install_package(mod)
                        if not success:
                            os.remove(temp_path)
                            return await status.edit(f"❌ **Pip Failed:** `{PACKAGE_MAPPING[mod]}`\n\nError: `{err[:150]}...`")
                        installed_count += 1
                
                # Check generic uninstalled modules
                elif not is_installed(mod):
                     # Try to install if it looks like a 3rd party lib
                     # (This is risky but necessary for auto-install)
                     await status.edit(f"🛠 **Installing:** `{mod}`...")
                     success, err = await install_package(mod)
                     if success:
                         installed_count += 1
                     # We don't fail here if generic install fails, might be a false positive (local file)

            # 4. Finalize File
            if is_update: os.remove(final_path)
            os.rename(temp_path, final_path)

            # 5. Hot-Load
            await status.edit("🔄 **Activating...**")
            
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            if hasattr(module, "init"): module.init(event.client)
            if hasattr(module, "register_commands"): await module.register_commands()

            action = "Updated" if is_update else "Installed"
            libs_msg = f"\n📦 **Libs Added:** `{installed_count}`" if installed_count > 0 else ""
            
            await status.edit(
                f"🎭 **Cipher Elite Manager**\n\n"
                f"✅ **Plugin {action}:** `{file_name}`"
                f"{libs_msg}\n"
                f"✨ **Status:** Active!"
            )

        except Exception as e:
            if os.path.exists(temp_path): os.remove(temp_path)
            await status.edit(f"❌ **Error:** {str(e)}")

    # -------------------------------------------------------------------------
    # 2. UNINSTALLER
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
            with open(file_path, "r", encoding="utf-8") as f: source = f.read()
            help_key = get_plugin_key(source)
            
            os.remove(file_path)
            if module_name in sys.modules: del sys.modules[module_name]

            help_msg = ""
            if help_key and remove_handler:
                remove_handler(help_key)
                help_msg = f"\n✅ **Removed from Help:** `{help_key}`"

            await event.reply(f"🗑 **Deleted:** `{file_name}`{help_msg}")

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
            
