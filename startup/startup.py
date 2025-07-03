import importlib
import platform
import asyncio
from datetime import datetime
from pathlib import Path
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from telethon import Button
from telethon.errors import UserNotParticipantError, UserAlreadyParticipantError, ChatAdminRequiredError
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

async def ensure_bot_in_group(bot_client, user_client, log_chat_id):
    """Ensure bot is in logger group and has admin privileges"""
    try:
        # Get bot information
        bot_me = await bot_client.get_me()
        bot_id = bot_me.id
        bot_username = bot_me.username
        
        print(f"\033[1;33mBot info: @{bot_username} (ID: {bot_id})\033[0m")
        
        # Get the logger group entity
        chat = await user_client.get_entity(log_chat_id)
        
        # Check if bot is in the group
        is_bot_in_group = False
        try:
            # Try to get bot permissions in the group
            bot_perms = await user_client.get_permissions(chat, bot_me)
            is_bot_in_group = True
            print(f"\033[1;32mBot is already in logger group ({log_chat_id})\033[0m")
            
            # Check if bot is already an admin
            if bot_perms.is_admin:
                print(f"\033[1;32mBot is already an admin in logger group\033[0m")
                return True
                
        except (UserNotParticipantError, ValueError, TypeError) as e:
            print(f"\033[1;33mBot is not in logger group. Error: {e}\033[0m")
            is_bot_in_group = False
            
        # Add bot to group if not present
        if not is_bot_in_group:
            print(f"\033[1;33mAdding bot to logger group ({log_chat_id})...\033[0m")
            try:
                # Use bot username instead of ID for invitation
                await user_client(InviteToChannelRequest(
                    channel=chat,
                    users=[bot_username]  # Use username instead of ID
                ))
                print(f"\033[1;32mBot added to logger group ({log_chat_id})\033[0m")
                await asyncio.sleep(3)  # Wait longer for group to update
                
            except UserAlreadyParticipantError:
                print(f"\033[1;32mBot was already in the group\033[0m")
            except Exception as e:
                print(f"\033[1;31mFailed to add bot to group: {e}\033[0m")
                # Try alternative method using bot ID
                try:
                    await user_client(InviteToChannelRequest(
                        channel=chat,
                        users=[bot_id]
                    ))
                    print(f"\033[1;32mBot added to logger group using ID\033[0m")
                    await asyncio.sleep(3)
                except Exception as e2:
                    print(f"\033[1;31mFailed to add bot using ID: {e2}\033[0m")
                    return False
        
        # Now promote bot to admin
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
                user_id=bot_username,  # Use username instead of ID
                admin_rights=admin_rights,
                rank="Cipher Elite Bot"
            ))
            print(f"\033[1;32mBot promoted to admin in logger group ({log_chat_id})\033[0m")
            return True
            
        except Exception as e:
            print(f"\033[1;31mFailed to promote bot to admin using username: {e}\033[0m")
            # Try with bot ID as fallback
            try:
                await user_client(EditAdminRequest(
                    channel=chat,
                    user_id=bot_id,
                    admin_rights=admin_rights,
                    rank="Cipher Elite Bot"
                ))
                print(f"\033[1;32mBot promoted to admin using ID\033[0m")
                return True
            except Exception as e2:
                print(f"\033[1;31mFailed to promote bot to admin using ID: {e2}\033[0m")
                return False
        
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
        if not await ensure_bot_in_group(bot_client, user_client, config.LOG_CHAT_ID):
            print("\033[1;33mSkipping startup message due to bot setup issues\033[0m")
            return
            
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
        
        # Send message using bot client
        await bot_client.send_message(
            config.LOG_CHAT_ID,
            message,
            file=logo_url,
            buttons=buttons
        )
        print(f"\033[1;32mStartup message sent to LOG_CHAT_ID ({config.LOG_CHAT_ID}) using bot token\033[0m")
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
