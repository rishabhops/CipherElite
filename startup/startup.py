import importlib
import platform
import asyncio
from datetime import datetime
from pathlib import Path
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import Button  # Correct import for buttons
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

async def send_startup_message(client, plugins, system_info, config):
    if not getattr(config, 'LOG_CHAT_ID', None):
        print(
            "\033[1;33mWarning: LOG_CHAT_ID not set."
            " Startup message not sent.\033[0m"
        )
        return

    try:
        user = await client.get_me()
        message = (
            "=====================\n"
            "**CIPHER ELITE USERBOT**\n"
            "=====================\n"
            f"**Status**: ONLINE\n"
            f"**User**: {user.first_name} (`{user.id}`)\n"
            f"**Python**: v{system_info['python']}\n"
            f"**Telethon**: v{system_info['telethon']}\n"
            f"**OS**: {system_info['os']}\n"
            f"**Plugins**: {len(plugins)} loaded\n"
            f"**Started**: {system_info['uptime']}\n"
            "=====================\n"
            "**Elite Power Activated!**"
        )
        # Correct button construction
        buttons = [[Button.url("Support", "https://t.me/thanosprosss")]]
        logo_url = "https://files.catbox.moe/tocisn.png"
        
        # Send message with buttons using send_message instead of send_file
        await client.send_message(
            config.LOG_CHAT_ID,
            message,
            file=logo_url,
            buttons=buttons
        )
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

    bot = await init_bot()

    print("\033[1;33mLoading plugins...\033[0m")
    plugins = await load_plugins(client)

    system_info = await display_startup_message(client, plugins)
    from config.config import Config
    await send_startup_message(client, plugins, system_info, Config)

    print("\033[1;32mCipher Elite is ready and serving!\033[0m")
    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected()
    )
