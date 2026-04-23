# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    chats
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

from telethon import events
from telethon.tl.functions.channels import CreateChannelRequest, DeleteChannelRequest, EditPhotoRequest, EditTitleRequest
from telethon.tl.functions.messages import ExportChatInviteRequest, CreateChatRequest
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".delchat - Delete/leave current chat",
        ".getlink - Get chat invite link",
        ".create <group/channel> <name> - Create new group/channel",
        ".setgpic <reply> - Set group photo",
        ".setgname <name> - Set group name"
    ]
    description = "Chat Management for creating and managing groups/channels"
    add_handler("chats", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.delchat"))
    @rishabh()
    async def delchat(event):
        chat = await event.get_chat()
        
        if event.is_private:
            await event.reply("❌ This command only works in groups and channels!")
            return
        
        try:
            # Try to delete the channel/group
            await event.client(DeleteChannelRequest(chat.id))
            await event.reply("✅ Chat deleted successfully!")
        except:
            # If we can't delete, just leave
            try:
                await event.client.delete_dialog(chat.id)
                await event.reply("✅ Left the chat successfully!")
            except Exception as e:
                await event.reply(f"❌ Failed to delete/leave chat: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.getlink"))
    @rishabh()
    async def getlink(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups and channels!")
            return
        
        try:
            invite = await event.client(ExportChatInviteRequest(event.chat_id))
            await event.reply(f"🔗 **Invite Link:**\n\n{invite.link}")
        except Exception as e:
            await event.reply(f"❌ Failed to get invite link: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.create"))
    @rishabh()
    async def create(event):
        text = event.text.split(maxsplit=2)
        
        if len(text) < 3:
            await event.reply("❌ Usage: `.create <group/channel> <name>`\n\nExample: `.create group My Group`")
            return
        
        chat_type = text[1].lower()
        chat_name = text[2]
        
        try:
            if chat_type == "channel":
                # Create channel
                result = await event.client(CreateChannelRequest(
                    title=chat_name,
                    about="Created by CipherElite",
                    megagroup=False
                ))
                await event.reply(f"✅ **Channel Created!**\n\n📢 Name: {chat_name}\n🆔 ID: `{result.chats[0].id}`")
            elif chat_type == "group":
                # Create group
                result = await event.client(CreateChannelRequest(
                    title=chat_name,
                    about="Created by CipherElite",
                    megagroup=True
                ))
                await event.reply(f"✅ **Group Created!**\n\n👥 Name: {chat_name}\n🆔 ID: `{result.chats[0].id}`")
            else:
                await event.reply("❌ Invalid type! Use: `group` or `channel`")
        except Exception as e:
            await event.reply(f"❌ Failed to create chat: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.setgpic"))
    @rishabh()
    async def setgpic(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups and channels!")
            return
        
        if not event.is_reply:
            await event.reply("❌ Reply to a photo to set it as group picture!")
            return
        
        reply = await event.get_reply_message()
        
        if not reply.photo:
            await event.reply("❌ Reply to a photo!")
            return
        
        try:
            photo = await event.client.download_media(reply.photo)
            file = await event.client.upload_file(photo)
            
            await event.client(EditPhotoRequest(
                channel=event.chat_id,
                photo=file
            ))
            
            await event.reply("✅ Group photo updated successfully!")
            
            # Clean up downloaded file
            # import os moved to top
            if os.path.exists(photo):
                os.remove(photo)
        except Exception as e:
            await event.reply(f"❌ Failed to set group photo: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.setgname"))
    @rishabh()
    async def setgname(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups and channels!")
            return
        
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.setgname <new name>`")
            return
        
        new_name = text[1]
        
        try:
            await event.client(EditTitleRequest(
                channel=event.chat_id,
                title=new_name
            ))
            
            await event.reply(f"✅ Group name updated to: **{new_name}**")
        except Exception as e:
            await event.reply(f"❌ Failed to update group name: {str(e)}")
