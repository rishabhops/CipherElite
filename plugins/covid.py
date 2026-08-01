# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    covid
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Command:        .covid <country>
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
        ".covid <country> - COVID-19 stats for a country"
    ]
    description = "COVID-19 statistics via disease.sh"
    add_handler("covid", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.covid(?: |$)([\s\S]*)"))
    @rishabh()
    async def covid_cmd(event):
        country = event.pattern_match.group(1).strip()
        if event.is_reply:
            country = (await event.get_reply_message()).text or country
        country = country.title() if country else "World"
        if country.lower() == "world":
            url = "https://disease.sh/v3/covid-19/all"
        else:
            url = f"https://disease.sh/v3/covid-19/countries/{country}"
        status = await event.reply("`Collecting data...`")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await status.edit(f"⚠️ COVID data for **{country}** not available.")
                    return
                data = await resp.json()
        result = (
            f"🦠 **COVID-19 Info: {country}**\n\n"
            f"⚠️ **Confirmed:** `{data.get('cases', 'N/A')}`\n"
            f"😔 **Active:** `{data.get('active', 'N/A')}`\n"
            f"⚰️ **Deaths:** `{data.get('deaths', 'N/A')}`\n"
            f"😊 **Recovered:** `{data.get('recovered', 'N/A')}`\n"
            f"🧪 **Tests:** `{data.get('tests', 'N/A')}`\n"
            f"🥺 **Today Cases:** `{data.get('todayCases', 'N/A')}`\n"
            f"😟 **Today Deaths:** `{data.get('todayDeaths', 'N/A')}`"
        )
        await status.edit(result)
