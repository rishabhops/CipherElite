# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    alive
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from telethon import events, version, Button
from telethon.errors import BotInlineDisabledError
from plugins.bot import add_handler, CMD_LIST
from utils.utils import CipherElite
from utils.decorators import rishabh
from config.config import Config


try:
    from plugins.bot import bot 
except ImportError:
    try:
        from utils.utils import bot
    except ImportError:
        bot = None
        logging.warning("Could not import 'bot' client. Inline buttons for .alive will fail.")

PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
CONFIG_FILE = DB_DIR / "alive_config.json"


# ---------------------------------------------------------------------------
ALIVE_BUTTONS = [
    [
        Button.url("💬 Support", "https://t.me/cipherelitesupport"),
        Button.url("📢 Channel", "https://t.me/THANOS_PRO"),
    ]
]

class UserConfig:
    def __init__(self):
        self.alive_style_index = 0
        self.ping_style_index = 0
        self.custom_alive_text = None
        self.custom_ping_text = None
        self.alive_pic = DEFAULT_ALIVE_PIC
        self.ping_pic = DEFAULT_PING_PIC
        self.use_pic_for_alive = True
        self.use_pic_for_ping = True

    def to_dict(self):
        return self.__dict__

    def from_dict(self, data):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

# -- CONFIG PERSISTENCE --
user_config = UserConfig()

def load_config():
    if CONFIG_FILE.exists():
        try:
            user_config.from_dict(json.loads(CONFIG_FILE.read_text()))
        except Exception:
            pass

def save_config():
    try:
        CONFIG_FILE.write_text(json.dumps(user_config.to_dict(), indent=2))
    except Exception:
        pass

load_config()
# ------------------------

START_TIME = datetime.now()
DEFAULT_ALIVE_PIC = Config.DEFAULT_ALIVE_PIC
DEFAULT_PING_PIC = Config.DEFAULT_PING_PIC

# Globals to pass data from Userbot -> Inline Bot
LAST_ALIVE_DATA = {}
LAST_PING_DATA = {}

def get_readable_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d: return f"{d}d {h}h {m}m"
    if h: return f"{h}h {m}m"
    return f"{m}m {s}s"

ALIVE_STYLES = [
    r"""⚡ 𝘾𝙄𝙋𝙃𝙀𝙍 𝙀𝙇𝙄𝙏𝙀 𝙎𝙔𝙎𝙏𝙀𝙈 ⚡

▰▱▰▱▰▱▰▱▰▱▰▱▰▱
➺ 𝙈𝘼𝙎𝙏𝙀𝙍: {name}
➺ 𝙑𝙀𝙍𝙎𝙄𝙊𝙉: 1.0
➺ 𝙏𝙀𝙇𝙀𝙏𝙃𝙊𝙉: {telethon}
▰▱▰▱▰▱▰▱▰▱▰▱▰▱

⚔️ 𝙋𝙇𝙐𝙶𝙄𝙉𝙎: {plugins}
⚔️ 𝙐𝙋𝙏𝙄𝙈𝙀: {uptime}
⚔️ 𝘽𝙍𝘼𝙉𝘾𝙃: MASTER

▰▱▰▱ ELITE NETWORK ▰▱▰▱""",
    r"""╔══『 CIPHER ELITE 』══╗

◈ CODENAME: {name}
◈ VERSION: [1.0]
◈ TELETHON: [{telethon}]

▣ PLUGINS: {plugins}
▣ UPTIME: {uptime}
▣ STATUS: OPERATIONAL

╚══『 ELITE FORCE 』══╝""",
]

PING_STYLES = [
    r"""⚡ 𝙋𝙄𝙉𝙂 𝙎𝙏𝘼𝙏𝙐𝙎 ⚡

▰▱▰▱▰▱▰▱▰▱▰▱▰▱
➺ 𝙎𝙋𝙀𝙀𝘿: {speed}ms
➺ 𝙐𝙋𝙏𝙄𝙈𝙀: {uptime}
▰▱▰▱▰▱▰▱▰▱▰▱▰▱""",
    r"""╔══『 PING STATUS 』══╗

◈ SPEED: [{speed}ms]
◈ UPTIME: [{uptime}]

╚══『 CIPHER ELITE 』══╝""",
]

