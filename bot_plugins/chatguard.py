# =============================================================================
#  CipherElite Assistant Bot Plugin
#
#  Plugin Name:    chatguard
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
#
#  What it does:
#    permission locks, flood rate-limiting, force-subscribe and a button captcha.
#
#  Merged from modlock.py, floodguard.py, forcesub.py, gatekeeper.py so related commands live in one file and share a single
#  init_bot_plugin().
#
#  Thank you for respecting open-source software!
# =============================================================================

import time
import secrets
from telethon import Button, events
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import (
    ChatBannedRights,
    MessageActionChatAddUser,
    MessageActionChatJoinedByLink,
)
from collections import defaultdict, deque
from telethon.errors import UserNotParticipantError

try:
    from bot_plugins._shared import (
        clip,
        group_only,
        human_duration,
        is_admin,
        parse_duration,
        require_admin,
        safe_edit,
        user_label,
    )
except ImportError:
    from _shared import (
        clip,
        group_only,
        human_duration,
        is_admin,
        parse_duration,
        require_admin,
        safe_edit,
        user_label,
    )

# ---------------------------------------------------------------------------
#  modlock.py — module level
# ---------------------------------------------------------------------------

PRESETS = {
    "media": {"icon": "🖼", "label": "media (photos, videos, files, audio)",
              "rights": {"send_media": True, "send_photos": True, "send_videos": True,
                         "send_roundvideos": True, "send_audios": True,
                         "send_voices": True, "send_docs": True}},
    "sticker": {"icon": "🎭", "label": "stickers", "rights": {"send_stickers": True}},
    "gif": {"icon": "🎞", "label": "GIFs", "rights": {"send_gifs": True}},
    "game": {"icon": "🎮", "label": "games", "rights": {"send_games": True}},
    "inline": {"icon": "🔎", "label": "inline bot results", "rights": {"send_inline": True}},
    "link": {"icon": "🔗", "label": "link previews", "rights": {"embed_links": True}},
    "poll": {"icon": "📊", "label": "polls", "rights": {"send_polls": True}},
    "invite": {"icon": "📨", "label": "inviting users", "rights": {"invite_users": True}},
    "pin": {"icon": "📌", "label": "pinning messages", "rights": {"pin_messages": True}},
    "info": {"icon": "ℹ️", "label": "changing group info", "rights": {"change_info": True}},
    "message": {"icon": "💬", "label": "sending any message", "rights": {"send_messages": True}},
    "all": {"icon": "🔒", "label": "everything (read-only chat)",
            "rights": {"view_messages": False, "send_messages": True, "send_media": True,
                       "send_photos": True, "send_videos": True, "send_roundvideos": True,
                       "send_audios": True, "send_voices": True, "send_docs": True,
                       "send_stickers": True, "send_gifs": True, "send_games": True,
                       "send_inline": True, "embed_links": True, "send_polls": True,
                       "invite_users": True, "pin_messages": True, "change_info": True}},
}


ORDER = ["all", "message", "media", "sticker", "gif", "game", "inline",
         "link", "poll", "invite", "pin", "info"]


ALIASES = {
    "media": "media", "medias": "media", "photo": "media", "photos": "media",
    "video": "media", "videos": "media", "file": "media", "files": "media",
    "document": "media", "audio": "media", "voice": "media",
    "sticker": "sticker", "stickers": "sticker", "gif": "gif", "gifs": "gif",
    "game": "game", "games": "game", "inline": "inline", "bot": "inline",
    "link": "link", "links": "link", "url": "link", "preview": "link",
    "poll": "poll", "polls": "poll", "invite": "invite", "adduser": "invite",
    "pin": "pin", "pins": "pin", "info": "info", "about": "info",
    "message": "message", "messages": "message", "text": "message", "msg": "message",
    "all": "all", "everything": "all", "readonly": "all",
}


_FIELDS = ("view_messages", "send_messages", "send_media", "send_stickers",
           "send_gifs", "send_games", "send_inline", "embed_links", "send_polls",
           "change_info", "invite_users", "pin_messages", "manage_topics",
           "send_photos", "send_videos", "send_roundvideos", "send_audios",
           "send_voices", "send_docs", "send_plain")


