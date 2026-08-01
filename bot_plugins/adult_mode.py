# =============================================================================
#  CipherElite Bot Plugin - 18+ Mode (R-Rated Add-ons)
#
#  Plugin Name:    adult_mode
#  Version:        1.0.0
#  Author:         CipherElite Dev
# =============================================================================

import sys
import json
import asyncio
import importlib
import urllib.request
from pathlib import Path
from telethon import events, Button

VERSION = "1.0.0"

REPO_OWNER = "rishabhops"
REPO_NAME = "r_rated_cipher_addons"
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main"

STATE_FILE = Path(__file__).parent.parent / "DB" / "adult_mode.json"


def load_state():
    """Load adult-mode state from JSON."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"enabled": False, "installed_files": []}


def save_state(state):
    """Save adult-mode state to JSON."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def is_enabled():
    return load_state().get("enabled", False)


def _api_request(url):
    req = urllib.request.Request(url, headers={"User-Agent": "CipherElite-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download_file(url, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "CipherElite-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        dest.write_bytes(resp.read())


def fetch_repo_contents(path=""):
    """Fetch contents of a repo path via GitHub API."""
    url = f"{API_BASE}/{path}".rstrip("/")
    return _api_request(url)


def install_adult_plugins():
    """Download all .py userbot plugins from the R-rated repo into plugins/."""
    plugins_dir = Path(__file__).parent.parent / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    installed = []

    # Prefer plugins/ subdirectory if it exists, otherwise use repo root
    try:
        contents = fetch_repo_contents("plugins")
    except Exception:
        contents = fetch_repo_contents("")

    if isinstance(contents, dict):
        # Single file returned instead of list
        contents = [contents]

    for item in contents:
        if item.get("type") != "file" or not item.get("name", "").endswith(".py"):
            continue

        dest = plugins_dir / item["name"]
        download_url = item.get("download_url")
        if not download_url:
            download_url = f"{RAW_BASE}/{item['path']}"

        _download_file(download_url, dest)
        installed.append(item["name"])

    return installed


def uninstall_adult_plugins():
    """Remove previously installed R-rated userbot plugins."""
    state = load_state()
    plugins_dir = Path(__file__).parent.parent / "plugins"
    removed = []

    for filename in state.get("installed_files", []):
        target = plugins_dir / filename
        if target.exists():
            target.unlink()
            removed.append(filename)

    state["enabled"] = False
    state["installed_files"] = []
    save_state(state)
    return removed


# Runtime refs for dynamic loading after install
_bot_ref = None
_owner_id_ref = None
_owner_name_ref = None


def init_bot_plugin(bot, owner_id, owner_name):
    """Initialize adult-mode bot plugin."""
    global _bot_ref, _owner_id_ref, _owner_name_ref
    _bot_ref = bot
    _owner_id_ref = owner_id
    _owner_name_ref = owner_name

    async def _owner_check(event):
        if event.sender_id != owner_id:
            await event.answer("⛔ This is only for the bot owner!", alert=True)
            return False
        return True

    @bot.on(events.CallbackQuery(pattern=r"^enable_adult_mode$"))
    async def enable_adult_mode_cb(event):
        if not await _owner_check(event):
            return

        text = (
            "🔞 <b>18+ Mode - Terms & Conditions</b>\n\n"
            "⚠️ The plugins that will be installed are <b>R-rated</b>.\n"
            "🔞 This content is intended only for users aged 18 and above.\n"
            "🛑 Do not enable if you are underage or in a region where such content is restricted.\n\n"
            "<i>By clicking Agree, you confirm that you are 18+ and accept full responsibility.</i>"
        )
        buttons = [
            [Button.inline("✅ I Agree (18+)", "adult_agree")],
            [Button.inline("◀️ Back", "menu_main")],
        ]
        await event.edit(text, buttons=buttons, parse_mode='html')

    @bot.on(events.CallbackQuery(pattern=r"^adult_agree$"))
    async def adult_agree_cb(event):
        if not await _owner_check(event):
            return

        await event.answer("⏳ Installing 18+ plugins...", alert=True)

        try:
            installed = install_adult_plugins()
            state = load_state()
            state["enabled"] = True
            state["installed_files"] = installed
            save_state(state)

            # Dynamically load newly installed userbot plugins into CMD_LIST
            loaded_now = []
            try:
                from utils.utils import CipherElite
                for filename in installed:
                    try:
                        module_name = f"plugins.{filename[:-3]}"
                        if module_name in sys.modules:
                            module = sys.modules[module_name]
                        else:
                            module = importlib.import_module(module_name)

                        # Register in CMD_LIST via init()
                        if hasattr(module, "init") and CipherElite is not None:
                            module.init(CipherElite)
                            if hasattr(module, "register_commands"):
                                if asyncio.iscoroutinefunction(module.register_commands):
                                    await module.register_commands()
                                else:
                                    module.register_commands()
                            loaded_now.append(filename)
                    except Exception as load_err:
                        print(f"⚠️ Failed to load {filename}: {load_err}")
            except Exception as e:
                print(f"⚠️ Dynamic load error: {e}")

            files_list = "".join(f"• <code>{f}</code>\n" for f in installed) or "<i>(none)</i>"
            load_msg = f"🚀 <b>{len(loaded_now)}</b> loaded & visible in help menu" if loaded_now else "<i>Restart userbot to load new plugins.</i>"
            text = (
                "✅ <b>18+ Mode Enabled</b>\n\n"
                f"📦 Installed <b>{len(installed)}</b> plugin(s):\n"
                f"{files_list}\n"
                f"{load_msg}"
            )
        except Exception as e:
            text = f"❌ <b>Installation Failed:</b>\n<code>{e}</code>"

        buttons = [
            [Button.inline("🏠 Main Menu", "menu_main")],
        ]
        await event.edit(text, buttons=buttons, parse_mode='html')

    @bot.on(events.CallbackQuery(pattern=r"^disable_adult_mode$"))
    async def disable_adult_mode_cb(event):
        if not await _owner_check(event):
            return

        await event.answer("⏳ Disabling 18+ mode...", alert=True)

        try:
            removed = uninstall_adult_plugins()
            files_list = "".join(f"• <code>{f}</code>\n" for f in removed) or "<i>(none)</i>"
            text = (
                "✅ <b>18+ Mode Disabled</b>\n\n"
                f"🗑 Removed <b>{len(removed)}</b> plugin(s):\n"
                f"{files_list}"
            )
        except Exception as e:
            text = f"❌ <b>Error:</b>\n<code>{e}</code>"

        buttons = [
            [Button.inline("🏠 Main Menu", "menu_main")],
        ]
        await event.edit(text, buttons=buttons, parse_mode='html')

    @bot.on(events.NewMessage(pattern=r"^/adultmode$"))
    async def adultmode_command(event):
        if event.sender_id != owner_id:
            return

        state = load_state()
        if state.get("enabled"):
            text = "🔞 <b>18+ Mode is currently enabled.</b>\n\nClick below to disable it."
            btn = Button.inline("🔞 Disable 18+ Mode", "disable_adult_mode")
        else:
            text = "🔞 <b>18+ Mode is currently disabled.</b>\n\nClick below to enable it."
            btn = Button.inline("🔞 Enable 18+ Mode", "enable_adult_mode")

        await event.reply(text, buttons=[[btn]], parse_mode='html')

    print("✅ Adult Mode plugin loaded")
