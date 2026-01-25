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
from datetime import datetime
from pathlib import Path

from telethon import events, version, Button  # Added Button
from plugins.bot import add_handler, CMD_LIST
from utils.utils import CipherElite
from utils.decorators import rishabh
from config.config import Config

PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
CONFIG_FILE = DB_DIR / "alive_config.json"


ALIVE_BUTTONS = [
    [
        Button.url("💬 Support", "https://t.me/cipherelitesupport"),
        Button.url("📢 Channel", "https://t.me/THANOSPRO"),
    ],
]

class UserConfig:
    def __init__(self):
        # defaults
        self.alive_style_index = 0
        self.ping_style_index = 0
        self.custom_alive_text = None
        self.custom_ping_text = None
        self.alive_pic = DEFAULT_ALIVE_PIC
        self.ping_pic = DEFAULT_PING_PIC
        self.use_pic_for_alive = True
        self.use_pic_for_ping = True

    def to_dict(self):
        return {
            "alive_style_index": self.alive_style_index,
            "ping_style_index": self.ping_style_index,
            "custom_alive_text": self.custom_alive_text,
            "custom_ping_text": self.custom_ping_text,
            "alive_pic": self.alive_pic,
            "ping_pic": self.ping_pic,
            "use_pic_for_alive": self.use_pic_for_alive,
            "use_pic_for_ping": self.use_pic_for_ping,
        }

    def from_dict(self, data):
        for key, val in data.items():
            if hasattr(self, key):
                setattr(self, key, val)


def load_config():
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            user_config.from_dict(data)
        except Exception:
            pass  # ignore corrupt


