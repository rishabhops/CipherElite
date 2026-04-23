# =============================================================================
#  CipherElite Digital Scrubber
#  Author:         CipherElite Dev (@rishabhops)
# =============================================================================

import asyncio
from telethon import events
from telethon.errors import ChatAdminRequiredError, FloodWaitError
from telethon.utils import get_display_name

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".scrub - Delete ALL your messages in the current chat",
        ".scrub <@username> - Delete ALL messages by a specific user (Requires Admin)",
        ".scrub (reply) - Reply to someone to delete all their messages (Requires Admin)"
    ]
    description = (
        "🧹 **Digital Scrubber**\n"
        "🗑️ Erases digital footprints instantly.\n"
        "⚡ Batches deletions 100 at a time to bypass limits.\n"
        "🛡️ Built-in anti-ban delays.\n\n"
    )
    add_handler("scrubber", commands, description)

# ==========================================
# COMMAND HANDLER
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"^\.scrub(?: |$)(.*)", outgoing=True))
@rishabh
async def scrub_messages(event):
    args = event.pattern_match.group(1).strip()
    target_user = None
    target_name = "your"
    me = await event.client.get_me()

    # Determine who we are scrubbing
    if args:
        try:
            target_user = await event.client.get_entity(args)
            target_name = f"{get_display_name(target_user)}'s"
        except Exception:
            return await event.reply("❌ **Error:** Could not find that user.")
    elif event.is_reply:
        reply_msg = await event.get_reply_message()
        target_user = await reply_msg.get_sender()
        target_name = f"{get_display_name(target_user)}'s"
    else:
        target_user = me

    status = await event.reply(f"🔍 **Scanning chat history for {target_name} messages...**\n*This may take a moment.*")

    deleted_count = 0
    msg_ids = []

    try:
        # Fetch messages specifically from the target user
        async for msg in event.client.iter_messages(event.chat_id, from_user=target_user):
            msg_ids.append(msg.id)
            
            # Telegram allows deleting a max of 100 messages per API call
            if len(msg_ids) >= 100:
                await event.client.delete_messages(event.chat_id, msg_ids)
                deleted_count += len(msg_ids)
                msg_ids = [] # Reset the list for the next batch
                
                # Update status and sleep to prevent FloodWait bans
                await status.edit(f"🧹 **Scrubbing in progress...**\n🗑️ Deleted: `{deleted_count}` messages so far.")
                await asyncio.sleep(1.5)

        # Delete any remaining messages that didn't make a full 100 batch
        if msg_ids:
            await event.client.delete_messages(event.chat_id, msg_ids)
            deleted_count += len(msg_ids)

        await status.edit(f"✅ **Scrub Complete!**\n🧹 Successfully erased `{deleted_count}` of {target_name} messages from this chat.")

    except ChatAdminRequiredError:
        await status.edit("🛑 **Error:** You need Admin rights with 'Delete Messages' permission to scrub someone else's messages!")
    except FloodWaitError as e:
        await status.edit(f"🛑 **Rate Limited!** Telegram is forcing a wait of {e.seconds} seconds. Try again later.")
    except Exception as e:
        await status.edit(f"❌ **Error during scrubbing:** `{str(e)}`")

    # Clean up the final status message after 5 seconds
    await asyncio.sleep(5)
    await status.delete()