async def _current_rights(client, chat):
    try:
        if type(chat).__name__ == "Channel":
            res = await client(GetFullChannelRequest(channel=chat))
        elif type(chat).__name__ == "Chat":
            res = await client(GetFullChatRequest(chat_id=chat.id))
        else:
            return None
        return getattr(getattr(res, "full_chat", None), "default_banned_rights", None)
    except Exception:
        return None


def _blocked(rights):
    if rights is None:
        return set()
    return {f for f in _FIELDS if f != "view_messages" and getattr(rights, f, False)}


def _merge(base, changes):
    """New rights = the chat's existing ones, with `changes` applied on top."""
    current = {}
    if base is not None:
        for field in _FIELDS:
            value = getattr(base, field, None)
            if value is not None:
                current[field] = value
    current.update(changes)
    return ChatBannedRights(until_date=None, **current)


def _active_presets(rights):
    blocked = _blocked(rights)
    out = []
    for name in ORDER:
        need = {k for k, v in PRESETS[name]["rights"].items() if v is True}
        if need and need <= blocked:
            out.append(name)
    return out, blocked


def _list_text_modlock():
    lines = ["🔐 **Cipher Elite Chat Locks**\n", "**Available lock types:**\n"]
    for name in ORDER:
        p = PRESETS[name]
        lines.append(f"  {p['icon']} `{name}` — {p['label']}")
    lines.append("\n**Usage:** `/lock media` · `/unlock media` · `/lock all`")
    lines.append("👑 Admins are never affected.")
    lines.append("🤖 **Powered by Cipher Elite**")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
#  floodguard.py — module level
# ---------------------------------------------------------------------------

COLLECTION_floodguard = "bot_flood"


DEFAULT_LIMIT = 7              # messages...


DEFAULT_WINDOW = 5             # ...per this many seconds


DEFAULT_MUTE = 60              # seconds of silence after a violation


MIN_LIMIT = 3


MAX_LIMIT = 100


MIN_WINDOW = 2


MAX_WINDOW = 120


_seen = defaultdict(lambda: defaultdict(deque))


_muted_until = {}              # (chat_id, user_id) -> unix ts


async def _get_floodguard(chat_id):
    try:
        from DB.database import db_get
        data = await db_get(COLLECTION_floodguard, str(chat_id), default=None)
    except Exception:
        data = None
    if not isinstance(data, dict):
        data = {}
    data.setdefault("on", False)
    data.setdefault("limit", DEFAULT_LIMIT)
    data.setdefault("window", DEFAULT_WINDOW)
    data.setdefault("mute", DEFAULT_MUTE)
    return data


async def _save_floodguard(chat_id, doc):
    try:
        from DB.database import db_set
        await db_set(COLLECTION_floodguard, str(chat_id), doc)
        return True
    except Exception:
        return False


def _status_floodguard(doc):
    state = "🟢 **ON**" if doc.get("on") else "🔴 **OFF**"
    return (
        "🌊 **Cipher Elite Flood Guard**\n\n"
        f"{state}\n"
        f"🔢 **Limit:** {doc['limit']} messages per {doc['window']}s\n"
        f"🤐 **Punishment:** muted for {human_duration(doc['mute'])}\n\n"
        "**Commands:**\n"
        "• `/setflood <limit> [window] [mute]`\n"
        "• `/setflood 10 5 120` — 10 msgs / 5s, mute 120s\n"
        "• `/floodoff` — disable\n\n"
        "👑 Admins are never limited.\n"
        "🤖 **Powered by Cipher Elite**"
    )

# ---------------------------------------------------------------------------
#  forcesub.py — module level
# ---------------------------------------------------------------------------

COLLECTION_forcesub = "bot_forcesub"


MAX_CHANNELS = 10


async def _get_forcesub(chat_id):
    try:
        from DB.database import db_get
        data = await db_get(COLLECTION_forcesub, str(chat_id), default=None)
    except Exception:
        data = None
    if not isinstance(data, dict):
        data = {}
    channels = data.get("channels")
    if not isinstance(channels, list):
        channels = []
    data["channels"] = channels
    return data


async def _save_forcesub(chat_id, doc):
    try:
        from DB.database import db_set
        await db_set(COLLECTION_forcesub, str(chat_id), doc)
        return True
    except Exception:
        return False