def init(client):
    commands = [".alive", ".ping"]
    add_handler("alive", commands, "Alive & Ping with Inline Buttons")

# ============================================================================
#  USERBOT HANDLERS (The Trigger)
# ============================================================================

@CipherElite.on(events.NewMessage(pattern=r"\.alive"))
@rishabh()
async def alive(event):
    # 1. Prepare Data
    uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
    template = user_config.custom_alive_text or ALIVE_STYLES[user_config.alive_style_index]
    text = template.format(
        name=event.sender.first_name,
        plugins=len(CMD_LIST),
        uptime=uptime,
        telethon=version.__version__,
    )
    
    # 2. Store data for the bot to read
    global LAST_ALIVE_DATA
    LAST_ALIVE_DATA = {
        "text": text,
        "media": user_config.alive_pic if user_config.use_pic_for_alive else None
    }

    # 3. Trigger Inline Query (Like help.py)
    if Config.TG_BOT_USERNAME:
        try:
            results = await event.client.inline_query(Config.TG_BOT_USERNAME, "alive")
            await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True
            )
            await event.delete()
        except BotInlineDisabledError:
            await event.reply("❌ **Inline Error:** Please enable Inline Mode in @BotFather for your assistant bot.")
        except Exception as e:
            await event.reply(f"❌ **Inline Error:** {e}\n(Fallback to text only)")
    else:
        await event.reply(text) # Fallback

@CipherElite.on(events.NewMessage(pattern=r"\.ping"))
@rishabh()
async def ping(event):
    start = datetime.now()
    # We calculate speed here, but we can't show "Pinging..." then delete it 
    # effectively with inline query. So we just calculate and send.
    speed = (datetime.now() - start).microseconds // 1000
    uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
    template = user_config.custom_ping_text or PING_STYLES[user_config.ping_style_index]
    text = template.format(speed=speed, uptime=uptime)

    global LAST_PING_DATA
    LAST_PING_DATA = {
        "text": text,
        "media": user_config.ping_pic if user_config.use_pic_for_ping else None
    }

    if Config.TG_BOT_USERNAME:
        try:
            results = await event.client.inline_query(Config.TG_BOT_USERNAME, "ping")
            await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True
            )
            await event.delete()
        except Exception as e:
            await event.reply(text)
    else:
        await event.reply(text)

# ============================================================================
#  BOT INLINE HANDLERS (The Response)
# ============================================================================
# This part registers the "alive" answer on your Assistant Bot.

if bot:
    @bot.on(events.InlineQuery(pattern=r"^alive$"))
    async def inline_alive_handler(event):
        builder = event.builder
        
        # Retrieve the latest generated text/media from the global variable
        # Default fallback if variable is empty
        text = LAST_ALIVE_DATA.get("text", "CipherElite is Online.")
        media = LAST_ALIVE_DATA.get("media", DEFAULT_ALIVE_PIC)

        if media:
            # Return photo with caption
            result = builder.photo(
                media,
                text=text,
                buttons=ALIVE_BUTTONS
            )
        else:
            # Return text article
            result = builder.article(
                "Alive",
                text=text,
                buttons=ALIVE_BUTTONS
            )
        
        await event.answer([result], cache_time=1)

    @bot.on(events.InlineQuery(pattern=r"^ping$"))
    async def inline_ping_handler(event):
        builder = event.builder
        text = LAST_PING_DATA.get("text", "Pong!")
        media = LAST_PING_DATA.get("media", DEFAULT_PING_PIC)

        if media:
            result = builder.photo(
                media,
                text=text,
                buttons=ALIVE_BUTTONS
            )
        else:
            result = builder.article(
                "Ping",
                text=text,
                buttons=ALIVE_BUTTONS
            )
        await event.answer([result], cache_time=1)

