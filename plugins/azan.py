# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    azan
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Command:        .azan <city>
# =============================================================================

from telethon import events
import aiohttp
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "utilities"

def init(client_instance):
    commands = [
        ".azan <city> - Islamic prayer times for a city"
    ]
    description = "Get Islamic prayer times via Aladhan API"
    add_handler("azan", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.azan(?: |$)([\s\S]*)"))
    @rishabh()
    async def azan(event):
        city = event.pattern_match.group(1).strip()
        if event.is_reply:
            city = (await event.get_reply_message()).text or city
        if not city:
            city = "Delhi"
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=&method=2"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await event.reply(f"⚠️ Could not fetch prayer times for **{city}**.")
                    return
                data = await resp.json()
        if data.get("code") != 200 or not data.get("data"):
            await event.reply(f"⚠️ No data found for **{city}**.")
            return
        timings = data["data"]["timings"]
        result = (
            f"🕌 **Islamic Prayer Times for {city}**\n\n"
            f"🌅 **Fajr:** `{timings.get('Fajr', 'N/A')}`\n"
            f"🌄 **Sunrise:** `{timings.get('Sunrise', 'N/A')}`\n"
            f"☀️ **Dhuhr:** `{timings.get('Dhuhr', 'N/A')}`\n"
            f"🌇 **Asr:** `{timings.get('Asr', 'N/A')}`\n"
            f"🌆 **Maghrib:** `{timings.get('Maghrib', 'N/A')}`\n"
            f"🌙 **Isha:** `{timings.get('Isha', 'N/A')}`\n"
        )
        await event.reply(result)