async def _missing(client, channels, user_id):
    """Return the required channels the user has NOT joined."""
    missing = []
    for entry in channels:
        cid = entry.get("id")
        if not cid:
            continue
        try:
            await client(GetParticipantRequest(channel=cid, participant=user_id))
        except UserNotParticipantError:
            missing.append(entry)
        except Exception:
            # the bot is not an admin of that channel, so we cannot verify it
            missing.append(entry)
    return missing


def _channel_label(entry):
    title = entry.get("title") or entry.get("username")
    return title or f"`{entry.get('id')}`"


def _list_text_forcesub(doc):
    channels = doc.get("channels", [])
    if not channels:
        return (
            "📢 **Cipher Elite Force Subscribe**\n\n"
            "ℹ️ **No required channels here.**\n\n"
            "💡 `/forcesub <@channel>` to add one\n"
            "🤖 **Powered by Cipher Elite**"
        )
    lines = ["📢 **Cipher Elite Force Subscribe**\n",
             f"🔢 **Required channels:** {len(channels)}/{MAX_CHANNELS}\n"]
    for entry in channels:
        lines.append(f"  └ {_channel_label(entry)}")
    lines.append("\n💡 `/unforcesub <@channel>` removes one")
    lines.append("🤖 **Powered by Cipher Elite**")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
#  gatekeeper.py — module level
# ---------------------------------------------------------------------------

COLLECTION_gatekeeper = "bot_captcha"


DEFAULT_TIMEOUT = 120            # seconds to tap the button


MIN_TIMEOUT = 30


MAX_TIMEOUT = 600


PENDING = {}                     # token -> {chat_id, user_id, expires, message_id}


SWEEP_EVERY = 30                 # seconds between expiry sweeps


JOIN_ACTIONS = (MessageActionChatAddUser, MessageActionChatJoinedByLink)


async def _get_gatekeeper(chat_id):
    try:
        from DB.database import db_get
        data = await db_get(COLLECTION_gatekeeper, str(chat_id), default=None)
    except Exception:
        data = None
    if not isinstance(data, dict):
        data = {}
    data.setdefault("on", False)
    data.setdefault("timeout", DEFAULT_TIMEOUT)
    return data


async def _save_gatekeeper(chat_id, doc):
    try:
        from DB.database import db_set
        await db_set(COLLECTION_gatekeeper, str(chat_id), doc)
        return True
    except Exception:
        return False


def _status_gatekeeper(doc):
    state = "🟢 **ON**" if doc.get("on") else "🔴 **OFF**"
    return (
        "🛡 **Cipher Elite Captcha**\n\n"
        f"{state}\n"
        f"⏱ **Timeout:** {doc.get('timeout', DEFAULT_TIMEOUT)}s\n\n"
        "**Commands:**\n"
        "• `/captchaset on` · `/captchaset off`\n"
        "• `/captchaset <seconds>` — time to tap the button\n"
        "• `/verify <user>` — verify someone by hand\n\n"
        "🤖 **Powered by Cipher Elite**"
    )


async def _restrict(client, chat_id, user_id):
    """Silence a new member until they verify."""
    await client.edit_permissions(
        chat_id, user_id, send_messages=False, send_media=False,
        send_stickers=False, send_gifs=False, send_inline=False,
    )


async def _release(client, chat_id, user_id):
    """Restore full rights after a successful verify."""
    await client.edit_permissions(chat_id, user_id)

# ---------------------------------------------------------------------------
#  COMMAND REGISTRATION
# ---------------------------------------------------------------------------

