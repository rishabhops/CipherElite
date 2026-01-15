# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    glitch
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
import random
from PIL import Image, ImageChops
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".glitch <reply> - Create glitchy GIF from image"
    ]
    description = "Glitch Effect for creating glitchy images"
    add_handler("glitch", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.glitch"))
    @rishabh()
    async def glitch(event):
        if not event.is_reply:
            await event.reply("❌ Reply to an image!")
            return
        
        msg = await event.reply("⚡ Creating glitch effect...")
        
        try:
            reply = await event.get_reply_message()
            
            if not reply.photo:
                await msg.edit("❌ Reply to an image!")
                return
            
            # Download image
            file_path = await event.client.download_media(reply.photo, "/tmp/")
            
            # Open image
            img = Image.open(file_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create glitch frames
            frames = []
            num_frames = 10
            
            for i in range(num_frames):
                # Copy the image
                glitched = img.copy()
                pixels = glitched.load()
                width, height = glitched.size
                
                # Apply random glitch effects
                # 1. RGB shift
                r, g, b = glitched.split()
                
                # Random offset
                offset = random.randint(-10, 10)
                r = ImageChops.offset(r, offset, 0)
                g = ImageChops.offset(g, -offset, 0)
                
                glitched = Image.merge('RGB', (r, g, b))
                
                # 2. Random horizontal stripes
                for _ in range(random.randint(3, 8)):
                    y = random.randint(0, height - 20)
                    stripe_height = random.randint(5, 20)
                    offset_x = random.randint(-50, 50)
                    
                    # Crop stripe
                    stripe = glitched.crop((0, y, width, y + stripe_height))
                    
                    # Paste with offset
                    if 0 <= y < height:
                        glitched.paste(stripe, (offset_x, y))
                
                frames.append(glitched)
            
            # Save as GIF
            output_path = "/tmp/glitch.gif"
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=100,
                loop=0
            )
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption="⚡ Glitch Effect"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
