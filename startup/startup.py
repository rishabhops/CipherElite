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
from plugins.bot import init_bot
from utils.utils import init_client

async def load_plugins(client):
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

async def display_startup_message(client, plugins):
    system_info = await generate_startup_info()
    user_name = (await client.get_me()).first_name
    banner = f"""
\033[1;36m=====================
 CIPHER ELITE USERBOT
=====================
\033[1;32mStatus  : ONLINE
Python  : v{system_info["python"]}
Telethon: v{system_info["telethon"]}
OS      : {system_info["os"]}
Plugins : {len(plugins)} loaded
User    : {user_name}
Started : {system_info["uptime"]}
\033[1;36m=====================
\033[1;33mElite Power Activated!\033[0m
"""
    print(banner)
    return system_info

async def configure_bot_via_botfather(user_client, bot_username):
    """Automatically configure bot through BotFather using user account"""
    botfather_id = 93372553  # BotFather's user ID
    user = await user_client.get_me()
    user_first_name = user.first_name
    
    # Define bot configuration
    bot_name = f"{user_first_name}'s Assistant"
    bot_bio = (
        f"🤖 Personal Assistant Bot for {user_first_name}\n\n"
        "🔰 Cipher Elite Userbot Assistant\n"
        "⚡ Powered by thanospros\n"
        "🛡️ Advanced Automation & Management\n\n"
        "🔗 Support: @thanosprosss"
    )
    
    print(f"\033[1;33mConfiguring bot @{bot_username} via BotFather...\033[0m")
    
    try:
        # Start conversation with BotFather
        await user_client.send_message(botfather_id, "/start")
        await asyncio.sleep(1)
        
        # Select the bot to configure
        await user_client.send_message(botfather_id, "/setcommands")
        await asyncio.sleep(1)
        await user_client.send_message(botfather_id, f"@{bot_username}")
        await asyncio.sleep(1)
        
        # Set bot commands
        commands = [
            "start - Start the bot",
            "help - Show help information",
            "ping - Check bot responsiveness",
            "status - Show system status"
        ]
        await user_client.send_message(botfather_id, "\n".join(commands))
        await asyncio.sleep(2)
        
        # Set bot name
        await user_client.send_message(botfather_id, "/setname")
        await asyncio.sleep(1)
        await user_client.send_message(botfather_id, f"@{bot_username}")
        await asyncio.sleep(1)
        await user_client.send_message(botfather_id, bot_name)
        await asyncio.sleep(2)
        
        # Set bot description
        await user_client.send_message(botfather_id, "/setdescription")
        await asyncio.sleep(1)
        await user_client.send_message(botfather_id, f"@{bot_username}")
        await asyncio.sleep(1)
        await user_client.send_message(botfather_id, bot_bio)
        await asyncio.sleep(2)
        
        # Set bot about text
        await user_client.send_message(botfather_id, "/setabouttext")
        await asyncio.sleep(1)
        await user_client.send_message(botfather_id, f"@{bot_username}")
        await asyncio.sleep(1)
        await user_client.send_message(botfather_id, bot_bio)
        await asyncio.sleep(2)
        
        print("\033[1;32m✅ Bot successfully configured via BotFather\033[0m")
        return True
        
    except Exception as e:
        print(f"\033[1;31m❌ Failed to configure bot via BotFather: {e}\033[0m")
        return False

async def update_bot_profile_picture(bot_client, user_client):
    """Update bot profile picture using cipher.jpg from images folder"""
    try:
        # Path to the cipher.jpg image
        cipher_image_path = Path(__file__).parent.parent / "images" / "cipher.jpg"
        
        if not cipher_image_path.exists():
            print(f"\033[1;31m❌ cipher.jpg not found at: {cipher_image_path}\033[0m")
            print(f"\033[1;33m💡 Please ensure cipher.jpg exists in the images folder\033[0m")
            return
        
        print(f"\033[1;33m📸 Found cipher.jpg at: {cipher_image_path}\033[0m")
        
        # Upload cipher.jpg as bot profile picture
        with open(cipher_image_path, 'rb') as f:
            file = await bot_client.upload_file(f)
            await bot_client(UploadProfilePhotoRequest(file=file))
        
        print(f"\033[1;32m✅ Bot profile picture updated with cipher.jpg\033[0m")
        
    except Exception as e:
        print(f"\033[1;31m❌ Failed to update bot profile picture: {e}\033[0m")

