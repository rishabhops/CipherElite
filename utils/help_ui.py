# =============================================================================
#  CipherElite — Shared Help UI Theme  (minimalist edition)
#  Target path:  utils/help_ui.py
#
#  Single source of truth for the help aesthetic. Clean, minimal, and built
#  around Telegram's blockquotes (needs Telethon >= 1.44). Pure functions only
#  (no telethon / no CMD_LIST import) to avoid circular imports.
# =============================================================================

import random

# ── Theme knobs ──────────────────────────────────────────────────────────────
BRAND = "Cipher Elite"

# Expandable blockquotes need Telethon >= 1.44. If a command list shows the raw
# "<blockquote expandable>" text instead of a collapsible box:
#   • run  pip install -U telethon , OR
#   • set EXPANDABLE = False (plain quote), OR
#   • set USE_BLOCKQUOTE = False (plain lines).
USE_BLOCKQUOTE = True
EXPANDABLE = True

# ── Per-plugin category icons ────────────────────────────────────────────────
# Add your own plugin names here. Unknown plugins fall back to DEFAULT_ICON.
PLUGIN_ICONS = {
    "quickhelp": "⚡",
    "admin": "👑",
    "afk": "😴",
    "ai_setup": "🤖",
    "ai": "🤖",
    "alive": "💫",
    "androidtools": "📱",
    "animation": "🎞",
    "antiflood": "🛡",
    "arts": "🎨",
    "spam": "🚫",
    "broadcast": "📡",
    "gcast": "📢",
    "download": "⬇️",
    "downloader": "⬇️",
    "tools": "🛠",
    "utility": "🧰",
    "sudo": "🔑",
    "fun": "🎲",
    "media": "🎬",
    "sticker": "🎨",
    "info": "ℹ️",
    "system": "🖥",
    "ping": "📶",
    "profile": "🪪",
    "chat": "💬",
    "logo": "🖌",
    "weather": "🌦",
    "translate": "🌐",
}
DEFAULT_ICON = "📦"

# Any command containing one of these words is hidden behind a spoiler so the
# menu stays clean and destructive actions aren't tapped by accident.
DANGER_KEYWORDS = (
    "uninstall", "delete", "remove", "reset", "wipe",
    "logout", "restart", "shutdown", "clearcache", "purge",
)

# Rotating tips (HTML-safe). Kept short and available for reuse if you want them.
TIPS = [
    "<code>.help &lt;plugin&gt;</code> = direct plugin help.",
    "<code>.findplugin &lt;term&gt;</code> = search modules.",
    "<code>.plugins</code> = all modules at a glance.",
    "<code>.helpstats</code> = live system stats.",
]


# ── Helpers ──────────────────────────────────────────────────────────────────
def esc(text):
    return str(text).replace("<", "&lt;").replace(">", "&gt;")


def icon_for(plugin_name):
    return PLUGIN_ICONS.get(str(plugin_name).lower(), DEFAULT_ICON)


def random_tip():
    return random.choice(TIPS)


def is_danger(cmd_line):
    low = str(cmd_line).lower()
    return any(k in low for k in DANGER_KEYWORDS)


def stat_bar(count, total, length=10):
    filled = round((count / total) * length) if total else 0
    filled = max(0, min(length, filled))
    return "▰" * filled + "▱" * (length - filled)


def button_label(plugin_name):
    ic = icon_for(plugin_name)
    if plugin_name == "quickhelp":
        return f"{ic} Quick Guide"
    name = plugin_name.title()
    if len(name) > 11:
        name = name[:10] + "…"
    return f"{ic} {name}"


# ── Block builders ───────────────────────────────────────────────────────────
def build_command_block(commands):
    """Render a command list as an (optionally expandable) blockquote."""
    lines = []
    for cmd in commands:
        if not (isinstance(cmd, str) and cmd.strip()):
            continue
        if " - " in cmd:
            c, d = cmd.split(" - ", 1)
            line = f"❯ <code>{esc(c.strip())}</code> — <i>{d.strip()}</i>"
        else:
            line = f"❯ <code>{esc(cmd.strip())}</code>"
        if is_danger(cmd):
            line = f"<tg-spoiler>{line}</tg-spoiler>"
        lines.append(line)

    body = "\n".join(lines) if lines else "<i>(no commands)</i>"

    if USE_BLOCKQUOTE:
        tag = "blockquote expandable" if EXPANDABLE else "blockquote"
        return f"<{tag}>{body}</blockquote>"
    return body


def build_menu_text(total_plugins, total_commands, page, total_pages):
    """Minimalist main help-menu caption. Stats live inside a quote block."""
    return (
        f"✦ <b>{BRAND}</b> ✦\n\n"
        f"<blockquote>📦 <b>{total_plugins}</b> plugins\n"
        f"⚙️ <b>{total_commands}</b> commands\n"
        f"🟢 online</blockquote>\n"
        f"<i>Select a module below</i>   ·   <code>{page + 1}/{total_pages}</code>"
    )


def build_quickhelp_text():
    return (
        f"⚡ <b>Quick Guide</b>\n\n"
        f"<blockquote>"
        f"❯ <code>.help</code> — interactive menu\n"
        f"❯ <code>.help &lt;plugin&gt;</code> — direct plugin help\n"
        f"❯ <code>.plugins</code> — list all modules\n"
        f"❯ <code>.findplugin &lt;term&gt;</code> — search\n"
        f"❯ <code>.helpstats</code> — system stats"
        f"</blockquote>"
    )


def build_plugin_text(plugin_name, plugin_data):
    """Full plugin-detail body. Works for inline (bot) and reply (userbot)."""
    if plugin_name == "quickhelp":
        return build_quickhelp_text()

    ic = icon_for(plugin_name)
    desc = plugin_data.get("description") or "No description"
    commands = plugin_data.get("commands", [])
    return (
        f"{ic} <b>{esc(plugin_name.title())}</b>   <code>{len(commands)} cmds</code>\n"
        f"<i>{esc(desc)}</i>\n\n"
        f"{build_command_block(commands)}"
    )