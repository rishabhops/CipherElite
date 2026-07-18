import importlib
import platform
import asyncio
import re
from datetime import datetime
from pathlib import Path
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from telethon import Button, events
from telethon.errors import UserNotParticipantError, UserAlreadyParticipantError, ChatAdminRequiredError
from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

from plugins.bot import init_bot
from utils.utils import init_client

async def load_plugins(client):
    """Loads standard Userbot plugins"""
    path = Path(__file__).parent.parent / "plugins"
    plugins = [
        f"plugins.{f.stem}"
        for f in path.glob("*.py")
        if f.stem != "__init__"
    ]

    loaded_plugins = []
    for plugin_name in plugins:
        try:
            module = importlib.import_module(plugin_name)
            module.init(client)
            if hasattr(module, "register_commands"):
                await module.register_commands()
            loaded_plugins.append(plugin_name.split(".")[-1])
            print(f"Loaded plugin: {plugin_name.split('.')[-1]}")
        except Exception as e:
            print(f"\033[1;31mFailed to load plugin {plugin_name}: {e}\033[0m")
    return loaded_plugins

async def load_bot_plugins(bot_client, user_client):
    """Loads Assistant Bot plugins (like assistant.py)"""
    path = Path(__file__).parent.parent / "bot_plugins"
    
    if not path.exists():
        print("\033[1;33mDirectory 'bot_plugins' not found. Skipping bot plugins.\033[0m")
        return []

    # Get owner details to pass to the bot plugins
    owner = await user_client.get_me()
    owner_id = owner.id
    owner_name = owner.first_name or "Owner"
    
    # 👇 INJECT OWNER ID TO CONFIG HERE 👇
    from config.config import Config
    Config.OWNER_ID = owner_id
    # 👆 ============================== 👆

    plugins = [
        f"bot_plugins.{f.stem}"
        for f in path.glob("*.py")
        if f.stem != "__init__"
    ]

    loaded_bot_plugins = []
    for plugin_name in plugins:
        try:
            module = importlib.import_module(plugin_name)
            
            # Assistant plugins use init_bot_plugin instead of init/register_commands
            if hasattr(module, "init_bot_plugin"):
                if asyncio.iscoroutinefunction(module.init_bot_plugin):
                    await module.init_bot_plugin(bot_client, owner_id, owner_name)
                else:
                    module.init_bot_plugin(bot_client, owner_id, owner_name)
                    
                loaded_bot_plugins.append(plugin_name.split(".")[-1])
                # Note: assistant.py already prints its own success message, but we log it here too
                print(f"Loaded bot plugin: {plugin_name.split('.')[-1]}")
            else:
                print(f"\033[1;33mWarning: {plugin_name} is missing init_bot_plugin()\033[0m")
                
        except Exception as e:
            print(f"\033[1;31mFailed to load bot plugin {plugin_name}: {e}\033[0m")
            
    return loaded_bot_plugins

async def generate_startup_info():
    """Generate system and bot information for startup message"""
    python_version = platform.python_version()
    telethon_version = importlib.import_module("telethon").__version__
    os_info = f"{platform.system()} {platform.release()}"
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "python": python_version,
        "telethon": telethon_version,
        "os": os_info,
        "uptime": uptime
    }

async def display_startup_message(client, plugins, bot_plugins):
    system_info = await generate_startup_info()
    user_name = (await client.get_me()).first_name
    banner = f"""
\033[1;36m=====================
 CIPHER ELITE USERBOT
=====================
\033[1;32mStatus   : ONLINE
Python   : v{system_info["python"]}
Telethon : v{system_info["telethon"]}
OS       : {system_info["os"]}
Plugins  : {len(plugins)} UB | {len(bot_plugins)} Bot
User     : {user_name}
Started  : {system_info["uptime"]}
\033[1;36m=====================
\033[1;33mElite Power Activated!\033[0m
"""
    print(banner)
    return system_info