def save_config():
    try:
        CONFIG_FILE.write_text(
            json.dumps(user_config.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


# -- END CONFIG PERSISTENCE SETUP -------------------------------------------

START_TIME = datetime.now()


DEFAULT_ALIVE_PIC = Config.DEFAULT_ALIVE_PIC
DEFAULT_PING_PIC = Config.DEFAULT_PING_PIC


def get_readable_time(seconds: float) -> str:
    count = 0
    time_list = []
    suffixes = ["s", "m", "h", "d"]
    while count < 4:
        count += 1
        if count < 3:
            seconds, result = divmod(seconds, 60)
        else:
            seconds, result = divmod(seconds, 24)
        if seconds == 0 and result == 0:
            break
        time_list.append(f"{int(result)}{suffixes[count - 1]}")
    return ":".join(reversed(time_list))

# --- HELPER: Convert Buttons to Markdown Links ---
def format_buttons_to_text(buttons_list):
    """Converts a list of Button.url into a markdown string [Text](Link) | [Text](Link)"""
    if not buttons_list:
        return ""
        
    lines = []
    for row in buttons_list:
        row_text = []
        for button in row:
            # Check if it's a URL button object
            if hasattr(button, 'url'):
                row_text.append(f"[{button.text}]({button.url})")
            # Fallback if someone defined it as simple text
            elif isinstance(button, str):
                row_text.append(button)
        if row_text:
            lines.append(" | ".join(row_text)) 
            
    # Return with a newline prefix to separate from main text
    return "\n\n" + "\n".join(lines)


# Raw-string templates to preserve special characters and spacing
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

user_config = UserConfig()
load_config()


def init(client):
    commands = [
        ".alive", ".ping",
        ".setalive <num>", ".setping <num>",
        ".setalivetext <text>", ".setpingtext <text>",
        ".setalivepic <url/reply>", ".setpingpic <url/reply>",
        ".togglealivepic", ".togglepingpic",
        ".alivestyles", ".pingstyles",
        ".resetalive", ".resetping"
    ]
    desc = "Alive/ping with ASCII art, images & persistent settings"
    add_handler("alive", commands, desc)


async def send_plain(event, text: str, file=None, add_buttons=False):
    """
    Send as plain text. 
    If add_buttons is True, appends the formatted links to the bottom.
    """
    # 1. Append buttons as links if requested
    if add_buttons:
        text += format_buttons_to_text(ALIVE_BUTTONS)

    # 2. Handle NBSP for spacing
    lines = text.splitlines()
    nbsp_lines = [line.replace(" ", "\u00A0") for line in lines]
    payload = "\n".join(nbsp_lines)

    # 3. Send (Link preview disabled to keep it clean)
    await event.reply(payload, file=file, link_preview=False)


@CipherElite.on(events.NewMessage(pattern=r"\.alive"))
@rishabh()
async def alive(event):
    uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
    template = (
        user_config.custom_alive_text
        if user_config.custom_alive_text
        else ALIVE_STYLES[user_config.alive_style_index]
    )
    text = template.format(
        name=event.sender.first_name,
        telethon=version.__version__,
        plugins=len(CMD_LIST),
        uptime=uptime
    )
    
    # We pass add_buttons=True here
    if user_config.use_pic_for_alive:
        await send_plain(event, text, file=user_config.alive_pic, add_buttons=True)
    else:
        await send_plain(event, text, add_buttons=True)


@CipherElite.on(events.NewMessage(pattern=r"\.ping"))
@rishabh()
async def ping(event):
    start = datetime.now()
    msg = await event.reply("⏳ Pinging…")
    elapsed = (datetime.now() - start).microseconds // 1000
    uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
    template = (
        user_config.custom_ping_text
        if user_config.custom_ping_text
        else PING_STYLES[user_config.ping_style_index]
    )
    text = template.format(speed=elapsed, uptime=uptime)
    
    # We pass add_buttons=True here as well
    if user_config.use_pic_for_ping:
        await send_plain(msg, text, file=user_config.ping_pic, add_buttons=True)
    else:
        await send_plain(msg, text, add_buttons=True)


# -- HANDLERS THAT MODIFY CONFIG --------------------------------------------

@CipherElite.on(events.NewMessage(pattern=r"\.setalive\s+(\d+)"))
@rishabh()
async def set_alive(event):
    idx = int(event.pattern_match.group(1)) - 1
    if 0 <= idx < len(ALIVE_STYLES):
        user_config.alive_style_index = idx
        user_config.custom_alive_text = None
        save_config()
        await event.reply(f"✅ Alive style set to #{idx+1}")
        preview = ALIVE_STYLES[idx].format(
            name=event.sender.first_name,
            telethon=version.__version__,
            plugins=len(CMD_LIST),
            uptime=get_readable_time((datetime.now() - START_TIME).total_seconds())
        )
        await send_plain(event, preview, add_buttons=True)
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
        preview = PING_STYLES[idx].format(speed=100, uptime="1m")
        await send_plain(event, preview, add_buttons=True)
    else:
        await event.reply(f"❌ Invalid. Choose 1–{len(PING_STYLES)}")


@CipherElite.on(events.NewMessage(pattern=r"\.setalivetext\s+(.+)"))
@rishabh()
async def set_alive_text(event):
    tpl = event.pattern_match.group(1)
    user_config.custom_alive_text = tpl
    save_config()
    try:
        preview = tpl.format(
            name=event.sender.first_name,
            telethon=version.__version__,
            plugins=len(CMD_LIST),
            uptime=get_readable_time((datetime.now() - START_TIME).total_seconds())
        )
        await event.reply("✅ Custom alive text set. Preview:")
        await send_plain(event, preview, add_buttons=True)
    except Exception as e:
        await event.reply(f"⚠️ Template error: {e}")


@CipherElite.on(events.NewMessage(pattern=r"\.setpingtext\s+(.+)"))
@rishabh()
async def set_ping_text(event):
    tpl = event.pattern_match.group(1)
    user_config.custom_ping_text = tpl
    save_config()
    try:
        preview = tpl.format(speed=123, uptime="1m")
        await event.reply("✅ Custom ping text set. Preview:")
        await send_plain(event, preview, add_buttons=True)
    except Exception as e:
        await event.reply(f"⚠️ Template error: {e}")


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
            await event.reply("❌ Reply to an image.")
    else:
        parts = event.text.split(None, 1)
        if len(parts) > 1:
            user_config.alive_pic = parts[1]
            user_config.use_pic_for_alive = True
            save_config()
            await event.reply("✅ Alive picture set from URL")
        else:
            await event.reply("❌ Provide a URL or reply to an image.")


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
            await event.reply("❌ Reply to an image.")
    else:
        parts = event.text.split(None, 1)
        if len(parts) > 1:
            user_config.ping_pic = parts[1]
            user_config.use_pic_for_ping = True
            save_config()
            await event.reply("✅ Ping picture set from URL")
        else:
            await event.reply("❌ Provide a URL or reply to an image.")


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


@CipherElite.on(events.NewMessage(pattern=r"\.alivestyles"))
@rishabh()
async def show_alive_styles(event):
    await event.reply("Available Alive Styles:")
    for i, style in enumerate(ALIVE_STYLES, 1):
        filled = style.format(name="Example", telethon="1.24.0", plugins=50, uptime="1m")
        await event.reply(f"Style #{i}:")
        await send_plain(event, filled, add_buttons=True)
        await asyncio.sleep(0.3)


@CipherElite.on(events.NewMessage(pattern=r"\.pingstyles"))
@rishabh()
async def show_ping_styles(event):
    await event.reply("Available Ping Styles:")
    for i, style in enumerate(PING_STYLES, 1):
        filled = style.format(speed=100, uptime="1m")
        await event.reply(f"Style #{i}:")
        await send_plain(event, filled, add_buttons=True)
        await asyncio.sleep(0.3)


@CipherElite.on(events.NewMessage(pattern=r"\.resetalive"))
@rishabh()
async def reset_alive(event):
    user_config.__init__()  # reset defaults
    save_config()
    await event.reply("✅ Alive settings reset to default")


@CipherElite.on(events.NewMessage(pattern=r"\.resetping"))
@rishabh()
async def reset_ping(event):
    user_config.__init__()  # reset defaults
    save_config()
    await event.reply("✅ Ping settings reset to default")
