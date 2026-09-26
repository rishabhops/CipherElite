# =============================================================================
#  CipherElite Assistant Bot Plugin
#
#  Plugin Name:    moderation
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
#    ban / mute / warn / purge / pin — the core moderation tools for a group.
#
#  Merged from modban.py, modmute.py, modwarn.py, modpurge.py, modpin.py so related commands live in one file and share a single
#  init_bot_plugin().
#
#  Thank you for respecting open-source software!
# =============================================================================

import asyncio
import re
from datetime import datetime
from telethon import events
from telethon.errors import UserAdminInvalidError, UserNotParticipantError

try:
    from bot_plugins._shared import (
        IST,
        clip,
        fmt_when,
        group_only,
        human_duration,
        is_admin,
        now_str,
        parse_duration,
        require_admin,
        safe_delete,
        safe_edit,
        target_from_event,
        until,
        user_label,
    )
except ImportError:
    from _shared import (
        IST,
        clip,
        fmt_when,
        group_only,
        human_duration,
        is_admin,
        now_str,
        parse_duration,
        require_admin,
        safe_delete,
        safe_edit,
        target_from_event,
        until,
        user_label,
    )

# ---------------------------------------------------------------------------
#  modban.py — module level
# ---------------------------------------------------------------------------

COLLECTION_modban = "bot_modlog"


LOG_LIMIT = 100

# ---------------------------------------------------------------------------
#  modmute.py — module level
# ---------------------------------------------------------------------------

USAGE = (
    "🔇 **Cipher Elite Mute**\n\n"
    "**Usage:** `/mute <user> <duration> [reason]`\n\n"
    "**Examples:**\n"
    "• `/mute @user 30m` — 30 minutes\n"
    "• `/mute @user 2h spamming`\n"
    "• `/mute @user 1d`\n"
    "• reply to a message: `/mute 30m`\n\n"
    "**Durations:** `30s` `10m` `2h` `1d` `2w` (a bare number = minutes)\n"
    "💡 `/unmute <user>` lifts it early\n"
    "🤖 **Powered by Cipher Elite**"
)

# ---------------------------------------------------------------------------
#  modwarn.py — module level
# ---------------------------------------------------------------------------

COLLECTION_modwarn = "bot_warns"


DEFAULT_LIMIT = 3


MIN_LIMIT = 1


MAX_LIMIT = 20


MAX_WARNS_KEPT = 50


async def _chat_doc(chat_id):
    try:
        from DB.database import db_get
        doc = await db_get(COLLECTION_modwarn, str(chat_id), default=None)
    except Exception:
        doc = None
    if not isinstance(doc, dict):
        doc = {}
    doc.setdefault("limit", DEFAULT_LIMIT)
    users = doc.get("users")
    if not isinstance(users, dict):
        users = {}
    doc["users"] = users
    return doc


async def _save(chat_id, doc):
    try:
        from DB.database import db_set
        await db_set(COLLECTION_modwarn, str(chat_id), doc)
        return True
    except Exception:
        return False


def _help():
    return (
        "⚠️ **Cipher Elite Warns**\n\n"
        "**Commands:**\n"
        "• `/warn <user> <reason>` — warn someone\n"
        "• `/warns <user>` — see one member's warnings\n"
        "• `/warnlist` — every member with active warnings\n"
        "• `/resetwarn <user>` — clear one member\n"
        "• `/setwarnlimit <n>` — auto-ban threshold\n\n"
        "💡 Reply to a message instead of typing a username.\n"
        "🤖 **Powered by Cipher Elite**"
    )

# ---------------------------------------------------------------------------
#  modpurge.py — module level
# ---------------------------------------------------------------------------

MAX_PURGE = 5000          # hard ceiling so a stray reply cannot wipe a chat


BATCH = 100               # Telegram accepts up to 100 ids per call


MAX_CLEAN = 500


PAUSE = 0.4               # seconds between batches, to stay under flood limits

# ---------------------------------------------------------------------------
#  modfilter.py — module level
# ---------------------------------------------------------------------------

COLLECTION = "bot_filters"


MAX_PER_GROUP = 30


DEFAULT_COOLDOWN = 20          # seconds between two triggers of the same filter


_last_fired = {}               # (chat_id, trigger) -> timestamp


async def _chat_filters(chat_id):
    try:
        from DB.database import db_get
        data = await db_get(COLLECTION, str(chat_id), default=None)
    except Exception:
        data = None
    return data if isinstance(data, dict) else {}


