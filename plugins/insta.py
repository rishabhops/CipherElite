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
    GETs the Instagram page and extracts media URLs using various methods:
    1. Look for JSON data with media URLs
    2. Look for og:video/image meta tags
    3. Try advanced content extraction

    Raises ValueError on HTTP errors or missing media.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.instagram.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as sess:
            async with sess.get(url, allow_redirects=True) as resp:
                if resp.status != 200:
                    raise ValueError(f"HTTP {resp.status} fetching {url}")
                text = await resp.text()
    except aiohttp.ClientError as e:
        raise ValueError(f"Network error: {str(e)}")

    # Method 1: Extract from JSON data in script tags
    json_match = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', text, re.DOTALL)
    if json_match:
        import json
        try:
            # Clean the JSON string - sometimes Instagram adds weird characters
            json_str = json_match.group(1).strip()
            # Try to fix malformed JSON
            json_str = re.sub(r'\\u0022', '"', json_str)
            json_str = re.sub(r'\\\\\"', '\"', json_str)
            json_str = re.sub(r'\\"', '"', json_str)
            
            data = json.loads(json_str)
            
            # Look for video_url or image_url in the JSON structure
            # This is a simplified approach - real implementation would need to traverse the JSON
            media_str = str(data)
            
            # Look for high-quality video URLs
            video_urls = re.findall(r'(https://scontent[^"\']+\.mp4[^"\'\s]*)', media_str)
            if video_urls:
                return max(video_urls, key=len)  # Return the longest URL which likely has best quality
                
            # Look for high-quality image URLs  
            image_urls = re.findall(r'(https://scontent[^"\']+\.jpg[^"\'\s]*)', media_str)
            if image_urls:
                return max(image_urls, key=len)
        except (json.JSONDecodeError, Exception) as e:
            # If JSON parsing fails, continue to next method
            pass
    
    # Method 2: Direct regex search for media URLs in the entire page
    # Look for video URLs first
    video_urls = re.findall(r'(https://(?:scontent|instagram|cdninstagram)[^"\']+\.mp4[^"\'\s]*)', text)
    if video_urls:
        # Filter out low-quality versions
        hq_urls = [url for url in video_urls if '&amp;' not in url and 'lowres' not in url]
        if hq_urls:
            return max(hq_urls, key=len)
        return max(video_urls, key=len)
    
    # If no videos found, look for images
    image_urls = re.findall(r'(https://(?:scontent|instagram|cdninstagram)[^"\']+\.jpg[^"\'\s]*)', text)
    if image_urls:
        # Filter out low-quality versions and profile pictures
        hq_urls = [url for url in image_urls if '&amp;' not in url and 'profile_pic' not in url]
        if hq_urls:
            return max(hq_urls, key=len)
        return max(image_urls, key=len)
    
    # Method 3: Fallback to og meta tags
    video_match = re.search(r'<meta property="og:video" content="([^"]+)"', text)
    if video_match:
        return video_match.group(1)
    
    image_match = re.search(r'<meta property="og:image" content="([^"]+)"', text)
    if image_match:
        return image_match.group(1)
    
    raise ValueError("Could not find public media URL. Is the post public? Instagram may require login for this content.")
