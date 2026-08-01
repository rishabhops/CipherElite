# =============================================================================
#  CipherElite Userbot Plugin - Trolls
#  Ported from CatUserBot (uses public nekobot API, no key needed)
# =============================================================================

import os
import io
import requests
from PIL import Image

from telethon import events

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "fun"

NEKO_API = "https://nekobot.xyz/api/imagegen"
CATBOX_UPLOAD = "https://catbox.moe/user/api.php"


def init(client):
    commands = [
        ".trash <reply> - Trash meme on replied image",
        ".threats <reply> - Threats meme on replied image",
        ".trap <name1> ; <name2> <reply> - Yu-Gi-Oh trap card",
        ".phub <comment> ; <username> <reply> - Pornhub comment meme",
    ]
    description = "😈 Troll memes on replied images"
    add_handler("trolls", commands, description)


async def _upload_image(file_path: str) -> str:
    with open(file_path, "rb") as f:
        resp = requests.post(
            CATBOX_UPLOAD,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            timeout=60,
        )
    resp.raise_for_status()
    url = resp.text.strip()
    if not url.startswith("http"):
        raise Exception(f"Upload failed: {url}")
    return url


async def _download_image(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    path = "/tmp/troll_result.jpg"
    img = Image.open(io.BytesIO(resp.content))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, "JPEG")
    return path


async def _process(event, endpoint: str, params: dict):
    reply = await event.get_reply_message()
    if not reply or not (reply.photo or reply.sticker):
        return await event.edit("Reply to a photo or sticker first!")

    await event.edit("😈 Generating...")
    try:
        temp_path = "/tmp/troll_input.png"
        await event.client.download_media(reply, temp_path)
        img_url = await _upload_image(temp_path)

        # Build API params with the image URL
        api_params = {"type": endpoint}
        if endpoint in ("trap", "phcomment"):
            api_params.update(params)
            if endpoint == "trap":
                api_params["image"] = img_url
            else:
                api_params["image"] = img_url
        else:
            api_params["url"] = img_url

        resp = requests.get(NEKO_API, params=api_params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        image_url = data.get("message")
        if not image_url:
            return await event.edit("❌ API returned no image")

        result_path = await _download_image(image_url)
        await event.client.send_file(
            event.chat_id,
            result_path,
            reply_to=reply.id,
        )
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ Error: {e}")
    finally:
        for p in ["/tmp/troll_input.png", "/tmp/troll_result.jpg"]:
            if os.path.exists(p):
                os.remove(p)


@CipherElite.on(events.NewMessage(pattern=r"^\.trash$", outgoing=True))
@rishabh
async def trash(event):
    await _process(event, "trash", {})


@CipherElite.on(events.NewMessage(pattern=r"^\.threats$", outgoing=True))
@rishabh
async def threats(event):
    await _process(event, "threats", {})


@CipherElite.on(events.NewMessage(pattern=r"^\.trap(?:\s+(.+))?$", outgoing=True))
@rishabh
async def trap(event):
    text = event.pattern_match.group(1) or ""
    parts = [p.strip() for p in text.split(";")]
    if len(parts) < 2:
        return await event.edit("Usage: `.trap victim_name ; trapper_name`")
    await _process(event, "trap", {"name": parts[0], "author": parts[1]})


@CipherElite.on(events.NewMessage(pattern=r"^\.phub(?:\s+(.+))?$", outgoing=True))
@rishabh
async def phub(event):
    text = event.pattern_match.group(1) or ""
    parts = [p.strip() for p in text.split(";")]
    if len(parts) < 2:
        return await event.edit("Usage: `.phub comment_text ; username`")
    await _process(event, "phcomment", {"text": parts[0], "username": parts[1]})
