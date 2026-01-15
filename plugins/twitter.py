# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    twitter
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
import glob
import asyncio
import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".tweet <text> - Post a tweet (requires API keys)",
        ".twdl <url> - Download Twitter video/media",
        ".twuser <username> - Get Twitter user info"
    ]
    description = "Twitter Integration for posting and downloading"
    add_handler("twitter", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.tweet"))
    @rishabh()
    async def tweet(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.tweet <text>`")
            return
        
        tweet_text = text[1].strip()
        
        # Note: This requires Twitter API keys to be set in config
        await event.reply("⚠️ Twitter API integration requires API keys to be configured.\n\n"
                         "Please set up Twitter Developer account and add API keys to config.")

    @CipherElite.on(events.NewMessage(pattern=r"\.twdl"))
    @rishabh()
    async def twitter_download(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.twdl <Twitter URL>`")
            return
        
        url = text[1].strip()
        msg = await event.reply("⬇️ Downloading from Twitter...")
        
        try:
            # Use yt-dlp which supports Twitter
            output_path = "/tmp/twitter_%(title)s.%(ext)s"
            cmd = f'yt-dlp -o "{output_path}" "{url}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Find the downloaded file
            # import glob moved to top
            files = glob.glob("/tmp/twitter_*")
            
            if files:
                file_path = files[0]
                
                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    await msg.edit("❌ File is too large (>50MB)!")
                    os.remove(file_path)
                    return
                
                await msg.edit("⬆️ Uploading media...")
                
                # Upload the file
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption="🐦 Downloaded from Twitter by CipherElite"
                )
                
                await msg.delete()
                
                # Clean up
                os.remove(file_path)
            else:
                await msg.edit("❌ Failed to download media!")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.twuser"))
    @rishabh()
    async def twitter_user(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.twuser <username>`")
            return
        
        username = text[1].strip().replace('@', '')
        msg = await event.reply(f"🔍 Fetching info for @{username}...")
        
        try:
            # Using a public API to get basic Twitter user info
            async with aiohttp.ClientSession() as session:
                # Note: This is a placeholder. You would need a proper API or scraping method
                await msg.edit(f"ℹ️ **Twitter User Info**\n\n"
                             f"👤 Username: @{username}\n\n"
                             f"⚠️ Full user info requires Twitter API keys.\n"
                             f"Visit: https://twitter.com/{username}")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
