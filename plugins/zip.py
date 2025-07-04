# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    zip
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

import os
import time
import zipfile
import shutil  # Added for directory removal

from telethon import events
from telethon.types import Message
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".zip - Zip the replied media",
        ".unzip - Unzip the replied zip file"
    ]
    description = "Archive management plugin"
    add_handler("zip", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.zip"))
    @rishabh()
    async def zip_files(event: Message):
        if not event.reply_to_msg_id:
            return await event.reply("`Reply to a message to zip it.`")
        
        reply = await event.get_reply_message()
        if not reply.media:
            return await event.reply("`Reply to a media message to zip it.`")
        
        elite = await event.reply("`Zipping...`")
        start = time.time()
        download_path = await reply.download_media(f"temp_{round(time.time())}")

        zip_path = f"zipped_{int(time.time())}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(download_path, os.path.basename(download_path))

        await elite.edit("`Zipped Successfully. Uploading...`")
        await event.reply(
            f"**Zipped in {time.time() - start:.2f}s.**",
            file=zip_path
        )
        
        os.remove(zip_path)
        os.remove(download_path)
        await elite.delete()

    @CipherElite.on(events.NewMessage(pattern=r"\.unzip"))
    @rishabh()
    async def unzip_file(event: Message):
        if not event.reply_to_msg_id:
            return await event.reply("`Reply to a message to unzip it.`")
        
        reply = await event.get_reply_message()
        if not reply.media:
            return await event.reply("`Reply to a zip file to unzip it.`")
        
        elite = await event.reply("`Unzipping...`")
        start = time.time()
        download_path = await reply.download_media(f"temp_{round(time.time())}")
        
        unzip_dir = f"unzipped_{int(time.time())}"
        os.makedirs(unzip_dir, exist_ok=True)
        
        with zipfile.ZipFile(download_path, "r") as zip_file:
            zip_file.extractall(unzip_dir)
        
        await elite.edit("`Unzipped Successfully. Uploading files...`")
        uploaded = 0
        
        # Recursively process all files in all subdirectories
        for root, _, files in os.walk(unzip_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    await event.reply(
                        f"**Unzipped {file}**",
                        file=file_path
                    )
                    uploaded += 1
                except Exception as e:
                    print(f"Error uploading {file}: {e}")
                finally:
                    # Ensure file is removed even if upload fails
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        await elite.edit(f"**Successfully uploaded {uploaded} files!**")
        
        # Remove the directory and all its contents
        shutil.rmtree(unzip_dir, ignore_errors=True)
        os.remove(download_path)
