# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    carbon (ultra edition)
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
# =============================================================================

import asyncio
import json
import os
import random
import re
import tempfile
import urllib.parse

import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "media"

# -----------------------------------------------------------------------------
#  Config / Endpoints
# -----------------------------------------------------------------------------
# Primary + fallback endpoints. Each is tried in order until one succeeds.
CARBON_ENDPOINTS = [
    "https://carbonara.solopov.dev/api/cook",
    "https://carbonara-42.fly.dev/api/cook",
]

# ray.so community mirrors (ray.so itself has no image API).
RAYSO_ENDPOINTS = [
    "https://rayso-api.vercel.app/api",
    "https://rayso.dev/api",
]

# sourcecodeshots.com — stable, officially documented image API.
SNAP_API = "https://sourcecodeshots.com/api/image"

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=45)
MAX_CODE_CHARS = 12000
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "DB", "carbon_config.json")

CARBON_THEMES = [
    "3024-night", "a11y-dark", "blackboard", "base16-dark",
    "base16-light", "cobalt", "dracula", "duotone-dark",
    "hopscotch", "lucario", "material", "monokai",
    "night-owl", "nord", "oceanic-next", "one-light",
    "one-dark", "panda-syntax", "paraiso-dark", "seti",
    "shades-of-purple", "solarized-dark", "solarized-light",
    "synthwave-84", "twilight", "verminal", "vscode",
    "yeti", "zenburn",
]

RAYSO_THEMES = [
    "breeze", "candy", "crimson", "falcon",
    "meadow", "midnight", "raindrop", "sunset",
]

SNAP_THEMES = [
    "dark-plus", "light-plus", "github-dark", "github-light",
    "monokai", "dracula-soft", "nord", "one-dark-pro",
    "solarized-dark", "solarized-light",
]

FONTS = [
    "Fira Code", "JetBrains Mono", "Hack", "Source Code Pro",
    "IBM Plex Mono", "Space Mono", "Ubuntu Mono", "Anonymous Pro",
]

# language guessing from code-fence tags and file extensions
EXT_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".tsx": "tsx", ".jsx": "jsx", ".java": "java", ".c": "c",
    ".cpp": "cpp", ".cs": "csharp", ".go": "go", ".rs": "rust",
    ".rb": "ruby", ".php": "php", ".sh": "shell", ".sql": "sql",
    ".html": "html", ".css": "css", ".json": "json", ".yml": "yaml",
    ".yaml": "yaml", ".kt": "kotlin", ".swift": "swift", ".lua": "lua",
}

DEFAULT_CONFIG = {
    "carbon_theme": "dracula",
    "rayso_theme": "midnight",
    "snap_theme": "github-dark",
    "font": "Fira Code",
    "background": "rgba(171, 184, 195, 1)",
    "line_numbers": True,
    "window_controls": True,
}


def init(client_instance):
    commands = [
        ".carbon <reply/code/file> - Carbon image (your default theme)",
        ".rcarbon <reply/code> - Carbon with a random theme",
        ".tcarbon <theme> <reply/code> - Carbon with a chosen theme",
        ".carbonall <reply/code> - Preview 4 random themes side by side",
        ".rayso <reply/code> - ray.so style image",
        ".rrayso <reply/code> - ray.so with a random theme",
        ".snap <reply/code/file> - sourcecodeshots image (most reliable)",
        ".tsnap <theme> <reply/code> - snap with a chosen theme",
        ".themes - List all themes for every engine",
        ".cset <key> <value> - Set defaults (theme/font/bg/linenumbers)",
        ".cset - Show current configuration",
        ".creset - Reset configuration to defaults",
    ]
    description = "Ultra code beautifier — Carbon, ray.so & sourcecodeshots with themes, fallbacks and per-user config"
    add_handler("carbon", commands, description)


# -----------------------------------------------------------------------------
#  Persistent config
# -----------------------------------------------------------------------------
def _load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
        return {**DEFAULT_CONFIG, **cfg}
    except (OSError, ValueError):
        return dict(DEFAULT_CONFIG)


def _save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except OSError:
        pass


