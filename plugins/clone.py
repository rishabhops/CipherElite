from telethon import events
from telethon.tl import functions, types
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.types import InputPhoto
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import html
import os
import json
import logging
import asyncio

# Configure logging
logger = logging.getLogger(__name__)
BACKUP_DIR = "profile_backups"

def init(client_instance):
    commands = [
        ".clone <username/userid/reply> - Clone a user's profile",
        ".revert - Revert to original profile"
    ]
    description = "Clone and revert user profiles"
    add_handler("clone", commands, description)

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

async def delete_messages_after_delay(event, response, delay=5):
    """Delete both command and response messages after delay"""
    await asyncio.sleep(delay)
    try:
        await event.delete()
    except Exception as e:
        logger.warning(f"Failed to delete command: {e}")
    try:
        await response.delete()
    except Exception as e:
        logger.warning(f"Failed to delete response: {e}")

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.clone"))
    @rishabh()
    async def clone_profile(event):
        response = None
        try:
            sender_id = event.sender_id
            backup_file = os.path.join(BACKUP_DIR, f"{sender_id}.json")

            # Create backup if doesn't exist
            if not os.path.exists(backup_file):
                me = await event.client.get_entity("me")
                my_full = await event.client(GetFullUserRequest(me))
                photo_path = await event.client.download_profile_photo("me", file=os.path.join(BACKUP_DIR, f"{sender_id}_photo"))

                backup_data = {
                    "first_name": me.first_name or "",
                    "last_name": me.last_name or "",
                    "about": my_full.full_user.about if my_full.full_user else "",
                    "photo_path": photo_path
                }

                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f)
                logger.info(f"Created profile backup for {sender_id}")

            # Get target user to clone
            replied_user = await get_user_from_event(event)
            if not replied_user:
                response = await event.reply("❌ No user specified to clone!")
                asyncio.create_task(delete_messages_after_delay(event, response))
                return

            user_id = replied_user.id
            full_user = await event.client(GetFullUserRequest(replied_user))
            profile_pic = await event.client.download_profile_photo(user_id, file="temp_clone_photo")

            # Update profile
            first_name = html.escape(replied_user.first_name or "")
            last_name = html.escape(replied_user.last_name or "") or "⁪⁬⁮⁮ ‌‌‌‌"

            await event.client(functions.account.UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name
            ))

            if full_user.full_user and full_user.full_user.about:
                await event.client(functions.account.UpdateProfileRequest(
                    about=full_user.full_user.about
                ))

            # Handle profile photo
            photo_error = None
            if profile_pic:
                try:
                    with open(profile_pic, 'rb') as file:
                        upload_file = await event.client.upload_file(file)
                        await event.client(UploadProfilePhotoRequest(
                            file=upload_file
                        ))
                except Exception as e:
                    photo_error = str(e)
                    logger.warning(f"Profile photo upload failed: {e}")
                finally:
                    if os.path.exists(profile_pic):
                        os.remove(profile_pic)

            # Send success message with optional photo error
            if photo_error:
                response = await event.reply(f"👥 Profile cloned! ⚠️ Photo failed: {photo_error}")
            else:
                response = await event.reply("👥 Profile successfully cloned!")

        except Exception as e:
            logger.error(f"Clone error: {e}", exc_info=True)
            response = await event.reply(f"❌ Clone failed: {str(e)}")
        finally:
            if response:
                asyncio.create_task(delete_messages_after_delay(event, response))

    @CipherElite.on(events.NewMessage(pattern=r"\.revert"))
    @rishabh()
    async def revert_profile(event):
        response = None
        try:
            sender_id = event.sender_id
            backup_file = os.path.join(BACKUP_DIR, f"{sender_id}.json")

            if not os.path.exists(backup_file):
                response = await event.reply("❌ No backup found! Please clone first before reverting.")
                asyncio.create_task(delete_messages_after_delay(event, response))
                return

            with open(backup_file, 'r') as f:
                backup_data = json.load(f)

            # Revert profile details
            await event.client(functions.account.UpdateProfileRequest(
                first_name=backup_data.get("first_name", ""),
                last_name=backup_data.get("last_name", "")
            ))

            await event.client(functions.account.UpdateProfileRequest(
                about=backup_data.get("about", "")
            ))

            # Revert profile photo
            photo_error = None
            try:
                # Remove current photos
                current_photos = await event.client.get_profile_photos("me")
                if current_photos:
                    input_photos = [
                        InputPhoto(
                            id=photo.id,
                            access_hash=photo.access_hash,
                            file_reference=photo.file_reference
                        ) for photo in current_photos
                    ]
                    await event.client(DeletePhotosRequest(id=input_photos))

                # Restore original photo if existed
                photo_path = backup_data.get("photo_path")
                if photo_path and os.path.exists(photo_path):
                    with open(photo_path, 'rb') as f:
                        file = await event.client.upload_file(f)
                        await event.client(UploadProfilePhotoRequest(file=file))
            except Exception as e:
                photo_error = str(e)
                logger.warning(f"Photo revert error: {e}")

            # Cleanup backup files
            if os.path.exists(backup_file):
                os.remove(backup_file)
            photo_path = backup_data.get("photo_path")
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)

            # Send success message with optional photo error
            if photo_error:
                response = await event.reply(f"🔄 Profile reverted! ⚠️ Photo failed: {photo_error}")
            else:
                response = await event.reply("🔄 Profile successfully reverted!")

        except Exception as e:
            logger.error(f"Revert error: {e}", exc_info=True)
            response = await event.reply(f"❌ Revert failed: {str(e)}")
        finally:
            if response:
                asyncio.create_task(delete_messages_after_delay(event, response))

async def get_user_from_event(event):
    try:
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            return await event.client.get_entity(reply_message.sender_id)
        elif event.pattern_match.group(1):
            user_input = event.pattern_match.group(1).strip()
            return await event.client.get_entity(user_input)
        return None
    except Exception as e:
        logger.error(f"User fetch error: {e}")
        return None
