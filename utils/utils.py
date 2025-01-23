from telethon import TelegramClient

CipherElite = None

def init_client(client_instance):
    global CipherElite
    CipherElite = client_instance
    