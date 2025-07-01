from telethon import events
from telethon.tl.functions.channels import GetAdminedPublicChannelsRequest
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import time
import asyncio
from datetime import timedelta

def init(client_instance):
    """
    Initialize the statistics plugin with command descriptions.
    """
    commands = [
        ".count - Quick overview of chat counts with progress animation",
        ".stats - Detailed chat statistics with progress animation",
        ".reserved - List admin-reserved public usernames with loading animation"
    ]
    description = "Statistics plugin for chat counts and reserved usernames"
    add_handler("statistics", commands, description)

def format_time(seconds):
    """Convert seconds to a human-readable time string."""
    delta = timedelta(seconds=int(seconds))
    if delta.total_seconds() < 60:
        return f"{delta.seconds}s"
    minutes, seconds = divmod(delta.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.count$"))
    @rishabh()
    async def count_stats(event):
        """
        .count — Quick overview of chat counts with a progress animation.
        """
        try:
            me = await event.client.get_me()
            mention = f"[{me.first_name}](tg://user?id={me.id})"
            dialogs = [d async for d in event.client.iter_dialogs()]
            total = len(dialogs)
            msg = await event.reply(f"🔍 Counting chats… 0/{total}")

            bots = users = groups = super_groups = channels = 0
            step = max(1, total // 10)

            for idx, dialog in enumerate(dialogs, start=1):
                if dialog.is_user:
                    if getattr(dialog.entity, "bot", False):
                        bots += 1
                    else:
                        users += 1
                elif dialog.is_group and not getattr(dialog.entity, "megagroup", False):
                    groups += 1
                elif getattr(dialog.entity, "megagroup", False):
                    super_groups += 1
                elif dialog.is_channel and not getattr(dialog.entity, "megagroup", False):
                    channels += 1

                if idx % step == 0 or idx == total:
                    await msg.edit(f"🔍 Counting chats… {idx}/{total}")
                    await asyncio.sleep(0.15)

            overall = bots + users + groups + super_groups + channels
            text = (
                f"📊 **{mention}'s Chat Stats**\n\n"
                f"👤 **Users**: {users}\n"
                f"🤖 **Bots**: {bots}\n"
                f"👥 **Groups**: {groups}\n"
                f"🏛 **Supergroups**: {super_groups}\n"
                f"📢 **Channels**: {channels}\n\n"
                f"🌐 **Total Chats**: {overall}"
            )
            await msg.edit(text)
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.stats$"))
    @rishabh()
    async def detailed_stats(event):
        """
        .stats — Detailed chat statistics with progress animation.
        """
        try:
            me = await event.client.get_me()
            mention = f"[{me.first_name}](tg://user?id={me.id})"
            dialogs = [d async for d in event.client.iter_dialogs()]
            total = len(dialogs)
            msg = await event.reply(f"📈 Collecting stats… 0/{total}")

            start = time.time()
            bots = users = groups = super_groups = channels = 0
            unread_msg = unread_mention = 0
            step = max(1, total // 10)

            for idx, dialog in enumerate(dialogs, start=1):
                if dialog.is_user:
                    if getattr(dialog.entity, "bot", False):
                        bots += 1
                    else:
                        users += 1
                elif dialog.is_group and not getattr(dialog.entity, "megagroup", False):
                    groups += 1
                elif getattr(dialog.entity, "megagroup", False):
                    super_groups += 1
                elif dialog.is_channel and not getattr(dialog.entity, "megagroup", False):
                    channels += 1

                unread_msg += getattr(dialog, "unread_count", 0)
                unread_mention += getattr(dialog, "unread_mentions", 0)

                if idx % step == 0 or idx == total:
                    await msg.edit(f"📈 Collecting stats… {idx}/{total}")
                    await asyncio.sleep(0.15)

            duration = format_time(time.time() - start)
            text = (
                f"📊 **{mention}'s Detailed Stats**\n\n"
                f"**🔗 Chats Overview**\n"
                f"👤 Users: {users}\n"
                f"🤖 Bots: {bots}\n"
                f"👥 Groups: {groups}\n"
                f"🏛 Supergroups: {super_groups}\n"
                f"📢 Channels: {channels}\n\n"
                f"**📬 Messages**\n"
                f"✉️ Unread Messages: {unread_msg}\n"
                f"🔔 Unread Mentions: {unread_mention}\n\n"
                f"⏱ **Time Taken**: {duration}"
            )
            await msg.edit(text)
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.reserved$"))
    @rishabh()
    async def reserved_usernames(event):
        """
        .reserved — List admin-reserved public usernames with a loading animation.
        """
        try:
            me = await event.client.get_me()
            mention = f"[{me.first_name}](tg://user?id={me.id})"
            msg = await event.reply("🔐 Fetching reserved usernames…")

            for dots in ("", ".", "..", "..."):
                await msg.edit(f"🔐 Fetching reserved usernames{dots}")
                await asyncio.sleep(0.3)

            result = await event.client(GetAdminedPublicChannelsRequest())
            lines = [f"🔐 **{mention}'s Reserved Usernames**\n"]
            for chat in result.chats:
                if chat.username:
                    lines.append(f"• {chat.title} — **@{chat.username}**")

            text = "\n".join(lines) if len(lines) > 1 else "ℹ️ No reserved usernames found."
            await msg.edit(text)
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")
