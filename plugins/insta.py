from telethon import events
import instaloader
import os
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Initialize instaloader
L = instaloader.Instaloader()

def init(client_instance):
    commands = [
        ".insta <link> - Download Instagram content"
    ]
    description = "Download content from Instagram 📥"
    add_handler("instagram", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.insta (.*)"))
    @rishabh()
    async def instagram_dl(event):
        url = event.pattern_match.group(1)
        msg = await event.reply("📥 **Downloading...**")
        
        try:
            # Extract post shortcode from URL
            shortcode = url.split("/")[-2]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Download the post
            L.download_post(post, target="downloads")
            
            # Find downloaded file
            for file in os.listdir("downloads"):
                if file.endswith((".jpg", ".mp4")):
                    file_path = f"downloads/{file}"
                    await event.client.send_file(
                        event.chat_id,
                        file_path,
                        caption="**📥 Downloaded by CipherElite userbot**"
                    )
                    os.remove(file_path)
            
            await msg.delete()
            
        except Exception as e:
            await msg.edit("❌ **Download failed!**\nMake sure the post is public.")

