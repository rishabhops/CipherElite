# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    randomsticker
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .cat, .dab, .brain, .pat
# =============================================================================

from telethon import events, functions, types, utils
from PIL import Image
import aiohttp
import json
import random
from os import remove
from pathlib import Path
from urllib import parse
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

BASE_URL = "https://headp.at/pats/{}"
PAT_IMAGE = "pat.webp"

def init(client_instance):
    commands = [
        ".cat - Random cat sticker",
        ".dab - Random dab sticker",
        ".brain - Random brain sticker",
        ".pat - Random pat sticker"
    ]
    description = "Random sticker commands"
    add_handler("randomsticker", commands, description)

async def register_commands():

    async def _reply_to(event):
        if event.is_reply:
            return (await event.get_reply_message()).id
        return None

    @CipherElite.on(events.NewMessage(pattern=r"\.cat$"))
    @rishabh()
    async def cat(event):
        reply_to_id = await _reply_to(event)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.life/api/v2/img/meow") as resp:
                data = await resp.json()
            url = data.get("url")
            if not url:
                await event.reply("```Can't find any cat...```")
                return
            async with session.get(url) as img_resp:
                content = await img_resp.read()
        with open("temp.png", "wb") as f:
            f.write(content)
        img = Image.open("temp.png")
        img.save("temp.webp", "webp")
        await event.client.send_file(event.chat_id, "temp.webp", reply_to=reply_to_id)
        remove("temp.webp")
        remove("temp.png")
        try:
            await event.delete()
        except Exception:
            pass

    @CipherElite.on(events.NewMessage(pattern=r"\.dab$"))
    @rishabh()
    async def dab(event):
        reply_to_id = await _reply_to(event)
        blacklist = {
            1653974154589768377, 1653974154589768312, 1653974154589767857,
            1653974154589768311, 1653974154589767816, 1653974154589767939,
            1653974154589767944, 1653974154589767912, 1653974154589767911,
            1653974154589767910, 1653974154589767909, 1653974154589767863,
            1653974154589767852, 1653974154589768677,
        }
        try:
            result = await event.client(
                functions.messages.GetStickerSetRequest(
                    types.InputStickerSetShortName("DabOnHaters"),
                    hash=0,
                )
            )
            docs = [
                utils.get_input_document(x)
                for x in result.documents
                if x.id not in blacklist
            ]
            await event.respond(file=random.choice(docs), reply_to=reply_to_id)
            try:
                await event.delete()
            except Exception:
                pass
        except Exception as e:
            await event.reply(f"⚠️ Dab sticker error: `{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.brain$"))
    @rishabh()
    async def brain(event):
        reply_to_id = await _reply_to(event)
        try:
            result = await event.client(
                functions.messages.GetStickerSetRequest(
                    types.InputStickerSetShortName("supermind"),
                    hash=0,
                )
            )
            docs = [utils.get_input_document(x) for x in result.documents]
            await event.respond(file=random.choice(docs), reply_to=reply_to_id)
            try:
                await event.delete()
            except Exception:
                pass
        except Exception as e:
            await event.reply(f"⚠️ Brain sticker error: `{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.pat$"))
    @rishabh()
    async def pat(event):
        reply_to_id = await _reply_to(event)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://headp.at/js/pats.json") as resp:
                pats = await resp.json()
            pat_url = BASE_URL.format(parse.quote(random.choice(pats)))
            async with session.get(pat_url) as img_resp:
                content = await img_resp.read()
        with open(PAT_IMAGE, "wb") as f:
            f.write(content)
        await event.client.send_file(event.chat_id, PAT_IMAGE, reply_to=reply_to_id)
        remove(PAT_IMAGE)
        try:
            await event.delete()
        except Exception:
            pass
