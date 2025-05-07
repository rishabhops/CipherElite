import re
import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    """
    Called by your loader to register the command help text.
    """
    commands = [
        ".insta <url>  — Download a public Instagram post (image or video)"
    ]
    description = "Fetch public Instagram posts without login"
    add_handler("instagram", commands, description)

async def register_commands():
    """
    Registers the .insta command handler.
    """
    @CipherElite.on(events.NewMessage(pattern=r"\.insta\s+(https?://[^\s]+)"))
    @rishabh()
    async def instagram_dl(event):
        post_url = event.pattern_match.group(1)
        msg = await event.reply("📥 Fetching media URL…")

        try:
            media_url = await _fetch_media_url(post_url)
            await event.client.send_file(
                event.chat_id,
                media_url,
                caption="📥 Downloaded by CipherElite userbot"
            )
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ Failed to download:\n{e}")

async def _fetch_media_url(url: str) -> str:
    """
    Fetches the Instagram post page and scrapes the Open-Graph tags:
      - og:video if it’s a video post, else
      - og:image for a photo.
    Raises ValueError if no media URL is found.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.get(url) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise ValueError(f"HTTP {resp.status} fetching {url}")

    # Try video
    m = re.search(r'<meta property="og:video" content="([^"]+)"', text)
    if m:
        return m.group(1)

    # Fallback to image
    m = re.search(r'<meta property="og:image" content="([^"]+)"', text)
    if m:
        return m.group(1)

    raise ValueError("Could not find public media URL. Is the post public?")