# -----------------------------------------------------------------------------
#  Code extraction helpers
# -----------------------------------------------------------------------------
FENCE_RE = re.compile(r"^```(\w+)?\n(.*?)```$", re.S)


def _strip_fences(code):
    """Strip ```lang ... ``` fences; return (code, language_or_None)."""
    m = FENCE_RE.match(code.strip())
    if m:
        return m.group(2).rstrip(), (m.group(1) or None)
    return code, None


async def _code_from_document(event, reply):
    """If the reply is a small text/code file, download and decode it."""
    doc = getattr(reply, "document", None)
    if not doc or doc.size > 200_000:
        return None, None
    name = ""
    for attr in doc.attributes:
        if hasattr(attr, "file_name"):
            name = attr.file_name or ""
    ext = os.path.splitext(name)[1].lower()
    if ext not in EXT_LANG:
        return None, None
    raw = await reply.download_media(bytes)
    try:
        return raw.decode("utf-8", errors="replace"), EXT_LANG[ext]
    except Exception:
        return None, None


async def _resolve_code(event):
    """
    Return (code, language) from — in priority order —
    inline text, replied text, or a replied code file.
    """
    parts = event.text.split(maxsplit=1)
    if len(parts) >= 2 and parts[1].strip():
        return _strip_fences(parts[1])

    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            text = reply.text or reply.message
            if text:
                return _strip_fences(text)
            return await _code_from_document(event, reply)

    return None, None


async def _resolve_theme_and_code(event, valid_themes):
    """For '.tcarbon <theme> ...' style commands."""
    parts = event.text.split(maxsplit=2)
    if len(parts) < 2:
        return None, None, "❌ Usage: `.tcarbon <theme> <code>` or reply to a message"

    theme = parts[1].lower()
    if theme not in valid_themes:
        close = [t for t in valid_themes if theme in t][:5]
        hint = f"\nDid you mean: {', '.join(f'`{t}`' for t in close)}" if close else ""
        return None, None, f"❌ Unknown theme: `{theme}`{hint}\nUse `.themes` for the full list."

    if len(parts) >= 3 and parts[2].strip():
        code, _ = _strip_fences(parts[2])
        return theme, code, None

    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            text = reply.text or reply.message
            if text:
                code, _ = _strip_fences(text)
                return theme, code, None
            code, _ = await _code_from_document(event, reply)
            return theme, code, None

    return theme, None, None


def _validate(code):
    if not code or not code.strip():
        return "❌ No code found — reply to a message/code file or pass code inline."
    if len(code) > MAX_CODE_CHARS:
        return f"❌ Code too long ({len(code)} chars, max {MAX_CODE_CHARS})."
    return None


# -----------------------------------------------------------------------------
#  Render engines (all with endpoint fallback + retry)
# -----------------------------------------------------------------------------
async def _post_first_ok(endpoints, payload):
    """POST payload to each endpoint until one returns image bytes."""
    last_err = None
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
        for url in endpoints:
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        if data[:8].startswith(b"\x89PNG") or data[:3] == b"\xff\xd8\xff":
                            return data
                        last_err = RuntimeError(f"{url} returned non-image data")
                    else:
                        last_err = RuntimeError(f"{url} returned HTTP {resp.status}")
            except Exception as e:
                last_err = e
    raise last_err or RuntimeError("All endpoints failed")


async def _fetch_carbon(code, theme, cfg):
    payload = {
        "code": code,
        "theme": theme,
        "backgroundColor": cfg["background"],
        "dropShadow": True,
        "dropShadowOffsetY": "20px",
        "dropShadowBlurRadius": "68px",
        "fontFamily": cfg["font"],
        "fontSize": "14px",
        "lineNumbers": cfg["line_numbers"],
        "windowControls": cfg["window_controls"],
        "paddingVertical": "56px",
        "paddingHorizontal": "56px",
        "exportSize": "2x",
        "widthAdjustment": True,
    }
    return await _post_first_ok(CARBON_ENDPOINTS, payload)


async def _fetch_rayso(code, theme):
    payload = {
        "code": code,
        "title": "CipherElite",
        "theme": theme,
        "darkMode": True,
        "padding": 32,
        "language": "auto",
    }
    return await _post_first_ok(RAYSO_ENDPOINTS, payload)


