# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    videotools
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
import asyncio
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".sample <reply> <seconds> - Create video sample (default 30s)",
        ".vshots <reply> <count> - Take screenshots from video",
        ".vtrim <reply> <start>-<end> - Trim video"
    ]
    description = "Video Tools using ffmpeg for editing videos"
    add_handler("videotools", commands, description)

async def get_video_from_reply(event):
    """Download video from reply"""
    if not event.is_reply:
        await event.reply("❌ Reply to a video!")
        return None
    
    reply = await event.get_reply_message()
    if not reply.video:
        await event.reply("❌ Reply to a video!")
        return None
    
    # Download video
    file_path = await event.client.download_media(reply.video, "/tmp/")
    return file_path

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.sample"))
    @rishabh()
    async def sample(event):
        msg = await event.reply("🎬 Creating video sample...")
        
        try:
            file_path = await get_video_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Get duration from command
            text = event.text.split()
            duration = int(text[1]) if len(text) > 1 else 30
            
            output_path = "/tmp/sample.mp4"
            cmd = f'ffmpeg -i "{file_path}" -t {duration} -c copy "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption=f"🎬 {duration}s sample"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.vshots"))
    @rishabh()
    async def vshots(event):
        msg = await event.reply("📸 Taking screenshots...")
        
        try:
            file_path = await get_video_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Get count from command
            text = event.text.split()
            count = int(text[1]) if len(text) > 1 else 5
            
            if count > 10:
                await msg.edit("❌ Maximum 10 screenshots allowed!")
                os.remove(file_path)
                return
            
            # Get video duration
            duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
            process = await asyncio.create_subprocess_shell(
                duration_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            duration = float(stdout.decode().strip())
            
            # Take screenshots
            screenshots = []
            interval = duration / (count + 1)
            
            for i in range(1, count + 1):
                timestamp = interval * i
                output = f"/tmp/shot_{i}.png"
                cmd = f'ffmpeg -ss {timestamp} -i "{file_path}" -vframes 1 "{output}"'
                
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                screenshots.append(output)
            
            # Send screenshots
            await event.client.send_file(
                event.chat_id,
                screenshots,
                caption=f"📸 {count} screenshots"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            for shot in screenshots:
                if os.path.exists(shot):
                    os.remove(shot)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.vtrim"))
    @rishabh()
    async def vtrim(event):
        msg = await event.reply("✂️ Trimming video...")
        
        try:
            file_path = await get_video_from_reply(event)
            if not file_path:
                await msg.delete()
                return
            
            # Get timestamps from command
            text = event.text.split(maxsplit=1)
            if len(text) < 2 or '-' not in text[1]:
                await msg.edit("❌ Usage: `.vtrim <start>-<end>`\n\nExample: `.vtrim 10-30`")
                os.remove(file_path)
                return
            
            times = text[1].split('-')
            start = times[0].strip()
            end = times[1].strip()
            
            output_path = "/tmp/trimmed.mp4"
            cmd = f'ffmpeg -i "{file_path}" -ss {start} -to {end} -c copy "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Send result
            await event.client.send_file(
                event.chat_id,
                output_path,
                caption=f"✂️ Trimmed ({start}s - {end}s)"
            )
            
            await msg.delete()
            
            # Clean up
            os.remove(file_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
