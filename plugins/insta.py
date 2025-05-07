import re
import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    """
    Register the .insta command in your /help text.
    """
    commands = [
        ".insta <url>  — Download a public Instagram post (image, video or reel)"
    ]
    description = "Fetch public Instagram media without login"
    add_handler("instagram", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.insta\s+(https?://[^\s]+)"))
    @rishabh()
    async def instagram_dl(event):
        original_url = event.pattern_match.group(1).strip()

        # 1) Normalize /share URLs → / (Instagram does a redirect)
        url = original_url.replace("instagram.com/share/", "instagram.com/")

        # 2) Ensure trailing slash
        if not url.endswith("/"):
            url = url + "/"

        msg = await event.reply("📥 Fetching media URL…")

        try:
            media_url = await _fetch_media_url(url)
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
    GETs the Instagram page, follows redirects, and scrapes:
     • <meta property="og:video" content="…"> if it’s a video/reel
     • otherwise <meta property="og:image" content="…">
    Raises ValueError on HTTP errors or missing tags.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.get(url, allow_redirects=True) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise ValueError(f"HTTP {resp.status} fetching {url}")

    # Try video first (reels or video posts)
    m = re.search(r'<meta property="og:video" content="([^"]+)"', text)
    if m:
        return m.group(1)

    # Fallback to image
    m = re.search(r'<meta property="og:image" content="([^"]+)"', text)
    if m:
        return m.group(1)

    raise ValueError("Could not find public media URL. Is the post public?")
    
