import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from config.config import Config
from startup.startup import start_bot

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

# Initialize Telegram client
# main.py
client = TelegramClient(
    StringSession(Config.STRING_SESSION),  # REMOVE thanos_protect!
    Config.API_ID,
    Config.API_HASH
)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(start_bot(client))
