import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from config.config import Config
from utils.thanos import thanos_protect
from startup.startup import start_bot
from core.console import ColourFormatter

logging.basicConfig(
    level=logging.WARNING,
    handlers=[logging.StreamHandler()]
)
logging.getLogger().handlers[0].setFormatter(ColourFormatter("cipherelite")())

# Initialize Telegram client
eliteses = thanos_protect(Config.STRING_SESSION)
client = TelegramClient(
    StringSession(eliteses),
    Config.API_ID,
    Config.API_HASH
)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(start_bot(client))
