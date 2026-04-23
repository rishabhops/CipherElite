from functools import wraps
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from config.config import Config

# ==========================================
# HELPER FUNCTION
# ==========================================
async def is_owner_or_sudo(event):
    """
    Checks if the user sending the command is the deployer (Owner) 
    or a registered Sudo User.
    """
    sender_id = event.sender_id
    me = await event.client.get_me()
    
    if sender_id == me.id or sender_id in Config.SUDO_USERS:
        return True
    return False

# ==========================================
# 1. ADMIN / OWNER / SUDO DECORATOR
# ==========================================
def authorized_users_only(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event):
            sender_id = event.sender_id
            
            # 🎭 PRIORITY 1: Always allow Owner & Sudo users (no exceptions)
            if await is_owner_or_sudo(event):
                print(f"✅ Owner/Sudo user {sender_id} authorized - bypassing checks")
                return await f(event)
            
            # 🎭 PRIORITY 2: Allow in private chats for non-sudo users
            if event.is_private:
                print(f"✅ Private chat authorized for user {sender_id}")
                return await f(event)
            
            # 🎭 PRIORITY 3: Check admin rights for normal users in groups
            try:
                chat = await event.get_chat()
                
                if hasattr(chat, 'admin_rights') and chat.admin_rights:
                    if chat.admin_rights.delete_messages or chat.admin_rights.ban_users:
                        return await f(event)
                
                if hasattr(chat, 'creator') and chat.creator:
                    return await f(event)
                
                try:
                    participant = await event.client(GetParticipantRequest(
                        channel=chat,
                        participant=sender_id
                    ))
                    if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                        return await f(event)
                except (UserNotParticipantError, ChatAdminRequiredError, AttributeError):
                    pass
                
            except Exception as e:
                print(f"❌ Error checking admin rights: {e}")
                pass
            
            # 🎭 Deny access
            await event.reply("🎭 **Cipher Elite Access Denied**\n\n"
                             "❌ **This command is restricted to admins only!**\n"
                             "🛡️ **Required:** Admin privileges, Sudo access, or Bot Owner")
            return
        return wrapper

    # Magic logic to allow both @authorized_users_only and @authorized_users_only()
    if func is None:
        return decorator
    else:
        return decorator(func)

# ==========================================
# 2. OWNER & SUDO ONLY DECORATOR (Silent Fail)
# ==========================================
def rishabh(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event):
            sender_id = event.sender_id
            
            if not await is_owner_or_sudo(event):
                print(f"❌ Unauthorized access attempt by {sender_id}")
                return
            
            print(f"✅ Owner/Sudo user {sender_id} executing command: {f.__name__}")
            return await f(event)
        return wrapper

    # Magic logic to allow both @rishabh and @rishabh()
    if func is None:
        return decorator
    else:
        return decorator(func)

# ==========================================
# 3. OWNER & SUDO ONLY DECORATOR (With Alert)
# ==========================================
def rishabh_help(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event):
            
            if not await is_owner_or_sudo(event):
                await event.answer(
                    "🎭 **Cipher Elite Access Restricted!**\n\n"
                    "🔒 **Deploy your own Cipher Elite Bot:**\n"
                    "github.com/rishabhops/CipherElite\n\n"
                    "⚡ **Unauthorized access denied**", 
                    alert=True
                )
                return
                
            return await f(event)
        return wrapper

    # Magic logic to allow both @rishabh_help and @rishabh_help()
    if func is None:
        return decorator
    else:
        return decorator(func)