async def _fetch_snap(code, theme, language=None):
    payload = {
        "code": code,
        "theme": theme,
        "language": language or "auto",
    }
    return await _post_first_ok([SNAP_API], payload)


async def _send_image_bytes(event, image_data, caption):
    fd, path = tempfile.mkstemp(suffix=".png")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(image_data)
        await event.client.send_file(event.chat_id, path, caption=caption)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


async def _run_render(event, status_text, fetch_coro, caption):
    """Shared status-message / error-handling wrapper."""
    msg = await event.reply(status_text)
    try:
        image_data = await fetch_coro
        await _send_image_bytes(event, image_data, caption)
        await msg.delete()
    except asyncio.TimeoutError:
        await msg.edit("❌ Timed out — the render API is slow or down. Try `.snap` instead.")
    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`\nTip: `.snap` uses the most reliable API.")


# -----------------------------------------------------------------------------
#  Command handlers
# -----------------------------------------------------------------------------
async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.carbon(\s|$)"))
    @rishabh()
    async def carbon(event):
        code, _ = await _resolve_code(event)
        err = _validate(code)
        if err:
            await event.reply(err)
            return
        cfg = _load_config()
        await _run_render(
            event, "🎨 Creating carbon image...",
            _fetch_carbon(code, cfg["carbon_theme"], cfg),
            f"✨ Carbon · `{cfg['carbon_theme']}`",
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.rcarbon(\s|$)"))
    @rishabh()
    async def rcarbon(event):
        code, _ = await _resolve_code(event)
        err = _validate(code)
        if err:
            await event.reply(err)
            return
        cfg = _load_config()
        theme = random.choice(CARBON_THEMES)
        await _run_render(
            event, f"🎨 Carbon with random theme `{theme}`...",
            _fetch_carbon(code, theme, cfg),
            f"✨ Carbon · 🎲 `{theme}`",
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.tcarbon(\s|$)"))
    @rishabh()
    async def tcarbon(event):
        theme, code, err = await _resolve_theme_and_code(event, CARBON_THEMES)
        if err:
            await event.reply(err)
            return
        verr = _validate(code)
        if verr:
            await event.reply(verr)
            return
        cfg = _load_config()
        await _run_render(
            event, f"🎨 Carbon with `{theme}`...",
            _fetch_carbon(code, theme, cfg),
            f"✨ Carbon · `{theme}`",
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.carbonall(\s|$)"))
    @rishabh()
    async def carbonall(event):
        """Render the same code in 4 random themes so you can pick one."""
        code, _ = await _resolve_code(event)
        err = _validate(code)
        if err:
            await event.reply(err)
            return
        cfg = _load_config()
        themes = random.sample(CARBON_THEMES, 4)
        msg = await event.reply(f"🎨 Rendering 4 themes: {', '.join(f'`{t}`' for t in themes)}...")
        sent = 0
        for theme in themes:
            try:
                image_data = await _fetch_carbon(code, theme, cfg)
                await _send_image_bytes(event, image_data, f"🎨 `{theme}`")
                sent += 1
            except Exception:
                continue
        if sent:
            await msg.delete()
        else:
            await msg.edit("❌ All renders failed — the carbon API may be down.")

    @CipherElite.on(events.NewMessage(pattern=r"\.rayso(\s|$)"))
    @rishabh()
    async def rayso(event):
        code, _ = await _resolve_code(event)
        err = _validate(code)
        if err:
            await event.reply(err)
            return
        cfg = _load_config()
        await _run_render(
            event, "🎨 Creating ray.so image...",
            _fetch_rayso(code, cfg["rayso_theme"]),
            f"✨ ray.so · `{cfg['rayso_theme']}`",
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.rrayso(\s|$)"))
    @rishabh()
    async def rrayso(event):
        code, _ = await _resolve_code(event)
        err = _validate(code)
        if err:
            await event.reply(err)
            return
        theme = random.choice(RAYSO_THEMES)
        await _run_render(
            event, f"🎨 ray.so with random theme `{theme}`...",
            _fetch_rayso(code, theme),
            f"✨ ray.so · 🎲 `{theme}`",
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.snap(\s|$)"))
    @rishabh()
    async def snap(event):
        code, lang = await _resolve_code(event)
        err = _validate(code)
        if err:
            await event.reply(err)
            return
        cfg = _load_config()
        await _run_render(
            event, "📸 Creating snapshot...",
            _fetch_snap(code, cfg["snap_theme"], lang),
            f"✨ Snap · `{cfg['snap_theme']}`",
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.tsnap(\s|$)"))
    @rishabh()
    async def tsnap(event):
        theme, code, err = await _resolve_theme_and_code(event, SNAP_THEMES)
        if err:
            await event.reply(err)
            return
        verr = _validate(code)
        if verr:
            await event.reply(verr)
            return
        await _run_render(
            event, f"📸 Snapshot with `{theme}`...",
            _fetch_snap(code, theme),
            f"✨ Snap · `{theme}`",
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.themes(\s|$)"))
    @rishabh()
    async def themes(event):
        carbon_list = ", ".join(f"`{t}`" for t in CARBON_THEMES)
        rayso_list = ", ".join(f"`{t}`" for t in RAYSO_THEMES)
        snap_list = ", ".join(f"`{t}`" for t in SNAP_THEMES)
        font_list = ", ".join(f"`{f}`" for f in FONTS)
        await event.reply(
            f"🎨 **Carbon** ({len(CARBON_THEMES)}):\n{carbon_list}\n\n"
            f"🌈 **ray.so** ({len(RAYSO_THEMES)}):\n{rayso_list}\n\n"
            f"📸 **Snap** ({len(SNAP_THEMES)}):\n{snap_list}\n\n"
            f"🔤 **Fonts**:\n{font_list}\n\n"
            f"Use: `.tcarbon <theme>`, `.tsnap <theme>`, `.cset theme <name>`"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.cset(\s|$)"))
    @rishabh()
    async def cset(event):
        cfg = _load_config()
        parts = event.text.split(maxsplit=2)

        if len(parts) == 1:
            lines = [f"• `{k}`: `{v}`" for k, v in cfg.items()]
            await event.reply(
                "⚙️ **Carbon config:**\n" + "\n".join(lines) +
                "\n\nSet with `.cset <key> <value>` — keys: "
                "`theme`, `raysotheme`, `snaptheme`, `font`, `bg`, `linenumbers`, `windowcontrols`"
            )
            return

        if len(parts) < 3:
            await event.reply("❌ Usage: `.cset <key> <value>`")
            return

        key, value = parts[1].lower(), parts[2].strip()

        if key == "theme":
            if value not in CARBON_THEMES:
                await event.reply(f"❌ Unknown carbon theme `{value}`. See `.themes`.")
                return
            cfg["carbon_theme"] = value
        elif key == "raysotheme":
            if value not in RAYSO_THEMES:
                await event.reply(f"❌ Unknown ray.so theme `{value}`. See `.themes`.")
                return
            cfg["rayso_theme"] = value
        elif key == "snaptheme":
            if value not in SNAP_THEMES:
                await event.reply(f"❌ Unknown snap theme `{value}`. See `.themes`.")
                return
            cfg["snap_theme"] = value
        elif key == "font":
            match = next((f for f in FONTS if f.lower() == value.lower()), None)
            if not match:
                await event.reply(f"❌ Unknown font `{value}`. See `.themes`.")
                return
            cfg["font"] = match
        elif key == "bg":
            cfg["background"] = value  # any CSS color: hex, rgb(), rgba()
        elif key == "linenumbers":
            cfg["line_numbers"] = value.lower() in ("on", "true", "yes", "1")
        elif key == "windowcontrols":
            cfg["window_controls"] = value.lower() in ("on", "true", "yes", "1")
        else:
            await event.reply(f"❌ Unknown key `{key}`.")
            return

        _save_config(cfg)
        await event.reply(f"✅ Saved: `{key}` → `{value}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.creset(\s|$)"))
    @rishabh()
    async def creset(event):
        _save_config(dict(DEFAULT_CONFIG))
        await event.reply("♻️ Carbon config reset to defaults.")
