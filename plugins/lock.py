# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    lock
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
#  Thank you for respecting open-source software!
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "admin"

from datetime import datetime, timedelta, timezone

from telethon import events
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import (
    ChatBannedRights,
    InputPeerChannel,
    InputPeerChat,
)
from telethon.types import Message

from utils.utils import CipherElite
from utils.decorators import authorized_users_only, rishabh
from plugins.bot import add_handler

# -----------------------------------------------------------------------------
#  Lock presets — each maps to real ChatBannedRights fields (verified on
#  Telethon 1.37). Telegram applies these to every non-admin member.
# -----------------------------------------------------------------------------
IST = timezone(timedelta(hours=5, minutes=30))

LOCK_PRESETS = {
    "media": {
        "icon": "🖼",
        "label": "media (photos, videos, files, audio)",
        "rights": {"send_media": True, "send_photos": True, "send_videos": True,
                   "send_roundvideos": True, "send_audios": True, "send_voices": True,
                   "send_docs": True},
    },
    "sticker": {
        "icon": "🎭",
        "label": "stickers",
        "rights": {"send_stickers": True},
    },
    "gif": {
        "icon": "🎞",
        "label": "GIFs",
        "rights": {"send_gifs": True},
    },
    "game": {
        "icon": "🎮",
        "label": "games",
        "rights": {"send_games": True},
    },
    "inline": {
        "icon": "🔎",
        "label": "inline bot results",
        "rights": {"send_inline": True},
    },
    "link": {
        "icon": "🔗",
        "label": "link previews",
        "rights": {"embed_links": True},
    },
    "poll": {
        "icon": "📊",
        "label": "polls",
        "rights": {"send_polls": True},
    },
    "invite": {
        "icon": "📨",
        "label": "inviting users",
        "rights": {"invite_users": True},
    },
    "pin": {
        "icon": "📌",
        "label": "pinning messages",
        "rights": {"pin_messages": True},
    },
    "info": {
        "icon": "ℹ️",
        "label": "changing group info",
        "rights": {"change_info": True},
    },
    "topics": {
        "icon": "🗂",
        "label": "managing topics",
        "rights": {"manage_topics": True},
    },
    "message": {
        "icon": "💬",
        "label": "sending any message",
        "rights": {"send_messages": True},
    },
    "all": {
        "icon": "🔒",
        "label": "everything (read-only chat)",
        "rights": {"view_messages": False, "send_messages": True, "send_media": True,
                   "send_photos": True, "send_videos": True, "send_roundvideos": True,
                   "send_audios": True, "send_voices": True, "send_docs": True,
                   "send_stickers": True, "send_gifs": True, "send_games": True,
                   "send_inline": True, "embed_links": True, "send_polls": True,
                   "invite_users": True, "pin_messages": True, "change_info": True,
                   "send_plain": True},
    },
}

PRESET_ORDER = ["all", "message", "media", "sticker", "gif", "game", "inline",
                "link", "poll", "invite", "pin", "info", "topics"]

# aliases people tend to type
ALIASES = {
    "media": "media", "medias": "media", "photo": "media", "photos": "media",
    "video": "media", "videos": "media", "file": "media", "files": "media",
    "document": "media", "documents": "media", "audio": "media", "voice": "media",
    "sticker": "sticker", "stickers": "sticker",
    "gif": "gif", "gifs": "gif",
    "game": "game", "games": "game",
    "inline": "inline", "bot": "inline",
    "link": "link", "links": "link", "url": "link", "preview": "link",
    "poll": "poll", "polls": "poll",
    "invite": "invite", "adduser": "invite", "addusers": "invite",
    "pin": "pin", "pins": "pin",
    "info": "info", "about": "info",
    "topic": "topics", "topics": "topics",
    "message": "message", "messages": "message", "text": "message", "msg": "message",
    "all": "all", "everything": "all", "readonly": "all", "read-only": "all",
}


def init(client_instance):
    commands = [
        ".lock <type> - Restrict something for non-admins (media, sticker, link, all, ...)",
        ".unlock <type> - Give that permission back",
        ".lock all - Make the chat read-only for non-admins",
        ".locks - Show which locks are currently active here",
        ".locklist - List every lock type you can use"
    ]
    description = (
        "🔐 Chat Locks - one command to restrict non-admins\n"
        "🎯 13 lock types: media, sticker, gif, game, inline, link, poll,\n"
        "   invite, pin, info, topics, message, all\n"
        "👑 Admins and the owner are never affected (Telegram's own permission system)"
    )
    add_handler("lock", commands, description)


# -----------------------------------------------------------------------------
#  Helpers
# -----------------------------------------------------------------------------

def _chat_title(event):
    chat = getattr(event, "chat", None)
    return getattr(chat, "title", None) or getattr(chat, "first_name", None) or "this chat"


