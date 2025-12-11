import json
import requests
from bs4 import BeautifulSoup
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".magisk - Get latest Magisk releases",
        ".device <codename> - Get device info from codename",
        ".codename <brand> <model> - Search codename by model",
        ".twrp <codename> - Get latest TWRP download link"
    ]
    description = "🎭 Android Tools - Device info, TWRP & Magisk"
    add_handler("androidtools", commands, description)

async def register_commands():
    # ---------------------------------------------------------------------------------
    # 1. MAGISK COMMAND
    # ---------------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.magisk"))
    @rishabh()
    async def magisk_handler(event):
        status = await event.reply("🔄 **Fetching Magisk releases...**")
        try:
            magisk_repo = "https://raw.githubusercontent.com/topjohnwu/magisk-files/"
            magisk_dict = {
                "Stable": f"{magisk_repo}master/stable.json",
                "Beta": f"{magisk_repo}master/beta.json",
                "Canary": f"{magisk_repo}master/canary.json",
            }

            releases = ""
            for name, release_url in magisk_dict.items():
                data = requests.get(release_url).json()
                releases += (
                    f"🔹 **{name}**: [APK v{data['magisk']['version']}]({data['magisk']['link']}) | "
                    f"[Changelog]({data['magisk']['note']})\n"
                )

            await status.edit(f"🎭 **Cipher Elite Magisk**\n\n"
                              f"{releases}\n"
                              f"✅ **Success!**")
        except Exception as e:
            await status.edit(f"❌ **Error:** {str(e)}")

    # ---------------------------------------------------------------------------------
    # 2. DEVICE INFO (Codename -> Model)
    # ---------------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.device\s+(.+)"))
    @rishabh()
    async def device_handler(event):
        try:
            codename = event.pattern_match.group(1).strip().lower()
            status = await event.reply(f"🔄 **Searching for `{codename}`...**")
            
            url = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"
            data = json.loads(requests.get(url).text)
            
            if results := data.get(codename):
                reply_text = ""
                for item in results:
                    reply_text += (
                        f"📱 **Brand**: `{item['brand']}`\n"
                        f"🏷 **Name**: `{item['name']}`\n"
                        f"🔢 **Model**: `{item['model']}`\n\n"
                    )
                await status.edit(f"🎭 **Cipher Elite Device Search**\n\n"
                                  f"🔎 **Result for:** `{codename}`\n\n"
                                  f"{reply_text}"
                                  f"✅ **Found!**")
            else:
                await status.edit(f"❌ **Error:** Couldn't find info for `{codename}`")
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    # ---------------------------------------------------------------------------------
    # 3. CODENAME SEARCH (Brand + Model -> Codename)
    # ---------------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.codename\s+(.+)"))
    @rishabh()
    async def codename_handler(event):
        try:
            input_str = event.pattern_match.group(1).strip()
            args = input_str.split(" ", 1)
            
            if len(args) < 2:
                return await event.reply("💡 **Usage:** `.codename <brand> <model>`\nExample: `.codename Xiaomi Redmi Note 5`")

            brand = args[0].lower()
            device_name = args[1].lower()
            
            status = await event.reply(f"🔄 **Searching for `{brand} {device_name}`...**")

            url = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_brand.json"
            data = json.loads(requests.get(url).text)
            
            devices_lower = {k.lower(): v for k, v in data.items()}
            devices = devices_lower.get(brand)

            if not devices:
                return await status.edit(f"❌ **Error:** Brand `{brand}` not found.")

            results = [
                i for i in devices
                if i["name"].lower() == device_name or i["model"].lower() == device_name
            ]

            if results:
                reply_text = ""
                # Limit to 5 results to prevent spam
                for item in results[:5]:
                    reply_text += (
                        f"🔑 **Codename**: `{item['device']}`\n"
                        f"🏷 **Name**: `{item['name']}`\n"
                        f"🔢 **Model**: `{item['model']}`\n\n"
                    )
                await status.edit(f"🎭 **Cipher Elite Codename Search**\n\n"
                                  f"{reply_text}"
                                  f"✅ **Success!**")
            else:
                await status.edit(f"❌ **Error:** Couldn't find codename for `{device_name}`")
                
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    # ---------------------------------------------------------------------------------
    # 4. TWRP FINDER
    # ---------------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.twrp\s+(.+)"))
    @rishabh()
    async def twrp_handler(event):
        try:
            device = event.pattern_match.group(1).strip()
            status = await event.reply(f"🔄 **Searching TWRP for `{device}`...**")
            
            url = requests.get(f"https://dl.twrp.me/{device}/")
            
            if url.status_code == 404:
                return await status.edit(f"❌ **Error:** TWRP not found for `{device}`")
            
            page = BeautifulSoup(url.content, "lxml")
            download = page.find("table").find("tr").find("a")
            dl_link = f"https://dl.twrp.me{download['href']}"
            dl_file = download.text
            size = page.find("span", {"class": "filesize"}).text
            date = page.find("em").text.strip()
            
            await status.edit(f"🎭 **Cipher Elite TWRP Finder**\n\n"
                              f"📱 **Device:** `{device}`\n"
                              f"💾 **File:** `{dl_file}`\n"
                              f"📦 **Size:** `{size}`\n"
                              f"📅 **Date:** `{date}`\n\n"
                              f"🔗 [Click to Download]({dl_link})\n"
                              f"✅ **Success!**")
        except Exception as e:
            await status.edit(f"❌ **Error:** {str(e)}")
