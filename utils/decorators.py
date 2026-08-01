from functools import wraps
from telethon import events  # Required to check the event type
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
    
    # 1. Check if the sender is the automatically extracted OWNER_ID
    if hasattr(Config, 'OWNER_ID') and sender_id == Config.OWNER_ID:
        return True
        
    # 2. Check if the sender is in the SUDO_USERS list
    if hasattr(Config, 'SUDO_USERS') and sender_id in Config.SUDO_USERS:
        return True

    # 3. Fallback: If the event is on the userbot client, me.id will match sender_id
    try:
        me = await event.client.get_me()
        if sender_id == me.id:
            return True
    except Exception:
        pass
        
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
                try:
                    return await f(event)
                except Exception as e:
                    import traceback
                    print(f"❌ Exception in command {f.__name__}: {e}")
                    traceback.print_exc()
                    await event.reply(f"❌ **Command Error in `{f.__name__}`:**\n`{e}`")
                    raise
            
            # 🎭 PRIORITY 2: Allow in private chats for non-sudo users
            if event.is_private:
                print(f"✅ Private chat authorized for user {sender_id}")
                try:
                    return await f(event)
                except Exception as e:
                    import traceback
                    print(f"❌ Exception in command {f.__name__}: {e}")
                    traceback.print_exc()
                    await event.reply(f"❌ **Command Error in `{f.__name__}`:**\n`{e}`")
                    raise
            
            # 🎭 PRIORITY 3: Check admin rights for normal users in groups
            try:
                chat = await event.get_chat()
                
                if hasattr(chat, 'admin_rights') and chat.admin_rights:
                    if chat.admin_rights.delete_messages or chat.admin_rights.ban_users:
                        try:
                            return await f(event)
                        except Exception as e:
                            import traceback
                            print(f"❌ Exception in command {f.__name__}: {e}")
                            traceback.print_exc()
                            await event.reply(f"❌ **Command Error in `{f.__name__}`:**\n`{e}`")
                            raise
                
                if hasattr(chat, 'creator') and chat.creator:
                    try:
                        return await f(event)
                    except Exception as e:
                        import traceback
                        print(f"❌ Exception in command {f.__name__}: {e}")
                        traceback.print_exc()
                        await event.reply(f"❌ **Command Error in `{f.__name__}`:**\n`{e}`")
                        raise
                
                try:
                    participant = await event.client(GetParticipantRequest(
                        channel=chat,
                        participant=sender_id
                    ))
                    if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                        try:
                            return await f(event)
                        except Exception as e:
                            import traceback
                            print(f"❌ Exception in command {f.__name__}: {e}")
                            traceback.print_exc()
                            await event.reply(f"❌ **Command Error in `{f.__name__}`:**\n`{e}`")
                            raise
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
            try:
                return await f(event)
            except Exception as e:
                import traceback
                print(f"❌ Exception in command {f.__name__}: {e}")
                traceback.print_exc()
                await event.reply(f"❌ **Command Error in `{f.__name__}`:**\n`{e}`")
                raise
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
                error_msg = (
                    "🎭 **Cipher Elite Access Restricted!**\n\n"
                    "🔒 **Deploy your own Cipher Elite Bot:**\n"
                    "https://github.com/rishabhops/CipherElite\n\n"
                    "⚡ **Unauthorized access denied**"
                )
                
                # Safely handle the response based on the incoming event type
                if isinstance(event, events.CallbackQuery.Event):
                    await event.answer(error_msg, alert=True)
                elif isinstance(event, events.InlineQuery.Event):
                    # Inline queries require a list of results. Passing an empty list prevents the timeout crash.
                    await event.answer([]) 
                else:
                    # Fallback for standard messages
                    await event.reply(error_msg)
                return
            
            try:
                return await f(event)
            except Exception as e:
                import traceback
                print(f"❌ Exception in command {f.__name__}: {e}")
                traceback.print_exc()
                if isinstance(event, events.CallbackQuery.Event):
                    await event.answer(f"❌ Error in {f.__name__}: {e}", alert=True)
                elif isinstance(event, events.InlineQuery.Event):
                    await event.answer([])
                else:
                    await event.reply(f"❌ **Command Error in `{f.__name__}`:**\n`{e}`")
                raise
        return wrapper

    # Magic logic to allow both @rishabh_help and @rishabh_help()
    if func is None:
        return decorator
    else:
        return decorator(func)

