import asyncio
from telethon import events
from telethon.errors import RPCError
from telethon.tl.types import ChannelParticipantsAdmins

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        ".purge    — Delete all messages from replied message to current (DM/Group)",
        ".p        — Alias for .purge"
    ]
    add_handler("purge", commands, "Message Purge Plugin")

async def is_user_admin(client, chat_id, user_id):
    """
    Check if the user is an admin in the chat or if it's a DM.
    """
    if hasattr(chat_id, 'chat_id'):  # For DMs or groups
        chat_id = chat_id.chat_id
    try:
        async for admin in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
            if admin.id == user_id:
                return True
        return False
    except Exception:  # DMs or chats where admin check fails
        return True  # Allow in DMs

@CipherElite.on(events.NewMessage(pattern=r"^\.(purge|p)$", outgoing=True))
@rishabh()
async def purge(event):
    """
    Delete all messages from the replied message to the current message.
    Works in DMs and groups (if user is admin).
    """
    if not event.is_reply:
        await event.reply("Please reply to a message to start purging from there.")
        return

    chat_id = event.chat_id
    user_id = event.sender_id

    # Check if user has permission
    if not await is_user_admin(CipherElite, chat_id, user_id):
        await event.reply("You need to be an admin to purge messages in this chat.")
        return

    # Get the replied message
    replied_msg = await event.get_reply_message()
    start_msg_id = replied_msg.id
    end_msg_id = event.message.id

    if start_msg_id >= end_msg_id:
        await event.reply("No messages to purge.")
        return

    # Delete messages in batches
    batch_size = 100  # Telegram API limit
    try:
        msg_ids = list(range(start_msg_id, end_msg_id + 1))
        for i in range(0, len(msg_ids), batch_size):
            batch = msg_ids[i:i + batch_size]
            await CipherElite.delete_messages(chat_id, batch)
            await asyncio.sleep(0.5)  # Avoid rate limits

        # Confirm purge
        confirmation = await event.reply("Purge completed successfully!")
        await asyncio.sleep(5)  # Let the confirmation stay for 5 seconds
        await confirmation.delete()

    except RPCError as e:
        await event.reply(f"Error during purge: {str(e)}")
    except Exception as e:
        await event.reply(f"An unexpected error occurred: {str(e)}")
