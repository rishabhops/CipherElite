# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    imgfun
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .imirror, .irotate, .iresize, .square, .dotify
# =============================================================================

from telethon import events
import io
import os
from io import BytesIO
from PIL import Image, ImageFilter, ImageOps
from pathlib import Path
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

TEMP_DIR = Path("./temp")

def _media_type(media):
    if media.photo:
        return "Photo"
    if media.sticker:
        return "Sticker"
    return None

async def _download_image(event, reply, filename):
    TEMP_DIR.mkdir(exist_ok=True)
    path = await event.client.download_media(reply, file=str(TEMP_DIR / filename))
    return path

def init(client_instance):
    commands = [
        ".imirror [flag] - Mirror image",
        ".irotate <angle> - Rotate image",
        ".iresize <w> <h> - Resize image",
        ".square - Make image square",
        ".dotify <pixels> - Dotted/pixelated image"
    ]
    description = "Image manipulation fun commands"
    add_handler("imgfun", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.imirror(s)? ?(-)?(l|r|u|b)?$"))
    @rishabh()
    async def imirror(event):
        reply = await event.get_reply_message()
        if not reply or not _media_type(reply):
            await event.reply("❌ Reply to a photo or sticker.")
            return
        as_sticker = bool(event.pattern_match.group(1))
        flag = event.pattern_match.group(3) or "r"
        status = await event.reply("__Reflecting the image...__")
        path = await _download_image(event, reply, "imirror.png")
        if not path:
            await status.edit("❌ Could not download image.")
            return
        image = Image.open(path)
        w, h = image.size
        if w % 2 != 0 and flag in ["r", "l"] or h % 2 != 0 and flag in ["u", "b"]:
            image = image.resize((w + 1, h + 1))
            h, w = image.size
        if flag == "b":
            left, upper, right, lower, nw, nh = 0, h // 2, w, h, 0, 0
        elif flag == "l":
            left, upper, right, lower, nw, nh = 0, 0, w // 2, h, w // 2, 0
        elif flag == "r":
            left, upper, right, lower, nw, nh = w // 2, 0, w, h, 0, 0
        elif flag == "u":
            left, upper, right, lower, nw, nh = 0, 0, w, h // 2, 0, h // 2
        temp = image.crop((left, upper, right, lower))
        temp = ImageOps.mirror(temp) if flag in ["l", "r"] else ImageOps.flip(temp)
        image.paste(temp, (nw, nh))
        img = BytesIO()
        if as_sticker:
            img.name = "imirror.webp"
            image.save(img, "webp")
        else:
            img.name = "imirror.jpg"
            image.save(img, "jpeg")
        img.seek(0)
        await event.client.send_file(event.chat_id, img, reply_to=reply)
        await status.delete()
        os.remove(path)

    @CipherElite.on(events.NewMessage(pattern=r"\.irotate(?: |$)(\d+)$"))
    @rishabh()
    async def irotate(event):
        reply = await event.get_reply_message()
        if not reply or not _media_type(reply):
            await event.reply("❌ Reply to a photo or sticker.")
            return
        angle = int(event.pattern_match.group(1))
        path = await _download_image(event, reply, "irotate.png")
        if not path:
            await event.reply("❌ Could not download image.")
            return
        image = Image.open(path)
        image = image.rotate(angle, expand=True)
        img = BytesIO()
        img.name = "irotate.png"
        image.save(img, "PNG")
        img.seek(0)
        await event.client.send_file(event.chat_id, img, reply_to=reply)
        try:
            await event.delete()
        except Exception:
            pass
        os.remove(path)

    @CipherElite.on(events.NewMessage(pattern=r"\.iresize(?:\s|$)([\s\S]*)$"))
    @rishabh()
    async def iresize(event):
        reply = await event.get_reply_message()
        if not reply or not _media_type(reply):
            await event.reply("❌ Reply to a photo or sticker.")
            return
        args = event.pattern_match.group(1).strip().split()
        if not args:
            await event.reply("❌ Usage: `.iresize <dimension>` or `.iresize <width> <height>`")
            return
        try:
            if len(args) == 1:
                nw = nh = int(args[0])
            else:
                nw, nh = int(args[0]), int(args[1])
        except ValueError:
            await event.reply("❌ Invalid dimensions.")
            return
        path = await _download_image(event, reply, "iresize.png")
        if not path:
            await event.reply("❌ Could not download image.")
            return
        image = Image.open(path)
        image = image.resize((nw, nh))
        img = BytesIO()
        img.name = "iresize.png"
        image.save(img, "PNG")
        img.seek(0)
        await event.client.send_file(event.chat_id, img, reply_to=reply)
        try:
            await event.delete()
        except Exception:
            pass
        os.remove(path)

    @CipherElite.on(events.NewMessage(pattern=r"\.square$"))
    @rishabh()
    async def square(event):
        reply = await event.get_reply_message()
        if not reply or not reply.photo:
            await event.reply("❌ Reply to a photo.")
            return
        path = await _download_image(event, reply, "square.png")
        if not path:
            await event.reply("❌ Could not download image.")
            return
        img = Image.open(path)
        w, h = img.size
        if w == h:
            await event.reply("❌ Image is already square.")
            os.remove(path)
            return
        _min, _max = min(w, h), max(w, h)
        bg = img.crop(((w - _min) // 2, (h - _min) // 2, (w + _min) // 2, (h + _min) // 2))
        bg = bg.filter(ImageFilter.GaussianBlur(5))
        bg = bg.resize((_max, _max))
        bg.paste(img, ((_max - w) // 2, (_max - h) // 2))
        out = BytesIO()
        out.name = "square.jpg"
        bg.save(out, "JPEG")
        out.seek(0)
        await event.client.send_file(event.chat_id, out, reply_to=reply)
        os.remove(path)

    @CipherElite.on(events.NewMessage(pattern=r"\.dotify(?: |$)(\d+)?$"))
    @rishabh()
    async def dotify_cmd(event):
        reply = await event.get_reply_message()
        if not reply or not _media_type(reply):
            await event.reply("❌ Reply to a photo or sticker.")
            return
        args = event.pattern_match.group(1)
        pix = int(args) if args and args.isdigit() and int(args) > 0 else 100
        status = await event.reply("__🎞 Dotifying image...__")
        path = await _download_image(event, reply, "dotify.png")
        if not path:
            await status.edit("❌ Could not download image.")
            return
        image = Image.open(path)
        image = image.resize((pix, pix))
        image = image.resize((image.width * 10, image.height * 10), Image.NEAREST)
        out = BytesIO()
        out.name = "dotify.png"
        image.save(out, "PNG")
        out.seek(0)
        await event.client.send_file(event.chat_id, out, reply_to=reply)
        await status.delete()
        os.remove(path)
