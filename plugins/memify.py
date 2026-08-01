# =============================================================================
#  CipherElite Userbot Plugin - Memify
#  Simplified local image meme generator (no external API)
# =============================================================================

import os
import io
import random
import textwrap
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from telethon import events

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "fun"

FONT_DIR = "/tmp/memify_fonts"
FONT_URL = "https://github.com/TgCatUB/CatUserbot-Resources/raw/master/Resources/Spotify/ArialUnicodeMS.ttf"


def init(client):
    commands = [
        ".mmf <top> ; <bottom> <reply> - Meme text on image",
        ".stcr <text> - Text to sticker",
        ".invert <reply> - Invert image colors",
        ".gray <reply> - Grayscale image",
        ".solarize <reply> - Solarize image",
        ".frame <reply> - Add frame to image",
        ".zoom <reply> - Zoom effect",
    ]
    description = "🖼️ Local image meme tools"
    add_handler("memify", commands, description)


def _ensure_font():
    os.makedirs(FONT_DIR, exist_ok=True)
    font_path = os.path.join(FONT_DIR, "ArialUnicodeMS.ttf")
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(FONT_URL, font_path)
    return font_path


def _text_to_sticker(text: str):
    rgb = tuple(random.sample(range(255), 3))
    font_path = _ensure_font()
    wrapped = textwrap.wrap(text, width=10)
    wrapped = "\n".join(wrapped)
    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230
    font = ImageFont.truetype(font_path, fontsize)
    def _text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    while _text_size(wrapped, font)[0] > 500 or _text_size(wrapped, font)[1] > 500:
        fontsize -= 3
        font = ImageFont.truetype(font_path, fontsize)
    w, h = _text_size(wrapped, font)
    draw.multiline_text(((512 - w) // 2, (512 - h) // 2), wrapped, font=font, fill=rgb)
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    output.name = "sticker.png"
    return output


def _meme_text(img: Image.Image, top: str, bottom: str):
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    font_path = _ensure_font()
    width, height = img.size

    def _text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def draw_text(text, y):
        if not text:
            return
        fontsize = int(width / 8)
        font = ImageFont.truetype(font_path, fontsize)
        while _text_size(text, font)[0] > width - 20 and fontsize > 10:
            fontsize -= 5
            font = ImageFont.truetype(font_path, fontsize)
        tw, th = _text_size(text, font)
        x = (width - tw) // 2
        # Outline
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

    draw_text(top.upper(), 10)
    if bottom:
        bh = _text_size(bottom.upper(), font=ImageFont.truetype(font_path, int(width / 8)))[1]
        draw_text(bottom.upper(), height - bh - 10)
    return img


async def _reply_with_image(event, img: Image.Image, filename: str, caption: str = ""):
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    output.name = filename
    reply = await event.get_reply_message()
    await event.client.send_file(
        event.chat_id,
        output,
        reply_to=reply.id if reply else None,
        caption=caption,
    )
    await event.delete()


@CipherElite.on(events.NewMessage(pattern=r"^\.mmf(?:\s+(.+))?$", outgoing=True))
@rishabh
async def mmf(event):
    reply = await event.get_reply_message()
    if not reply or not (reply.photo or reply.sticker):
        return await event.edit("Reply to a photo/sticker with `.mmf top text ; bottom text`")
    text = event.pattern_match.group(1) or ""
    if ";" in text:
        top, bottom = text.split(";", 1)
    else:
        top, bottom = text, ""
    await event.edit("🖼️ Memifying...")
    try:
        temp_path = "/tmp/mmf_input.png"
        await event.client.download_media(reply, temp_path)
        img = Image.open(temp_path)
        result = _meme_text(img, top.strip(), bottom.strip())
        await _reply_with_image(event, result, "meme.png")
    except Exception as e:
        await event.edit(f"❌ Error: {e}")
    finally:
        if os.path.exists("/tmp/mmf_input.png"):
            os.remove("/tmp/mmf_input.png")


@CipherElite.on(events.NewMessage(pattern=r"^\.stcr(?:\s+(.+))?$", outgoing=True))
@rishabh
async def stcr(event):
    text = event.pattern_match.group(1) or ""
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text
    if not text:
        return await event.edit("Usage: `.stcr <text>` or reply to a text message")
    await event.delete()
    try:
        sticker = _text_to_sticker(text)
        await event.client.send_file(event.chat_id, sticker, force_document=False)
    except Exception as e:
        await event.reply(f"❌ Error: {e}")


@CipherElite.on(events.NewMessage(pattern=r"^\.invert$", outgoing=True))
@rishabh
async def invert(event):
    await _simple_filter(event, ImageOps.invert, "inverted.png")


@CipherElite.on(events.NewMessage(pattern=r"^\.gray$", outgoing=True))
@rishabh
async def gray(event):
    await _simple_filter(event, lambda img: img.convert("L"), "gray.png")


@CipherElite.on(events.NewMessage(pattern=r"^\.solarize$", outgoing=True))
@rishabh
async def solarize(event):
    await _simple_filter(event, lambda img: ImageOps.solarize(img.convert("RGB"), threshold=128), "solarize.png")


@CipherElite.on(events.NewMessage(pattern=r"^\.frame$", outgoing=True))
@rishabh
async def frame(event):
    await event.edit("🖼️ Framing...")
    try:
        reply = await event.get_reply_message()
        if not reply or not (reply.photo or reply.sticker):
            return await event.edit("Reply to a photo/sticker")
        temp_path = "/tmp/frame_input.png"
        await event.client.download_media(reply, temp_path)
        img = Image.open(temp_path).convert("RGB")
        width, height = img.size
        scale = min(width, height) // 40
        new_size = (width + scale * 10, height + scale * 10)
        bg = Image.new("RGB", new_size, "white")
        bg.paste(img, ((new_size[0] - width) // 2, (new_size[1] - height) // 2))
        await _reply_with_image(event, bg, "frame.png")
    except Exception as e:
        await event.edit(f"❌ Error: {e}")
    finally:
        if os.path.exists("/tmp/frame_input.png"):
            os.remove("/tmp/frame_input.png")


@CipherElite.on(events.NewMessage(pattern=r"^\.zoom$", outgoing=True))
@rishabh
async def zoom(event):
    await event.edit("🖼️ Zooming...")
    try:
        reply = await event.get_reply_message()
        if not reply or not (reply.photo or reply.sticker):
            return await event.edit("Reply to a photo/sticker")
        temp_path = "/tmp/zoom_input.png"
        await event.client.download_media(reply, temp_path)
        img = Image.open(temp_path).convert("RGB")
        w, h = img.size
        crop = img.crop((w * 0.1, h * 0.1, w * 0.9, h * 0.9))
        zoomed = crop.resize((w, h), Image.LANCZOS)
        await _reply_with_image(event, zoomed, "zoom.png")
    except Exception as e:
        await event.edit(f"❌ Error: {e}")
    finally:
        if os.path.exists("/tmp/zoom_input.png"):
            os.remove("/tmp/zoom_input.png")


async def _simple_filter(event, filter_func, filename):
    await event.edit("🖼️ Processing...")
    try:
        reply = await event.get_reply_message()
        if not reply or not (reply.photo or reply.sticker):
            return await event.edit("Reply to a photo/sticker")
        temp_path = "/tmp/filter_input.png"
        await event.client.download_media(reply, temp_path)
        img = Image.open(temp_path)
        result = filter_func(img)
        await _reply_with_image(event, result, filename)
    except Exception as e:
        await event.edit(f"❌ Error: {e}")
    finally:
        if os.path.exists("/tmp/filter_input.png"):
            os.remove("/tmp/filter_input.png")