async def configure_bot_via_botfather(user_client, bot_username):
    """Automatically configure bot through BotFather using user account"""
    user = await user_client.get_me()
    user_first_name = user.first_name
    
    bot_name = f"{user_first_name}'s Assistant"
    bot_bio = (
        f"🤖 Personal Assistant Bot for {user_first_name}\n\n"
        "🔰 Cipher Elite Userbot Assistant\n"
        "⚡ Powered by thanospros\n"
        "🛡️ Advanced Automation & Management\n\n"
        "🔗 Support: @thanosprosss"
    )
    bot_about = f"🤖 Assistant for {user_first_name} | Cipher Elite | @thanosprosss"
    
    desired_commands = {
        "start": "Start the bot",
        "help": "Show help information",
        "ping": "Check bot responsiveness",
        "status": "Show system status"
    }

    print(f"\033[1;34m🔍 Checking current @{bot_username} settings...\033[0m")
    
    try:
        bot_entity = await user_client.get_entity(bot_username)
        full_user_response = await user_client(GetFullUserRequest(bot_entity))
        full_user = full_user_response.full_user
        
        current_name = bot_entity.first_name or ""
        current_about = getattr(full_user, 'about', "") or ""
        
        bot_info = getattr(full_user, 'bot_info', None)
        current_description = getattr(bot_info, 'description', "") if bot_info else ""
        
        current_commands_dict = {}
        if bot_info and getattr(bot_info, 'commands', None):
            current_commands_dict = {cmd.command: cmd.description for cmd in bot_info.commands}

        needs_name = current_name != bot_name
        needs_about = current_about != bot_about
        needs_description = current_description != bot_bio
        needs_commands = current_commands_dict != desired_commands
        
        if not any([needs_name, needs_about, needs_description, needs_commands]):
            print("\033[1;32m✅ Bot settings are already up to date - Skipping BotFather setup\033[0m")
            return True
            
    except Exception as e:
        print(f"\033[1;33m⚠️ Couldn't verify current bot settings: {e}\033[0m")
        needs_name = needs_about = needs_description = needs_commands = True

    print(f"\033[1;33mConfiguring bot @{bot_username} via BotFather...\033[0m")
    
    try:
        async with user_client.conversation('BotFather') as conv:
            if needs_commands:
                print("\033[1;36m➡️ Updating commands...\033[0m")
                await conv.send_message("/setcommands")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                commands_str = "\n".join([f"{k} - {v}" for k, v in desired_commands.items()])
                await conv.send_message(commands_str)
                await asyncio.sleep(2)
                
            if needs_name:
                print("\033[1;36m➡️ Updating name...\033[0m")
                await conv.send_message("/setname")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                await conv.send_message(bot_name)
                await asyncio.sleep(2)
                
            if needs_description:
                print("\033[1;36m➡️ Updating description...\033[0m")
                await conv.send_message("/setdescription")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                await conv.send_message(bot_bio)
                await asyncio.sleep(2)
                
            if needs_about:
                print("\033[1;36m➡️ Updating about text...\033[0m")
                await conv.send_message("/setabouttext")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                await conv.send_message(bot_about)
                await asyncio.sleep(2)
                
        print("\033[1;32m✅ Bot successfully updated via BotFather\033[0m")
        return True
        
    except Exception as e:
        print(f"\033[1;31m❌ Failed to configure bot via BotFather: {e}\033[0m")
        print("\033[1;33m⚠️ Please configure bot manually through @BotFather if necessary.\033[0m")
        return False

async def update_bot_profile_picture(bot_client, user_client):
    """Update bot profile picture using cipher.jpg if it doesn't have one already"""
    try:
        print("\033[1;34m🔍 Checking bot profile picture status...\033[0m")
        current_photos = await bot_client.get_profile_photos('me', limit=1)
        
        if current_photos:
            print("\033[1;32m✅ Bot already has a profile picture - Skipping upload\033[0m")
            return True

        cipher_image_path = Path(__file__).parent.parent / "images" / "cipher.jpg"
        
        if not cipher_image_path.exists():
            print(f"\033[1;31m❌ cipher.jpg not found at: {cipher_image_path}\033[0m")
            return False
        
        print(f"\033[1;33m📸 No profile picture found. Uploading from: {cipher_image_path}\033[0m")
        file = await bot_client.upload_file(str(cipher_image_path))
        await bot_client(UploadProfilePhotoRequest(file=file))
        
        print(f"\033[1;32m✅ Bot profile picture successfully updated with cipher.jpg\033[0m")
        return True
        
    except Exception as e:
        print(f"\033[1;31m❌ Failed to update bot profile picture: {e}\033[0m")
        return False

async def ensure_bot_in_group(bot_client, user_client, log_chat_id):
    """Ensure bot is in logger group and has admin privileges"""
    try:
        bot_me = await bot_client.get_me()
        bot_id = bot_me.id
        bot_username = bot_me.username
        
        chat = await user_client.get_entity(log_chat_id)
        
        is_bot_in_group = False
        is_bot_admin = False
        
        try:
            async for participant in user_client.iter_participants(chat):
                if participant.id == bot_id:
                    is_bot_in_group = True
                    perms = await user_client.get_permissions(chat, participant)
                    if perms.is_admin:
                        is_bot_admin = True
                    break
        except Exception as e:
            is_bot_in_group = False
            
        if not is_bot_in_group:
            print(f"\033[1;33mAdding bot to logger group ({log_chat_id})...\033[0m")
            try:
                await user_client(InviteToChannelRequest(
                    channel=chat,
                    users=[bot_username] if bot_username else [bot_id]
                ))
                await asyncio.sleep(3)
                is_bot_in_group = True
            except UserAlreadyParticipantError:
                is_bot_in_group = True
            except Exception as e:
                return False
        
        if is_bot_in_group and not is_bot_admin:
            print(f"\033[1;33mMaking bot admin in logger group ({log_chat_id})...\033[0m")
            try:
                admin_rights = ChatAdminRights(
                    post_messages=True, add_admins=False, invite_users=True,
                    change_info=False, ban_users=True, delete_messages=True,
                    pin_messages=True, edit_messages=True, manage_call=True, other=True
                )
                await user_client(EditAdminRequest(
                    channel=chat,
                    user_id=bot_username if bot_username else bot_id,
                    admin_rights=admin_rights,
                    rank="Cipher Elite Bot"
                ))
                return True
            except Exception as e:
                return False
        
        return True
        
    except ChatAdminRequiredError:
        return False
    except Exception as e:
        return False