def _input_peer(event):
    """Build the InputPeer Telegram needs for permission calls."""
    chat = getattr(event, "chat", None)
    chat_id = getattr(event, "chat_id", None)
    if chat is not None:
        access = getattr(chat, "access_hash", None)
        if type(chat).__name__ == "Channel":
            return InputPeerChannel(channel_id=chat.id, access_hash=access)
        if type(chat).__name__ == "Chat":
            return InputPeerChat(chat_id=chat.id)
    return chat_id


async def _current_rights(event):
    """Read the chat's existing default_banned_rights, or None."""
    try:
        client = event.client
        chat = getattr(event, "chat", None)
        if type(chat).__name__ == "Channel":
            res = await client(GetFullChannelRequest(channel=chat))
        elif type(chat).__name__ == "Chat":
            res = await client(GetFullChatRequest(chat_id=chat.id))
        else:
            return None
        full = getattr(res, "full_chat", None)
        return getattr(full, "default_banned_rights", None)
    except Exception:
        return None


def _rights_snapshot(rights):
    """Which ChatBannedRights flags are currently True (i.e. blocked)."""
    if rights is None:
        return set()
    blocked = set()
    for field in ("send_messages", "send_media", "send_stickers", "send_gifs",
                  "send_games", "send_inline", "embed_links", "send_polls",
                  "change_info", "invite_users", "pin_messages", "manage_topics",
                  "send_photos", "send_videos", "send_roundvideos", "send_audios",
                  "send_voices", "send_docs"):
        if getattr(rights, field, False):
            blocked.add(field)
    return blocked


def _merge(base_rights, changes):
    """
    Produce a new ChatBannedRights from the chat's current one plus `changes`.
    Fields the chat already sets are preserved so an unlock does not silently
    re-enable something the owner locked by hand.
    """
    current = {}
    if base_rights is not None:
        for field in ("view_messages", "send_messages", "send_media", "send_stickers",
                      "send_gifs", "send_games", "send_inline", "embed_links",
                      "send_polls", "change_info", "invite_users", "pin_messages",
                      "manage_topics", "send_photos", "send_videos", "send_roundvideos",
                      "send_audios", "send_voices", "send_docs", "send_plain"):
            value = getattr(base_rights, field, None)
            if value is not None:
                current[field] = value
    current.update(changes)
    return ChatBannedRights(until_date=None, **current)


def _preset_summary(rights):
    """Which presets look active given the current blocked flags."""
    blocked = _rights_snapshot(rights)
    active = []
    for name in PRESET_ORDER:
        need = {k for k, v in LOCK_PRESETS[name]["rights"].items() if v is True}
        if need and need <= blocked:
            active.append(name)
    return active, blocked


def _locklist_text():
    lines = ["🔐 **Cipher Elite Chat Locks**\n", "**Available lock types:**\n"]
    for name in PRESET_ORDER:
        p = LOCK_PRESETS[name]
        lines.append(f"  {p['icon']} `{name}` — {p['label']}")
    lines.append("\n**Usage:**")
    lines.append("• `.lock media` / `.unlock media`")
    lines.append("• `.lock all` / `.unlock all`")
    lines.append("• `.locks` — what is locked right now")
    lines.append("\n👑 Admins are never affected.")
    lines.append("🤖 **Powered by Cipher Elite**")
    return "\n".join(lines)


async def _apply(event, names, locking):
    """Apply (or remove) one or more presets. Returns a report string."""
    preset = LOCK_PRESETS["all"] if "all" in names else None
    changes = {}
    if preset:
        for field, value in preset["rights"].items():
            changes[field] = value if locking else False
        # unlocking "all" must also restore the ability to see the chat
        if not locking:
            changes["view_messages"] = False
        labels = [f"{preset['icon']} {preset['label']}"]
    else:
        labels = []
        for name in names:
            p = LOCK_PRESETS[name]
            for field, value in p["rights"].items():
                changes[field] = value if locking else False
            labels.append(f"{p['icon']} {p['label']}")

    base = await _current_rights(event)
    new_rights = _merge(base, changes)

    client = event.client
    peer = _input_peer(event)
    if peer is None:
        return "❌ **This chat does not support permission locks.**"

    try:
        await client.edit_permissions(peer, new_rights)
    except Exception:
        # older Telethon / basic groups: fall back to the raw request
        try:
            from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
            await client(EditChatDefaultBannedRightsRequest(peer=peer, banned_rights=new_rights))
        except Exception as e:
            return (f"❌ **Telegram refused the change:** `{str(e)[:160]}`\n"
                    "💡 You must be an admin with the *Change Info* / *Ban Users* right.")

    verb = "Locked" if locking else "Unlocked"
    icon = "🔒" if locking else "🔓"
    body = "\n".join(f"  └ {x}" for x in labels)
    return (f"{icon} **{verb} in `{_chat_title(event)}`**\n"
            f"{body}\n\n"
            f"🕐 **At:** {datetime.now(IST).strftime('%d %b, %I:%M %p')} IST\n"
            "👑 **Admins and you are not affected.**")


