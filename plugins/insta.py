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
        
        msg = await event.reply("📥 Fetching media URL...")
        try:
            media_url = await fetch_media_url(url)
            
            # Use proper error handling for the file sending
            try:
                await msg.edit("📥 Downloading and sending media...")
                async with aiohttp.ClientSession() as session:
                    async with session.get(media_url) as resp:
                        if resp.status != 200:
                            await msg.edit(f"❌ Failed to download media: HTTP {resp.status}")
                            return
                            
                        # Determine file extension
                        content_type = resp.headers.get('Content-Type', '')
                        ext = get_extension_from_content_type(content_type)
                        
                        # Download file content
                        file_data = await resp.read()
                        
                        # Use a proper file name
                        file_name = f"instagram_media{ext}"
                        
                        # Send as file with proper content
                        await event.client.send_file(
                            event.chat_id,
                            file_data,
                            caption="📥 Downloaded by CipherElite userbot",
                            file_name=file_name
                        )
                        await msg.delete()
            except Exception as e:
                await msg.edit(f"❌ Failed to send media: {str(e)}")
        except Exception as e:
            await msg.edit(f"❌ Failed to download: {str(e)}")

def get_extension_from_content_type(content_type):
    """Determine file extension based on content type"""
    if 'video' in content_type:
        return '.mp4'
    elif 'image' in content_type:
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        else:
            return '.jpg'  # Default to jpg
    else:
        return '.bin'  # Generic binary extension as fallback

async def fetch_media_url(url: str) -> str:
    """
    GETs the Instagram page, follows redirects, and scrapes:
     • <meta property="og:video" content="…"> if it's a video/reel
     • otherwise <meta property="og:image" content="…">
    Raises ValueError on HTTP errors or missing tags.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as sess:
            async with sess.get(url, allow_redirects=True) as resp:
                if resp.status != 200:
                    raise ValueError(f"HTTP {resp.status} fetching {url}")
                text = await resp.text()
    except aiohttp.ClientError as e:
        raise ValueError(f"Network error: {str(e)}")
        
    # Try video first (reels or video posts)
    m = re.search(r'<meta property="og:video" content="([^"]+)"', text)
    if m:
        return m.group(1)
    
    # Fallback to image
    m = re.search(r'<meta property="og:image" content="([^"]+)"', text)
    if m:
        return m.group(1)
    
    raise ValueError("Could not find public media URL. Is the post public?")
