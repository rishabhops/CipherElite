# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    stickertools
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
from PIL import Image, ImageDraw
from telethon import events
from telethon.tl.types import DocumentAttributeSticker, InputStickerSetShortName
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".kang <reply> - Kang/steal sticker to your pack",
        ".tiny <reply> - Create tiny sticker",
        ".round <reply> - Create round sticker"
    ]
    description = "Sticker Tools for creating and stealing stickers"
    add_handler("stickertools", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.kang"))
    @rishabh()
    async def kang(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a sticker, image, or GIF!")
            return
        
        msg = await event.reply("🎨 Kanging sticker...")
        
        try:
            reply = await event.get_reply_message()
            user = await event.client.get_me()
            
            # Download media
            if reply.sticker:
                file_path = await event.client.download_media(reply.sticker, "/tmp/")
            elif reply.photo:
                file_path = await event.client.download_media(reply.photo, "/tmp/")
            elif reply.gif:
                file_path = await event.client.download_media(reply.gif, "/tmp/")
            else:
                await msg.edit("❌ Reply to a sticker, image, or GIF!")
                return
            
            # Convert to PNG if needed
            if not file_path.endswith('.png'):
                img = Image.open(file_path)
                new_path = "/tmp/sticker.png"
                img.save(new_path)
                os.remove(file_path)
                file_path = new_path
            
            # Resize if needed (Telegram sticker requirements: 512x512)
            img = Image.open(file_path)
            if img.size != (512, 512):
                img.thumbnail((512, 512), Image.LANCZOS)
                img.save(file_path)
            
            # Try to add to pack via @Stickers bot
            pack_name = f"cipher_{user.id}_by_{(await event.client.get_me()).username or 'CipherElite'}"
            
            await msg.edit(f"✨ Sticker ready! Add it to your pack manually:\n\n"
                          f"1. Send to @Stickers bot\n"
                          f"2. Use /addsticker command\n"
                          f"3. Pack name: `{pack_name}`")
            
            # Send the processed sticker
            await event.client.send_file(event.chat_id, file_path)
            
            # Clean up
            os.remove(file_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.tiny"))
    @rishabh()
    async def tiny(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a sticker or image!")
            return
        
        msg = await event.reply("🔬 Making tiny sticker...")
        
        try:
            reply = await event.get_reply_message()
            
            # Download media
            if reply.sticker:
                file_path = await event.client.download_media(reply.sticker, "/tmp/")
            elif reply.photo:
                file_path = await event.client.download_media(reply.photo, "/tmp/")
            else:
                await msg.edit("❌ Reply to a sticker or image!")
                return
            
            # Open and make tiny
            img = Image.open(file_path)
            
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize to tiny (100x100)
            tiny_size = (100, 100)
            img.thumbnail(tiny_size, Image.LANCZOS)
            
            # Create a 512x512 transparent canvas
            canvas = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            
            # Paste tiny image in center
            offset = ((512 - img.width) // 2, (512 - img.height) // 2)
            canvas.paste(img, offset, img)
            
            output_path = "/tmp/tiny_sticker.png"
            canvas.save(output_path)
            
            # Send as sticker
            await event.client.send_file(
                event.chat_id,
                output_path,
                force_document=False
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.round"))
    @rishabh()
    async def round_sticker(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a sticker or image!")
            return
        
        msg = await event.reply("⭕ Making round sticker...")
        
        try:
            reply = await event.get_reply_message()
            
            # Download media
            if reply.sticker:
                file_path = await event.client.download_media(reply.sticker, "/tmp/")
            elif reply.photo:
                file_path = await event.client.download_media(reply.photo, "/tmp/")
            else:
                await msg.edit("❌ Reply to a sticker or image!")
                return
            
            # Open image
            img = Image.open(file_path)
            
            # Convert to RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize to 512x512
            img = img.resize((512, 512), Image.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', (512, 512), 0)
            # from PIL import ImageDraw moved to top
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 512, 512), fill=255)
            
            # Apply mask
            output = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            output.paste(img, (0, 0))
            output.putalpha(mask)
            
            output_path = "/tmp/round_sticker.png"
            output.save(output_path)
            
            # Send as sticker
            await event.client.send_file(
                event.chat_id,
                output_path,
                force_document=False
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