# ============================================================================
#  CONFIG SETTERS (No changes needed here, keeping your original logic)
# ============================================================================

@CipherElite.on(events.NewMessage(pattern=r"\.setalive\s+(\d+)"))
@rishabh()
async def set_alive(event):
    idx = int(event.pattern_match.group(1)) - 1
    if 0 <= idx < len(ALIVE_STYLES):
        user_config.alive_style_index = idx
        user_config.custom_alive_text = None
        save_config()
        await event.reply(f"✅ Alive style set to #{idx+1}")
    else:
        await event.reply(f"❌ Invalid. Choose 1–{len(ALIVE_STYLES)}")

@CipherElite.on(events.NewMessage(pattern=r"\.setping\s+(\d+)"))
@rishabh()
async def set_ping(event):
    idx = int(event.pattern_match.group(1)) - 1
    if 0 <= idx < len(PING_STYLES):
        user_config.ping_style_index = idx
        user_config.custom_ping_text = None
        save_config()
        await event.reply(f"✅ Ping style set to #{idx+1}")
    else:
        await event.reply(f"❌ Invalid. Choose 1–{len(PING_STYLES)}")

@CipherElite.on(events.NewMessage(pattern=r"\.setalivetext\s+(.+)"))
@rishabh()
async def set_alive_text(event):
    tpl = event.pattern_match.group(1)
    user_config.custom_alive_text = tpl
    save_config()
    await event.reply("✅ Custom alive text set.")

@CipherElite.on(events.NewMessage(pattern=r"\.setpingtext\s+(.+)"))
@rishabh()
async def set_ping_text(event):
    tpl = event.pattern_match.group(1)
    user_config.custom_ping_text = tpl
    save_config()
    await event.reply("✅ Custom ping text set.")

@CipherElite.on(events.NewMessage(pattern=r"\.setalivepic"))
@rishabh()
async def set_alive_pic(event):
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        if msg.media:
            path = await CipherElite.download_media(msg)
            user_config.alive_pic = path
            user_config.use_pic_for_alive = True
            save_config()
            await event.reply("✅ Alive picture set from reply")
    else:
        parts = event.text.split(None, 1)
        if len(parts) > 1:
            user_config.alive_pic = parts[1]
            user_config.use_pic_for_alive = True
            save_config()
            await event.reply("✅ Alive picture set from URL")

@CipherElite.on(events.NewMessage(pattern=r"\.setpingpic"))
@rishabh()
async def set_ping_pic(event):
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        if msg.media:
            path = await CipherElite.download_media(msg)
            user_config.ping_pic = path
            user_config.use_pic_for_ping = True
            save_config()
            await event.reply("✅ Ping picture set from reply")
    else:
        parts = event.text.split(None, 1)
        if len(parts) > 1:
            user_config.ping_pic = parts[1]
            user_config.use_pic_for_ping = True
            save_config()
            await event.reply("✅ Ping picture set from URL")

@CipherElite.on(events.NewMessage(pattern=r"\.togglealivepic"))
@rishabh()
async def toggle_alive_pic(event):
    user_config.use_pic_for_alive = not user_config.use_pic_for_alive
    save_config()
    state = "enabled" if user_config.use_pic_for_alive else "disabled"
    await event.reply(f"✅ Alive picture {state}")

@CipherElite.on(events.NewMessage(pattern=r"\.togglepingpic"))
@rishabh()
async def toggle_ping_pic(event):
    user_config.use_pic_for_ping = not user_config.use_pic_for_ping
    save_config()
    state = "enabled" if user_config.use_pic_for_ping else "disabled"
    await event.reply(f"✅ Ping picture {state}")

@CipherElite.on(events.NewMessage(pattern=r"\.resetalive"))
@rishabh()
async def reset_alive(event):
    user_config.__init__()
    save_config()
    await event.reply("✅ Alive settings reset to default")

@CipherElite.on(events.NewMessage(pattern=r"\.resetping"))
@rishabh()
async def reset_ping(event):
    user_config.__init__()
    save_config()
    await event.reply("✅ Ping settings reset to default")