async def ensure_bot_in_group(bot_client, user_client, log_chat_id):
    """Ensure bot is in logger group and has admin privileges"""
    try:
        # Get bot information
        bot_me = await bot_client.get_me()
        bot_id = bot_me.id
        bot_username = bot_me.username
        
        print(f"\033[1;33mBot info: @{bot_username} (ID: {bot_id})\033[0m")
        
        # Get the logger group entity using user client
        chat = await user_client.get_entity(log_chat_id)
        print(f"\033[1;33mGroup info: {chat.title} (ID: {chat.id})\033[0m")
        
        # Check if bot is actually in the group by getting all participants
        is_bot_in_group = False
        is_bot_admin = False
        
        try:
            # Get all participants to check if bot is really there
            async for participant in user_client.iter_participants(chat):
                if participant.id == bot_id:
                    is_bot_in_group = True
                    # Check if bot has admin rights
                    perms = await user_client.get_permissions(chat, participant)
                    if perms.is_admin:
                        is_bot_admin = True
                        print(f"\033[1;32mBot is in group and is admin\033[0m")
                    else:
                        print(f"\033[1;33mBot is in group but not admin\033[0m")
                    break
                    
            if not is_bot_in_group:
                print(f"\033[1;33mBot is NOT in the group\033[0m")
                
        except Exception as e:
            print(f"\033[1;31mError checking bot participation: {e}\033[0m")
            is_bot_in_group = False
            
        # Add bot to group if not present
        if not is_bot_in_group:
            print(f"\033[1;33mAdding bot to logger group ({log_chat_id})...\033[0m")
            try:
                # Use bot username for invitation
                await user_client(InviteToChannelRequest(
                    channel=chat,
                    users=[bot_username] if bot_username else [bot_id]
                ))
                print(f"\033[1;32mBot added to logger group ({log_chat_id})\033[0m")
                await asyncio.sleep(3)  # Wait for group to update
                is_bot_in_group = True
                
            except UserAlreadyParticipantError:
                print(f"\033[1;32mBot was already in the group\033[0m")
                is_bot_in_group = True
            except Exception as e:
                print(f"\033[1;31mFailed to add bot to group: {e}\033[0m")
                return False
        
        # Promote bot to admin if not already admin
        if is_bot_in_group and not is_bot_admin:
            print(f"\033[1;33mMaking bot admin in logger group ({log_chat_id})...\033[0m")
            try:
                admin_rights = ChatAdminRights(
                    post_messages=True,
                    add_admins=False,
                    invite_users=True,
                    change_info=False,
                    ban_users=True,
                    delete_messages=True,
                    pin_messages=True,
                    edit_messages=True,
                    manage_call=True,
                    other=True
                )
                
                # Use bot username for admin promotion
                await user_client(EditAdminRequest(
                    channel=chat,
                    user_id=bot_username if bot_username else bot_id,
                    admin_rights=admin_rights,
                    rank="Cipher Elite Bot"
                ))
                print(f"\033[1;32mBot promoted to admin in logger group ({log_chat_id})\033[0m")
                return True
                
            except Exception as e:
                print(f"\033[1;31mFailed to promote bot to admin: {e}\033[0m")
                return False
        
        return True
        
    except ChatAdminRequiredError:
        print(f"\033[1;31mError: You need admin privileges in the logger group to add/promote the bot\033[0m")
        return False
    except Exception as e:
        print(f"\033[1;31mFailed to add/make bot admin in logger group: {e}\033[0m")
        return False

