# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    purge
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

import asyncio
from telethon import events
from telethon.errors import RPCError
from telethon.tl.types import ChannelParticipantsAdmins, PeerUser

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        ".purge    — Delete all messages from replied message to current (DM/Group)",
        ".p        — Alias for .purge",
        ".delall   — Delete all messages (optionally for a specific user) with 20s delay"
    ]
    add_handler("purge", commands, "Message Purge Plugin")

async def is_user_admin(client, chat_id, user_id):
    """Check if user is admin in chat or if it's a DM."""
    if hasattr(chat_id, 'chat_id'):
        chat_id = chat_id.chat_id
    try:
        async for admin in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
            if admin.id == user_id:
                return True
        return False
    except Exception:
        return True  # Allow in DMs

@CipherElite.on(events.NewMessage(pattern=r"^\.(purge|p)$", outgoing=True))
@rishabh()
async def purge(event):
    """Delete messages from replied message to current message."""
    if not event.is_reply:
        await event.reply("Please reply to a message to start purging from there.")
        return

    chat_id = event.chat_id
    user_id = event.sender_id

    if not await is_user_admin(CipherElite, chat_id, user_id):
        await event.reply("You need to be an admin to purge messages in this chat.")
        return

    replied_msg = await event.get_reply_message()
    start_msg_id = replied_msg.id
    end_msg_id = event.message.id

    if start_msg_id >= end_msg_id:
        await event.reply("No messages to purge.")
        return

    batch_size = 100
    try:
        msg_ids = list(range(start_msg_id, end_msg_id + 1))
        for i in range(0, len(msg_ids), batch_size):
            await CipherElite.delete_messages(chat_id, msg_ids[i:i + batch_size])
            await asyncio.sleep(0.5)

        confirmation = await event.reply("Purge completed successfully!")
        await asyncio.sleep(5)
        await confirmation.delete()
    except RPCError as e:
        await event.reply(f"Error during purge: {str(e)}")
    except Exception as e:
        await event.reply(f"An unexpected error occurred: {str(e)}")

# Global dictionary to track cancellation flags
cancellation_flags = {}

@CipherElite.on(events.NewMessage(pattern=r"^\.delall$", outgoing=True))
@rishabh()
async def delall(event):
    """Delete all messages (optionally for a specific user) with cancellation support."""
    chat = event.chat
    user_id = event.sender_id
    is_private = isinstance(chat, PeerUser)
    
    # Delete command message immediately
    try:
        await event.delete()
    except Exception:
        pass

    # Determine target user (if any)
    target_user = None
    if event.is_reply:
        reply = await event.get_reply_message()
        target_user = reply.sender_id

    # Permission checks
    if not is_private:
        if target_user and target_user != user_id:
            # Deleting another user's messages - need admin
            if not await is_user_admin(CipherElite, chat, user_id):
                msg = await event.respond("🚫 You need admin rights to delete other users' messages!")
                await asyncio.sleep(5)
                await msg.delete()
                return
        elif not target_user:
            # Deleting all messages - need admin
            if not await is_user_admin(CipherElite, chat, user_id):
                msg = await event.respond("🚫 You need admin rights to delete all messages!")
                await asyncio.sleep(5)
                await msg.delete()
                return

    # Create cancellation flag for this chat
    cancellation_flags[event.chat_id] = asyncio.Event()
    cancel_flag = cancellation_flags[event.chat_id]

    # Send warning with cancellation instructions
    warning_msg = await event.respond(
        "⚠️ Deleting ALL messages in 20 seconds!\n"
        f"Type `.cancel` to abort. {'(Deleting only your messages)' if target_user == user_id else ''}"
    )

    # Wait for 20 seconds or cancellation
    try:
        await asyncio.wait_for(cancel_flag.wait(), timeout=20)
        await warning_msg.edit("🚫 Deletion cancelled!")
        await asyncio.sleep(3)
        await warning_msg.delete()
        return
    except asyncio.TimeoutError:
        pass
    finally:
        cancellation_flags.pop(event.chat_id, None)

    # Start deletion process
    await warning_msg.edit("🗑️ Deleting messages...")
    deleted_count = 0

    try:
        async for message in CipherElite.iter_messages(
            event.chat_id,
            from_user=target_user,
            reverse=True  # Process oldest first to avoid gaps
        ):
            if message.id == warning_msg.id:
                continue  # Skip our own warning message
                
            try:
                await message.delete()
                deleted_count += 1
                # Small delay to avoid flood limits
                if deleted_count % 10 == 0:
                    await asyncio.sleep(0.5)
            except Exception:
                pass
    except Exception as e:
        await warning_msg.edit(f"❌ Error: {str(e)}")
        await asyncio.sleep(5)
    else:
        await warning_msg.edit(f"✅ Deleted {deleted_count} messages!")
        await asyncio.sleep(3)
    
    # Final cleanup
    try:
        await warning_msg.delete()
    except Exception:
        pass

@CipherElite.on(events.NewMessage(pattern=r"^\.cancel$"))
async def cancel_delall(event):
    """Handle cancellation requests for delall operations."""
    chat_id = event.chat_id
    if chat_id in cancellation_flags:
        cancellation_flags[chat_id].set()
        try:
            await event.delete()
        except Exception:
            pass
