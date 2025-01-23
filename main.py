
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import logging
from pathlib import Path
import importlib
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
    path = Path(__file__).parent / "plugins"
    plugins = [f"plugins.{f.stem}" for f in path.glob("*.py") if f.stem != "__init__"]
    
    for plugin_name in plugins:
        module = importlib.import_module(plugin_name)
        module.init(client)
        if hasattr(module, 'register_commands'):
            await module.register_commands()
        print(f"Loaded plugin: {plugin_name.split('.')[-1]}")

async def start_bot():
    print("\n==================================================")
    print("      CIPHER ELITE USERBOT")
    print("==================================================\n")
    
    await client.start()
    init_client(client)
    bot = await init_bot()
    await load_plugins()
    print("Cipher Elite is ready!")
    
    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(start_bot())
        