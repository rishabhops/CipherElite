# =============================================================================
#  CipherElite Assistant Bot Plugin
#
#  Plugin Name:    joinmod
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
#    welcome/goodbye messages and the join-request approval queue.
#
#  Merged from greeter.py, joinreq.py so related commands live in one file and share a single
#  init_bot_plugin().
#
#  Thank you for respecting open-source software!
# =============================================================================

from datetime import datetime
from telethon import Button, events
from telethon.tl.types import (
    MessageActionChatAddUser,
    MessageActionChatDeleteUser,
    MessageActionChatJoinedByLink,
    MessageActionChatJoinedByRequest,
)
from telethon.tl.functions.messages import (
    GetChatInviteImportersRequest,
    HideAllChatJoinRequestsRequest,
    HideChatJoinRequestRequest,
)

try:
    from bot_plugins._shared import (
        IST,
        clip,
        group_only,
        require_admin,
        safe_edit,
        user_label,
    )
except ImportError:
    from _shared import (
        IST,
        clip,
        group_only,
        require_admin,
        safe_edit,
        user_label,
    )

# ---------------------------------------------------------------------------
#  greeter.py — module level
# ---------------------------------------------------------------------------

COLLECTION = "bot_greetings"


MAX_LEN = 1000


JOIN_ACTIONS = (
    MessageActionChatAddUser,
    MessageActionChatJoinedByLink,
    MessageActionChatJoinedByRequest,
)


LEAVE_ACTIONS = (MessageActionChatDeleteUser,)


async def _get(chat_id):
    try:
        from DB.database import db_get
        data = await db_get(COLLECTION, str(chat_id), default=None)
    except Exception:
        data = None
    return data if isinstance(data, dict) else {}


async def _save(chat_id, doc):
    try:
        from DB.database import db_set
        await db_set(COLLECTION, str(chat_id), doc)
        return True
    except Exception:
        return False


async def _member_count(client, chat_id):
    try:
        return len(await client.get_participants(chat_id))
    except Exception:
        return 0


def render(template, user, chat_title, count):
    """Fill in the placeholders a greeting may use."""
    now = datetime.now(IST)
    first = getattr(user, "first_name", None) or ""
    values = {
        "user": user_label(user),
        "first": first,
        "mention": user_label(user),
        "chat": chat_title or "this group",
        "count": str(count),
        "time": now.strftime("%I:%M %p"),
        "date": now.strftime("%d %b %Y"),
    }
    out = template or ""
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return out


def _preview(doc, kind):
    text = (doc.get(kind) or "").strip()
    label = "Welcome" if kind == "welcome" else "Goodbye"
    icon = "👋" if kind == "welcome" else "👋"
    if not text:
        return (
            f"{icon} **Cipher Elite {label}**\n\n"
            f"ℹ️ **No {kind} message is set here.**\n\n"
            f"💡 `/set{kind} <text>` to add one\n"
            "🤖 **Powered by Cipher Elite**"
        )
    return (
        f"{icon} **Cipher Elite {label}**\n\n"
        f"{text}\n\n"
        "🧪 **That is the raw text** — placeholders are filled in when it is sent.\n"
        "🤖 **Powered by Cipher Elite**"
    )


def _help():
    return (
        "👋 **Cipher Elite Greetings**\n\n"
        "**Commands:**\n"
        "• `/setwelcome <text>` — message for new members\n"
        "• `/setgoodbye <text>` — message when someone leaves\n"
        "• `/welcome` · `/goodbye` — preview the current text\n"
        "• `/delwelcome` · `/delgoodbye` — turn one off\n\n"
        "**Placeholders:** `{user}` `{first}` `{mention}` `{chat}` `{count}` `{time}` `{date}`\n\n"
        "**Example:** `/setwelcome Welcome {mention} to {chat}!`\n"
        "🤖 **Powered by Cipher Elite**"
    )

# ---------------------------------------------------------------------------
#  joinreq.py — module level
# ---------------------------------------------------------------------------

PAGE = 5


