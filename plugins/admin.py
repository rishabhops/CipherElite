from telethon import events, errors
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

def init(client_instance):
    commands = [
        ".ban - Ban a user from the group",
        ".unban - Unban a user from the group",
        ".mute - Mute a user in the group",
        ".unmute - Unmute a user in the group",
        ".promote - Promote a user to admin",
        ".demote - Remove admin rights from a user",
        ".pin - Pin a message in the group",
        ".unpin - Unpin a message in the group"
    ]
    description = "Admin commands for group management 👮‍♂️"
    add_handler("admin", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.ban"))
    @rishabh()
    async def ban(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await event.client(EditBannedRequest(
                    event.chat_id,
                    reply.sender_id,
                    ChatBannedRights(until_date=None, view_messages=True)
                ))
                await event.reply("🚫 User has been banned!")
            except:
                await event.reply("❌ Failed to ban user. Make sure you have the right permissions!")

    @CipherElite.on(events.NewMessage(pattern=r"\.unban"))
    @rishabh()
    async def unban(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await event.client(EditBannedRequest(
                    event.chat_id,
                    reply.sender_id,
                    ChatBannedRights(until_date=None, view_messages=False)
                ))
                await event.reply("✅ User has been unbanned!")
            except:
                await event.reply("❌ Failed to unban user. Make sure you have the right permissions!")

    @CipherElite.on(events.NewMessage(pattern=r"\.mute"))
    @rishabh()
    async def mute(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await event.client(EditBannedRequest(
                    event.chat_id,
                    reply.sender_id,
                    ChatBannedRights(until_date=None, send_messages=True)
                ))
                await event.reply("🤐 User has been muted!")
            except:
                await event.reply("❌ Failed to mute user. Make sure you have the right permissions!")

    @CipherElite.on(events.NewMessage(pattern=r"\.unmute"))
    @rishabh()
    async def unmute(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await event.client(EditBannedRequest(
                    event.chat_id,
                    reply.sender_id,
                    ChatBannedRights(until_date=None, send_messages=False)
                ))
                await event.reply("🔊 User has been unmuted!")
            except:
                await event.reply("❌ Failed to unmute user. Make sure you have the right permissions!")

    @CipherElite.on(events.NewMessage(pattern=r"\.promote"))
    @rishabh()
    async def promote(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await event.client.edit_admin(
                    event.chat_id,
                    reply.sender_id,
                    is_admin=True,
                    title="Admin"
                )
                await event.reply("👑 User has been promoted to admin!")
            except:
                await event.reply("❌ Failed to promote user. Make sure you have the right permissions!")

    @CipherElite.on(events.NewMessage(pattern=r"\.demote"))
    @rishabh()
    async def demote(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                await event.client.edit_admin(
                    event.chat_id,
                    reply.sender_id,
                    is_admin=False,
                    title=None
                )
                await event.reply("⬇️ User has been demoted!")
            except:
                await event.reply("❌ Failed to demote user. Make sure you have the right permissions!")

    @CipherElite.on(events.NewMessage(pattern=r"\.pin"))
    @rishabh()
    async def pin_message(event):
        if event.is_reply:
            try:
                await event.client.pin_message(
                    event.chat_id,
                    (await event.get_reply_message()).id,
                    notify=True
                )
                await event.reply("📌 Message pinned successfully!")
            except:
                await event.reply("❌ Failed to pin message. Make sure you have the right permissions!")

    @CipherElite.on(events.NewMessage(pattern=r"\.unpin"))
    @rishabh()
    async def unpin_message(event):
        if event.is_reply:
            try:
                await event.client.unpin_message(
                    event.chat_id,
                    (await event.get_reply_message()).id
                )
                await event.reply("📍 Message unpinned successfully!")
            except:
                await event.reply("❌ Failed to unpin message. Make sure you have the right permissions!")
                