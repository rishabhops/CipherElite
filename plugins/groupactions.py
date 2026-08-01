# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    groupactions
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  Commands:       .kickme
#                  .kickall
#                  .banall
#                  .unbanall
#                  .zombies
# =============================================================================

from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import (
    ChatBannedRights,
    ChannelParticipantsAdmins,
    ChannelParticipantsBanned,
    ChannelParticipantsKicked,
    UserStatusEmpty,
)
from telethon.errors import FloodWaitError, ChatAdminRequiredError, UserAdminInvalidError
from asyncio import sleep
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "admin"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(until_date=None, view_messages=False)

def init(client_instance):
    commands = [
        ".kickme - Leave the group",
        ".kickall - Kick all non-admin members",
        ".banall - Ban all non-admin members",
        ".unbanall - Unban all banned users",
        ".zombies - Kick deleted accounts"
    ]
    description = "Bulk group actions for mass member management"
    add_handler("groupactions", commands, description)

async def _get_admin_ids(client, chat_id):
    admins = []
    try:
        async for p in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
            admins.append(p.id)
    except Exception:
        pass
    return admins

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.kickme"))
    @rishabh()
    async def kickme(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups/channels!")
            return
        try:
            await event.client.kick_participant(event.chat_id, "me")
        except Exception as e:
            await event.reply(f"❌ Failed to leave: `{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.kickall"))
    @rishabh()
    async def kickall(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups/channels!")
            return
        msg = await event.reply("👢 **Kicking all non-admin members...**")
        admin_ids = await _get_admin_ids(event.client, event.chat_id)
        total = 0
        success = 0
        failed = 0
        async for user in event.client.iter_participants(event.chat_id):
            total += 1
            if user.id in admin_ids or user.is_self:
                continue
            try:
                await event.client.kick_participant(event.chat_id, user.id)
                success += 1
                await sleep(0.5)
            except FloodWaitError as e:
                await sleep(e.seconds)
            except Exception:
                failed += 1
        await msg.edit(f"✅ **Kickall complete**\n\n👥 Total: `{total}`\n👢 Kicked: `{success}`\n❌ Failed: `{failed}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.banall"))
    @rishabh()
    async def banall(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups/channels!")
            return
        msg = await event.reply("🚫 **Banning all non-admin members...**")
        admin_ids = await _get_admin_ids(event.client, event.chat_id)
        total = 0
        success = 0
        failed = 0
        async for user in event.client.iter_participants(event.chat_id):
            total += 1
            if user.id in admin_ids or user.is_self:
                continue
            try:
                await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
                success += 1
                await sleep(0.5)
            except FloodWaitError as e:
                await sleep(e.seconds)
            except Exception:
                failed += 1
        await msg.edit(f"✅ **Banall complete**\n\n👥 Total: `{total}`\n🚫 Banned: `{success}`\n❌ Failed: `{failed}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.unbanall"))
    @rishabh()
    async def unbanall(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups/channels!")
            return
        msg = await event.reply("✅ **Unbanning all banned users...**")
        success = 0
        failed = 0
        try:
            async for user in event.client.iter_participants(event.chat_id, filter=ChannelParticipantsBanned):
                try:
                    await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
                    success += 1
                    await sleep(0.5)
                except Exception:
                    failed += 1
        except Exception as e:
            await msg.edit(f"⚠️ Error reading banned users: `{str(e)}`")
            return
        await msg.edit(f"✅ **Unbanall complete**\n\n🔓 Unbanned: `{success}`\n❌ Failed: `{failed}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.zombies"))
    @rishabh()
    async def zombies(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups/channels!")
            return
        msg = await event.reply("🧟 **Searching for deleted accounts...**")
        success = 0
        failed = 0
        async for user in event.client.iter_participants(event.chat_id):
            if user.deleted:
                try:
                    await event.client.kick_participant(event.chat_id, user.id)
                    success += 1
                    await sleep(0.5)
                except Exception:
                    failed += 1
        await msg.edit(f"✅ **Zombies cleaned**\n\n🧟 Kicked deleted accounts: `{success}`\n❌ Failed: `{failed}`")
