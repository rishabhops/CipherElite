# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    youtube
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
# import glob moved to top
import asyncio
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".yta <url> - Download audio from YouTube",
        ".ytv <url> - Download video from YouTube",
        ".ytsa <query> - Search and download audio",
        ".ytsv <query> - Search and download video"
    ]
    description = "YouTube Downloader using yt-dlp"
    add_handler("youtube", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.yta"))
    @rishabh()
    async def youtube_audio(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.yta <YouTube URL>`")
            return
        
        url = text[1].strip()
        msg = await event.reply("⬇️ Downloading audio from YouTube...")
        
        try:
            # Use yt-dlp to download audio
            output_path = "/tmp/yt_audio_%(title)s.%(ext)s"
            cmd = f'yt-dlp -f "bestaudio" --extract-audio --audio-format mp3 --audio-quality 0 -o "{output_path}" "{url}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Find the downloaded file
            # import glob moved to top
            files = glob.glob("/tmp/yt_audio_*.mp3")
            
            if files:
                file_path = files[0]
                await msg.edit("⬆️ Uploading audio...")
                
                # Upload the file
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption="🎵 Downloaded by CipherElite"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
            else:
                await msg.edit("❌ Failed to download audio!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.ytv"))
    @rishabh()
    async def youtube_video(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.ytv <YouTube URL>`")
            return
        
        url = text[1].strip()
        msg = await event.reply("⬇️ Downloading video from YouTube...")
        
        try:
            # Use yt-dlp to download video
            output_path = "/tmp/yt_video_%(title)s.%(ext)s"
            cmd = f'yt-dlp -f "best[height<=720]" -o "{output_path}" "{url}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Find the downloaded file
            # import glob moved to top
            files = glob.glob("/tmp/yt_video_*")
            
            if files:
                file_path = files[0]
                
                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    await msg.edit("❌ Video is too large (>50MB)! Try audio instead.")
                    os.remove(file_path)
                    return
                
                await msg.edit("⬆️ Uploading video...")
                
                # Upload the file
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption="🎬 Downloaded by CipherElite"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
            else:
                await msg.edit("❌ Failed to download video!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.ytsa"))
    @rishabh()
    async def youtube_search_audio(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.ytsa <search query>`")
            return
        
        query = text[1].strip()
        msg = await event.reply(f"🔍 Searching and downloading audio for: **{query}**")
        
        try:
            # Search and download audio
            output_path = "/tmp/yt_audio_%(title)s.%(ext)s"
            cmd = f'yt-dlp "ytsearch1:{query}" -f "bestaudio" --extract-audio --audio-format mp3 --audio-quality 0 -o "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Find the downloaded file
            # import glob moved to top
            files = glob.glob("/tmp/yt_audio_*.mp3")
            
            if files:
                file_path = files[0]
                await msg.edit("⬆️ Uploading audio...")
                
                # Upload the file
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"🎵 {query}\n\nDownloaded by CipherElite"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
            else:
                await msg.edit("❌ No results found!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.ytsv"))
    @rishabh()
    async def youtube_search_video(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.ytsv <search query>`")
            return
        
        query = text[1].strip()
        msg = await event.reply(f"🔍 Searching and downloading video for: **{query}**")
        
        try:
            # Search and download video
            output_path = "/tmp/yt_video_%(title)s.%(ext)s"
            cmd = f'yt-dlp "ytsearch1:{query}" -f "best[height<=720]" -o "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Find the downloaded file
            # import glob moved to top
            files = glob.glob("/tmp/yt_video_*")
            
            if files:
                file_path = files[0]
                
                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    await msg.edit("❌ Video is too large (>50MB)! Try audio instead.")
                    os.remove(file_path)
                    return
                
                await msg.edit("⬆️ Uploading video...")
                
                # Upload the file
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"🎬 {query}\n\nDownloaded by CipherElite"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
            else:
                await msg.edit("❌ No results found!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
