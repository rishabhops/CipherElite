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

from plugins.bot import init_bot, CMD_LIST
from utils.utils import init_client
from core.console import (
    banner, box, rule, step, ok, fail, warn, info,
    blockquote, panel,
    RESET, BOLD, DIM, RED, GREEN, YELLOW, BLUE, PURPLE, CYAN, GREY
)


async def init_database():
    try:
        from DB.database import init_db, USE_MONGO
        await init_db()
        from DB.database import USE_MONGO as updated_use_mongo
        if updated_use_mongo:
            return "MongoDB"
        return "Local JSON"
    except Exception as e:
        warn(f"Database init error: {e}")
        return "Local JSON (fallback)"


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
            name = plugin_name.split(".")[-1]
            version = getattr(module, "VERSION", None)
            loaded_plugins.append(name)
            ver_str = f"{DIM}v{version}{RESET}" if version else ""
            ok(f"{name}  {ver_str}")
        except Exception as e:
            fail(f"{plugin_name}  {DIM}- {str(e)[:50]}{RESET}")
    return loaded_plugins


async def load_bot_plugins(bot_client, user_client):
    path = Path(__file__).parent.parent / "bot_plugins"
    
    if not path.exists():
        warn("Directory 'bot_plugins' not found. Skipping bot plugins.")
        return []

    owner = await user_client.get_me()
    owner_id = owner.id
    owner_name = owner.first_name or "Owner"
    
    from config.config import Config
    Config.OWNER_ID = owner_id

    plugins = [
        f"bot_plugins.{f.stem}"
        for f in path.glob("*.py")
        if f.stem != "__init__"
    ]

    loaded_bot_plugins = []
    # Guard to avoid loading bot plugins twice if plugins/bot.py also loads them
    if not hasattr(bot_client, "_loaded_bot_plugins"):
        bot_client._loaded_bot_plugins = set()

    for plugin_name in plugins:
        try:
            name = plugin_name.split(".")[-1]
            
            # Already loaded by plugins/bot.py; just count it, don't re-initialize
            if plugin_name in bot_client._loaded_bot_plugins:
                loaded_bot_plugins.append(name)
                continue
            
            module = importlib.import_module(plugin_name)
            
            if hasattr(module, "init_bot_plugin"):
                if asyncio.iscoroutinefunction(module.init_bot_plugin):
                    await module.init_bot_plugin(bot_client, owner_id, owner_name)
                else:
                    module.init_bot_plugin(bot_client, owner_id, owner_name)
                
                bot_client._loaded_bot_plugins.add(plugin_name)
                version = getattr(module, "VERSION", None)
                loaded_bot_plugins.append(name)
                ver_str = f"{DIM}v{version}{RESET}" if version else ""
                ok(f"{name}  {ver_str}")
            else:
                warn(f"{plugin_name} is missing init_bot_plugin()")
                
        except Exception as e:
            fail(f"{plugin_name}  {DIM}- {str(e)[:50]}{RESET}")
            
    return loaded_bot_plugins


async def generate_startup_info():
    python_version = platform.python_version()
    telethon_version = importlib.import_module("telethon").__version__
    os_info = f"{platform.system()} {platform.release()}"
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    from config.config import Config
    return {
        "python": python_version,
        "telethon": telethon_version,
        "os": os_info,
        "uptime": uptime,
        "version": Config.VERSION,
        "branch": getattr(Config, "BRANCH", "main"),
    }


async def display_startup_message(client, plugins, bot_plugins, db_type):
    system_info = await generate_startup_info()
    user = await client.get_me()
    user_name = user.first_name
    user_id = user.id

    total_commands = 0
    for p in CMD_LIST.values():
        total_commands += len(p.get("commands", []))

    print()

    panel(
        "CIPHER ELITE USERBOT",
        [
            ("Status", f"{GREEN}{BOLD}ONLINE{RESET}"),
            ("Version", f"v{system_info['version']}"),
            ("Branch", f"{system_info['branch']}"),
            ("User", f"{user_name} {DIM}(@{user.username}){RESET}" if user.username else user_name),
            ("User ID", f"{DIM}{user_id}{RESET}"),
            ("Python", f"v{system_info['python']}"),
            ("Telethon", f"v{system_info['telethon']}"),
            ("OS", system_info['os']),
            ("Database", f"{CYAN}{db_type}{RESET}"),
            ("Plugins", f"{len(plugins)} Userbot  ·  {len(bot_plugins)} Bot"),
            ("Commands", f"{total_commands}"),
            ("Started", f"{DIM}{system_info['uptime']}{RESET}"),
        ],
        CYAN,
    )

    print()
    blockquote(
        [
            f"{GREEN}✔{RESET} Userbot connected",
            f"{GREEN}✔{RESET} Assistant bot initialized",
            f"{GREEN}✔{RESET} Database ready ({db_type})",
            f"{GREEN}✔{RESET} {len(plugins)} userbot + {len(bot_plugins)} bot plugins loaded",
        ],
        _title=f"{BOLD}Launch Summary{RESET}",
        _colour=GREEN,
    )

    print()
    print(f"  {YELLOW}{BOLD}✦ Elite Power Activated!{RESET}")
    print()
    return system_info


