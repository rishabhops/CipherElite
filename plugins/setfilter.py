# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    setfilter
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "utilities"

import re
import time

from telethon import events
from telethon.types import Message

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from DB.database import db_get, db_set

# -----------------------------------------------------------------------------
#  Settings
# -----------------------------------------------------------------------------
COLLECTION = "filter_db"
MAX_PER_CHAT = 25
DEFAULT_COOLDOWN = 30          # seconds between two replies from the same filter
MAX_REPLY = 3500
MAX_TRIGGER = 60

# trigger kinds
KIND_WORD = "word"             # matches as a whole word, case-insensitive
KIND_CONTAINS = "contains"     # plain substring, case-insensitive
KIND_REGEX = "regex"           # user-supplied regular expression


def init(client_instance):
    commands = [
        ".setfilter <keyword> <reply> - Auto-reply whenever the keyword appears",
        ".setfilter -r <regex> <reply> - Same, but the trigger is a regex",
        ".setfilter -c <keyword> <reply> - Match as a substring instead of a whole word",
        ".filters - List every filter active in this chat",
        ".filteroff <keyword> - Remove one filter",
        ".filtersoff - Remove every filter in this chat",
        ".filtercd <seconds> - Set this chat's cooldown between auto-replies"
    ]
    description = (
        "🔤 Filters - keyword auto-replies\n"
        "🎯 Whole-word / substring / regex triggers\n"
        "🧩 Placeholders: {user} {chat} {count} {time}\n"
        "🚦 Per-chat cooldown stops reply spam"
    )
    add_handler("setfilter", commands, description)


# -----------------------------------------------------------------------------
#  Helpers
# -----------------------------------------------------------------------------

def _key(event):
    peer_id = getattr(event, "peer_id", None)
    if peer_id is not None:
        val = (getattr(peer_id, "channel_id", None)
               or getattr(peer_id, "chat_id", None)
               or getattr(peer_id, "user_id", None))
        return str(val) if val is not None else str(getattr(event, "chat_id", 0))
    return str(getattr(event, "chat_id", 0))


def _chat_name(event):
    chat = getattr(event, "chat", None)
    return (getattr(chat, "title", None)
            or getattr(chat, "first_name", None)
            or _key(event))


async def _chat_filters(chat_key):
    data = await db_get(COLLECTION, chat_key, default={}) or {}
    return data if isinstance(data, dict) else {}


async def _save_filters(chat_key, data):
    await db_set(COLLECTION, chat_key, data)


def _compile(trigger, kind):
    """Pre-compile a trigger. Returns a pattern object or None when invalid."""
    try:
        if kind == KIND_REGEX:
            return re.compile(trigger, re.I)
        escaped = re.escape(trigger)
        if kind == KIND_WORD:
            return re.compile(rf"(?<![\w]){escaped}(?![\w])", re.I)
        return re.compile(escaped, re.I)
    except re.error:
        return None


def _render(template, event):
    """Fill the placeholders a filter reply can use."""
    sender = getattr(event, "sender", None)
    first = getattr(sender, "first_name", None) or "there"
    last = getattr(sender, "last_name", None) or ""
    full = (first + " " + last).strip()
    mapping = {
        "{user}": full,
        "{first}": first,
        "{mention}": f"[{full}](tg://user?id={getattr(event, 'sender_id', 0)})",
        "{chat}": str(_chat_name(event)),
        "{id}": str(getattr(event, "sender_id", 0)),
        "{count}": str(getattr(event, "message_count", 0) or 0),
        "{time}": time.strftime("%I:%M %p"),
        "{date}": time.strftime("%d %b %Y"),
    }
    out = template
    for token, value in mapping.items():
        out = out.replace(token, value)
    return out


def _kind_label(kind):
    return {KIND_WORD: "word", KIND_CONTAINS: "contains", KIND_REGEX: "regex"}.get(kind, kind)


def _usage():
    return (
        "🔤 **Cipher Elite Filters**\n\n"
        "**Add:**\n"
        "• `.setfilter price Our list: bit.ly/prices` — whole-word match\n"
        "• `.setfilter -c order Thanks for ordering` — substring match\n"
        "• `.setfilter -r ^hi+$ Hello {user}` — regex match\n\n"
        "**Placeholders:** `{user}` `{first}` `{mention}` `{chat}` `{id}` `{time}` `{date}`\n\n"
        "**Manage:**\n"
        "• `.filters` — list\n"
        "• `.filteroff <keyword>`\n"
        "• `.filtersoff`\n"
        f"• `.filtercd <seconds>` — cooldown (default {DEFAULT_COOLDOWN}s)\n\n"
        "🤖 **Powered by Cipher Elite**"
    )


# -----------------------------------------------------------------------------

_LAST_REPLY = {}          # chat_key -> timestamp of the last auto-reply
_HITS = {}                # "chat|trigger" -> hit count