def init_bot_plugin(bot, owner_id, owner_name):
    """Register every Chat Guard handler on the assistant bot."""

    # =======================================================================
    #  modlock.py
    # =======================================================================
    """Register the lock handlers on the assistant bot."""

    async def _apply(event, names, locking):
        changes = {}
        labels = []
        if "all" in names:
            p = PRESETS["all"]
            for field, value in p["rights"].items():
                changes[field] = value if locking else False
            if not locking:
                changes["view_messages"] = False    # let members see the chat again
            labels = [f"{p['icon']} {p['label']}"]
        else:
            for name in names:
                p = PRESETS[name]
                for field, value in p["rights"].items():
                    changes[field] = value if locking else False
                labels.append(f"{p['icon']} {p['label']}")

        chat = await event.client.get_entity(event.chat_id)
        base = await _current_rights(event.client, chat)
        new_rights = _merge(base, changes)

        try:
            await event.client.edit_permissions(event.chat_id, new_rights)
        except Exception as e:
            return (f"❌ **Telegram refused the change:** `{str(e)[:160]}`\n"
                    "💡 I need admin rights with *Change Info* / *Ban Users*.")

        verb = "Locked" if locking else "Unlocked"
        icon = "🔒" if locking else "🔓"
        body = "\n".join(f"  └ {x}" for x in labels)
        return f"{icon} **{verb}**\n{body}\n\n👑 **Admins and you are not affected.**"

    def _parse(raw):
        names, unknown = [], []
        for tok in (raw or "").replace(",", " ").split():
            mapped = ALIASES.get(tok.lower())
            if mapped:
                if mapped not in names:
                    names.append(mapped)
            else:
                unknown.append(tok)
        if "all" in names:
            names = ["all"]
        return names, unknown

    # -------------------------------------------------------------------------
    #  /lock <type>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/lock(?:\s+([\s\S]*))?$"))
    async def lock_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        raw = (event.pattern_match.group(1) or "").strip().lower()
        if not raw or raw in ("help", "list", "types", "-h"):
            return await event.reply(_list_text_modlock())

        names, unknown = _parse(raw)
        if unknown:
            return await event.reply(
                "🔐 **Cipher Elite Chat Locks**\n\n"
                f"❌ **Unknown lock type:** `{', '.join(unknown)}`\n\n"
                f"✅ **Valid:** `{', '.join(ORDER)}`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        status = await event.reply("🔄 **Applying lock...**")
        result = await _apply(event, names, locking=True)
        await safe_edit(status, clip(
            "🔐 **Cipher Elite Chat Locks**\n\n" + result +
            "\n\n🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /unlock <type>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/unlock(?:\s+([\s\S]*))?$"))
    async def unlock_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        raw = (event.pattern_match.group(1) or "").strip().lower()
        if not raw or raw in ("help", "-h"):
            return await event.reply(
                "🔐 **Cipher Elite Chat Locks**\n\n"
                "❌ **Usage:** `/unlock <type>`\n"
                f"✅ **Valid:** `{', '.join(ORDER)}`\n"
                "💡 `/unlock all` removes every restriction\n"
                "🤖 **Powered by Cipher Elite**"
            )

        names, unknown = _parse(raw)
        if unknown:
            return await event.reply(
                "🔐 **Cipher Elite Chat Locks**\n\n"
                f"❌ **Unknown lock type:** `{', '.join(unknown)}`\n\n"
                f"✅ **Valid:** `{', '.join(ORDER)}`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        status = await event.reply("🔄 **Removing lock...**")
        result = await _apply(event, names, locking=False)
        await safe_edit(status, clip(
            "🔐 **Cipher Elite Chat Locks**\n\n" + result +
            "\n\n🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /locks — current state
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/locks$"))
    async def locks_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")

        status = await event.reply("🔄 **Reading chat permissions...**")
        chat = await event.client.get_entity(event.chat_id)
        rights = await _current_rights(event.client, chat)
        active, blocked = _active_presets(rights)

        lines = ["🔐 **Cipher Elite Chat Locks**\n"]
        if not active and not blocked:
            lines.append("🟢 **No lock active** — everyone can post normally.")
        else:
            if active:
                lines.append("🔒 **Active presets:**")
                for name in active:
                    p = PRESETS[name]
                    lines.append(f"  └ {p['icon']} `{name}` — {p['label']}")
            if blocked:
                flags = sorted(blocked)
                lines.append(f"\n🧾 **Raw flags blocked ({len(flags)}):**")
                lines.append("  └ `" + "`, `".join(flags) + "`")
        lines.append("\n💡 `/lock <type>` · `/unlock <type>`")
        lines.append("🤖 **Powered by Cipher Elite**")
        await safe_edit(status, clip("\n".join(lines)))

    # =======================================================================
    #  floodguard.py
    # =======================================================================
    """Register the flood-guard handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /setflood <limit> [window] [mute]
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/setflood(?:\s+([\s\S]*))?$"))
    async def setflood_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        tokens = (event.pattern_match.group(1) or "").strip().split()
        doc = await _get_floodguard(event.chat_id)

        if not tokens:
            return await event.reply(clip(_status_floodguard(doc)))

        # /setflood off
        if tokens[0].lower() in ("off", "disable", "0"):
            doc["on"] = False
            if not await _save_floodguard(event.chat_id, doc):
                return await event.reply("❌ **Could not save the setting.**")
            return await event.reply(clip(_status_floodguard(doc)))

        limit = None
        if tokens[0].isdigit():
            limit = max(MIN_LIMIT, min(int(tokens[0]), MAX_LIMIT))
        else:
            return await event.reply(
                "❌ **Usage:** `/setflood <limit> [window] [mute]`\n"
                f"💡 limit {MIN_LIMIT}-{MAX_LIMIT} · window {MIN_WINDOW}-{MAX_WINDOW}s\n"
                "🤖 **Powered by Cipher Elite**"
            )

        window = doc["window"]
        if len(tokens) > 1:
            parsed = parse_duration(tokens[1])
            if parsed:
                window = max(MIN_WINDOW, min(parsed, MAX_WINDOW))

        mute = doc["mute"]
        if len(tokens) > 2:
            parsed = parse_duration(tokens[2])
            if parsed:
                mute = max(10, min(parsed, 3600))

        doc.update({"on": True, "limit": limit, "window": window, "mute": mute})
        if not await _save_floodguard(event.chat_id, doc):
            return await event.reply("❌ **Could not save the setting.**")

        await event.reply(clip(_status_floodguard(doc)))

    # -------------------------------------------------------------------------
    #  /flood — show the setting
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/flood$"))
    async def flood_status_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        doc = await _get_floodguard(event.chat_id)
        await event.reply(clip(_status_floodguard(doc)))

    # -------------------------------------------------------------------------
    #  /floodoff
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/floodoff$"))
    async def floodoff_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        doc = await _get_floodguard(event.chat_id)
        doc["on"] = False
        _seen.pop(event.chat_id, None)
        if not await _save_floodguard(event.chat_id, doc):
            return await event.reply("❌ **Could not save the setting.**")

        await event.reply(clip(
            "🌊 **Cipher Elite Flood Guard**\n\n"
            "🔴 **Disabled for this group.**\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  Watcher — count messages and punish floods
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(incoming=True, func=lambda e: not e.is_private))
    async def flood_watcher(event):
        try:
            sender_id = getattr(event, "sender_id", None)
            if sender_id is None:
                return
            if sender_id == owner_id:
                return
            if getattr(event, "via_bot_id", None):
                return

            doc = await _get_floodguard(event.chat_id)
            if not doc.get("on"):
                return

            chat_id = event.chat_id
            key = (chat_id, sender_id)
            now = time.time()

            # still serving a punishment? drop the message and stop
            until = _muted_until.get(key, 0)
            if now < until:
                try:
                    await event.delete()
                except Exception:
                    pass
                return

            if await is_admin(event, sender_id):
                return

            window = int(doc["window"])
            limit = int(doc["limit"])
            bucket = _seen[chat_id][sender_id]
            bucket.append(now)
            while bucket and now - bucket[0] > window:
                bucket.popleft()

            if len(bucket) < limit:
                return

            # violation -> mute and clear their history
            bucket.clear()
            mute = int(doc["mute"])
            _muted_until[key] = now + mute

            try:
                from datetime import datetime, timedelta, timezone
                until_date = datetime.now(timezone.utc) + timedelta(seconds=mute)
                await event.client.edit_permissions(
                    chat_id, sender_id, until_date=until_date,
                    send_messages=False, send_media=False, send_stickers=False,
                    send_gifs=False, send_inline=False, send_polls=False,
                )
            except Exception:
                return

            try:
                await event.delete()
            except Exception:
                pass

            try:
                await event.client.send_message(
                    chat_id,
                    clip(
                        "🌊 **Cipher Elite Flood Guard**\n\n"
                        f"🤐 **{user_label(event.sender)} flooded** "
                        f"({limit} messages in {window}s).\n"
                        f"⏱ **Muted for {human_duration(mute)}.**\n\n"
                        "🤖 **Powered by Cipher Elite**"
                    ),
                )
            except Exception:
                pass
        except Exception:
            pass

    # =======================================================================
    #  forcesub.py
    # =======================================================================
    """Register the force-subscribe handlers on the assistant bot."""

    async def _resolve_channel(event, arg):
        """Turn '@channel' or an id into (entry_dict, error_text)."""
        arg = (arg or "").strip()
        if not arg:
            return None, "❌ **Give a @channel username or a channel id.**"
        try:
            entity = await event.client.get_entity(int(arg) if arg.lstrip("-").isdigit() else arg)
        except Exception:
            return None, f"❌ **Could not find** `{arg}`.\n💡 The bot must already be an admin there."

        if type(entity).__name__ != "Channel":
            return None, "❌ **That is not a channel.**"

        return {
            "id": entity.id,
            "username": getattr(entity, "username", None),
            "title": getattr(entity, "title", None),
        }, None

    # -------------------------------------------------------------------------
    #  /forcesub <@channel|id>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/forcesub(?:\s+([\s\S]*))?$"))
    async def forcesub_add_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        doc = await _get_forcesub(event.chat_id)
        arg = (event.pattern_match.group(1) or "").strip()
        if not arg:
            return await event.reply(clip(_list_text_forcesub(doc)))

        entry, err = await _resolve_channel(event, arg)
        if err:
            return await event.reply(err)

        if any(c.get("id") == entry["id"] for c in doc["channels"]):
            return await event.reply(
                f"ℹ️ **{_channel_label(entry)} is already required.**\n"
                "🤖 **Powered by Cipher Elite**"
            )
        if len(doc["channels"]) >= MAX_CHANNELS:
            return await event.reply(
                f"❌ **Limit reached** ({MAX_CHANNELS} channels).\n"
                "🤖 **Powered by Cipher Elite**"
            )

        # make sure we can actually verify membership
        try:
            await event.client(GetParticipantRequest(channel=entry["id"], participant=owner_id))
        except UserNotParticipantError:
            pass
        except Exception:
            return await event.reply(
                f"❌ **I cannot check members of {_channel_label(entry)}.**\n"
                "💡 Add the bot as an admin there first.\n"
                "🤖 **Powered by Cipher Elite**"
            )

        doc["channels"].append(entry)
        if not await _save_forcesub(event.chat_id, doc):
            return await event.reply("❌ **Could not save the channel.**")

        await event.reply(clip(
            "📢 **Cipher Elite Force Subscribe**\n\n"
            f"✅ **Now required:** {_channel_label(entry)}\n"
            f"🔢 **Total:** {len(doc['channels'])}/{MAX_CHANNELS}\n\n"
            "💡 New members must join before they can post\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /unforcesub <@channel|id>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/unforcesub(?:\s+([\s\S]*))?$"))
    async def forcesub_remove_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        doc = await _get_forcesub(event.chat_id)
        arg = (event.pattern_match.group(1) or "").strip()
        if not arg:
            return await event.reply(clip(_list_text_forcesub(doc)))

        entry, err = await _resolve_channel(event, arg)
        if err:
            return await event.reply(err)

        before = len(doc["channels"])
        doc["channels"] = [c for c in doc["channels"] if c.get("id") != entry["id"]]
        if len(doc["channels"]) == before:
            return await event.reply(
                f"ℹ️ **{_channel_label(entry)} was not required here.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        if not await _save_forcesub(event.chat_id, doc):
            return await event.reply("❌ **Could not save the change.**")

        await event.reply(clip(
            "📢 **Cipher Elite Force Subscribe**\n\n"
            f"🗑 **No longer required:** {_channel_label(entry)}\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /fsublist
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/fsublist$"))
    async def fsublist_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        doc = await _get_forcesub(event.chat_id)
        await event.reply(clip(_list_text_forcesub(doc)))

    # -------------------------------------------------------------------------
    #  /fsub — re-check yourself
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/fsub$"))
    async def fsub_check_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")

        doc = await _get_forcesub(event.chat_id)
        channels = doc.get("channels", [])
        if not channels:
            return await event.reply(
                "✅ **This group has no required channels.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        missing = await _missing(event.client, channels, event.sender_id)
        if not missing:
            try:
                await event.client.edit_permissions(event.chat_id, event.sender_id)
            except Exception:
                pass
            return await event.reply(clip(
                "📢 **Cipher Elite Force Subscribe**\n\n"
                "✅ **You have joined every required channel — welcome!**\n\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        lines = ["📢 **Cipher Elite Force Subscribe**\n",
                 "❌ **Join these channels first:**\n"]
        for entry in missing:
            uname = entry.get("username")
            link = f"https://t.me/{uname}" if uname else f"tg://resolve?domain={uname}"
            lines.append(f"  └ [{_channel_label(entry)}]({link})")
        lines.append("\n💡 Then send `/fsub` again")
        lines.append("🤖 **Powered by Cipher Elite**")
        await event.reply(clip("\n".join(lines)))

    # -------------------------------------------------------------------------
    #  Callback — "I have joined" button
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"^fs_check$"))
    async def fsub_button_handler(event):
        doc = await _get_forcesub(event.chat_id)
        channels = doc.get("channels", [])
        if not channels:
            return await event.answer("✅ This group has no required channels.", alert=True)

        missing = await _missing(event.client, channels, event.sender_id)
        if missing:
            names = ", ".join(_channel_label(c) for c in missing[:5])
            return await event.answer(f"❌ Still missing: {names}", alert=True)

        try:
            await event.client.edit_permissions(event.chat_id, event.sender_id)
        except Exception:
            return await event.answer("⚠️ I could not lift the restriction.", alert=True)
        await event.answer("✅ Verified — welcome!", alert=True)

    # -------------------------------------------------------------------------
    #  Watcher — mute new members until they subscribe
    # -------------------------------------------------------------------------
    @bot.on(events.ChatAction(func=lambda e: not e.is_private))
    async def forcesub_watcher(event):
        try:
            from telethon.tl.types import (
                MessageActionChatAddUser, MessageActionChatJoinedByLink,
            )
            action = getattr(getattr(event, "action_message", None), "action", None)
            if not isinstance(action, (MessageActionChatAddUser, MessageActionChatJoinedByLink)):
                return

            doc = await _get_forcesub(event.chat_id)
            channels = doc.get("channels", [])
            if not channels:
                return

            user_ids = getattr(action, "users", None) or []
            if not user_ids:
                uid = getattr(event, "user_id", None)
                user_ids = [uid] if uid else []

            for uid in user_ids:
                if uid is None:
                    continue
                missing = await _missing(event.client, channels, uid)
                if not missing:
                    continue
                try:
                    await event.client.edit_permissions(
                        event.chat_id, uid, send_messages=False, send_media=False,
                        send_stickers=False, send_gifs=False, send_inline=False,
                    )
                except Exception:
                    continue
                try:
                    await event.client.send_message(
                        event.chat_id,
                        clip(
                            "📢 **Cipher Elite Force Subscribe**\n\n"
                            "👋 **Welcome!** Join the required channels, then tap "
                            "the button to start posting.\n\n"
                            "💡 You can also send `/fsub`\n"
                            "🤖 **Powered by Cipher Elite**"
                        ),
                        buttons=[Button.inline("✅ I have joined", data="fs_check")],
                    )
                except Exception:
                    pass
        except Exception:
            pass

    # =======================================================================
    #  gatekeeper.py
    # =======================================================================
    """Register the captcha handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /captchaset on|off|<seconds>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/captchaset(?:\s+([\s\S]*))?$"))
    async def captchaset_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip().lower()
        doc = await _get_gatekeeper(event.chat_id)

        if not arg or arg in ("status", "info"):
            return await event.reply(clip(_status_gatekeeper(doc)))

        if arg in ("on", "enable", "true", "1"):
            doc["on"] = True
        elif arg in ("off", "disable", "false", "0"):
            doc["on"] = False
        elif arg.isdigit():
            doc["timeout"] = max(MIN_TIMEOUT, min(int(arg), MAX_TIMEOUT))
            doc["on"] = True
        else:
            return await event.reply(
                "❌ **Usage:** `/captchaset on` · `/captchaset off` · "
                f"`/captchaset <{MIN_TIMEOUT}-{MAX_TIMEOUT}>`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        if not await _save_gatekeeper(event.chat_id, doc):
            return await event.reply("❌ **Could not save the setting.**")
        await event.reply(clip(_status_gatekeeper(doc)))

    # -------------------------------------------------------------------------
    #  /captcha — show the setting
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/captcha$"))
    async def captcha_status_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        doc = await _get_gatekeeper(event.chat_id)
        await event.reply(clip(_status_gatekeeper(doc)))

    # -------------------------------------------------------------------------
    #  /verify <user> — manual override
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/verify(?:\s+([\s\S]*))?$"))
    async def verify_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        reply = await event.get_reply_message()
        arg = (event.pattern_match.group(1) or "").strip()
        user_id = None
        if reply and reply.sender_id:
            user_id = reply.sender_id
        elif arg.isdigit():
            user_id = int(arg)
        elif arg.startswith("@"):
            try:
                user_id = (await event.client.get_entity(arg)).id
            except Exception:
                return await event.reply("❌ **Could not find that user.**")

        if not user_id:
            return await event.reply(
                "❌ **Reply to the member, or give a @username / id.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        # drop any pending challenge for them
        for token in [t for t, v in PENDING.items() if v["user_id"] == user_id]:
            PENDING.pop(token, None)

        try:
            await _release(event.client, event.chat_id, user_id)
        except Exception as e:
            return await event.reply(
                f"❌ **Verify failed:** `{str(e)[:160]}`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        await event.reply(clip(
            "🛡 **Cipher Elite Captcha**\n\n"
            f"✅ **Verified user** `{user_id}` **by hand.**\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  Button callback — the member proved they are human
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"^gk_([a-f0-9]+)$"))
    async def captcha_button_handler(event):
        token = event.pattern_match.group(1)
        entry = PENDING.get(token)
        if not entry:
            return await event.answer(
                "🛑 This challenge expired. Ask an admin to /verify you.", alert=True
            )
        if event.sender_id != entry["user_id"]:
            return await event.answer("🛑 This button is not for you.", alert=True)
        if time.time() > entry["expires"]:
            PENDING.pop(token, None)
            return await event.answer("🛑 Too late — this challenge expired.", alert=True)

        PENDING.pop(token, None)
        try:
            await _release(event.client, event.chat_id, event.sender_id)
        except Exception:
            return await event.answer(
                "⚠️ I could not lift the restriction. Ask an admin to /verify you.",
                alert=True,
            )

        await event.answer("✅ Verified — welcome!", alert=True)
        try:
            await event.delete()          # remove the challenge message
        except Exception:
            pass

    # -------------------------------------------------------------------------
    #  Watcher — challenge every new member
    # -------------------------------------------------------------------------
    @bot.on(events.ChatAction(func=lambda e: not e.is_private))
    async def captcha_watcher(event):
        try:
            action = getattr(getattr(event, "action_message", None), "action", None)
            if not isinstance(action, JOIN_ACTIONS):
                return

            doc = await _get_gatekeeper(event.chat_id)
            if not doc.get("on"):
                return

            timeout = int(doc.get("timeout", DEFAULT_TIMEOUT))
            user_ids = getattr(action, "users", None) or []
            if not user_ids:
                uid = getattr(event, "user_id", None)
                user_ids = [uid] if uid else []

            for uid in user_ids:
                if uid is None:
                    continue
                try:
                    await _restrict(event.client, event.chat_id, uid)
                except Exception:
                    continue        # not an admin here, or already restricted

                token = secrets.token_hex(8)
                PENDING[token] = {
                    "chat_id": event.chat_id,
                    "user_id": uid,
                    "expires": time.time() + timeout,
                }
                try:
                    await event.client.send_message(
                        event.chat_id,
                        clip(
                            "🛡 **Cipher Elite Captcha**\n\n"
                            f"👋 **Welcome!** Please prove you are human within "
                            f"**{timeout} seconds**, or you will be removed.\n\n"
                            "🤖 **Powered by Cipher Elite**"
                        ),
                        buttons=[Button.inline("✅ I am human", data=f"gk_{token}")],
                    )
                except Exception:
                    PENDING.pop(token, None)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    #  Sweeper — kick anyone whose challenge expired
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(func=lambda e: e.is_private and e.sender_id == owner_id))
    async def captcha_sweeper(event):
        """
        Piggybacks on owner PMs so no background task is needed. Cheap: it only
        scans the small PENDING dict and exits immediately when it is empty.
        """
        try:
            if not PENDING:
                return
            now = time.time()
            for token in [t for t, v in PENDING.items() if now > v["expires"]]:
                entry = PENDING.pop(token)
                try:
                    await bot.kick_participant(entry["chat_id"], entry["user_id"])
                except Exception:
                    pass
        except Exception:
            pass

    print("✅ Chat Guard Plugin: All handlers registered successfully")