# -----------------------------------------------------------------------------


async def register_commands():

    # =========================================================================
    #  .lock <type>
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.lock(?![\w.-])(?:\s+([\s\S]*))?"))
    @authorized_users_only()
    async def lock_cmd(event: Message):
        raw = (event.pattern_match.group(1) or "").strip().lower()

        if not raw or raw in ("help", "-h", "--help", "list"):
            return await event.reply(_locklist_text())

        tokens = [t for t in raw.replace(",", " ").split() if t]
        names = []
        unknown = []
        for tok in tokens:
            mapped = ALIASES.get(tok)
            if mapped:
                if mapped not in names:
                    names.append(mapped)
            else:
                unknown.append(tok)

        if unknown:
            return await event.reply(
                "🔐 **Cipher Elite Chat Locks**\n\n"
                f"❌ **Unknown lock type:** `{', '.join(unknown)}`\n\n"
                f"✅ **Valid:** `{', '.join(PRESET_ORDER)}`\n"
                "💡 **Try:** `.locklist` to see them all\n"
                "🤖 **Powered by Cipher Elite**"
            )

        if "all" in names:
            names = ["all"]              # "all" already covers everything

        status = await event.reply(f"🔄 **Applying lock in `{_chat_title(event)}`...**")
        try:
            report = await _apply(event, names, locking=True)
            await event.reply("🔐 **Cipher Elite Chat Locks**\n\n" + report +
                              "\n🤖 **Powered by Cipher Elite**")
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "💡 **Are you an admin with permission to change chat settings?**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass

    # =========================================================================
    #  .unlock <type>
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.unlock(?![\w.-])(?:\s+([\s\S]*))?"))
    @authorized_users_only()
    async def unlock_cmd(event: Message):
        raw = (event.pattern_match.group(1) or "").strip().lower()

        if not raw or raw in ("help", "-h", "--help"):
            return await event.reply(
                "🔐 **Cipher Elite Chat Locks**\n\n"
                "❌ **Usage:** `.unlock <type>`\n"
                f"✅ **Valid:** `{', '.join(PRESET_ORDER)}`\n"
                "💡 `.unlock all` removes every restriction\n"
                "🤖 **Powered by Cipher Elite**"
            )

        tokens = [t for t in raw.replace(",", " ").split() if t]
        names, unknown = [], []
        for tok in tokens:
            mapped = ALIASES.get(tok)
            if mapped:
                if mapped not in names:
                    names.append(mapped)
            else:
                unknown.append(tok)

        if unknown:
            return await event.reply(
                "🔐 **Cipher Elite Chat Locks**\n\n"
                f"❌ **Unknown lock type:** `{', '.join(unknown)}`\n\n"
                f"✅ **Valid:** `{', '.join(PRESET_ORDER)}`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        if "all" in names:
            names = ["all"]

        status = await event.reply(f"🔄 **Removing lock in `{_chat_title(event)}`...**")
        try:
            report = await _apply(event, names, locking=False)
            await event.reply("🔐 **Cipher Elite Chat Locks**\n\n" + report +
                              "\n🤖 **Powered by Cipher Elite**")
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "💡 **Are you an admin with permission to change chat settings?**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass

    # =========================================================================
    #  .locks — current state
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.locks(?![\w.-])"))
    @rishabh()
    async def locks_status_cmd(event: Message):
        status = await event.reply("🔄 **Reading chat permissions...**")
        try:
            rights = await _current_rights(event)
            active, blocked = _preset_summary(rights)

            lines = ["🔐 **Cipher Elite Chat Locks**\n",
                     f"📍 **Chat:** {_chat_title(event)}\n"]
            if not active and not blocked:
                lines.append("🟢 **No lock active** — everyone can post normally.")
            else:
                if active:
                    lines.append("🔒 **Active presets:**")
                    for name in active:
                        p = LOCK_PRESETS[name]
                        lines.append(f"  └ {p['icon']} `{name}` — {p['label']}")
                raw_flags = sorted(blocked)
                if raw_flags:
                    lines.append(f"\n🧾 **Raw flags blocked ({len(raw_flags)}):**")
                    lines.append("  └ `" + "`, `".join(raw_flags) + "`")

            lines.append("\n💡 `.lock <type>` · `.unlock <type>` · `.locklist`")
            lines.append("🤖 **Powered by Cipher Elite**")
            await event.reply("\n".join(lines)[:4000])
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "🤖 **Powered by Cipher Elite**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass

    # =========================================================================
    #  .locklist — what you can lock
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.locklist(?![\w.-])"))
    @rishabh()
    async def locklist_cmd(event: Message):
        await event.reply(_locklist_text())