async def register_commands():

    # =========================================================================
    #  Background watcher — answers when a trigger matches
    # =========================================================================
    @CipherElite.on(events.NewMessage(incoming=True))
    async def filter_watcher(event):
        try:
            text = event.raw_text
            if not text:
                return
            # never answer our own messages or other bots
            if getattr(event, "out", False) or getattr(event, "via_bot_id", None):
                return
            sender = getattr(event, "sender", None)
            if getattr(sender, "bot", False):
                return

            chat_key = _key(event)
            filters = await _chat_filters(chat_key)
            if not filters:
                return

            now = time.time()
            cooldown = float(filters.get("_cooldown", DEFAULT_COOLDOWN))
            last = _LAST_REPLY.get(chat_key, 0)
            if now - last < cooldown:
                return

            for trigger, rule in filters.items():
                if trigger.startswith("_") or not isinstance(rule, dict):
                    continue
                pattern = _compile(trigger, rule.get("kind", KIND_WORD))
                if pattern is None or not pattern.search(text):
                    continue

                reply = _render(rule.get("reply", ""), event)
                if not reply.strip():
                    continue

                try:
                    await event.reply(reply[:MAX_REPLY])
                except Exception:
                    return
                _LAST_REPLY[chat_key] = time.time()
                hit_key = f"{chat_key}|{trigger}"
                _HITS[hit_key] = _HITS.get(hit_key, 0) + 1
                rule["hits"] = _HITS[hit_key]
                await _save_filters(chat_key, filters)
                return                     # one reply per message
        except Exception:
            return

    # =========================================================================
    #  .setfilter — add a trigger
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.setfilter(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def setfilter_cmd(event: Message):
        arg = (event.pattern_match.group(1) or "").strip()
        if not arg or arg.lower() in ("help", "-h", "--help"):
            return await event.reply(_usage())

        try:
            kind = KIND_WORD
            rest = arg
            if arg.startswith("-r "):
                kind, rest = KIND_REGEX, arg[3:].strip()
            elif arg.startswith("-c "):
                kind, rest = KIND_CONTAINS, arg[3:].strip()

            parts = rest.split(None, 1)
            if len(parts) < 2 or not parts[1].strip():
                return await event.reply(
                    "🔤 **Cipher Elite Filters**\n\n"
                    "❌ **Both a keyword and a reply are required.**\n"
                    "💡 **Example:** `.setfilter price Our price list: bit.ly/prices`\n\n"
                    + _usage().split("**Add:**", 1)[1].split("**Placeholders:**")[0]
                )

            trigger, reply = parts[0].strip(), parts[1].strip()
            if len(trigger) > MAX_TRIGGER:
                return await event.reply(
                    "🔤 **Cipher Elite Filters**\n\n"
                    f"❌ **Trigger too long** (max {MAX_TRIGGER} characters).\n"
                    "🤖 **Powered by Cipher Elite**"
                )
            if _compile(trigger, kind) is None:
                return await event.reply(
                    "🔤 **Cipher Elite Filters**\n\n"
                    f"❌ **Invalid regex:** `{trigger}`\n"
                    "💡 Test it first, or drop `-r` to use a plain keyword.\n"
                    "🤖 **Powered by Cipher Elite**"
                )

            chat_key = _key(event)
            filters = await _chat_filters(chat_key)
            real = {k: v for k, v in filters.items() if not k.startswith("_")}
            if trigger not in real and len(real) >= MAX_PER_CHAT:
                return await event.reply(
                    "🔤 **Cipher Elite Filters**\n\n"
                    f"❌ **Filter limit reached** ({MAX_PER_CHAT} per chat).\n"
                    "💡 Remove one with `.filteroff <keyword>`\n"
                    "🤖 **Powered by Cipher Elite**"
                )

            is_update = trigger in real
            filters[trigger] = {
                "reply": reply,
                "kind": kind,
                "hits": real.get(trigger, {}).get("hits", 0) if is_update else 0,
                "created": real.get(trigger, {}).get("created", time.time()) if is_update else time.time(),
            }
            await _save_filters(chat_key, filters)

            preview = reply.replace("\n", " ")
            if len(preview) > 90:
                preview = preview[:90] + "…"
            await event.reply(
                "🔤 **Cipher Elite Filters**\n\n"
                + (f"✏️ **Updated** `{trigger}`\n" if is_update else f"✅ **Filter added** `{trigger}`\n")
                + f"🎯 **Match:** {_kind_label(kind)}\n"
                f"💬 **Reply:** {preview}\n"
                f"📍 **Chat:** {_chat_name(event)}\n\n"
                "💡 `.filters` to list · `.filteroff " + trigger + "` to remove\n"
                "🤖 **Powered by Cipher Elite**"
            )
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "💡 **Try `.setfilter help`**"
            )

    # =========================================================================
    #  .filters — list what is active here
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.filters(?![\w.-])"))
    @rishabh()
    async def filters_list_cmd(event: Message):
        try:
            chat_key = _key(event)
            filters = await _chat_filters(chat_key)
            real = {k: v for k, v in filters.items()
                    if not k.startswith("_") and isinstance(v, dict)}
            if not real:
                return await event.reply(
                    "🔤 **Cipher Elite Filters**\n\n"
                    "❌ **No filter in this chat.**\n"
                    "💡 Add one with `.setfilter price Our price list`\n"
                    "🤖 **Powered by Cipher Elite**"
                )

            cooldown = filters.get("_cooldown", DEFAULT_COOLDOWN)
            lines = ["🔤 **Cipher Elite Filters**\n",
                     f"📍 **Chat:** {_chat_name(event)}",
                     f"🚦 **Cooldown:** {cooldown}s",
                     f"📋 **{len(real)} filter(s):**\n"]
            for trigger, rule in sorted(real.items()):
                preview = str(rule.get("reply", "")).replace("\n", " ")
                if len(preview) > 55:
                    preview = preview[:55] + "…"
                lines.append(f"• `{trigger}`  [{_kind_label(rule.get('kind', KIND_WORD))}]"
                             f"  ·  {rule.get('hits', 0)} hit(s)\n   └ {preview}")
            lines.append("\n💡 `.filteroff <keyword>` · `.filtersoff` · `.filtercd <sec>`")
            lines.append("🤖 **Powered by Cipher Elite**")
            await event.reply("\n".join(lines)[:4000])
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "🤖 **Powered by Cipher Elite**"
            )

    # =========================================================================
    #  .filteroff / .filtersoff / .filtercd
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.filtersoff(?![\w.-])"))
    @rishabh()
    async def filters_off_cmd(event: Message):
        trigger = (event.pattern_match.group(1) or "").strip()
        if not trigger:
            return await event.reply(
                "🔤 **Cipher Elite Filters**\n\n"
                "❌ **Usage:** `.filteroff <keyword>`\n"
                "💡 See `.filters` for the list\n"
                "🤖 **Powered by Cipher Elite**"
            )
        try:
            chat_key = _key(event)
            filters = await _chat_filters(chat_key)
            if trigger not in filters or trigger.startswith("_"):
                return await event.reply(
                    "🔤 **Cipher Elite Filters**\n\n"
                    f"❌ **No filter `{trigger}` in this chat.**\n"
                    "🤖 **Powered by Cipher Elite**"
                )
            filters.pop(trigger, None)
            await _save_filters(chat_key, filters)
            await event.reply(
                "🔤 **Cipher Elite Filters**\n\n"
                f"🗑 **Removed** `{trigger}`\n"
                "🤖 **Powered by Cipher Elite**"
            )
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "🤖 **Powered by Cipher Elite**"
            )

    @CipherElite.on(events.NewMessage(pattern=r"\.filteroff(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def filter_off_cmd(event: Message):
        try:
            chat_key = _key(event)
            filters = await _chat_filters(chat_key)
            count = len([k for k in filters if not k.startswith("_")])
            cooldown = filters.get("_cooldown", DEFAULT_COOLDOWN)
            await _save_filters(chat_key, {"_cooldown": cooldown})
            _LAST_REPLY.pop(chat_key, None)
            await event.reply(
                "🔤 **Cipher Elite Filters**\n\n"
                f"🧹 **Removed {count} filter(s) from this chat.**\n"
                "🤖 **Powered by Cipher Elite**"
            )
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "🤖 **Powered by Cipher Elite**"
            )

    @CipherElite.on(events.NewMessage(pattern=r"\.filtercd(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def filter_cd_cmd(event: Message):
        raw = (event.pattern_match.group(1) or "").strip()
        if not raw or not raw.replace(".", "", 1).isdigit():
            return await event.reply(
                "🔤 **Cipher Elite Filters**\n\n"
                "❌ **Usage:** `.filtercd <seconds>`  (0 – 3600)\n"
                f"💡 Current cooldown: {DEFAULT_COOLDOWN}s by default\n"
                "🤖 **Powered by Cipher Elite**"
            )
        try:
            value = float(raw)
            if not 0 <= value <= 3600:
                return await event.reply(
                    "🔤 **Cipher Elite Filters**\n\n"
                    "❌ **Cooldown must be between 0 and 3600 seconds.**\n"
                    "🤖 **Powered by Cipher Elite**"
                )
            chat_key = _key(event)
            filters = await _chat_filters(chat_key)
            filters["_cooldown"] = value
            await _save_filters(chat_key, filters)
            _LAST_REPLY.pop(chat_key, None)
            await event.reply(
                "🔤 **Cipher Elite Filters**\n\n"
                f"🚦 **Cooldown set to** {value:g}s in this chat.\n"
                "🤖 **Powered by Cipher Elite**"
            )
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "🤖 **Powered by Cipher Elite**"
            )
