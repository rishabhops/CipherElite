# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    writer
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#  Created:        09/07/2026
# =============================================================================

import os
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from htmlwebshot import WebShot
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler


def init(client_instance):
    commands = [
        ".write <text or reply> - Write text on a paper template",
        ".image <text or reply to file> - Convert text/file to HTML image"
    ]
    description = "✍️ CipherElite Writer – Write on paper, convert text to image | Created: 09/07/2026"
    add_handler("writer", commands, description)


# ─── Helper: text wrapping ───────────────────────────────────────────────────
def text_set(text, font, max_width=600):
    """Wrap text to fit within max_width pixels using the given font."""
    lines = []
    for line in text.split('\n'):
        if not line:
            lines.append('')
            continue
        words = line.split()
        current_line = []
        current_width = 0
        for word in words:
            bbox = font.getbbox(current_line + [word] if current_line else [word])
            width = bbox[2] - bbox[0]
            if current_width + width <= max_width:
                current_line.append(word)
                current_width += width + font.getbbox(' ')[2]
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = font.getbbox(word)[2]
        if current_line:
            lines.append(' '.join(current_line))
    return lines


# ─── Commands ────────────────────────────────────────────────────────────────
async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.write(?:\s+(.*))?"))
    @rishabh()
    async def write_cmd(event):
        try:
            # Get text from command or reply
            text = event.pattern_match.group(1)
            if not text and event.is_reply:
                reply = await event.get_reply_message()
                text = reply.text
            if not text:
                await event.reply("❌ **Usage:** `.write <text>` or reply to a message with `.write`")
                return

            await event.delete()
            status = await event.reply("🔄 **Writing on paper...**")

            # Load template and font
            template_path = "resources/extras/template.jpg"
            font_path = "resources/fonts/assfont.ttf"

            if not os.path.exists(template_path):
                await status.edit("❌ **Template image not found!**\nMake sure `resources/extras/template.jpg` exists.")
                return
            if not os.path.exists(font_path):
                await status.edit("❌ **Font file not found!**\nMake sure `resources/fonts/assfont.ttf` exists.")
                return

            img = Image.open(template_path)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font_path, 30)

            # Wrap text
            lines = text_set(text, font, max_width=600)
            x, y = 150, 140
            line_height = font.getbbox("hg")[3] - font.getbbox("hg")[1]

            for line in lines:
                draw.text((x, y), line, fill=(1, 22, 55), font=font)
                y += line_height + 5

            output_file = "ult.jpg"
            img.save(output_file)

            await status.delete()
            await event.client.send_file(event.chat_id, output_file, reply_to=event.message.id)
            os.remove(output_file)

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.image(?:\s+(.*))?"))
    @rishabh()
    async def image_cmd(event):
        try:
            text = event.pattern_match.group(1)
            html_content = None
            file_path = None

            if text:
                html_content = text
            elif event.is_reply:
                reply = await event.get_reply_message()
                if reply.media:
                    file_path = await reply.download_media()
                    if file_path:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            html_content = f.read()
                elif reply.text:
                    html_content = reply.text

            if not html_content:
                await event.reply("❌ **Usage:** `.image <text>` or reply to a text/file with `.image`")
                return

            await event.delete()
            status = await event.reply("🔄 **Converting to image...**")

            # Convert text to HTML with basic styling
            html_content = html_content.replace('\n', '<br>')
            shot = WebShot(quality=85)
            css = "body {background: white;} p {color: black;}"
            pic = await shot.create_pic_async(html=html_content, css=css)

            await status.delete()
            await event.client.send_file(
                event.chat_id,
                pic,
                force_document=True,
                reply_to=event.message.id
            )
            os.remove(pic)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")