# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    info
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

from telethon import events
from telethon.tl.types import (
    UserStatusRecently, UserStatusOnline, UserStatusOffline,
    UserStatusLastWeek, UserStatusLastMonth, Channel, Chat, User
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from datetime import datetime, timedelta, timezone
import html

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler


# ─────────────────────────────────────────────────────────────────────────────
# 📚  Command registration
# ─────────────────────────────────────────────────────────────────────────────
def init(client_instance):
    commands = [
        ".info <username / user_id / reply>   - Show detailed Telegram user profile",
        ".chatinfo <chat_username / chat_id>  - Show detailed group or channel info"
    ]
    description = (
        "Advanced Telegram information commands.\n\n"
        "🧩  Example usage:\n"
        "    •  Reply to a message and send `.info` to inspect that user.\n"
        "    •  Send `.chatinfo` in any group to analyse that group.\n"
    )
    add_handler("info", commands, description)


# ─────────────────────────────────────────────────────────────────────────────
# 🛠  Helper functions
# ─────────────────────────────────────────────────────────────────────────────
def format_account_age(creation_date):
    if not creation_date:
        return "Unknown"
    if creation_date.tzinfo is None:
        creation_date = creation_date.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    age = now - creation_date
    years, rem_days = divmod(age.days, 365)
    months, days = divmod(rem_days, 30)
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years > 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months > 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    return ", ".join(parts) or "Just created"


def format_online_status(user: User):
    if not hasattr(user, 'status'):
        return "⚫ Status Unknown"

    status_map = {
        UserStatusOnline: "🟢 Online now",
        UserStatusRecently: "🟢 Recently online",
        UserStatusLastWeek: "🟠 Active this week",
        UserStatusLastMonth: "🔴 Active this month",
        UserStatusOffline: "⚫ Offline"
    }

    status_type = type(user.status)
    text = status_map.get(status_type, "⚫ Status Unknown")

    if status_type is UserStatusOffline and hasattr(user.status, 'was_online'):
        diff = datetime.now(timezone.utc) - user.status.was_online
        if diff < timedelta(minutes=1):
            return "🟢 Just now"
        if diff < timedelta(hours=1):
            return f"🟢 {diff.seconds // 60} min ago"
        if diff < timedelta(days=1):
            return f"🟠 {diff.seconds // 3600} h ago"
        return f"🔴 {diff.days} d ago"

    return text


def safe(text: str | None) -> str:
    return html.escape(text or "")


# ─────────────────────────────────────────────────────────────────────────────
# 👤  .info / .whois  (user analysis)
# ─────────────────────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.(?:whois|info)(?:\s|$)"))
@rishabh()
async def info_command(event):
    await event.delete()

    # Identify target user
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user = await event.client.get_entity(reply.sender_id)
    else:
        parts = event.text.split(maxsplit=1)
        if len(parts) == 2:
            user = await event.client.get_entity(parts[1])
        else:
            return await event.respond("❌ Please supply a username, ID, or reply to a user!")

    full = await event.client(GetFullUserRequest(user.id))
    photos = await event.client.get_profile_photos(user, limit=1)
    mutual = len(await event.client.get_common_chats(user.id))

    text = (
        "👤 <b>TELEGRAM USER ANALYSIS</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Name: {safe(user.first_name)} {safe(user.last_name)}\n"
        f"🔖 Username: @{safe(user.username) if user.username else 'N/A'}\n\n"
        "📊 <b>ACCOUNT STATUS</b>\n"
        f"{format_online_status(user)}\n"
        f"📅 Account age: {format_account_age(getattr(user, 'date', None))}\n"
        f"🤖 Is bot: {'✅' if user.bot else '❌'}\n"
        f"✅ Verified: {'✅' if user.verified else '❌'}\n"
        f"🚫 Restricted: {'✅' if getattr(user, 'restricted', False) else '❌'}\n\n"
        "📈 <b>ACTIVITY</b>\n"
        f"📸 Profile photos: {len(await event.client.get_profile_photos(user))}\n"
        f"👥 Mutual groups: {mutual}\n"
    )

    if full.full_user.about:
        text += f"\n📝 <b>BIO</b>\n{safe(full.full_user.about)}"

    if photos:
        await event.client.send_file(event.chat_id, photos[0], caption=text, parse_mode='html')
    else:
        await event.respond(text, parse_mode='html')


# ─────────────────────────────────────────────────────────────────────────────
# 👥  .chatinfo  (group / channel analysis)
# ─────────────────────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.chatinfo(?:\s|$)(.*)"))
@rishabh()
async def chatinfo_command(event):
    await event.delete()

    arg = event.pattern_match.group(1).strip()
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        entity = await event.client.get_entity(reply.to_id)
    elif arg:
        entity = await event.client.get_entity(arg)
    else:
        entity = await event.client.get_entity(event.chat_id)

    if not isinstance(entity, (Channel, Chat)):
        return await event.respond("❌ Target is not a group or channel!")

    full = (await event.client(GetFullChannelRequest(entity))
            if isinstance(entity, Channel)
            else await event.client(GetFullChatRequest(entity.id)))

    # Participant count
    try:
        members = len(await event.client.get_participants(entity, limit=0))
    except Exception:
        members = "Unknown"

    text = (
        "👥 <b>TELEGRAM GROUP ANALYSIS</b>\n\n"
        f"📛 Title: {safe(entity.title)}\n"
        f"🆔 ID: <code>{entity.id}</code>\n"
        f"🔗 Invite: {'https://t.me/' + entity.username if entity.username else 'N/A'}\n\n"
        "📊 <b>STATS</b>\n"
        f"👥 Members: {members}\n"
        f"📢 Type: {'Channel' if getattr(entity, 'broadcast', False) else 'Group'}\n"
        f"🔐 Visibility: {'Public' if entity.username else 'Private'}\n"
        f"✅ Verified: {'✅' if getattr(entity, 'verified', False) else '❌'}\n"
        f"💬 Scam: {'✅' if getattr(entity, 'scam', False) else '❌'}"
    )

    if full.full_chat.about:
        text += f"\n\n📝 <b>Description</b>\n{safe(full.full_chat.about)}"

    await event.respond(text, parse_mode='html')

