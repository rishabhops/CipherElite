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
    # get_me() fetches the account where the bot is logged in. 
    # Telethon caches this, so it won't slow down your bot!
    me = await event.client.get_me()
    
    # Return True if the sender is the deployer OR in the SUDO_USERS list
    if sender_id == me.id or sender_id in Config.SUDO_USERS:
        return True
    return False

# ==========================================
# 1. ADMIN / OWNER / SUDO DECORATOR
# ==========================================
def authorized_users_only(func):
    @wraps(func)
    async def wrapper(event):
        sender_id = event.sender_id
        
        # 🎭 PRIORITY 1: Always allow Owner & Sudo users (no exceptions)
        if await is_owner_or_sudo(event):
            print(f"✅ Owner/Sudo user {sender_id} authorized - bypassing checks")
            return await func(event)
        
        # 🎭 PRIORITY 2: Allow in private chats for non-sudo users
        if event.is_private:
            print(f"✅ Private chat authorized for user {sender_id}")
            return await func(event)
        
        # 🎭 PRIORITY 3: Check admin rights for normal users in groups
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
        
        # 🎭 Deny access for non-sudo, non-owner, non-admin users
        await event.reply("🎭 **Cipher Elite Access Denied**\n\n"
                         "❌ **This command is restricted to admins only!**\n"
                         "🛡️ **Required:** Admin privileges, Sudo access, or Bot Owner")
        return
        
    return wrapper

# ==========================================
# 2. OWNER & SUDO ONLY DECORATOR (Silent Fail)
# ==========================================
def rishabh(func):
    @wraps(func)
    async def wrapper(event):
        sender_id = event.sender_id
        
        # 🎭 Allow only if Owner or Sudo
        if not await is_owner_or_sudo(event):
            print(f"❌ Unauthorized access attempt by {sender_id}")
            return
        
        print(f"✅ Owner/Sudo user {sender_id} executing command: {func.__name__}")
        return await func(event)
    return wrapper

# ==========================================
# 3. OWNER & SUDO ONLY DECORATOR (With Alert)
# ==========================================
def rishabh_help(func):
    @wraps(func)
    async def wrapper(event):
        
        # 🎭 Allow only if Owner or Sudo
        if not await is_owner_or_sudo(event):
            # event.answer works for CallbackQueries (inline buttons). 
            # If used on normal messages, use event.reply instead.
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

# ==========================================
# 4. STRICT OWNER ONLY DECORATOR
# ==========================================
def owner_only(func):
    """
    Use this if you want a command to ONLY be used by the deployed account.
    Even Sudo users will be blocked from using commands with this decorator.
    """
    @wraps(func)
    async def wrapper(event):
        me = await event.client.get_me()
        
        if event.sender_id != me.id:
            return await event.reply("❌ **Only the Bot Owner can use this command.**")
            
        return await func(event)
    return wrapper
