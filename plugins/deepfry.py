# =============================================================================
#  CipherElite Userbot Plugin - Deep Fryer
#  Ported from CatUserBot (local-only, no external API)
# =============================================================================

import os
import io
from random import randint, uniform

from PIL import Image, ImageEnhance, ImageOps
from telethon import events

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "fun"


def init(client):
    commands = [
        ".deepfry <reply> - Fry an image/sticker",
    ]
    description = "🍟 Deep fry images locally"
    add_handler("fryer", commands, description)


async def _deepfry_image(img: Image.Image) -> Image.Image:
    colours = (
        (randint(50, 200), randint(40, 170), randint(40, 190)),
        (randint(190, 255), randint(170, 240), randint(180, 250)),
    )
    img = img.copy().convert("RGB")
    width, height = img.width, img.height
    img = img.resize(
        (int(width ** uniform(0.8, 0.9)), int(height ** uniform(0.8, 0.9))),
        resample=Image.LANCZOS,
    )
    img = img.resize(
        (int(width ** uniform(0.85, 0.95)), int(height ** uniform(0.85, 0.95))),
        resample=Image.BILINEAR,
    )
    img = img.resize(
        (int(width ** uniform(0.89, 0.98)), int(height ** uniform(0.89, 0.98))),
        resample=Image.BICUBIC,
    )
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, randint(3, 7))
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageOps.colorize(overlay, colours[0], colours[1])
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 300))
    return img


@CipherElite.on(events.NewMessage(pattern=r"^\.deepfry$", outgoing=True))
@rishabh
async def deepfry(event):
    reply = await event.get_reply_message()
    if not reply or not (reply.photo or reply.sticker):
        return await event.edit("Reply to a photo or sticker to deepfry it!")

    await event.edit("🍟 Frying...")
    try:
        temp_path = "/tmp/deepfry_input.png"
        await event.client.download_media(reply, temp_path)
        img = Image.open(temp_path)
        fried = await _deepfry_image(img)
        output = io.BytesIO()
        fried.save(output, format="PNG")
        output.seek(0)
        output.name = "deepfried.png"
        await event.client.send_file(
            event.chat_id,
            output,
            reply_to=reply.id,
            caption="🍟 Deep fried!"
        )
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ Error: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
