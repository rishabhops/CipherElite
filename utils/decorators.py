from functools import wraps
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from config.config import Config

def authorized_users_only(func):
    @wraps(func)
    async def wrapper(event):
        if event.sender_id in Config.SUDO_USERS:
            return await func(event)
            
        if event.is_private:
            return await func(event)
            
        chat = await event.get_chat()
        if not chat.admin_rights and not chat.creator:
            return await event.reply("This command is restricted to admins only!")
            
        return await func(event)
    return wrapper
    
    
def rishabh_help():
    def decorator(func):
        @wraps(func)
        async def wrapper(event):
            if event.sender_id not in Config.SUDO_USERS:
                await event.answer(
                    "🔒 Access Restricted!\n\n"
                    "Deploy your own Cipher Elite Bot:\n"
                    "github.com/rishabhops/CipherBot", 
                    alert=True
                )
                return
            return await func(event)
        return wrapper
    return decorator
   

def rishabh():
    def decorator(func):
        @wraps(func)
        async def wrapper(event):
            if event.sender_id not in Config.SUDO_USERS:
                print("sudo user only")
                return
            return await func(event)
        return wrapper
    return decorator
    