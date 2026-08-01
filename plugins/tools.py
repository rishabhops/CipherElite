# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    tools
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

from telethon import events
import aiohttp
import os
import time
import platform
import psutil
import urllib.parse
from datetime import datetime
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "utilities"

def init(client_instance):
    commands = [
        ".dc - Get DC info",
        ".ip - Get IP info (self or given IP)",
        ".qr - Generate a QR code",
        ".barcode - Generate a barcode",
        ".decode - Decode a QR/barcode image",
        ".ifsc - Get bank details by IFSC"
    ]
    description = "Useful utility tools for your userbot "
    add_handler("tools", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.dc"))
    @rishabh()
    async def dc(event):
        if event.is_reply:
            msg = await event.get_reply_message()
            user = await event.client.get_entity(msg.sender_id)
        else:
            user = await event.client.get_me()
        
        dc_id = user.photo.dc_id if user.photo else "No profile photo"
        await event.reply(f" **DC ID:** `{dc_id}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.ip(?: |$)(.*)"))
    @rishabh()
    async def ip_info(event):
        ip = event.pattern_match.group(1).strip()
        url = f"https://ipapi.co/{ip or 'json'}/json/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await event.reply("⚠️ Could not fetch IP info. Try again later.")
                    return
                data = await resp.json()
        if data.get("error"):
            await event.reply(f"⚠️ Error: {data.get('reason')}")
            return
        text = (
            f"🌐 **IP Info** `{data.get('ip', 'N/A')}`\n\n"
            f"🏢 **ISP:** `{data.get('org', 'N/A')}`\n"
            f"🏳️ **Country:** `{data.get('country_name', 'N/A')}` (`{data.get('country', 'N/A')}`)\n"
            f"🏙 **City:** `{data.get('city', 'N/A')}`\n"
            f"📍 **Region:** `{data.get('region', 'N/A')}`\n"
            f"🗺 **Latitude:** `{data.get('latitude', 'N/A')}`\n"
            f"🗺 **Longitude:** `{data.get('longitude', 'N/A')}`\n"
            f"📮 **Postal:** `{data.get('postal', 'N/A')}`\n"
            f"⏰ **Timezone:** `{data.get('timezone', 'N/A')}`"
        )
        await event.reply(text)

    @CipherElite.on(events.NewMessage(pattern=r"\.qr(?: |$)(.*)"))
    @rishabh()
    async def qr_gen(event):
        text = event.pattern_match.group(1).strip()
        if not text:
            await event.reply("❌ Provide text to encode. Example: `.qr hello world`")
            return
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        encoded = urllib.parse.quote(text)
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await event.reply("⚠️ Failed to generate QR code.")
                    return
                data = await resp.read()
        tmp = "qrcode.png"
        with open(tmp, "wb") as f:
            f.write(data)
        await event.reply("📱 **QR Code:**", file=tmp)
        os.remove(tmp)

    @CipherElite.on(events.NewMessage(pattern=r"\.barcode(?: |$)(.*)"))
    @rishabh()
    async def barcode_gen(event):
        text = event.pattern_match.group(1).strip()
        if not text:
            await event.reply("❌ Provide text to encode. Example: `.barcode 123456789`")
            return
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        encoded = urllib.parse.quote(text)
        url = f"https://bwipjs-api.metafloor.com/?bcid=code128&text={encoded}&scale=3&height=12&incltext=on"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await event.reply("⚠️ Failed to generate barcode.")
                    return
                data = await resp.read()
        tmp = "barcode.png"
        with open(tmp, "wb") as f:
            f.write(data)
        await event.reply("📊 **Barcode:**", file=tmp)
        os.remove(tmp)

    @CipherElite.on(events.NewMessage(pattern=r"\.decode"))
    @rishabh()
    async def decode_qr(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a QR code/barcode image.")
            return
        msg = await event.get_reply_message()
        if not msg.media:
            await event.reply("❌ Reply to an image with a QR code/barcode.")
            return
        tmp = await event.client.download_media(msg, file="decode_tmp")
        if not tmp:
            await event.reply("⚠️ Could not download image.")
            return
        try:
            url = "https://api.qrserver.com/v1/read-qr-code/"
            data = aiohttp.FormData()
            data.add_field("file", open(tmp, "rb"), filename="qr.png")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as resp:
                    result = await resp.json()
            symbol = result[0]["symbol"][0]
            decoded = symbol.get("data")
            if not decoded:
                await event.reply(f"⚠️ Could not decode: {symbol.get('error', 'unknown')}")
            else:
                await event.reply(f"🔓 **Decoded:**\n`{decoded}`")
        except Exception as e:
            await event.reply(f"⚠️ Decode error: `{str(e)}`")
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass

    @CipherElite.on(events.NewMessage(pattern=r"\.ifsc(?: |$)(.*)"))
    @rishabh()
    async def ifsc_info(event):
        code = event.pattern_match.group(1).strip().upper()
        if not code:
            await event.reply("❌ Provide an IFSC code. Example: `.ifsc SBIN0001111`")
            return
        url = f"https://ifsc.razorpay.com/{code}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await event.reply("⚠️ Invalid IFSC code or API error.")
                    return
                data = await resp.json()
        text = (
            f"🏦 **Bank Details for `{code}`**\n\n"
            f"🏛 **Bank:** `{data.get('BANK', 'N/A')}`\n"
            f"🏠 **Branch:** `{data.get('BRANCH', 'N/A')}`\n"
            f"📍 **Address:** `{data.get('ADDRESS', 'N/A')}`\n"
            f"🏙 **City:** `{data.get('CITY', 'N/A')}`\n"
            f"🗺 **State:** `{data.get('STATE', 'N/A')}`\n"
            f"📮 **RTGS:** `{data.get('RTGS', 'N/A')}`\n"
            f"📮 **NEFT:** `{data.get('NEFT', 'N/A')}`\n"
            f"📮 **IMPS:** `{data.get('IMPS', 'N/A')}`\n"
            f"📮 **UPI:** `{data.get('UPI', 'N/A')}`\n"
            f"📮 **MICR:** `{data.get('MICR', 'N/A')}`\n"
            f"🌐 **SWIFT:** `{data.get('SWIFT', 'N/A')}`"
        )
        await event.reply(text)


# Initialize start time
START_TIME = datetime.now()
