# =============================================================================
#  CipherElite Userbot Plugin
#  Plugin Name:    infos
#  Description:    Group & user information commands: info, chatinfo, users, admins, bots, id, recognize
#  Created:        18/07/2026
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "utilities"

import html
import os
from datetime import datetime
from math import sqrt

from telethon import events
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
    ChatAdminRequiredError,
    MessageTooLongError,
    YouBlockedUserError,
)
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetFullChatRequest, GetHistoryRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    MessageActionChannelMigrateFrom,
    MessageEntityMentionName,
)
from telethon.utils import pack_bot_file_id, get_input_location

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler


def init(client_instance):
    commands = [
        ".info <reply/username> - Get basic public info about a user",
        ".chatinfo <chat> - Get full chat/group/channel info",
        ".users <search> - List all users in group (optional search)",
        ".admins - List admins in current group",
        ".bots - List bots in current group",
        ".id <reply> - Get chat/user/photo file ID",
        ".recognize <reply to photo> - Recognize media using @Rekognition_Bot",
    ]
    description = "🔍 User & Group Info toolkit"
    add_handler("infos", commands, description)


# ─── Helper: get full user (new version) ──────────────────────────────────
async def get_full_user(event):
    """Return (UserFull, None) or (None, error_message)."""
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        target_id = (
            previous_message.forward.sender_id or previous_message.forward.channel_id
            if previous_message.forward
            else previous_message.sender_id
        )
        return await event.client(GetFullUserRequest(target_id)), None

    input_str = None
    try:
        input_str = event.pattern_match.group(1)
    except IndexError:
        return None, "No input provided"

    if not input_str or not input_str.strip():
        return None, "Please provide a username or reply to a user's message."

    if event.message.entities:
        for entity in event.message.entities:
            if isinstance(entity, MessageEntityMentionName):
                return await event.client(GetFullUserRequest(entity.user_id)), None

    try:
        if input_str.lstrip("+").isdigit():
            return await event.client(GetFullUserRequest(int(input_str))), None
        user_object = await event.client.get_entity(input_str)
        return await event.client(GetFullUserRequest(user_object.id)), None
    except Exception as e:
        return None, str(e)


# ─── Helper: get chat info ──────────────────────────────────────────────────
async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except Exception:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            return None, "Invalid channel/group"
        except ChannelPrivateError:
            return None, "This is a private channel/group or I am banned from there"
        except ChannelPublicGroupNaError:
            return None, "Channel or supergroup doesn't exist"
        except (TypeError, ValueError) as err:
            return None, str(err)
    return chat_info, None


