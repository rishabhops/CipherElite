# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    invite
#  Description:    Invite users from one group to another with progress bar
#  Created:        25/07/2026
# =============================================================================

import re
import asyncio
from telethon import events
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
    UserPrivacyRestrictedError,
    UserNotMutualContactError,
    FloodWaitError,
)
from telethon.tl import functions
from telethon.tl.functions.channels import GetFullChannelRequest, InviteToChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest, AddChatUserRequest

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler


def init(client_instance):
    commands = [
        ".inviteall <group username/link> - Invite all members from a group to current chat",
        ".add <username/id> - Add a single user to current chat",
    ]
    description = "👥 CipherElite Invite – Bulk user inviter"
    add_handler("inviteall", commands, description)


# ─── Helper: get chat info ──────────────────────────────────────────────────
async def get_chatinfo(event, chat_input):
    """Get chat info from username, link, or ID."""
    chat_info = None
    if chat_input:
        # Try to extract username from link
        link_match = re.search(r"(?:https?://)?t\.me/([a-zA-Z0-9_]+)", chat_input)
        if link_match:
            chat_input = link_match.group(1)
        try:
            chat_input = int(chat_input)
        except ValueError:
            pass
    else:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat_input = replied_msg.fwd_from.channel_id
        else:
            chat_input = event.chat_id

    try:
        chat_info = await event.client(GetFullChatRequest(chat_input))
    except Exception:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat_input))
        except ChannelInvalidError:
            return None, "Invalid channel/group"
        except ChannelPrivateError:
            return None, "This is a private channel/group or I am banned from there"
        except ChannelPublicGroupNaError:
            return None, "Channel or supergroup doesn't exist"
        except (TypeError, ValueError):
            return None, "Invalid channel/group"
    return chat_info, None


def create_progress_bar(current, total, length=20):
    """Create a visual progress bar."""
    if total == 0:
        return "[" + "░" * length + "] 0%"
    progress = current / total
    filled = int(progress * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {int(progress * 100)}%"


async def register_commands():

    # ─── INVITEALL ───────────────────────────────────────────────────────────
    @CipherElite.on(events.NewMessage(pattern=r"\.inviteall(?:\s+(.+))?"))
    @rishabh()
    async def inviteall_cmd(event):
        try:
            chat_input = event.pattern_match.group(1)
            if not chat_input:
                await event.reply("❌ **Usage:** `.inviteall <group username or link>`\nExample: `.inviteall @CipherElite`")
                return

            # Get target group info
            status = await event.reply(f"🔍 Fetching members from `{chat_input}`...")
            target_chat, error = await get_chatinfo(event, chat_input)
            if error:
                await status.edit(f"❌ {error}")
                return

            # Get current chat
            current_chat = await event.get_chat()
            if event.is_private:
                await status.edit("❌ This command must be used in a group, not a private chat.")
                return

            # Count members
            await status.edit("📊 Counting members...")
            members = []
            try:
                async for user in event.client.iter_participants(target_chat.full_chat.id):
                    if not user.deleted and not user.bot:
                        members.append(user.id)
            except Exception as e:
                await status.edit(f"❌ Error fetching members: {str(e)}")
                return

            if not members:
                await status.edit("❌ No members found in the target group.")
                return

            total = len(members)
            await status.edit(f"👥 Found **{total}** members. Starting invitation...\n\n{create_progress_bar(0, total)}")

            invited = 0
            failed = 0
            errors = []

            for i, user_id in enumerate(members, 1):
                try:
                    if current_chat.is_channel or current_chat.is_supergroup:
                        await event.client(
                            InviteToChannelRequest(
                                channel=current_chat.id,
                                users=[user_id]
                            )
                        )
                    else:
                        await event.client(
                            AddChatUserRequest(
                                chat_id=current_chat.id,
                                user_id=user_id,
                                fwd_limit=1000000
                            )
                        )
                    invited += 1
                except FloodWaitError as e:
                    await status.edit(f"⏳ Flood wait: {e.seconds}s. Waiting...")
                    await asyncio.sleep(e.seconds)
                    continue
                except UserPrivacyRestrictedError:
                    failed += 1
                    errors.append("Privacy restricted")
                except UserNotMutualContactError:
                    failed += 1
                    errors.append("Not mutual contact")
                except Exception as e:
                    failed += 1
                    errors.append(str(e)[:50])

                # Update progress bar every 5 users
                if i % 5 == 0 or i == total:
                    bar = create_progress_bar(i, total)
                    error_sample = errors[0] if errors else "None"
                    await status.edit(
                        f"👥 **Inviting Members**\n"
                        f"📊 Progress: {bar}\n\n"
                        f"✅ Invited: **{invited}**\n"
                        f"❌ Failed: **{failed}**\n"
                        f"⏳ Processed: {i}/{total}\n"
                        f"⚠️ Last Error: `{error_sample}`"
                    )

            # Final result
            result_msg = (
                f"✅ **Invitation Complete!**\n\n"
                f"📊 Total Members: **{total}**\n"
                f"✅ Invited: **{invited}**\n"
                f"❌ Failed: **{failed}**\n"
                f"📍 Target: `{chat_input}`\n"
                f"🏠 Current Chat: **{current_chat.title or 'Group'}**"
            )
            if errors:
                unique_errors = list(set(errors))[:3]
                result_msg += f"\n\n⚠️ **Common Errors:**\n" + "\n".join(f"• {e}" for e in unique_errors)

            await status.edit(result_msg)

        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    # ─── ADD ──────────────────────────────────────────────────────────────────
    @CipherElite.on(events.NewMessage(pattern=r"\.add(?:\s+(.+))?"))
    @rishabh()
    async def add_cmd(event):
        try:
            if "addsudo" in event.raw_text.lower() or "addblacklist" in event.raw_text.lower():
                return

            if event.is_private:
                await event.reply("❌ This command must be used in a group, not a private chat.")
                return

            users_input = event.pattern_match.group(1)
            if not users_input:
                await event.reply("❌ **Usage:** `.add <username or ID>`")
                return

            current_chat = await event.get_chat()
            status = await event.reply(f"➕ Adding users to **{current_chat.title or 'Group'}**...")

            added = 0
            failed = 0
            user_ids = users_input.split()

            for user_input in user_ids:
                try:
                    user_input = user_input.strip()
                    # Try to get entity
                    try:
                        entity = await event.client.get_entity(user_input)
                    except Exception:
                        failed += 1
                        continue

                    if current_chat.is_channel or current_chat.is_supergroup:
                        await event.client(
                            InviteToChannelRequest(
                                channel=current_chat.id,
                                users=[entity.id]
                            )
                        )
                    else:
                        await event.client(
                            AddChatUserRequest(
                                chat_id=current_chat.id,
                                user_id=entity.id,
                                fwd_limit=1000000
                            )
                        )
                    added += 1
                    await status.edit(f"➕ Added: **{added}** | ❌ Failed: **{failed}**")
                except FloodWaitError as e:
                    await status.edit(f"⏳ Flood wait: {e.seconds}s. Waiting...")
                    await asyncio.sleep(e.seconds)
                except Exception:
                    failed += 1

            await status.edit(
                f"✅ **Add Complete!**\n\n"
                f"➕ Added: **{added}**\n"
                f"❌ Failed: **{failed}**\n"
                f"🏠 Chat: **{current_chat.title or 'Group'}**"
            )
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")
