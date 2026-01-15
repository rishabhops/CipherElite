# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    imagetools
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".grey <reply> - Convert to grayscale",
        ".blur <reply> - Blur image",
        ".mirror <reply> - Mirror image",
        ".flip <reply> - Flip image vertically",
        ".negative <reply> - Negative effect",
        ".sketch <reply> - Pencil sketch effect",
        ".border <reply> <color> - Add colored border",
        ".pixelate <reply> - Pixelate image"
    ]
    description = "Image Tools for editing and transforming images"
    add_handler("imagetools", commands, description)

async def get_image_from_reply(event):
    """Download image from reply"""
    if not event.is_reply:
        await event.reply("❌ Reply to an image!")
        return None
    
    reply = await event.get_reply_message()
    if not reply.photo:
        await event.reply("❌ Reply to an image!")
        return None
    
    # Download image
    file_path = await event.client.download_media(reply.photo, "/tmp/")
    return file_path

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.grey"))
    @rishabh()
    async def grey(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Convert to grayscale
            img = Image.open(file_path)
            grey_img = ImageOps.grayscale(img)
            
            output_path = "/tmp/grey.png"
            grey_img.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="⚫⚪ Grayscale"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.blur"))
    @rishabh()
    async def blur(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Apply blur
            img = Image.open(file_path)
            blurred = img.filter(ImageFilter.GaussianBlur(radius=10))
            
            output_path = "/tmp/blurred.png"
            blurred.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="🌫️ Blurred"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.mirror"))
    @rishabh()
    async def mirror(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Mirror image
            img = Image.open(file_path)
            mirrored = ImageOps.mirror(img)
            
            output_path = "/tmp/mirrored.png"
            mirrored.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="🪞 Mirrored"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.flip"))
    @rishabh()
    async def flip(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Flip image vertically
            img = Image.open(file_path)
            flipped = ImageOps.flip(img)
            
            output_path = "/tmp/flipped.png"
            flipped.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="🔄 Flipped"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.negative"))
    @rishabh()
    async def negative(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Invert colors
            img = Image.open(file_path)
            inverted = ImageOps.invert(img.convert('RGB'))
            
            output_path = "/tmp/negative.png"
            inverted.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="🎞️ Negative"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.sketch"))
    @rishabh()
    async def sketch(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Convert to sketch
            img = Image.open(file_path)
            grey = ImageOps.grayscale(img)
            inverted = ImageOps.invert(grey)
            blurred = inverted.filter(ImageFilter.GaussianBlur(radius=5))
            sketch = ImageOps.invert(blurred)
            
            output_path = "/tmp/sketch.png"
            sketch.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="✏️ Sketch"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.border"))
    @rishabh()
    async def border(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Get color from command
            text = event.text.split()
            color = text[1] if len(text) > 1 else "black"
            
            # Add border
            img = Image.open(file_path)
            bordered = ImageOps.expand(img, border=20, fill=color)
            
            output_path = "/tmp/bordered.png"
            bordered.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption=f"🖼️ Border ({color})"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.pixelate"))
    @rishabh()
    async def pixelate(event):
        msg = await event.reply("🎨 Processing image...")
        
        try:
            file_path = await get_image_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Pixelate image
            img = Image.open(file_path)
            small = img.resize((img.width // 20, img.height // 20), Image.NEAREST)
            pixelated = small.resize(img.size, Image.NEAREST)
            
            output_path = "/tmp/pixelated.png"
            pixelated.save(output_path)
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="🎮 Pixelated"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