async def configure_bot_via_botfather(user_client, bot_username):
    user = await user_client.get_me()
    user_first_name = user.first_name
    
    bot_name = f"{user_first_name}'s Assistant"
    bot_bio = (
        f"Personal Assistant Bot for {user_first_name}\n\n"
        "Cipher Elite Userbot Assistant\n"
        "Powered by thanospros\n"
        "Advanced Automation & Management\n\n"
        "Support: @thanosprosss"
    )
    bot_about = f"Assistant for {user_first_name} | Cipher Elite | @thanosprosss"
    
    desired_commands = {
        "start": "Start the bot",
        "help": "Show help information",
        "ping": "Check bot responsiveness",
        "status": "Show system status"
    }

    print()
    info(f"Checking current @{bot_username} settings...")
    
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
            ok("Bot settings are already up to date")
            return True
            
    except Exception as e:
        warn(f"Couldn't verify current bot settings: {e}")
        needs_name = needs_about = needs_description = needs_commands = True

    info(f"Configuring bot @{bot_username} via BotFather...")
    
    try:
        async with user_client.conversation('BotFather') as conv:
            if needs_commands:
                print(f"  {DIM}Updating commands...{RESET}")
                await conv.send_message("/setcommands")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                commands_str = "\n".join([f"{k} - {v}" for k, v in desired_commands.items()])
                await conv.send_message(commands_str)
                await asyncio.sleep(2)
                
            if needs_name:
                print(f"  {DIM}Updating name...{RESET}")
                await conv.send_message("/setname")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                await conv.send_message(bot_name)
                await asyncio.sleep(2)
                
            if needs_description:
                print(f"  {DIM}Updating description...{RESET}")
                await conv.send_message("/setdescription")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                await conv.send_message(bot_bio)
                await asyncio.sleep(2)
                
            if needs_about:
                print(f"  {DIM}Updating about text...{RESET}")
                await conv.send_message("/setabouttext")
                await asyncio.sleep(1)
                await conv.send_message(f"@{bot_username}")
                await asyncio.sleep(1)
                await conv.send_message(bot_about)
                await asyncio.sleep(2)
                
        ok("Bot successfully updated via BotFather")
        return True
        
    except Exception as e:
        fail(f"Failed to configure bot via BotFather: {e}")
        warn("Please configure bot manually through @BotFather if necessary.")
        return False


async def update_bot_profile_picture(bot_client, user_client):
    try:
        print()
        info("Checking bot profile picture status...")
        current_photos = await bot_client.get_profile_photos('me', limit=1)
        
        if current_photos:
            ok("Bot already has a profile picture")
            return True

        cipher_image_path = Path(__file__).parent.parent / "images" / "cipher.jpg"
        
        if not cipher_image_path.exists():
            fail(f"cipher.jpg not found at: {cipher_image_path}")
            return False
        
        print(f"  {DIM}Uploading profile picture...{RESET}")
        file = await bot_client.upload_file(str(cipher_image_path))
        await bot_client(UploadProfilePhotoRequest(file=file))
        
        ok("Bot profile picture successfully updated")
        return True
        
    except Exception as e:
        fail(f"Failed to update bot profile picture: {e}")
        return False


async def ensure_bot_in_group(bot_client, user_client, log_chat_id):
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
        except Exception:
            is_bot_in_group = False
            
        if not is_bot_in_group:
            print()
            info(f"Adding bot to logger group ({log_chat_id})...")
            try:
                await user_client(InviteToChannelRequest(
                    channel=chat,
                    users=[bot_username] if bot_username else [bot_id]
                ))
                await asyncio.sleep(3)
                is_bot_in_group = True
            except UserAlreadyParticipantError:
                is_bot_in_group = True
            except Exception:
                return False
        
        if is_bot_in_group and not is_bot_admin:
            print(f"  {DIM}Making bot admin in logger group...{RESET}")
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
            except Exception:
                return False
        
        return True
        
    except ChatAdminRequiredError:
        return False
    except Exception:
        return False


