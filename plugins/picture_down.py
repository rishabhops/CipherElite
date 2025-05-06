from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import asyncio
import os

def init(client_instance):
    commands = [
        ".dlmedia - Download replied media",
        ".autodl - Toggle auto media download"
    ]
    description = "Media Download Plugin for Private Messages"
    add_handler("mediadl", commands, description)

async def register_commands():
    @CipherElite.on(
        events.NewMessage(
            func=lambda e: e.is_private and (e.photo or e.video) and e.media_unread
        )
    )
    @rishabh()
    async def auto_media_downloader(event):
        try:
            result = await event.download_media()
            if result:
                # Change 'me' to your desired chat
                await event.client.send_file(
                    event.chat_id,  # Send to original chat 
                    result, 
                    caption="Auto Downloaded Media"
                )
        except Exception as e:
            await event.client.send_message(event.chat_id, f"Auto Download Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.dlmedia"))
    @rishabh()
    async def manual_media_download(event):
        if event.reply_to_msg_id:
            try:
                reply_msg = await event.get_reply_message()
                if reply_msg.media:
                    downloaded_file = await reply_msg.download_media()
                    await event.client.send_file(
                        event.chat_id,  # Send to original chat
                        downloaded_file, 
                        caption="Manually Downloaded Media"
                    )
                else:
                    await event.reply("❌ No media found in replied message")
            except Exception as e:
                await event.client.send_message(event.chat_id, f"Download Error: {str(e)}")