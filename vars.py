from dotenv import load_dotenv
import os


load_dotenv()

# api Configuration
API_ID = int(os.getenv("API_ID", "10248430"))  
API_HASH = os.getenv("API_HASH", "42396a6ff14a569b9d59931643897d0d")  
#Please generate a session using @elite_session_maker_bot else your session not working 
TELETHON_SESSION = os.getenv("TELETHON_SESSION", "INVALID_SESSION")  
# Bot Settings
ELITE_BOT_PREFIX = os.getenv("ELITE_BOT_PREFIX", ".")
BOT_TOKEN = os.getenv("BOT_TOKEN", "INVALID_BOT_TOKEN")
ELITE_BOT_USERNAME = os.getenv("ELITE_BOT_USERNAME", "@InvalidBotUsername")

# Access Control
SUDO_USERS = [int(x) for x in os.getenv("SUDO_USERS", "5470956337").split(",") if x.strip()]
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "0"))

# Image URLs
PMPERMIT_PIC = os.getenv("PMPERMIT_PIC", "https://files.catbox.moe/tocisn.png")  
ALIVE_PIC = os.getenv("ALIVE_PIC", "https://files.catbox.moe/tocisn.png") 
PING_PIC = os.getenv("PING_PIC", "https://files.catbox.moe/tocisn.png")

# Update Configuration
UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "https://github.com/rishabhops/CipherElite")
BRANCH = os.getenv("BRANCH", "elite")

# for  debugging dont edit this
if API_ID == 0:
    print("Warning: API_ID is not set. Please update .env with a valid API_ID.")
if API_HASH == "INVALID_API_HASH":
    print("Warning: API_HASH is not set. Please update .env with a valid API_HASH.")
if ELITE_SESSION == "INVALID_SESSION":
    print("Warning: ELITE_SESSION is not set. Please generate a session using @elite_session_maker_bot.")
if BOT_TOKEN == "INVALID_BOT_TOKEN":
    print("Warning: BOT_TOKEN is not set. Please update .env with a valid bot token from @BotFather.")
if ELITE_BOT_USERNAME == "@InvalidBotUsername":
    print("Warning: ELITE_BOT_USERNAME is not set. Please update .env with your bot username.")
if SUDO_USERS == [0]:
    print("Warning: SUDO_USERS is not set. Please update .env with valid Telegram user ID(s).")
if LOG_CHAT_ID == 0:
    print("Warning: LOG_CHAT_ID is not set. Please update .env with a valid logger group ID.")
