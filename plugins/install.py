# ==============================================================================
#  Cipher Elite - Advanced Plugin Manager (Fixed)
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
from plugins.bot import add_handler, remove_handler

VERSION = "1.0.0"
CATEGORY = "developer"

PLUGIN_DIR = "plugins"

STDLIB_MODULES = {
    "os", "sys", "math", "time", "datetime", "json", "asyncio", "re", "pathlib",
    "collections", "itertools", "functools", "operator", "string", "textwrap",
    "unicodedata", "struct", "codecs", "io", "abc", "typing", "contextlib",
    "logging", "warnings", "traceback", "threading", "multiprocessing", "subprocess",
    "socket", "http", "urllib", "email", "html", "xml", "csv", "sqlite3", "hashlib",
    "hmac", "secrets", "random", "statistics", "copy", "pprint", "enum", "dataclasses",
    "inspect", "importlib", "pkgutil", "ast", "dis", "builtins", "types", "weakref",
    "gc", "pickle", "shelve", "marshal", "dbm", "gzip", "bz2", "lzma", "zipfile",
    "tarfile", "tempfile", "shutil", "glob", "fnmatch", "stat", "fileinput",
    "filecmp", "signal", "mmap", "ctypes", "concurrent", "queue", "sched",
    "selectors", "mimetypes", "base64", "binascii", "quopri", "uu", "ftplib",
    "poplib", "imaplib", "smtplib", "telnetlib", "xmlrpc", "ipaddress",
    "ssl", "select", "array", "bisect", "heapq", "decimal", "fractions",
    "numbers", "cmath", "operator", "keyword", "token", "tokenize", "pdb",
    "profile", "timeit", "platform", "errno", "faulthandler", "atexit",
    "configparser", "argparse", "getopt", "getpass", "locale", "gettext",
}

IGNORE_LOCAL = {"telethon", "utils", "plugins", "config", "DB", "core", "vars", "startup"}

PACKAGE_MAPPING = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "skimage": "scikit-image",
    "google.generativeai": "google-generativeai",
    "google.genai": "google-generativeai",
    "genai": "google-generativeai",
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
    "gtts": "gTTS",
    "aiohttp": "aiohttp",
    "aiofiles": "aiofiles",
    "motor": "motor",
    "pymongo": "pymongo",
    "lxml": "lxml",
    "beautifulsoup4": "beautifulsoup4",
    "speedtest": "speedtest-cli",
    "pyfiglet": "pyfiglet",
    "Faker": "Faker",
    "geopy": "geopy",
    "instaloader": "instaloader",
    "Faker": "Faker",
}