async def _save_modfilter(chat_id, filters):
    try:
        from DB.database import db_set
        await db_set(COLLECTION, str(chat_id), filters)
        return True
    except Exception:
        return False


def compile_trigger(trigger, kind):
    """Build the regex for a filter, or return None when the pattern is invalid."""
    try:
        if kind == "regex":
            return re.compile(trigger, re.I)
        if kind == "contains":
            return re.compile(re.escape(trigger), re.I)
        return re.compile(rf"(?<!\w){re.escape(trigger)}(?!\w)", re.I)
    except re.error:
        return None


def render(template, event):
    """Fill in the placeholders a reply may use."""
    sender = getattr(event, "sender", None)
    chat = getattr(event, "chat", None)
    now = datetime.now(IST)
    first = getattr(sender, "first_name", None) or ""
    values = {
        "user": user_label(sender),
        "first": first,
        "mention": user_label(sender),
        "chat": getattr(chat, "title", None) or getattr(chat, "first_name", None) or "this chat",
        "id": str(getattr(sender, "id", "")),
        "count": str(len(getattr(event, "message", "") or "")),
        "time": now.strftime("%I:%M %p"),
        "date": now.strftime("%d %b %Y"),
    }
    out = template or ""
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return out


def _usage():
    return (
        "🔤 **Cipher Elite Filters**\n\n"
        "**Usage:**\n"
        "• `/filter <word> <reply>` — whole-word match\n"
        "• `/filter -c <text> <reply>` — match anywhere in the message\n"
        "• `/filter -r <regex> <reply>` — regular expression\n\n"
        "**Examples:**\n"
        "• `/filter price It costs ₹99`\n"
        "• `/filter -c help Read the pinned message`\n\n"
        "**Placeholders:** `{user}` `{first}` `{mention}` `{chat}` `{id}` `{time}` `{date}`\n\n"
        "💡 `/unfilter <word>` removes one · `/filters` lists them\n"
        "🤖 **Powered by Cipher Elite**"
    )

# ---------------------------------------------------------------------------
#  COMMAND REGISTRATION
# ---------------------------------------------------------------------------

