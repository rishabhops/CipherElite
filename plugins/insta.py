import re
import os
import json
import aiohttp
import asyncio
from telethon import events
from instagrapi import Client
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Path to store Instagram session data
SESSIONS_DIR = os.path.join("data", "sessions")
SESSION_FILE = os.path.join(SESSIONS_DIR, "instagram_session.json")

# Ensure directories exist
os.makedirs(SESSIONS_DIR, exist_ok=True)

def init(client):
    """
    Register the Instagram commands in your /help text.
    """
    commands = [
        ".insta <url>  — Download an Instagram post (image, video or reel)",
        ".instalog <username> <password>  — Login to Instagram for accessing private content",
        ".instastatus  — Check Instagram login status"
    ]
    description = "Download Instagram media with proper authentication"
    add_handler("instagram", commands, description)

# Initialize Instagram client
ig_client = None

def load_session():
    """Load Instagram session from file if exists"""
    global ig_client
    
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
                
            ig_client = Client()
            ig_client.load_settings(session_data)
            # Verify the session is still valid (lightweight operation)
            try:
                # Just fetch account info to validate session
                ig_client.account_info()
                return True
            except Exception:
                # Session expired or invalid
                ig_client = None
                return False
        except Exception as e:
            print(f"Error loading Instagram session: {e}")
            return False
    return False

def save_session():
    """Save Instagram session to file"""
    global ig_client
    if ig_client:
        try:
            session_data = ig_client.get_settings()
            with open(SESSION_FILE, 'w') as f:
                json.dump(session_data, f)
            return True
        except Exception as e:
            print(f"Error saving Instagram session: {e}")
            return False
    return False

async def register_commands():
    # First attempt to load previous session
    load_session()
    
    @CipherElite.on(events.NewMessage(pattern=r"\.instalog\s+(\S+)\s+(.+)"))
    @rishabh()
    async def instagram_login(event):
        """Handler for logging in to Instagram"""
        global ig_client
        
        # Delete the message to protect credentials
        await event.delete()
        
        username = event.pattern_match.group(1)
        password = event.pattern_match.group(2)
        
        msg = await event.respond("🔐 Logging in to Instagram...")
        
        try:
            ig_client = Client()
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: ig_client.login(username, password)
            )
            
            # Save session for future use
            save_session()
            
            await msg.edit("✅ Successfully logged in to Instagram!")
        except Exception as e:
            await msg.edit(f"❌ Login failed: {str(e)}")
            ig_client = None
    
    @CipherElite.on(events.NewMessage(pattern=r"\.instastatus"))
    @rishabh()
    async def instagram_status(event):
        """Handler for checking Instagram login status"""
        global ig_client
        
        if not ig_client:
            is_logged_in = load_session()
            if not is_logged_in:
                await event.reply("❌ Not logged in to Instagram. Use `.instalog <username> <password>` to login.")
                return
                
        try:
            # Verify session is active
            account_info = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ig_client.account_info()
            )
            await event.reply(f"✅ Logged in as @{account_info.username}")
        except Exception as e:
            await event.reply(f"❌ Session error: {str(e)}\nPlease login again using `.instalog <username> <password>`")
            ig_client = None
    
    @CipherElite.on(events.NewMessage(pattern=r"\.insta\s+(https?://[^\s]+)"))
    @rishabh()
    async def instagram_dl(event):
        """Handler for downloading Instagram content"""
        global ig_client
        
        original_url = event.pattern_match.group(1).strip()
        
        # Check if logged in
        if not ig_client:
            is_logged_in = load_session()
            if not is_logged_in:
                await event.reply("❌ Not logged in to Instagram. Use `.instalog <username> <password>` to login first.")
                return
        
        msg = await event.reply("📥 Analyzing Instagram URL...")
        
        try:
            # Extract media ID from URL
            media_id = extract_media_id(original_url)
            if not media_id:
                await msg.edit("❌ Invalid Instagram URL. Make sure it's a post, reel or story URL.")
                return
                
            await msg.edit("📥 Downloading media...")
            
            # Use the Instagram client to download
            media_type, media_path = await download_instagram_media(media_id)
            
            if not os.path.exists(media_path):
                await msg.edit("❌ Failed to download media")
                return
                
            # Send the downloaded file
            await event.client.send_file(
                event.chat_id,
                media_path,
                caption="📥 Downloaded by CipherElite userbot"
            )
            
            # Clean up
            os.remove(media_path)
            await msg.delete()
            
        except Exception as e:
            await msg.edit(f"❌ Download failed: {str(e)}")

def extract_media_id(url):
    """Extract media ID from Instagram URL"""
    # Handle different URL formats
    patterns = [
        r'instagram.com/p/([^/]+)',      # Regular posts
        r'instagram.com/reel/([^/]+)',   # Reels
        r'instagram.com/stories/[^/]+/(\d+)'  # Stories
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    return None

async def download_instagram_media(media_id):
    """Download media using authenticated Instagram client"""
    global ig_client
    
    # Determine if it's a regular post or reel
    # Create temp file path
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # First try as a regular post
        try:
            media_info = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ig_client.media_info(media_id)
            )
            
            if media_info.media_type == 1:  # Photo
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.photo_download(media_id, folder=temp_dir)
                )
                return "photo", path
            elif media_info.media_type == 2:  # Video
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.video_download(media_id, folder=temp_dir)
                )
                return "video", path
            elif media_info.media_type == 8:  # Album
                # For albums, download first item for now
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.album_download(media_id, folder=temp_dir)
                )
                # Find the first file in album folder
                album_files = os.listdir(path)
                if album_files:
                    return "album", os.path.join(path, album_files[0])
                else:
                    raise Exception("Album is empty")
            else:
                raise Exception(f"Unsupported media type: {media_info.media_type}")
        except Exception as e:
            # Maybe it's a reel or story
            try:
                # Try as a reel
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.clip_download(media_id, folder=temp_dir)
                )
                return "reel", path
            except Exception:
                # Try as a story
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.story_download(media_id, folder=temp_dir)
                )
                return "story", path
                
    except Exception as e:
        raise Exception(f"Failed to download: {str(e)}")