async def send_startup_message(bot_client, user_client, plugins, bot_plugins, system_info, config):
    if not getattr(config, 'LOG_CHAT_ID', None):
        return

    try:
        await ensure_bot_in_group(bot_client, user_client, config.LOG_CHAT_ID)
        user = await user_client.get_me()
        bot_me = await bot_client.get_me()
        
        message = (
            "=====================\n"
            "**CIPHER ELITE USERBOT**\n"
            "=====================\n"
            f"**Status**: ONLINE\n"
            f"**User**: {user.first_name} (`{user.id}`)\n"
            f"**Bot**: {bot_me.first_name} (`{bot_me.id}`)\n"
            f"**Python**: v{system_info['python']}\n"
            f"**Telethon**: v{system_info['telethon']}\n"
            f"**OS**: {system_info['os']}\n"
            f"**Plugins**: {len(plugins)} UB | {len(bot_plugins)} Bot\n"
            f"**Started**: {system_info['uptime']}\n"
            "=====================\n"
            "**Elite Power Activated!**"
        )
        
        buttons = [[Button.url("Support", "https://t.me/thanosprosss")]]
        logo_url = "https://files.catbox.moe/tocisn.png"
        
        try:
            chat_entity = await user_client.get_entity(config.LOG_CHAT_ID)
            try:
                bot_chat_entity = await bot_client.get_entity(config.LOG_CHAT_ID)
            except Exception:
                bot_chat_entity = chat_entity
            
            await bot_client.send_message(bot_chat_entity, message, file=logo_url, buttons=buttons)
        except Exception:
            await bot_client.send_message(config.LOG_CHAT_ID, message, file=logo_url, buttons=buttons)
            
    except Exception as e:
        print(f"\033[1;31mError sending startup message: {e}\033[0m")

async def start_bot(client):
    print("\n\033[1;36m==================================================")
    print("      Initializing CIPHER ELITE USERBOT")
    print("==================================================\033[0m\n")

    required_configs = [
        (client.api_id, "API_ID"),
        (client.api_hash, "API_HASH"),
        (client.session, "STRING_SESSION")
    ]
    for value, name in required_configs:
        if not value:
            raise ValueError(f"Configuration error: {name} is not set")

    await client.start()
    init_client(client)

    for url, name in [
        ("https://t.me/THANOS_PRO", "channel"),
        ("https://t.me/cipherelite_support", "group")
    ]:
        try:
            await client(JoinChannelRequest(url))
            print(f"\033[1;32mJoined {name}: {url}\033[0m")
        except Exception as e:
            pass # Keep terminal clean on join fails

    bot = await init_bot(client)
    bot_plugins = [] # Initialize empty list for scope
    
    if not bot:
        print("\033[1;31mFailed to initialize bot client. Startup message won't be sent.\033[0m")
    else:
        bot_me = await bot.get_me()
        print(f"\033[1;32mBot client initialized: @{bot_me.username}\033[0m")
        
        print("\033[1;33m🔄 Configuring bot via BotFather...\033[0m")
        await configure_bot_via_botfather(client, bot_me.username)
        
        print("\033[1;33m🔄 Updating bot profile picture...\033[0m")
        await update_bot_profile_picture(bot, client)

    print("\033[1;33mLoading Userbot plugins...\033[0m")
    plugins = await load_plugins(client)

    # --- Load Bot Plugins (e.g., assistant.py) ---
    if bot:
        print("\033[1;33mLoading Bot plugins...\033[0m")
        bot_plugins = await load_bot_plugins(bot, client)

    system_info = await display_startup_message(client, plugins, bot_plugins)
    
    from config.config import Config
    if bot:
        await send_startup_message(bot, client, plugins, bot_plugins, system_info, Config)

    print("\033[1;32mCipher Elite is ready and serving!\033[0m")
    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected() if bot else asyncio.sleep(float('inf'))
    )