def init_bot_plugin(bot, owner_id, owner_name):
    """Register every Moderation handler on the assistant bot."""

    # =======================================================================
    #  modban.py
    # =======================================================================
    """Register the ban/unban/kick handlers on the assistant bot."""

    async def _log(chat_id, action, target_id, mod_id, reason):
        """Append an entry to the per-chat moderation log (best effort)."""
        try:
            from DB.database import db_get, db_set
            key = str(chat_id)
            entries = await db_get(COLLECTION_modban, key, default=[])
            if not isinstance(entries, list):
                entries = []
            entries.append({
                "action": action,
                "target": target_id,
                "mod": mod_id,
                "reason": reason or "",
                "at": int(datetime.now().timestamp()),
            })
            await db_set(COLLECTION_modban, key, entries[-LOG_LIMIT:])
        except Exception:
            pass

    # -------------------------------------------------------------------------
    #  /ban [user] [reason]
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/ban(?:\s+([\s\S]*))?$"))
    async def ban_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        # split off an optional duration is intentionally NOT supported here;
        # /ban is permanent, /mute handles timed restrictions.
        target, err = await target_from_event(event, arg.split(None, 1)[0] if arg else "")
        if err:
            return await event.reply(err)
        if target is None:
            return await event.reply("❌ **Reply to a message or give a @username / id.**")

        reason = arg.split(None, 1)[1].strip() if len(arg.split(None, 1)) > 1 else ""

        if await is_admin(event, target.id):
            return await event.reply("🛑 **That user is an admin** — I cannot ban them.")

        status = await event.reply("🔄 **Banning...**")
        try:
            await event.client.edit_permissions(event.chat_id, target, view_messages=False)
        except UserAdminInvalidError:
            return await safe_edit(status, "🛑 **I am not allowed to ban admins.**")
        except Exception as e:
            return await safe_edit(
                status,
                f"❌ **Ban failed:** `{str(e)[:160]}`\n"
                "💡 Make sure I am an admin with the *Ban Users* right."
            )

        await _log(event.chat_id, "ban", target.id, event.sender_id, reason)
        await safe_edit(status, clip(
            "🔨 **Cipher Elite Moderation**\n\n"
            f"🚫 **Banned:** {user_label(target)}\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n"
            f"📝 **Reason:** {reason or 'not given'}\n"
            f"🕐 **At:** {now_str()}\n\n"
            "💡 `/unban` to reverse\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /unban <user|id>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/unban(?:\s+([\s\S]*))?$"))
    async def unban_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        if not arg:
            return await event.reply(
                "❌ **Usage:** `/unban <@username or user id>`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        target, err = await target_from_event(event, arg.split()[0])
        if err:
            return await event.reply(err)

        status = await event.reply("🔄 **Unbanning...**")
        try:
            await event.client.edit_permissions(event.chat_id, target)
        except UserNotParticipantError:
            return await safe_edit(status, "ℹ️ **That user is not banned here.**")
        except Exception as e:
            return await safe_edit(
                status, f"❌ **Unban failed:** `{str(e)[:160]}`"
            )

        await _log(event.chat_id, "unban", target.id, event.sender_id, "")
        await safe_edit(status, clip(
            "🔨 **Cipher Elite Moderation**\n\n"
            f"✅ **Unbanned:** {user_label(target)}\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n"
            f"🕐 **At:** {now_str()}\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /kick [user] [reason]
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/kick(?:\s+([\s\S]*))?$"))
    async def kick_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        target, err = await target_from_event(event, arg.split(None, 1)[0] if arg else "")
        if err:
            return await event.reply(err)
        if target is None:
            return await event.reply("❌ **Reply to a message or give a @username / id.**")
        reason = arg.split(None, 1)[1].strip() if len(arg.split(None, 1)) > 1 else ""

        if await is_admin(event, target.id):
            return await event.reply("🛑 **That user is an admin** — I cannot kick them.")

        status = await event.reply("🔄 **Kicking...**")
        try:
            # kicking == removing from the chat; they can rejoin via an invite
            await event.client.kick_participant(event.chat_id, target)
        except UserAdminInvalidError:
            return await safe_edit(status, "🛑 **I am not allowed to kick admins.**")
        except Exception as e:
            return await safe_edit(
                status,
                f"❌ **Kick failed:** `{str(e)[:160]}`\n"
                "💡 Make sure I am an admin with the *Ban Users* right."
            )

        await _log(event.chat_id, "kick", target.id, event.sender_id, reason)
        await safe_edit(status, clip(
            "🔨 **Cipher Elite Moderation**\n\n"
            f"👢 **Kicked:** {user_label(target)}\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n"
            f"📝 **Reason:** {reason or 'not given'}\n"
            f"🕐 **At:** {now_str()}\n\n"
            "💡 They can rejoin with an invite link\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # =======================================================================
    #  modmute.py
    # =======================================================================
    """Register the mute/unmute handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /mute <user> <duration> [reason]
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/mute(?:\s+([\s\S]*))?$"))
    async def mute_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        if not arg and not event.reply_to_msg_id:
            return await event.reply(USAGE)

        # "/mute 30m" while replying -> first token is the duration.
        # "/mute @user 30m reason" -> first token is the user.
        tokens = arg.split()
        first = tokens[0] if tokens else ""
        replying = bool(event.reply_to_msg_id)

        if replying and parse_duration(first):
            seconds = parse_duration(first)
            reason = " ".join(tokens[1:])
            target, err = await target_from_event(event, "")
        else:
            user_arg = first
            seconds = parse_duration(tokens[1]) if len(tokens) > 1 else None
            reason = " ".join(tokens[2:]) if len(tokens) > 2 else ""
            target, err = await target_from_event(event, user_arg)

        if err:
            return await event.reply(err)
        if target is None:
            return await event.reply("❌ **Reply to a message or give a @username / id.**")
        if not seconds:
            return await event.reply(
                "❌ **Give a duration.**\n\n"
                "💡 `/mute @user 30m` · `/mute @user 2h reason`\n"
                "🤖 **Powered by Cipher Elite**"
            )
        if seconds < 30:
            return await event.reply("❌ **Minimum mute is 30 seconds.**")

        if await is_admin(event, target.id):
            return await event.reply("🛑 **That user is an admin** — I cannot mute them.")

        deadline = until(seconds)
        status = await event.reply("🔄 **Muting...**")
        try:
            await event.client.edit_permissions(
                event.chat_id, target, until_date=deadline,
                send_messages=False, send_media=False, send_stickers=False,
                send_gifs=False, send_games=False, send_inline=False,
                send_polls=False, embed_link_previews=False,
            )
        except UserAdminInvalidError:
            return await safe_edit(status, "🛑 **I am not allowed to mute admins.**")
        except Exception as e:
            return await safe_edit(
                status,
                f"❌ **Mute failed:** `{str(e)[:160]}`\n"
                "💡 Make sure I am an admin with the *Ban Users* right."
            )

        await safe_edit(status, clip(
            "🔇 **Cipher Elite Mute**\n\n"
            f"🤐 **Muted:** {user_label(target)}\n"
            f"⏱ **For:** {human_duration(seconds)}\n"
            f"📅 **Until:** {fmt_when(deadline)}\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n"
            f"📝 **Reason:** {reason or 'not given'}\n\n"
            "💡 Telegram lifts this automatically. `/unmute` to lift early.\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /unmute <user>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/unmute(?:\s+([\s\S]*))?$"))
    async def unmute_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        target, err = await target_from_event(event, arg.split()[0] if arg else "")
        if err:
            return await event.reply(err)
        if target is None:
            return await event.reply("❌ **Reply to a message or give a @username / id.**")

        status = await event.reply("🔄 **Unmuting...**")
        try:
            # passing no restrictions and no until_date restores full rights
            await event.client.edit_permissions(event.chat_id, target)
        except Exception as e:
            return await safe_edit(status, f"❌ **Unmute failed:** `{str(e)[:160]}`")

        await safe_edit(status, clip(
            "🔇 **Cipher Elite Mute**\n\n"
            f"🔊 **Unmuted:** {user_label(target)}\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # =======================================================================
    #  modwarn.py
    # =======================================================================
    """Register the warn handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /warn <user> <reason>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/warn(?:s|list|limit)?(?:\s+([\s\S]*))?$"))
    async def warn_router(event):
        """
        One registration handles /warn, /warns, /warnlist and /warnlimit so the
        four commands cannot drift apart. The text is re-read from the message
        to know which one was typed.
        """
        raw = (event.raw_text or "").strip()
        head = raw.split()[0].lower() if raw else "/warn"

        if head == "/warnlist":
            return await warnlist_handler(event)
        if head == "/warns":
            return await warns_handler(event)
        if head == "/warnlimit":
            return await setlimit_handler(event)
        return await warn_handler(event)

    async def warn_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        tokens = arg.split(None, 1)
        first = tokens[0] if tokens else ""
        reason = tokens[1].strip() if len(tokens) > 1 else ""

        target, err = await target_from_event(event, first)
        if err:
            return await event.reply(err)
        if target is None:
            return await event.reply(
                "❌ **Reply to a message or give a @username / id.**\n\n" + _help()
            )
        if await is_admin(event, target.id):
            return await event.reply("🛑 **That user is an admin** — I cannot warn them.")

        doc = await _chat_doc(event.chat_id)
        limit = int(doc.get("limit", DEFAULT_LIMIT))
        key = str(target.id)
        entries = doc["users"].get(key, [])
        entries.append({
            "reason": reason or "not given",
            "by": event.sender_id,
            "at": int(datetime.now().timestamp()),
        })
        entries = entries[-MAX_WARNS_KEPT:]
        doc["users"][key] = entries
        count = len(entries)

        # reached the threshold -> ban and clear the slate
        banned = False
        if count >= limit:
            try:
                await event.client.edit_permissions(
                    event.chat_id, target, view_messages=False
                )
                banned = True
                doc["users"].pop(key, None)
                count = 0
            except Exception:
                banned = False

        if not await _save(event.chat_id, doc):
            return await event.reply("❌ **Could not save the warning.**")

        if banned:
            return await event.reply(clip(
                "⚠️ **Cipher Elite Warns**\n\n"
                f"🔨 **{user_label(target)} reached {limit} warnings — banned.**\n"
                f"📝 **Last reason:** {reason or 'not given'}\n"
                f"👮 **By:** {user_label(await event.get_sender())}\n"
                f"🕐 **At:** {now_str()}\n\n"
                "💡 `/unban` to reverse\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        await event.reply(clip(
            "⚠️ **Cipher Elite Warns**\n\n"
            f"🚩 **Warned:** {user_label(target)}\n"
            f"🔢 **Count:** {count}/{limit}\n"
            f"📝 **Reason:** {reason or 'not given'}\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n\n"
            f"💡 {limit - count} more before an automatic ban\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    async def warns_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")

        arg = (event.pattern_match.group(1) or "").strip()
        target, err = await target_from_event(event, arg.split()[0] if arg else "")
        if err:
            return await event.reply(err)
        if target is None:
            return await event.reply("❌ **Reply to a message or give a @username / id.**")

        doc = await _chat_doc(event.chat_id)
        entries = doc["users"].get(str(target.id), [])
        limit = int(doc.get("limit", DEFAULT_LIMIT))

        if not entries:
            return await event.reply(clip(
                "⚠️ **Cipher Elite Warns**\n\n"
                f"✅ **{user_label(target)} has no warnings.**\n"
                f"🔢 **Limit:** {limit}\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        lines = [
            "⚠️ **Cipher Elite Warns**\n",
            f"👤 **Member:** {user_label(target)}",
            f"🔢 **Warnings:** {len(entries)}/{limit}\n",
        ]
        for i, entry in enumerate(entries[-10:], 1):
            when = datetime.fromtimestamp(entry.get("at", 0))
            stamp = when.strftime("%d %b %H:%M") if entry.get("at") else "?"
            lines.append(f"{i}. `{stamp}` — {entry.get('reason', '?')}")
        lines.append("\n💡 `/resetwarn` clears them")
        lines.append("🤖 **Powered by Cipher Elite**")
        await event.reply(clip("\n".join(lines)))

    async def warnlist_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        doc = await _chat_doc(event.chat_id)
        users = {k: v for k, v in doc["users"].items() if v}
        limit = int(doc.get("limit", DEFAULT_LIMIT))

        if not users:
            return await event.reply(clip(
                "⚠️ **Cipher Elite Warns**\n\n"
                "✅ **Nobody has active warnings here.**\n"
                f"🔢 **Limit:** {limit}\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        ordered = sorted(users.items(), key=lambda kv: len(kv[1]), reverse=True)
        lines = ["⚠️ **Cipher Elite Warns**\n",
                 f"🔢 **Limit:** {limit} · **Members warned:** {len(ordered)}\n"]
        for uid, entries in ordered[:25]:
            lines.append(f"  └ `{uid}` — **{len(entries)}** warning(s)")
        if len(ordered) > 25:
            lines.append(f"  … and {len(ordered) - 25} more")
        lines.append("\n💡 `/warns <user>` for the reasons")
        lines.append("🤖 **Powered by Cipher Elite**")
        await event.reply(clip("\n".join(lines)))

    async def setlimit_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        if not arg.isdigit():
            return await event.reply(
                "❌ **Usage:** `/setwarnlimit <n>`\n"
                f"💡 Between {MIN_LIMIT} and {MAX_LIMIT}\n"
                "🤖 **Powered by Cipher Elite**"
            )
        limit = max(MIN_LIMIT, min(int(arg), MAX_LIMIT))
        doc = await _chat_doc(event.chat_id)
        doc["limit"] = limit
        if not await _save(event.chat_id, doc):
            return await event.reply("❌ **Could not save the limit.**")
        await event.reply(clip(
            "⚠️ **Cipher Elite Warns**\n\n"
            f"🔢 **Auto-ban limit set to {limit}.**\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /resetwarn <user>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/resetwarn(?:\s+([\s\S]*))?$"))
    async def resetwarn_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        target, err = await target_from_event(event, arg.split()[0] if arg else "")
        if err:
            return await event.reply(err)
        if target is None:
            return await event.reply("❌ **Reply to a message or give a @username / id.**")

        doc = await _chat_doc(event.chat_id)
        had = doc["users"].pop(str(target.id), None)
        if not await _save(event.chat_id, doc):
            return await event.reply("❌ **Could not save the change.**")

        await event.reply(clip(
            "⚠️ **Cipher Elite Warns**\n\n"
            f"🧹 **Cleared {len(had) if had else 0} warning(s) for {user_label(target)}.**\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /setwarnlimit <n>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/setwarnlimit(?:\s+([\s\S]*))?$"))
    async def setwarnlimit_cmd(event):
        return await setlimit_handler(event)

    # =======================================================================
    #  modpurge.py
    # =======================================================================
    """Register the purge handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /purge — delete everything after the replied-to message
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/purge(?:\s+([\s\S]*))?$"))
    async def purge_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply(
                "🧹 **Cipher Elite Purge**\n\n"
                "❌ **Reply to the oldest message you want removed.**\n"
                "Everything after it will be deleted.\n\n"
                "💡 `/clean <n> @user` deletes one member's last n messages\n"
                "🤖 **Powered by Cipher Elite**"
            )

        status = await event.reply("🔄 **Purging...**")
        deleted = 0
        failed = 0
        try:
            batch = []
            async for message in event.client.iter_messages(
                event.chat_id, min_id=reply.id, reverse=False
            ):
                if message.id == event.id:
                    continue
                batch.append(message.id)
                if len(batch) >= BATCH:
                    try:
                        await event.client.delete_messages(event.chat_id, batch)
                        deleted += len(batch)
                    except Exception:
                        failed += len(batch)
                    batch = []
                    await asyncio.sleep(PAUSE)
                if deleted + failed >= MAX_PURGE:
                    break
            if batch:
                try:
                    await event.client.delete_messages(event.chat_id, batch)
                    deleted += len(batch)
                except Exception:
                    failed += len(batch)
        except Exception as e:
            return await safe_edit(
                status,
                f"❌ **Purge stopped:** `{str(e)[:160]}`\n"
                f"🗑 **Deleted {deleted} before failing.**\n"
                "💡 Make sure I am an admin with the *Delete Messages* right."
            )

        # remove the command itself last so the count stays visible briefly
        await safe_edit(status, clip(
            "🧹 **Cipher Elite Purge**\n\n"
            f"🗑 **Deleted:** {deleted} message(s)\n"
            + (f"⚠️ **Could not delete:** {failed}\n" if failed else "")
            + "\n💡 Telegram only allows deleting messages younger than 48 hours.\n"
            "🤖 **Powered by Cipher Elite**"
        ))
        await asyncio.sleep(4)
        await safe_delete(status)

    # -------------------------------------------------------------------------
    #  /del — delete one replied-to message
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/del$"))
    async def del_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply(
                "🧹 **Reply to the message you want deleted.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        try:
            await event.client.delete_messages(event.chat_id, [reply.id])
        except Exception as e:
            return await event.reply(
                f"❌ **Delete failed:** `{str(e)[:160]}`\n"
                "💡 Telegram only allows deleting messages younger than 48 hours.\n"
                "🤖 **Powered by Cipher Elite**"
            )

        notice = await event.reply(clip(
            "🧹 **Cipher Elite Purge**\n\n"
            f"🗑 **Deleted a message from {user_label(reply.sender)}.**\n"
            "🤖 **Powered by Cipher Elite**"
        ))
        await asyncio.sleep(3)
        await safe_delete(notice)

    # -------------------------------------------------------------------------
    #  /clean <n> [@user] — delete one member's last n messages
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/clean(?:\s+([\s\S]*))?$"))
    async def clean_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        tokens = arg.split()
        count = None
        user_arg = ""
        for tok in tokens:
            if tok.isdigit() and count is None:
                count = int(tok)
            else:
                user_arg = tok
                break

        if not count:
            return await event.reply(
                "🧹 **Cipher Elite Purge**\n\n"
                "❌ **Usage:** `/clean <n> [@user]`\n\n"
                "**Examples:**\n"
                "• `/clean 50 @user` — their last 50 messages\n"
                "• `/clean 100` — reply to one of their messages instead\n\n"
                f"💡 Maximum {MAX_CLEAN}\n"
                "🤖 **Powered by Cipher Elite**"
            )

        count = max(1, min(count, MAX_CLEAN))

        target = None
        if user_arg:
            target, err = await target_from_event(event, user_arg)
            if err:
                return await event.reply(err)
        else:
            reply = await event.get_reply_message()
            if reply and reply.sender_id:
                target = reply.sender
        if target is None:
            return await event.reply("❌ **Give a @username / id, or reply to one of their messages.**")

        status = await event.reply(f"🔄 **Cleaning up to {count} message(s)...**")
        deleted = 0
        try:
            batch = []
            async for message in event.client.iter_messages(
                event.chat_id, from_user=target, limit=count
            ):
                batch.append(message.id)
                if len(batch) >= BATCH:
                    await event.client.delete_messages(event.chat_id, batch)
                    deleted += len(batch)
                    batch = []
                    await asyncio.sleep(PAUSE)
            if batch:
                await event.client.delete_messages(event.chat_id, batch)
                deleted += len(batch)
        except Exception as e:
            return await safe_edit(
                status,
                f"❌ **Clean stopped:** `{str(e)[:160]}`\n"
                f"🗑 **Deleted {deleted} before failing.**"
            )

        await safe_edit(status, clip(
            "🧹 **Cipher Elite Purge**\n\n"
            f"🗑 **Deleted {deleted} message(s) from {user_label(target)}.**\n\n"
            "💡 Telegram only allows deleting messages younger than 48 hours.\n"
            "🤖 **Powered by Cipher Elite**"
        ))
        await asyncio.sleep(4)
        await safe_delete(status)

    # =======================================================================
    #  modpin.py
    # =======================================================================
    """Register the pin handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /pin  (reply to a message; optional "loud" to notify everyone)
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/pin(?:\s+([\s\S]*))?$"))
    async def pin_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply(
                "📌 **Cipher Elite Pin**\n\n"
                "❌ **Reply to the message you want pinned.**\n\n"
                "💡 Add `loud` to notify everyone: `/pin loud`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        arg = (event.pattern_match.group(1) or "").strip().lower()
        notify = arg in ("loud", "notify", "all", "-l")

        status = await event.reply("🔄 **Pinning...**")
        try:
            await event.client.pin_message(event.chat_id, reply.id, notify=notify)
        except Exception as e:
            return await safe_edit(
                status,
                f"❌ **Pin failed:** `{str(e)[:160]}`\n"
                "💡 Make sure I am an admin with the *Pin Messages* right."
            )

        await safe_edit(status, clip(
            "📌 **Cipher Elite Pin**\n\n"
            f"✅ **Pinned** [this message](t.me/c/{event.chat_id}/{reply.id})\n"
            f"🔔 **Members notified:** {'yes' if notify else 'no'}\n"
            f"👮 **By:** {user_label(await event.get_sender())}\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /unpin  (reply to one message, or no argument to clear every pin)
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/unpin(?:\s+([\s\S]*))?$"))
    async def unpin_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        reply = await event.get_reply_message()
        status = await event.reply("🔄 **Unpinning...**")

        # replying -> unpin that single message
        if reply:
            try:
                await event.client.unpin_message(event.chat_id, reply.id)
            except Exception as e:
                return await safe_edit(status, f"❌ **Unpin failed:** `{str(e)[:160]}`")
            return await safe_edit(status, clip(
                "📌 **Cipher Elite Pin**\n\n"
                "✅ **Unpinned that message.**\n\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        # no reply -> clear every pin
        arg = (event.pattern_match.group(1) or "").strip().lower()
        if arg not in ("", "all", "every", "*"):
            return await safe_edit(status,
                "❌ **Reply to a message to unpin it,** or use `/unpin all` "
                "to remove every pin.\n🤖 **Powered by Cipher Elite**")

        try:
            await event.client.unpin_message(event.chat_id)
        except Exception as e:
            return await safe_edit(status, f"❌ **Unpin failed:** `{str(e)[:160]}`")

        await safe_edit(status, clip(
            "📌 **Cipher Elite Pin**\n\n"
            "✅ **Removed every pin in this chat.**\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /pinned  — list what is pinned
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/pinned$"))
    async def pinned_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")

        status = await event.reply("🔄 **Reading pinned messages...**")
        try:
            chat = await event.client.get_entity(event.chat_id)
            pinned = getattr(chat, "pinned_message", None)
            if not pinned:
                # newer Telegram keeps several pins; fetch them from the chat
                res = await event.client.get_messages(event.chat_id, limit=100)
                pinned = [m for m in res if getattr(m, "pinned", False)]
        except Exception:
            pinned = None

        if not pinned:
            return await safe_edit(status, clip(
                "📌 **Cipher Elite Pin**\n\n"
                "ℹ️ **Nothing is pinned here.**\n\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        # a single pinned message arrives as an int id on some layer versions
        if isinstance(pinned, int):
            return await safe_edit(status, clip(
                "📌 **Cipher Elite Pin**\n\n"
                f"📍 **Pinned message id:** `{pinned}`\n\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        items = pinned if isinstance(pinned, list) else [pinned]
        lines = ["📌 **Cipher Elite Pin**\n", f"📍 **Pinned:** {len(items)}\n"]
        for i, msg in enumerate(items[:10], 1):
            mid = getattr(msg, "id", None)
            text = (getattr(msg, "message", None) or "(media)").strip().replace("\n", " ")
            if len(text) > 60:
                text = text[:57] + "…"
            lines.append(f"{i}. `{mid}` — {text}")
        lines.append("\n💡 `/unpin all` clears them")
        lines.append("🤖 **Powered by Cipher Elite**")
        await safe_edit(status, clip("\n".join(lines)))


    # =======================================================================
    #  modfilter.py
    # =======================================================================
    """Register the filter handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /filter [-c|-r] <trigger> <reply>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/filter(?:\s+([\s\S]*))?$"))
    async def filter_add_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        if not arg:
            return await event.reply(_usage())

        kind = "word"
        tokens = arg.split(None, 1)
        head = tokens[0].lower()
        if head in ("-c", "-contains", "contains"):
            kind = "contains"
            rest = tokens[1] if len(tokens) > 1 else ""
        elif head in ("-r", "-regex", "regex"):
            kind = "regex"
            rest = tokens[1] if len(tokens) > 1 else ""
        else:
            rest = arg

        parts = rest.split(None, 1)
        if len(parts) < 2 or not parts[0] or not parts[1].strip():
            return await event.reply(
                "❌ **Give both a trigger and a reply.**\n\n" + _usage()
            )
        trigger, reply_text = parts[0], parts[1].strip()

        if compile_trigger(trigger, kind) is None:
            return await event.reply(
                "❌ **That regex is invalid.**\n"
                "💡 Check the brackets and escapes, or drop `-r`.\n"
                "🤖 **Powered by Cipher Elite**"
            )

        filters = await _chat_filters(event.chat_id)
        existing = len([k for k in filters if not k.startswith("_")])
        if trigger not in filters and existing >= MAX_PER_GROUP:
            return await event.reply(
                f"❌ **Limit reached** ({MAX_PER_GROUP} filters per group).\n"
                "💡 `/unfilter <word>` to free a slot\n"
                "🤖 **Powered by Cipher Elite**"
            )

        filters[trigger] = {"kind": kind, "reply": reply_text, "hits": 0}
        if not await _save_modfilter(event.chat_id, filters):
            return await event.reply("❌ **Could not save the filter.**")

        mode = {"word": "whole word", "contains": "contains", "regex": "regex"}[kind]
        await event.reply(clip(
            "🔤 **Cipher Elite Filters**\n\n"
            f"✅ **Saved filter** `{trigger}`\n"
            f"🎯 **Match:** {mode}\n"
            f"💬 **Reply:** {reply_text[:120]}\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /unfilter <trigger>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/unfilter(?:\s+([\s\S]*))?$"))
    async def filter_remove_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        trigger = (event.pattern_match.group(1) or "").strip()
        if not trigger:
            return await event.reply(
                "❌ **Usage:** `/unfilter <word>`\n"
                "💡 `/filters` lists what you can remove\n"
                "🤖 **Powered by Cipher Elite**"
            )

        filters = await _chat_filters(event.chat_id)
        if trigger not in filters:
            return await event.reply(
                f"ℹ️ **No filter named** `{trigger}` **here.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        filters.pop(trigger, None)
        if not await _save_modfilter(event.chat_id, filters):
            return await event.reply("❌ **Could not save the change.**")

        await event.reply(clip(
            "🔤 **Cipher Elite Filters**\n\n"
            f"🗑 **Removed filter** `{trigger}`\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /filters — list
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/filters$"))
    async def filter_list_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")

        filters = await _chat_filters(event.chat_id)
        entries = {k: v for k, v in filters.items() if not k.startswith("_")}
        if not entries:
            return await event.reply(clip(
                "🔤 **Cipher Elite Filters**\n\n"
                "ℹ️ **No filters set in this group.**\n\n"
                "💡 `/filter <word> <reply>` to add one\n"
                "🤖 **Powered by Cipher Elite**"
            ))

        lines = ["🔤 **Cipher Elite Filters**\n",
                 f"🔢 **Count:** {len(entries)}/{MAX_PER_GROUP}\n"]
        for trigger, cfg in list(entries.items())[:25]:
            kind = cfg.get("kind", "word")
            hits = cfg.get("hits", 0)
            preview = (cfg.get("reply", "") or "").replace("\n", " ")[:40]
            lines.append(f"  └ `{trigger}` [{kind}] ×{hits} — {preview}")
        if len(entries) > 25:
            lines.append(f"  … and {len(entries) - 25} more")
        lines.append("\n💡 `/unfilter <word>` to remove one")
        lines.append("🤖 **Powered by Cipher Elite**")
        await event.reply(clip("\n".join(lines)))

    # -------------------------------------------------------------------------
    #  Watcher — fire a matching filter
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(incoming=True, func=lambda e: not e.is_private))
    async def filter_watcher(event):
        try:
            text = getattr(event, "raw_text", None) or ""
            if not text or text.startswith("/"):
                return
            # never answer other bots, or we can loop
            if getattr(event, "via_bot_id", None):
                return

            filters = await _chat_filters(event.chat_id)
            if not filters:
                return

            import time
            now = time.time()
            for trigger, cfg in filters.items():
                if trigger.startswith("_"):
                    continue
                kind = cfg.get("kind", "word")
                pattern = compile_trigger(trigger, kind)
                if pattern is None or not pattern.search(text):
                    continue

                key = (event.chat_id, trigger)
                last = _last_fired.get(key, 0)
                if now - last < DEFAULT_COOLDOWN:
                    continue
                _last_fired[key] = now

                cfg["hits"] = int(cfg.get("hits", 0)) + 1
                await _save_modfilter(event.chat_id, filters)

                await event.reply(render(cfg.get("reply", ""), event))
                return
        except Exception:
            pass

    print("✅ Moderation Plugin: All handlers registered successfully")