async def send_startup_message(bot_client, user_client, plugins, bot_plugins, system_info, config, db_type):
    if not getattr(config, 'LOG_CHAT_ID', None):
        return

    try:
        await ensure_bot_in_group(bot_client, user_client, config.LOG_CHAT_ID)
        user = await user_client.get_me()
        bot_me = await bot_client.get_me()
        
        total_commands = 0
        for p in CMD_LIST.values():
            total_commands += len(p.get("commands", []))

        user_link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        bot_link = f'<a href="tg://user?id={bot_me.id}">{bot_me.first_name}</a>'

        message = (
            f"✦ <b>{bot_me.first_name}</b> is online\n\n"
            f"<blockquote>\n"
            f"👤 <b>User:</b> {user_link} <code>{user.id}</code>\n"
            f"🤖 <b>Bot:</b> {bot_link} <code>{bot_me.id}</code>\n"
            f"📦 <b>Plugins:</b> {len(plugins)} Userbot · {len(bot_plugins)} Bot\n"
            f"⚙️ <b>Commands:</b> {total_commands}\n"
            f"🐍 <b>Python:</b> v{system_info['python']}\n"
            f"📡 <b>Telethon:</b> v{system_info['telethon']}\n"
            f"💾 <b>Database:</b> {db_type}\n"
            f"🖥 <b>OS:</b> {system_info['os']}\n"
            f"🌿 <b>Branch:</b> {system_info['branch']}\n"
            f"⏰ <b>Started:</b> {system_info['uptime']}\n"
            f"</blockquote>\n\n"
            f"<i>✨ Elite Power Activated!</i>"
        )
        
        buttons = [
            [Button.inline("🔞 Enable 18+ Mode", "enable_adult_mode")],
            [
                Button.url("📢 Updates", "https://t.me/THANOS_PRO"),
                Button.url("💬 Support", "https://t.me/thanosprosss"),
            ],
        ]
        logo_url = "https://files.catbox.moe/tocisn.png"
        
        try:
            chat_entity = await user_client.get_entity(config.LOG_CHAT_ID)
            try:
                bot_chat_entity = await bot_client.get_entity(config.LOG_CHAT_ID)
            except Exception:
                bot_chat_entity = chat_entity
            
            await bot_client.send_message(bot_chat_entity, message, file=logo_url, buttons=buttons, parse_mode='html')
        except Exception:
            await bot_client.send_message(config.LOG_CHAT_ID, message, file=logo_url, buttons=buttons, parse_mode='html')
            
    except Exception as e:
        fail(f"Error sending startup message: {e}")


async def start_bot(client):
    from config.config import Config
    
    banner(
        "CipherElite",
        Config.VERSION,
        "Rishabh Anand",
        "@thanosceo"
    )
    
    rule("initializing")
    print()

    required_configs = [
        (client.api_id, "API_ID"),
        (client.api_hash, "API_HASH"),
        (client.session, "STRING_SESSION")
    ]
    for value, name in required_configs:
        if not value:
            raise ValueError(f"Configuration error: {name} is not set")

    step("telegram", "Connecting to Telegram")
    await client.start()
    ok("Telegram client connected", "telegram")
    init_client(client)

    print()
    step("database", "Initializing Database")
    db_type = await init_database()
    if "MongoDB" in db_type:
        ok(f"Database: {GREEN}MongoDB{RESET}", "database")
    else:
        ok(f"Database: {YELLOW}Local JSON{RESET}", "database")

    print()
    info("Joining support channels...")
    for url, name in [
        ("https://t.me/THANOS_PRO", "channel"),
        ("https://t.me/cipherelite_support", "group")
    ]:
        try:
            await client(JoinChannelRequest(url))
            ok(f"Joined {name}: {url}")
        except Exception:
            pass

    print()
    step("bot", "Initializing bot client")
    bot = await init_bot(client)
    bot_plugins = []
    
    if not bot:
        fail("Failed to initialize bot client", "bot")
    else:
        bot_me = await bot.get_me()
        ok(f"Bot client initialized: @{bot_me.username}", "bot")
        
        print()
        rule("bot setup")
        print()
        await configure_bot_via_botfather(client, bot_me.username)
        await update_bot_profile_picture(bot, client)

    print()
    rule("loading plugins")
    print()
    info("Loading Userbot plugins...")
    plugins = await load_plugins(client)

    if bot:
        print()
        info("Loading Bot plugins...")
        bot_plugins = await load_bot_plugins(bot, client)

    print()
    rule("system ready")
    system_info = await display_startup_message(client, plugins, bot_plugins, db_type)
    
    if bot:
        await send_startup_message(bot, client, plugins, bot_plugins, system_info, Config, db_type)

    print(f"  {GREEN}{BOLD}Cipher Elite v{Config.VERSION} is ready!{RESET}")
    print()
    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected() if bot else asyncio.sleep(float('inf'))
    )