async def send_startup_message(bot_client, user_client, plugins, system_info, config):
    if not getattr(config, 'LOG_CHAT_ID', None):
        print(
            "\033[1;33mWarning: LOG_CHAT_ID not set."
            " Startup message not sent.\033[0m"
        )
        return

    try:
        # Ensure bot is in logger group and has admin rights
        bot_setup_success = await ensure_bot_in_group(bot_client, user_client, config.LOG_CHAT_ID)
        if not bot_setup_success:
            print("\033[1;33mBot setup failed, but trying to send startup message anyway\033[0m")
        
        # Get user info from user client
        user = await user_client.get_me()
        
        # Create message with bot info
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
            f"**Plugins**: {len(plugins)} loaded\n"
            f"**Started**: {system_info['uptime']}\n"
            "=====================\n"
            "**Elite Power Activated!**"
        )
        
        # Create button with support link
        buttons = [[Button.url("Support", "https://t.me/thanosprosss")]]
        logo_url = "https://files.catbox.moe/tocisn.png"
        
        # Try to get the group entity through user client first, then share it with bot
        try:
            # Get group entity from user client
            chat_entity = await user_client.get_entity(config.LOG_CHAT_ID)
            print(f"\033[1;33mGot group entity from user client: {chat_entity.title}\033[0m")
            
            # Try to get the same entity with bot client
            # This forces the bot client to cache the entity
            try:
                bot_chat_entity = await bot_client.get_entity(config.LOG_CHAT_ID)
                print(f"\033[1;32mBot client found group entity: {bot_chat_entity.title}\033[0m")
            except Exception as e:
                print(f"\033[1;33mBot client couldn't find group entity directly: {e}\033[0m")
                # Try using the entity from user client
                bot_chat_entity = chat_entity
            
            # Send message using bot client
            await bot_client.send_message(
                bot_chat_entity,
                message,
                file=logo_url,
                buttons=buttons
            )
            print(f"\033[1;32mStartup message sent to LOG_CHAT_ID ({config.LOG_CHAT_ID}) using bot token\033[0m")
            
        except Exception as entity_error:
            print(f"\033[1;31mFailed to get group entity: {entity_error}\033[0m")
            print(f"\033[1;33mTrying to send message using LOG_CHAT_ID directly\033[0m")
            
            # Last resort: try sending directly with the chat ID
            await bot_client.send_message(
                config.LOG_CHAT_ID,
                message,
                file=logo_url,
                buttons=buttons
            )
            print(f"\033[1;32mStartup message sent using direct chat ID\033[0m")
            
    except Exception as e:
        print(f"\033[1;31mError sending startup message: {e}\033[0m")

async def start_bot(client):
    print("\n\033[1;36m==================================================")
    print("      Initializing CIPHER ELITE USERBOT")
    print("==================================================\033[0m\n")

    # Validate configuration
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

    # Join group and channel with better error handling
    for url, name in [
        ("https://t.me/THANOS_PRO", "Group"),
        ("https://t.me/thanosprosss", "Channel")
    ]:
        try:
            await client(JoinChannelRequest(url))
            print(f"\033[1;32mJoined {name}: {url}\033[0m")
        except Exception as e:
            print(f"\033[1;31mFailed to join {name} {url}: {e}\033[0m")

    # Initialize bot client using BOT_TOKEN
    bot = await init_bot()
    if not bot:
        print("\033[1;31mFailed to initialize bot client. Startup message won't be sent.\033[0m")
    else:
        # Ensure bot is properly connected
        bot_me = await bot.get_me()
        print(f"\033[1;32mBot client initialized: @{bot_me.username}\033[0m")
        
        # Configure bot through BotFather using user account
        print("\033[1;33m🔄 Configuring bot via BotFather...\033[0m")
        await configure_bot_via_botfather(client, bot_me.username)
        
        # Update bot profile picture
        print("\033[1;33m🔄 Updating bot profile picture...\033[0m")
        await update_bot_profile_picture(bot, client)

    print("\033[1;33mLoading plugins...\033[0m")
    plugins = await load_plugins(client)

    system_info = await display_startup_message(client, plugins)
    
    from config.config import Config
    if bot:
        await send_startup_message(bot, client, plugins, system_info, Config)
    else:
        print("\033[1;33mSkipping startup message send due to missing bot client\033[0m")

    print("\033[1;32mCipher Elite is ready and serving!\033[0m")
    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected() if bot else asyncio.sleep(float('inf'))
    )
