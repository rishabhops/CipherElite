from telethon import events
from telethon.tl import functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputFile
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import html
import os

def init(client_instance):
    commands = [
        ".clone <username/userid/reply> - Clone a user's profile",
        ".revert - Revert to original profile"
    ]
    description = "Clone and revert user profiles"
    add_handler("clone", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.clone"))
    @rishabh()
    async def clone_profile(event):
        try:
            replied_user = await get_user_from_event(event)
            if not replied_user:
                return await event.reply("❌ No user specified to clone!")

            user_id = replied_user.id
            full_user = await event.client(GetFullUserRequest(user_id))
            
            profile_pic = await event.client.download_profile_photo(user_id, file="temp_profile_pic")
            
            first_name = html.escape(replied_user.first_name or "")
            last_name = html.escape(replied_user.last_name or "") or "⁪⁬⁮⁮⁮⁮ ‌‌‌‌"
            
            await event.client(functions.account.UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name
            ))
            
            if full_user.full_user.about:
                await event.client(functions.account.UpdateProfileRequest(
                    about=full_user.full_user.about
                ))
            
            if profile_pic:
                try:
                    with open(profile_pic, 'rb') as file:
                        upload_file = await event.client.upload_file(file)
                        await event.client(functions.photos.UploadProfilePhotoRequest(
                            file=upload_file
                        ))
                    os.remove(profile_pic)
                except Exception as e:
                    await event.reply(f"Error uploading profile pic: {e}")
                    if os.path.exists(profile_pic):
                        os.remove(profile_pic)
            
            await event.reply("👥 Profile successfully cloned!")
        
        except Exception as e:
            await event.reply(f"❌ Clone failed: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.revert"))
    @rishabh()
    async def revert_profile(event):
        try:
            default_first_name = "Your Original Name"
            default_last_name = ""
            default_bio = "Back to my original self"
            
            current_pics = await event.client.get_profile_photos("me", limit=1)
            if current_pics:
                await event.client(functions.photos.DeletePhotosRequest(current_pics))
            
            await event.client(functions.account.UpdateProfileRequest(
                first_name=default_first_name,
                last_name=default_last_name
            ))
            
            await event.client(functions.account.UpdateProfileRequest(
                about=default_bio
            ))
            
            await event.reply("🔄 Profile successfully reverted!")
        
        except Exception as e:
            await event.reply(f"❌ Revert failed: {str(e)}")

async def get_user_from_event(event):
    try:
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            user = await event.client.get_entity(reply_message.sender_id)
        else:
            user_input = event.pattern_match.group(1)
            if user_input:
                user = await event.client.get_entity(user_input)
            else:
                return None
        return user
    except Exception as e:
        await event.reply(f"Error getting user: {e}")
        return None