# ─── Helper: fetch chat info text (plain text, no HTML) ──────────────────
async def fetch_info(chat, event):
    chat_obj_info = await event.client.get_entity(chat.full_chat.id)
    broadcast = (
        chat_obj_info.broadcast if hasattr(chat_obj_info, "broadcast") else False
    )
    chat_type = "Channel" if broadcast else "Group"
    chat_title = chat_obj_info.title
    warn_emoji = "⚠️"
    try:
        msg_info = await event.client(
            GetHistoryRequest(
                peer=chat_obj_info.id,
                offset_id=0,
                offset_date=datetime(2010, 1, 1),
                add_offset=-1,
                limit=1,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
    except Exception:
        msg_info = None
    first_msg_valid = (
        True
        if msg_info and msg_info.messages and msg_info.messages[0].id == 1
        else False
    )
    creator_valid = True if first_msg_valid and msg_info.users else False
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = (
        msg_info.users[0].first_name
        if creator_valid and msg_info.users[0].first_name is not None
        else "Deleted Account"
    )
    creator_username = (
        msg_info.users[0].username
        if creator_valid and msg_info.users[0].username is not None
        else None
    )
    created = msg_info.messages[0].date if first_msg_valid else None
    former_title = (
        msg_info.messages[0].action.title
        if first_msg_valid
        and type(msg_info.messages[0].action) is MessageActionChannelMigrateFrom
        and msg_info.messages[0].action.title != chat_title
        else None
    )
    try:
        dc_id, location = get_input_location(chat.full_chat.chat_photo)
    except Exception:
        dc_id = "Unknown"

    description = chat.full_chat.about
    members = (
        chat.full_chat.participants_count
        if hasattr(chat.full_chat, "participants_count")
        else chat_obj_info.participants_count
    )
    admins = (
        chat.full_chat.admins_count if hasattr(chat.full_chat, "admins_count") else None
    )
    banned_users = (
        chat.full_chat.kicked_count if hasattr(chat.full_chat, "kicked_count") else None
    )
    restrcited_users = (
        chat.full_chat.banned_count if hasattr(chat.full_chat, "banned_count") else None
    )
    members_online = (
        chat.full_chat.online_count if hasattr(chat.full_chat, "online_count") else 0
    )
    group_stickers = (
        chat.full_chat.stickerset.title
        if hasattr(chat.full_chat, "stickerset") and chat.full_chat.stickerset
        else None
    )
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = (
        chat.full_chat.read_inbox_max_id
        if hasattr(chat.full_chat, "read_inbox_max_id")
        else None
    )
    messages_sent_alt = (
        chat.full_chat.read_outbox_max_id
        if hasattr(chat.full_chat, "read_outbox_max_id")
        else None
    )
    exp_count = chat.full_chat.pts if hasattr(chat.full_chat, "pts") else None
    username = chat_obj_info.username if hasattr(chat_obj_info, "username") else None
    bots_list = chat.full_chat.bot_info
    bots = 0
    supergroup = (
        "Yes" if hasattr(chat_obj_info, "megagroup") and chat_obj_info.megagroup else "No"
    )
    slowmode = (
        "Yes"
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled
        else "No"
    )
    slowmode_time = (
        chat.full_chat.slowmode_seconds
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled
        else None
    )
    restricted = (
        "Yes" if hasattr(chat_obj_info, "restricted") and chat_obj_info.restricted else "No"
    )
    verified = (
        "Yes" if hasattr(chat_obj_info, "verified") and chat_obj_info.verified else "No"
    )
    username = f"@{username}" if username else None
    creator_username = f"@{creator_username}" if creator_username else None

    if admins is None:
        try:
            participants_admins = await event.client(
                GetParticipantsRequest(
                    channel=chat.full_chat.id,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=0,
                    hash=0,
                )
            )
            admins = participants_admins.count if participants_admins else None
        except Exception:
            pass
    if bots_list:
        for bot in bots_list:
            bots += 1

    # Build plain text (no HTML)
    caption = "🔰 CHAT INFO 🔰\n"
    caption += f"🆔 ID : {chat_obj_info.id}\n"
    if chat_title is not None:
        caption += f"🚀 {chat_type} Name : {chat_title}\n"
    if former_title is not None:
        caption += f"✳️ Former name : {former_title}\n"
    if username is not None:
        caption += f"🔸 {chat_type} type : Public\n"
        caption += f"Link : {username}\n"
    else:
        caption += f"🔸 {chat_type} type : Private\n"
    if creator_username is not None:
        caption += f"👑 Creator : {creator_username}\n"
    elif creator_valid:
        caption += f"👑 Creator : {creator_firstname} (ID: {creator_id})\n"
    if created is not None:
        caption += f"🆕 Created : {created.date().strftime('%b %d, %Y')} - {created.time()}\n"
    else:
        caption += f"🆕 Created : {chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()} {warn_emoji}\n"
    caption += f"🌐 DataCentre ID : {dc_id}\n"
    if exp_count is not None:
        chat_level = int((1 + sqrt(1 + 7 * exp_count / 14)) / 2)
        caption += f"🔅 {chat_type} level : {chat_level}\n"
    if messages_viewable is not None:
        caption += f"🗨️ Viewable messages : {messages_viewable}\n"
    if messages_sent:
        caption += f"💬 Messages sent : {messages_sent}\n"
    elif messages_sent_alt:
        caption += f"💬 Messages sent : {messages_sent_alt} {warn_emoji}\n"
    if members is not None:
        caption += f"👪 Members : {members}\n"
    if admins is not None:
        caption += f"⚜️ Administrators : {admins}\n"
    if bots_list:
        caption += f"🤖 Bots : {bots}\n"
    if members_online:
        caption += f"👨‍💻 Currently online : {members_online}\n"
    if restrcited_users is not None:
        caption += f"🚫 Restricted users : {restrcited_users}\n"
    if banned_users is not None:
        caption += f"❌ Banned users : {banned_users}\n"
    if group_stickers is not None:
        caption += f'😋 {chat_type} stickers : https://t.me/addstickers/{chat.full_chat.stickerset.short_name}\n'
    caption += "\n"
    if not broadcast:
        caption += f"🐢 Slow mode : {slowmode}"
        if slowmode == "Yes" and slowmode_time is not None:
            caption += f", {slowmode_time}s\n\n"
        else:
            caption += "\n\n"
    if not broadcast:
        caption += f"🏬 Supergroup : {supergroup}\n\n"
    if hasattr(chat_obj_info, "restricted"):
        caption += f"⚠️ Restricted : {restricted}\n"
        if chat_obj_info.restricted:
            caption += f"> Platform: {chat_obj_info.restriction_reason[0].platform}\n"
            caption += f"> Reason: {chat_obj_info.restriction_reason[0].reason}\n"
            caption += f"> Text: {chat_obj_info.restriction_reason[0].text}\n\n"
        else:
            caption += "\n"
    if hasattr(chat_obj_info, "scam") and chat_obj_info.scam:
        caption += "📍 Scam : Yes\n\n"
    if hasattr(chat_obj_info, "verified"):
        caption += f"💟 Verified by Telegram : {verified}\n\n"
    if description:
        caption += f"📝 Description : \n{description}\n"
    return caption


# ─── COMMANDS ──────────────────────────────────────────────────────────────

# ─── info (new version, plain text) ─────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.info(?:\s|$)([\s\S]*)"))
@rishabh()
async def info_cmd(event):
    try:
        replied_user, error = await get_full_user(event)
        if replied_user is None:
            await event.reply(f"❌ Error: {error}")
            return

        # replied_user is UserFull; get the first user from .users list
        user = replied_user.users[0] if replied_user.users else None
        if user is None:
            await event.reply("❌ Error: Could not fetch user object.")
            return

        first_name = user.first_name or ""
        first_name = first_name.replace("\u2060", "")
        last_name = user.last_name if user.last_name else "Not set"
        last_name = last_name.replace("\u2060", "")
        bio = replied_user.about if replied_user.about else "No bio"
        common_chats = getattr(replied_user, "common_chats_count", 0)

        # Get profile photo if available
        profile_photo = user.photo if hasattr(user, "photo") else None

        caption = (
            "User Info\n\n"
            f"🆔 User ID: {user.id}\n"
            f"🔗 Profile: tg://user?id={user.id}\n"
            f"🗣️ First Name: {first_name}\n"
            f"🗣️ Last Name: {last_name}\n"
            f"📝 Bio: {bio}\n"
            f"🧐 Restricted: {user.restricted}\n"
            f"✅ Verified: {user.verified}\n"
            f"🤖 Bot: {user.bot}\n"
            f"👥 Groups in Common: {common_chats}\n"
        )

        await event.delete()
        await event.client.send_message(
            event.chat_id,
            caption,
            reply_to=event.reply_to_msg_id or event.id,
            file=profile_photo,
            force_document=False,
        )
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")


# ─── chatinfo ──────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.chatinfo(?:\s|$)([\s\S]*)"))
@rishabh()
async def chatinfo_cmd(event):
    try:
        status = await event.reply("🔍 Analysing the chat...")
        chat, error = await get_chatinfo(event)
        if error:
            await status.edit(f"❌ {error}")
            return
        caption = await fetch_info(chat, event)
        await status.edit(caption)
        await event.delete()
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")


# ─── users ──────────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.users(?:\s|$)([\s\S]*)"))
@rishabh()
async def users_cmd(event):
    try:
        if not event.is_group:
            await event.reply("❌ This command works only in groups.")
            return
        info = await event.client.get_entity(event.chat_id)
        title = info.title if info.title else "this chat"
        mentions = f"Users in {title}:\n"
        searchq = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
        try:
            async for user in event.client.iter_participants(event.chat_id, search=searchq):
                if not user.deleted:
                    mentions += f"\n{user.first_name} (ID: {user.id})"
                else:
                    mentions += f"\nDeleted Account (ID: {user.id})"
        except ChatAdminRequiredError as err:
            mentions += f" {str(err)}\n"

        await event.delete()
        try:
            await event.reply(mentions)
        except MessageTooLongError:
            file_path = "userslist.txt"
            with open(file_path, "w+") as f:
                f.write(mentions)
            await event.client.send_file(
                event.chat_id,
                file_path,
                caption=f"Users in {title}",
                reply_to=event.reply_to_msg_id or event.id,
            )
            os.remove(file_path)
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")


# ─── admins ─────────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.admins(?:\s|$)([\s\S]*)"))
@rishabh()
async def admins_cmd(event):
    try:
        if not event.is_group:
            await event.reply("❌ This command works only in groups.")
            return
        mentions = "⚜️ Admins in this Group:\n"
        input_str = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else None
        if input_str:
            try:
                chat = await event.client.get_entity(input_str)
                mentions = f"Admins in {input_str} Group:\n"
            except Exception as e:
                await event.reply(f"❌ {str(e)}")
                return
        else:
            chat = event.chat_id

        try:
            async for x in event.client.iter_participants(chat, filter=ChannelParticipantsAdmins):
                if not x.deleted and isinstance(x.participant, ChannelParticipantCreator):
                    mentions += f"\n 🔰 {x.first_name} (ID: {x.id})"
            mentions += "\n"
            async for x in event.client.iter_participants(chat, filter=ChannelParticipantsAdmins):
                if x.deleted:
                    mentions += f"\n Deleted Account (ID: {x.id})"
                else:
                    if isinstance(x.participant, ChannelParticipantAdmin):
                        mentions += f"\n 🔸 {x.first_name} (ID: {x.id})"
        except Exception as e:
            mentions += f" {str(e)}\n"

        await event.delete()
        await event.reply(mentions)
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")


# ─── bots ───────────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.bots(?:\s|$)([\s\S]*)"))
@rishabh()
async def bots_cmd(event):
    try:
        if not event.is_group:
            await event.reply("❌ This command works only in groups.")
            return
        mentions = "🤖 Bots in this Group:\n"
        input_str = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else None
        if input_str:
            try:
                chat = await event.client.get_entity(input_str)
                mentions = f"Bots in {input_str} group:\n"
            except Exception as e:
                await event.reply(f"❌ {str(e)}")
                return
        else:
            chat = event.chat_id

        try:
            async for x in event.client.iter_participants(chat, filter=ChannelParticipantsBots):
                if isinstance(x.participant, ChannelParticipantAdmin):
                    mentions += f"\n ⚜️ {x.first_name} (ID: {x.id})"
                else:
                    mentions += f"\n {x.first_name} (ID: {x.id})"
        except Exception as e:
            mentions += f" {str(e)}\n"

        await event.delete()
        await event.reply(mentions)
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")


# ─── id ─────────────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.id$"))
@rishabh()
async def id_cmd(event):
    try:
        status = await event.reply("🔍 Fetching IDs...")
        if event.reply_to_msg_id:
            r_msg = await event.get_reply_message()
            if r_msg.media:
                bot_api_file_id = pack_bot_file_id(r_msg.media)
                await status.edit(
                    f"🔸 Current Chat ID: {event.chat_id}\n\n"
                    f"🔰 From User ID: {r_msg.sender_id}\n\n"
                    f"🤖 Bot API File ID: {bot_api_file_id}"
                )
            else:
                await status.edit(
                    f"🔸 Current Chat ID: {event.chat_id}\n\n"
                    f"🔰 From User ID: {r_msg.sender_id}"
                )
        else:
            await status.edit(f"🔸 Current Chat ID: {event.chat_id}")
        await event.delete()
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")


# ─── recognize ──────────────────────────────────────────────────────────────
@CipherElite.on(events.NewMessage(pattern=r"\.recognize$"))
@rishabh()
async def recognize_cmd(event):
    try:
        if not event.reply_to_msg_id:
            await event.reply("❌ Reply to a media message.")
            return
        reply_message = await event.get_reply_message()
        if not reply_message.media:
            await event.reply("❌ Reply to a media file.")
            return
        if reply_message.sender and reply_message.sender.bot:
            await event.reply("❌ Reply to a user's media, not a bot.")
            return

        status = await event.reply("🔍 Recognizing this media...")
        chat = "@Rekognition_Bot"
        async with event.client.conversation(chat) as conv:
            try:
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=461083923))
                first = await event.client.forward_messages(chat, reply_message)
                second = await response
            except YouBlockedUserError:
                await status.edit("❌ Unblock @Rekognition_Bot and try again.")
                return

            if second.text.startswith("See next message."):
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=461083923))
                third = await response
                result = third.message.message
                await event.reply(result)
                await event.client.delete_messages(conv.chat_id, [first.id, second.id, third.id])
            else:
                await status.edit("❌ Sorry, I couldn't find that.")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")