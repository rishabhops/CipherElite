from functools import wraps
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from config.config import Config

def authorized_users_only(func):
    @wraps(func)
    async def wrapper(event):
        sender_id = event.sender_id
        
        # 🎭 PRIORITY 1: Always allow sudo users (no exceptions)
        if sender_id in Config.SUDO_USERS:
            print(f"✅ Sudo user {sender_id} authorized - bypassing all checks")
            return await func(event)
        
        # 🎭 PRIORITY 2: Allow in private chats for non-sudo users
        if event.is_private:
            print(f"✅ Private chat authorized for user {sender_id}")
            return await func(event)
        
        # 🎭 PRIORITY 3: Check admin rights for non-sudo users in groups
        try:
            chat = await event.get_chat()
            
            # Method 1: Check basic admin rights
            if hasattr(chat, 'admin_rights') and chat.admin_rights:
                if chat.admin_rights.delete_messages or chat.admin_rights.ban_users:
                    return await func(event)
            
            # Method 2: Check if creator
            if hasattr(chat, 'creator') and chat.creator:
                return await func(event)
            
            # Method 3: Detailed participant check (fallback)
            try:
                participant = await event.client(GetParticipantRequest(
                    channel=chat,
                    participant=sender_id
                ))
                
                if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                    return await func(event)
                    
            except (UserNotParticipantError, ChatAdminRequiredError, AttributeError):
                pass
            
        except Exception as e:
            print(f"❌ Error checking admin rights: {e}")
            pass
        
        # 🎭 Deny access for non-sudo, non-admin users
        await event.reply("🎭 **Cipher Elite Access Denied**\n\n"
                         "❌ **This command is restricted to admins only!**\n"
                         "🛡️ **Required:** Admin privileges or sudo access")
        return
        
    return wrapper

def rishabh():
    def decorator(func):
        @wraps(func)
        async def wrapper(event):
            sender_id = event.sender_id
            
            # 🎭 Enhanced sudo check with debugging
            if sender_id not in Config.SUDO_USERS:
                print(f"❌ Unauthorized access attempt by {sender_id}")
                print(f"📊 Current sudo users: {Config.SUDO_USERS}")
                print(f"🔍 Sender ID type: {type(sender_id)}")
                return
            
            print(f"✅ Sudo user {sender_id} executing command: {func.__name__}")
            return await func(event)
        return wrapper
    return decorator

def rishabh_help():
    def decorator(func):
        @wraps(func)
        async def wrapper(event):
            sender_id = event.sender_id
            
            if sender_id not in Config.SUDO_USERS:
                await event.answer(
                    "🎭 **Cipher Elite Access Restricted!**\n\n"
                    "🔒 **Deploy your own Cipher Elite Bot:**\n"
                    "github.com/rishabhops/CipherElite\n\n"
                    "⚡ **Unauthorized access denied**", 
                    alert=True
                )
                return
            return await func(event)
        return wrapper
    return decorator