def get_imports(source_code):
    """Scans code for imports. Returns list of import names."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []
    imports = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
                imports.add(node.module.split('.')[0])
                
    return list(imports)

def is_installed(module_name):
    """Checks if a library is installed."""
    if module_name in STDLIB_MODULES or module_name in sys.builtin_module_names:
        return True
    
    try:
        if importlib.util.find_spec(module_name) is not None:
            return True
    except (ModuleNotFoundError, ValueError):
        pass
        
    return False

def needs_install(module_name):
    """Determines if a module needs to be installed."""
    if module_name in STDLIB_MODULES or module_name in sys.builtin_module_names:
        return False
    if module_name in IGNORE_LOCAL:
        return False
    if is_installed(module_name):
        return False
    return True

async def install_package(import_name):
    """Installs the pip package corresponding to the import name."""
    pip_name = PACKAGE_MAPPING.get(import_name, import_name)
    
    process = await asyncio.create_subprocess_shell(
        f"{sys.executable} -m pip install {pip_name} --quiet",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    importlib.invalidate_caches()
    try:
        site.addsitedir(site.getsitepackages()[0])
    except (IndexError, AttributeError):
        pass
    
    return process.returncode == 0, stderr.decode() if stderr else ""

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
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == 'add_handler':
                    if node.args and isinstance(node.args[0], ast.Constant):
                        return node.args[0].value
                elif isinstance(func, ast.Attribute) and func.attr == 'add_handler':
                    if node.args and isinstance(node.args[0], ast.Constant):
                        return node.args[0].value
    except:
        pass
    return None

def get_event_handlers(module_name):
    """Get all event handlers registered by a module."""
    handlers = []
    if not hasattr(CipherElite, '_event_builders'):
        return handlers
    
    for item in CipherElite._event_builders:
        if isinstance(item, tuple) and len(item) >= 2:
            callback = item[1]
            if hasattr(callback, '__module__') and callback.__module__ == module_name:
                handlers.append(item)
        elif hasattr(item, 'callback'):
            callback = item.callback
            if hasattr(callback, '__module__') and callback.__module__ == module_name:
                handlers.append(item)
    
    return handlers

def remove_event_handlers(module_name):
    """Remove all event handlers registered by a module."""
    handlers = get_event_handlers(module_name)
    removed = 0
    
    for handler in handlers:
        try:
            if handler in CipherElite._event_builders:
                CipherElite._event_builders.remove(handler)
                removed += 1
        except (ValueError, AttributeError):
            pass
    
    return removed

def init(client_instance):
    commands = [
        ".install - Safe Update & Auto-Dependency Install",
        ".uninstall <name> - Remove plugin & clean help"
    ]
    description = "Developer - Smart Plugin Manager"
    add_handler("install", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.install$"))
    @rishabh()
    async def install_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.file or not reply.file.name.endswith('.py'):
            return await event.reply("Usage: Reply to a `.py` file with `.install`")

        status = await event.reply("Analyzing Code...")
        
        file_name = reply.file.name
        final_path = Path(PLUGIN_DIR) / file_name
        temp_path = Path(PLUGIN_DIR) / f"temp_{file_name}"
        module_name = f"plugins.{file_name[:-3]}"
        
        is_update = os.path.exists(final_path)

        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            await reply.download_media(file=temp_path)

            is_valid, error_msg, source_code = validate_python_code(temp_path)
            if not is_valid:
                os.remove(temp_path)
                return await status.edit(f"Install Failed: Syntax Error.\n`{error_msg}`")

            await status.edit("Checking Dependencies...")
            
            imports_found = get_imports(source_code)
            to_install = []
            
            for mod in imports_found:
                if needs_install(mod):
                    pip_name = PACKAGE_MAPPING.get(mod, mod)
                    if pip_name not in [PACKAGE_MAPPING.get(i, i) for i in to_install]:
                        to_install.append(mod)
            
            installed_count = 0
            for mod in to_install:
                pip_name = PACKAGE_MAPPING.get(mod, mod)
                await status.edit(f"Installing: `{pip_name}`...")
                success, err = await install_package(mod)
                if success:
                    installed_count += 1
                else:
                    await status.edit(f"Warning: Failed to install `{pip_name}`\n`{err[:100]}`")
                    await asyncio.sleep(1)

            if is_update:
                old_module_name = module_name
                if old_module_name in sys.modules:
                    remove_event_handlers(old_module_name)
                    del sys.modules[old_module_name]
                os.remove(final_path)
            os.rename(temp_path, final_path)

            await status.edit("Activating...")
            
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            if hasattr(module, "init"):
                module.init(event.client)
            if hasattr(module, "register_commands"):
                await module.register_commands()

            action = "Updated" if is_update else "Installed"
            libs_msg = f"\nLibs Added: `{installed_count}`" if installed_count > 0 else ""
            
            await status.edit(
                f"**Cipher Elite Manager**\n\n"
                f"Plugin {action}: `{file_name}`"
                f"{libs_msg}\n"
                f"Status: Active!"
            )

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            await status.edit(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.uninstall\s+(.+)"))
    @rishabh()
    async def uninstall_handler(event):
        plugin_name = event.pattern_match.group(1).strip()
        file_name = f"{plugin_name}.py" if not plugin_name.endswith(".py") else plugin_name
        file_path = Path(PLUGIN_DIR) / file_name
        module_name = f"plugins.{file_name[:-3]}"

        if not os.path.exists(file_path):
            return await event.reply(f"Error: `{file_name}` not found.")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            help_key = get_plugin_key(source)
            
            handlers_removed = remove_event_handlers(module_name)
            
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            os.remove(file_path)

            help_msg = ""
            if help_key:
                remove_handler(help_key)
                help_msg = f"\nRemoved from Help: `{help_key}`"

            await event.reply(
                f"Deleted: `{file_name}`\n"
                f"Event Handlers Removed: `{handlers_removed}`"
                f"{help_msg}"
            )

        except Exception as e:
            await event.reply(f"Error: {str(e)}")
            
