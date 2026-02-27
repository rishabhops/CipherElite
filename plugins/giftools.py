# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    giftools
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
import asyncio
import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".gif <query> - Search and send GIF",
        ".vtog <reply> - Convert video to GIF",
        ".rvgif <reply> - Reverse a GIF",
        ".bwgif <reply> - Black & white GIF"
    ]
    description = "GIF Tools for searching and editing GIFs"
    add_handler("giftools", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.gif"))
    @rishabh()
    async def gif_search(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.gif <search query>`")
            return
        
        query = text[1].strip()
        msg = await event.reply(f"🔍 Searching GIF for: **{query}**")
        
        try:
            # Using your new Giphy API key
            api_key = "LtqWfuGQ1agFnsBZL0o04dlf6BrVc38J" 
            url = "https://api.giphy.com/v1/gifs/search"
            
            # Using params ensures spaces in queries don't break the URL
            params = {
                "api_key": api_key,
                "q": query,
                "limit": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if data['data']:
                            gif_url = data['data'][0]['images']['original']['url']
                            
                            # Send the GIF
                            await event.client.send_file(
                                event.chat_id,
                                gif_url,
                                caption=f"🎞️ {query}"
                            )
                            
                            await msg.delete()
                        else:
                            await msg.edit(f"❌ No GIF found for: {query}")
                    else:
                        await msg.edit(f"❌ API Error: Received status {resp.status}")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.vtog"))
    @rishabh()
    async def video_to_gif(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a video!")
            return
        
        msg = await event.reply("🎬 Converting video to GIF...")
        
        try:
            reply = await event.get_reply_message()
            if not reply.video:
                await msg.edit("❌ Reply to a video!")
                return
            
            # Download video
            file_path = await event.client.download_media(reply.video, "/tmp/")
            
            output_path = "/tmp/video.gif"
            # Convert to GIF with ffmpeg
            cmd = f'ffmpeg -i "{file_path}" -vf "fps=10,scale=320:-1:flags=lanczos" -c:v gif "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Check file size
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    await msg.edit("❌ GIF is too large! Try a shorter video.")
                    os.remove(file_path)
                    os.remove(output_path)
                    return
                
                # Send result
                await event.client.send_file(
                    event.chat_id,
                    output_path,
                    caption="🎞️ Converted to GIF"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
                os.remove(output_path)
            else:
                await msg.edit("❌ Failed to convert video to GIF!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.rvgif"))
    @rishabh()
    async def reverse_gif(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a GIF or video!")
            return
        
        msg = await event.reply("🔄 Reversing GIF...")
        
        try:
            reply = await event.get_reply_message()
            if not reply.gif and not reply.video:
                await msg.edit("❌ Reply to a GIF or video!")
                return
            
            # Download file
            file_path = await event.client.download_media(reply, "/tmp/")
            
            output_path = "/tmp/reversed.gif"
            # Reverse with ffmpeg
            cmd = f'ffmpeg -i "{file_path}" -vf reverse "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if os.path.exists(output_path):
                # Send result
                await event.client.send_file(
                    event.chat_id,
                    output_path,
                    caption="🔄 Reversed GIF"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
                os.remove(output_path)
            else:
                await msg.edit("❌ Failed to reverse GIF!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.bwgif"))
    @rishabh()
    async def bw_gif(event):
        if not event.is_reply:
            await event.reply("❌ Reply to a GIF or video!")
            return
        
        msg = await event.reply("⚫⚪ Converting to B&W...")
        
        try:
            reply = await event.get_reply_message()
            if not reply.gif and not reply.video:
                await msg.edit("❌ Reply to a GIF or video!")
                return
            
            # Download file
            file_path = await event.client.download_media(reply, "/tmp/")
            
            output_path = "/tmp/bw.gif"
            # Convert to B&W with ffmpeg
            cmd = f'ffmpeg -i "{file_path}" -vf "format=gray" "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if os.path.exists(output_path):
                # Send result
                await event.client.send_file(
                    event.chat_id,
                    output_path,
                    caption="⚫⚪ Black & White GIF"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
                os.remove(output_path)
            else:
                await msg.edit("❌ Failed to convert GIF!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
