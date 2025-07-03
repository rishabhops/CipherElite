import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from config.config import Config
from utils.thanos import thanos_protect
from startup.startup import start_bot

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

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
