from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import logging
from pathlib import Path
import importlib
import time
import platform
import sys
import os
from datetime import datetime
from config.config import Config
from utils.utils import init_client
from plugins.bot import init_bot

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

# Initialize with StringSession
client = TelegramClient(
    StringSession(Config.STRING_SESSION),
    Config.API_ID,
    Config.API_HASH
)

async def load_plugins():
    path    = Path(__file__).parent / "plugins"
    plugins = [f"plugins.{f.stem}" for f in path.glob("*.py") if f.stem != "__init__"]

    loaded_plugins = []
    for plugin_name in plugins:
        module = importlib.import_module(plugin_name)
        module.init(client)
        if hasattr(module, "register_commands"):
            await module.register_commands()

        loaded_plugins.append(plugin_name.split(".")[-1])
        print(f"Loaded plugin: {plugin_name.split('.')[-1]}")

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

async def display_startup_message(plugins):
    """Display beautiful startup message in terminal"""
    system_info = await generate_startup_info()
    
    terminal_banner = f"""
\033[1;36m┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                     \033[1;33m𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐋𝐈𝐓𝐄 𝐔𝐒𝐄𝐑𝐁𝐎𝐓\033[1;36m                        ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ \033[1;32m▶ Status      : \033[1;32mONLINE                                        \033[1;36m┃
┃ \033[1;32m▶ Python      : \033[1;37mv{system_info["python"]}                                      \033[1;36m┃
┃ \033[1;32m▶ Telethon    : \033[1;37mv{system_info["telethon"]}                                      \033[1;36m┃
┃ \033[1;32m▶ OS          : \033[1;37m{system_info["os"]}                          \033[1;36m┃
┃ \033[1;32m▶ Plugins     : \033[1;37m{len(plugins)} loaded                                  \033[1;36m┃
┃ \033[1;32m▶ User        : \033[1;37m{(await client.get_me()).first_name}                                 \033[1;36m┃
┃ \033[1;32m▶ Started at  : \033[1;37m{system_info["uptime"]}                           \033[1;36m┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    \033[0m"""
    
    print(terminal_banner)
    return system_info

async def send_startup_message(plugins, system_info):
    """Send a beautiful startup message to LOG_CHAT_ID"""
    if not hasattr(Config, 'LOG_CHAT_ID') or not Config.LOG_CHAT_ID:
        print("\033[1;33mWarning: LOG_CHAT_ID not set. Startup message not sent to any chat.\033[0m")
        return
    
    try:
        user = await client.get_me()
        
        # Create a beautiful markdown message
        message = f"""
**╔══════ CIPHER ELITE USERBOT ══════╗**

✅ **Bot Successfully Deployed!**

**User:** `{user.first_name}`
**ID:** `{user.id}`
**Python:** `v{system_info['python']}`
**Telethon:** `v{system_info['telethon']}`
**OS:** `{system_info['os']}`
**Started at:** `{system_info['uptime']}`

**✨ {len(plugins)} Plugins Loaded:**
`{', '.join(plugins[:15])}{', ...' if len(plugins) > 15 else ''}`

**╚═══════════════════════════╝**
"""
        
        await client.send_message(Config.LOG_CHAT_ID, message)
    except Exception as e:
        print(f"\033[1;31mError sending startup message: {e}\033[0m")

async def start_bot():
    await client.start()
    init_client(client)
    bot = await init_bot()

    print("Loading plugins…")
    plugins = await load_plugins()

    system_info = await display_startup_message(plugins)
    await send_startup_message(plugins, system_info)

    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(start_bot