async def _pending(client, chat, limit=50):
    """Return the list of users waiting for approval."""
    try:
        res = await client(GetChatInviteImportersRequest(
            peer=chat, offset_date=None, offset_user=None,
            limit=limit, requested=True,
        ))
    except Exception:
        return None
    return getattr(res, "importers", []) or []

# ---------------------------------------------------------------------------
#  COMMAND REGISTRATION
# ---------------------------------------------------------------------------

def init_bot_plugin(bot, owner_id, owner_name):
    """Register every Join Moderation handler on the assistant bot."""

    # =======================================================================
    #  greeter.py
    # =======================================================================
    """Register the greeting handlers on the assistant bot."""

    # -------------------------------------------------------------------------
    #  /setwelcome <text>   and   /setgoodbye <text>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/set(welcome|goodbye)(?:\s+([\s\S]*))?$"))
    async def set_greeting_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        kind = event.pattern_match.group(1).lower()
        text = (event.pattern_match.group(2) or "").strip()
        if not text:
            reply = await event.get_reply_message()
            text = (reply.text or "").strip() if reply else ""
        if not text:
            return await event.reply(
                f"❌ **Usage:** `/set{kind} <text>`\n\n" + _help()
            )
        if len(text) > MAX_LEN:
            return await event.reply(
                f"❌ **Too long** (max {MAX_LEN} characters).\n"
                "🤖 **Powered by Cipher Elite**"
            )

        doc = await _get(event.chat_id)
        doc[kind] = text
        if not await _save(event.chat_id, doc):
            return await event.reply("❌ **Could not save the message.**")

        await event.reply(clip(
            "👋 **Cipher Elite Greetings**\n\n"
            f"✅ **{kind.title()} message saved.**\n\n"
            f"💡 `/{kind}` previews it\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /welcome   and   /goodbye — preview
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/(welcome|goodbye)$"))
    async def preview_greeting_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        kind = event.pattern_match.group(1).lower()
        doc = await _get(event.chat_id)
        await event.reply(clip(_preview(doc, kind)))

    # -------------------------------------------------------------------------
    #  /delwelcome   and   /delgoodbye
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/del(welcome|goodbye)$"))
    async def delete_greeting_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        kind = event.pattern_match.group(1).lower()
        doc = await _get(event.chat_id)
        if not doc.get(kind):
            return await event.reply(
                f"ℹ️ **No {kind} message is set here.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        doc.pop(kind, None)
        if not await _save(event.chat_id, doc):
            return await event.reply("❌ **Could not save the change.**")

        await event.reply(clip(
            "👋 **Cipher Elite Greetings**\n\n"
            f"🗑 **{kind.title()} message removed.**\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  Watcher — send the greeting when someone joins or leaves
    # -------------------------------------------------------------------------
    @bot.on(events.ChatAction(func=lambda e: not e.is_private))
    async def greeting_watcher(event):
        try:
            action = getattr(getattr(event, "action_message", None), "action", None)
            if action is None:
                return

            doc = await _get(event.chat_id)
            if not doc:
                return

            chat_title = getattr(getattr(event, "chat", None), "title", None)

            if isinstance(action, JOIN_ACTIONS) and doc.get("welcome"):
                users = getattr(action, "users", None) or []
                if not users:
                    users = [getattr(event, "user_id", None)]
                count = await _member_count(event.client, event.chat_id)
                for uid in users:
                    if uid is None:
                        continue
                    try:
                        user = await event.client.get_entity(uid)
                    except Exception:
                        continue
                    await event.client.send_message(
                        event.chat_id, clip(render(doc["welcome"], user, chat_title, count))
                    )
                return

            if isinstance(action, LEAVE_ACTIONS) and doc.get("goodbye"):
                uid = getattr(action, "user_id", None) or getattr(event, "user_id", None)
                if uid is None:
                    return
                try:
                    user = await event.client.get_entity(uid)
                except Exception:
                    return
                count = await _member_count(event.client, event.chat_id)
                await event.client.send_message(
                    event.chat_id, clip(render(doc["goodbye"], user, chat_title, count))
                )
        except Exception:
            pass

    # =======================================================================
    #  joinreq.py
    # =======================================================================
    """Register the join-request handlers on the assistant bot."""

    def _buttons(importers, start=0):
        rows = []
        page = importers[start:start + PAGE]
        for entry in page:
            uid = getattr(entry, "user_id", None)
            rows.append([
                Button.inline(f"✅ {uid}", data=f"jr_ok_{uid}"),
                Button.inline(f"❌ {uid}", data=f"jr_no_{uid}"),
            ])
        nav = []
        if start > 0:
            nav.append(Button.inline("◀ Prev", data=f"jr_pg_{start - PAGE}"))
        if start + PAGE < len(importers):
            nav.append(Button.inline("Next ▶", data=f"jr_pg_{start + PAGE}"))
        if nav:
            rows.append(nav)
        return rows

    async def _render(event_or_query, client, chat, start=0):
        importers = await _pending(client, chat)
        if importers is None:
            return (
                "📥 **Cipher Elite Join Requests**\n\n"
                "❌ **I could not read the queue.**\n"
                "💡 The group needs *Approve New Members* turned on, and I must "
                "be an admin with the *Add Users* right.\n"
                "🤖 **Powered by Cipher Elite**"
            ), []
        if not importers:
            return (
                "📥 **Cipher Elite Join Requests**\n\n"
                "✅ **Nobody is waiting for approval.**\n\n"
                "🤖 **Powered by Cipher Elite**"
            ), []

        lines = ["📥 **Cipher Elite Join Requests**\n",
                 f"🔢 **Waiting:** {len(importers)}\n"]
        for entry in importers[start:start + PAGE]:
            uid = getattr(entry, "user_id", None)
            about = (getattr(entry, "about", None) or "").strip()
            when = getattr(entry, "date", None)
            stamp = when.strftime("%d %b %H:%M") if when else ""
            extra = f" — {about[:40]}" if about else ""
            lines.append(f"  └ `{uid}` {stamp}{extra}")
        lines.append("\n💡 `/approve <id>` · `/deny <id>` · `/approverequests`")
        lines.append("🤖 **Powered by Cipher Elite**")
        return clip("\n".join(lines)), _buttons(importers, start)

    # -------------------------------------------------------------------------
    #  /requests
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/requests$"))
    async def requests_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        chat = await event.client.get_entity(event.chat_id)
        status = await event.reply("🔄 **Reading the queue...**")
        text, buttons = await _render(event, event.client, chat)
        try:
            if buttons:
                await event.client.send_message(event.chat_id, text, buttons=buttons)
            else:
                await event.client.send_message(event.chat_id, text)
        except Exception as e:
            await safe_edit(status, f"❌ **Could not post the queue:** `{str(e)[:140]}`")
            return
        await safe_edit(status, "✅ **Queue posted below.**")

    # -------------------------------------------------------------------------
    #  /approve <user|id>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/approve(?:\s+([\s\S]*))?$"))
    async def approve_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        reply = await event.get_reply_message()
        uid = None
        if arg.lstrip("-").isdigit():
            uid = int(arg)
        elif arg.startswith("@"):
            try:
                uid = (await event.client.get_entity(arg)).id
            except Exception:
                return await event.reply("❌ **Could not find that user.**")
        elif reply and reply.sender_id:
            uid = reply.sender_id

        if not uid:
            return await event.reply(
                "❌ **Give a user id or @username,** or reply to their request.\n"
                "💡 `/requests` lists everyone waiting\n"
                "🤖 **Powered by Cipher Elite**"
            )

        try:
            await event.client(HideChatJoinRequestRequest(
                peer=event.chat_id, user_id=uid, approved=True,
            ))
        except Exception as e:
            return await event.reply(
                f"❌ **Approve failed:** `{str(e)[:160]}`\n"
                "💡 The group needs *Approve New Members* on.\n"
                "🤖 **Powered by Cipher Elite**"
            )

        await event.reply(clip(
            "📥 **Cipher Elite Join Requests**\n\n"
            f"✅ **Approved** `{uid}`\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /deny <user|id>
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/deny(?:\s+([\s\S]*))?$"))
    async def deny_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        arg = (event.pattern_match.group(1) or "").strip()
        reply = await event.get_reply_message()
        uid = None
        if arg.lstrip("-").isdigit():
            uid = int(arg)
        elif arg.startswith("@"):
            try:
                uid = (await event.client.get_entity(arg)).id
            except Exception:
                return await event.reply("❌ **Could not find that user.**")
        elif reply and reply.sender_id:
            uid = reply.sender_id

        if not uid:
            return await event.reply(
                "❌ **Give a user id or @username.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        try:
            await event.client(HideChatJoinRequestRequest(
                peer=event.chat_id, user_id=uid, approved=False,
            ))
        except Exception as e:
            return await event.reply(f"❌ **Deny failed:** `{str(e)[:160]}`")

        await event.reply(clip(
            "📥 **Cipher Elite Join Requests**\n\n"
            f"❌ **Denied** `{uid}`\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  /approverequests — accept everyone
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/approverequests$"))
    async def approve_all_handler(event):
        if not group_only(event):
            return await event.reply("❌ **Use this inside a group.**")
        if not await require_admin(event, owner_id):
            return

        chat = await event.client.get_entity(event.chat_id)
        importers = await _pending(event.client, chat)
        if not importers:
            return await event.reply(
                "ℹ️ **Nobody is waiting for approval.**\n"
                "🤖 **Powered by Cipher Elite**"
            )

        status = await event.reply(f"🔄 **Approving {len(importers)} request(s)...**")
        try:
            await event.client(HideAllChatJoinRequestsRequest(
                peer=event.chat_id, approved=True, link=None,
            ))
            count = len(importers)
        except Exception:
            # fall back to approving one by one
            count = 0
            for entry in importers:
                uid = getattr(entry, "user_id", None)
                if uid is None:
                    continue
                try:
                    await event.client(HideChatJoinRequestRequest(
                        peer=event.chat_id, user_id=uid, approved=True,
                    ))
                    count += 1
                except Exception:
                    pass

        await safe_edit(status, clip(
            "📥 **Cipher Elite Join Requests**\n\n"
            f"✅ **Approved {count} request(s).**\n\n"
            "🤖 **Powered by Cipher Elite**"
        ))

    # -------------------------------------------------------------------------
    #  Buttons
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"^jr_ok_(\-?\d+)$"))
    async def jr_approve_button(event):
        if not await require_admin(event, owner_id):
            return await event.answer("🛑 Admins only.", alert=True)
        uid = int(event.pattern_match.group(1))
        try:
            await event.client(HideChatJoinRequestRequest(
                peer=event.chat_id, user_id=uid, approved=True,
            ))
        except Exception as e:
            return await event.answer(f"❌ {str(e)[:80]}", alert=True)
        await event.answer(f"✅ Approved {uid}", alert=True)
        try:
            await event.delete()
        except Exception:
            pass

    @bot.on(events.CallbackQuery(pattern=r"^jr_no_(\-?\d+)$"))
    async def jr_deny_button(event):
        if not await require_admin(event, owner_id):
            return await event.answer("🛑 Admins only.", alert=True)
        uid = int(event.pattern_match.group(1))
        try:
            await event.client(HideChatJoinRequestRequest(
                peer=event.chat_id, user_id=uid, approved=False,
            ))
        except Exception as e:
            return await event.answer(f"❌ {str(e)[:80]}", alert=True)
        await event.answer(f"❌ Denied {uid}", alert=True)
        try:
            await event.delete()
        except Exception:
            pass

    @bot.on(events.CallbackQuery(pattern=r"^jr_pg_(\-?\d+)$"))
    async def jr_page_button(event):
        if not await require_admin(event, owner_id):
            return await event.answer("🛑 Admins only.", alert=True)
        start = max(0, int(event.pattern_match.group(1)))
        chat = await event.client.get_entity(event.chat_id)
        text, buttons = await _render(event, event.client, chat, start)
        try:
            await event.edit(text, buttons=buttons)
        except Exception:
            await event.answer("Could not refresh the list.", alert=True)

    print("✅ Join Moderation Plugin: All handlers registered successfully")
