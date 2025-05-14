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
COOKIE_FILE = os.path.join(SESSIONS_DIR, "instagram_cookies.json")

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
    
    # Create a fresh client
    ig_client = Client()
    
    # First try to load from session file
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
                
            ig_client.load_settings(session_data)
            
            # Also load cookies if available for better session persistence
            if os.path.exists(COOKIE_FILE):
                with open(COOKIE_FILE, 'r') as f:
                    cookies = json.load(f)
                ig_client.set_cookies(cookies)
                
            # Verify the session is still valid (lightweight operation)
            try:
                # Just fetch account info to validate session
                ig_client.account_info()
                print("Instagram session loaded successfully")
                return True
            except Exception as e:
                print(f"Instagram session validation failed: {e}")
                # Session expired or invalid, but keep client for re-login
                return False
        except Exception as e:
            print(f"Error loading Instagram session: {e}")
            # Continue with a fresh client for login
            return False
    return False

def save_session():
    """Save Instagram session to file"""
    global ig_client
    if ig_client:
        try:
            # Save settings
            session_data = ig_client.get_settings()
            with open(SESSION_FILE, 'w') as f:
                json.dump(session_data, f)
                
            # Also save cookies separately for better persistence
            cookies = ig_client.get_cookies()
            with open(COOKIE_FILE, 'w') as f:
                json.dump(cookies, f)
                
            print("Instagram session saved successfully")
            return True
        except Exception as e:
            print(f"Error saving Instagram session: {e}")
            return False
    return False

async def register_commands():
    # Add force login command to bypass session loading
    @CipherElite.on(events.NewMessage(pattern=r"\.instaflogin\s+(\S+)\s+(.+)"))
    @rishabh()
    async def instagram_force_login(event):
        """Handler for forcing a fresh login to Instagram (bypassing session)"""
        global ig_client
        
        # Delete the message to protect credentials
        await event.delete()
        
        username = event.pattern_match.group(1)
        password = event.pattern_match.group(2)
        
        msg = await event.respond("🔐 Forcing fresh Instagram login...")
        
        # Clear any existing session files
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        if os.path.exists(COOKIE_FILE):
            os.remove(COOKIE_FILE)
        
        # Reset the client
        ig_client = Client()
        
        try:
            await msg.edit("🔄 Logging in with fresh session...")
            
            # Perform login in background
            login_success = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: perform_login(username, password)
            )
            
            if login_success:
                # Save new session
                if save_session():
                    await msg.edit("✅ Successfully logged in with fresh session!")
                else:
                    await msg.edit("⚠️ Logged in but failed to save session.")
            else:
                await msg.edit("❌ Login failed: Unknown error")
        except Exception as e:
            await msg.edit(f"❌ Force login failed: {str(e)}")
            ig_client = None
    
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
            # Create a fresh client if none exists
            if not ig_client:
                ig_client = Client()
                
            await msg.edit("🔐 Logging in to Instagram (this may take a moment)...")
            
            # Perform login in background to avoid blocking
            login_success = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: perform_login(username, password)
            )
            
            if login_success:
                # Save session for future use
                if save_session():
                    await msg.edit("✅ Successfully logged in to Instagram and saved session!")
                else:
                    await msg.edit("⚠️ Logged in to Instagram but failed to save session.")
            else:
                await msg.edit("❌ Login failed: Unknown error")
        except Exception as e:
            await msg.edit(f"❌ Login failed: {str(e)}")
            print(f"Instagram login error: {str(e)}")

def perform_login(username, password):
    """Perform login with robust error handling"""
    global ig_client
    
    try:
        # Clear any existing session data
        ig_client.set_settings({})
        ig_client.set_cookies({})
        
        # Try logging in with credentials
        ig_client.login(username, password)
        
        # Verify we're logged in by fetching profile
        account_info = ig_client.account_info()
        print(f"Instagram login successful as @{account_info.username}")
        return True
    except Exception as e:
        print(f"Instagram login exception: {str(e)}")
        return False
    
    @CipherElite.on(events.NewMessage(pattern=r"\.instastatus"))
    @rishabh()
    async def instagram_status(event):
        """Handler for checking Instagram login status"""
        global ig_client
        
        msg = await event.reply("🔍 Checking Instagram login status...")
        
        if not ig_client:
            await msg.edit("🔄 No active session, attempting to load saved session...")
            is_logged_in = load_session()
            if not is_logged_in:
                await msg.edit("❌ Not logged in to Instagram. Use `.instalog <username> <password>` to login.")
                return
                
        try:
            # Verify session is active
            await msg.edit("🔄 Verifying Instagram session...")
            
            account_info = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ig_client.account_info()
            )
            
            # Show detailed session info
            user_info = f"✅ Logged in as @{account_info.username}\n"
            user_info += f"👤 Name: {account_info.full_name}\n"
            user_info += f"📊 Followers: {account_info.follower_count} | Following: {account_info.following_count}\n"
            user_info += f"📝 Bio: {account_info.biography[:50] + '...' if len(account_info.biography) > 50 else account_info.biography}"
            
            await msg.edit(user_info)
        except Exception as e:
            error_msg = str(e)
            await msg.edit(f"❌ Session error: {error_msg}\nPlease login again using `.instalog <username> <password>`")
            
            # Try to provide more helpful error details
            if "login_required" in error_msg.lower():
                # Force cleanup of the invalid session
                if os.path.exists(SESSION_FILE):
                    os.remove(SESSION_FILE)
                if os.path.exists(COOKIE_FILE):
                    os.remove(COOKIE_FILE)
                
                ig_client = None
                await event.reply("⚠️ Your previous session has expired. Instagram requires re-authentication.")
            elif "checkpoint" in error_msg.lower() or "challenge" in error_msg.lower():
                await event.reply("⚠️ Instagram has flagged your account for verification. Please login to Instagram app directly to resolve this.")
            elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                await event.reply("⚠️ Instagram is rate limiting requests. Please try again later.")
            else:
                print(f"Instagram session error: {error_msg}")
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
                
            await msg.edit(f"📥 Downloading media with ID: {media_id}...")
            
            # Use the Instagram client to download
            try:
                media_type, media_path = await download_instagram_media(media_id)
                
                if not os.path.exists(media_path):
                    await msg.edit("❌ Failed to download media: File not found")
                    return
                    
                # Send the downloaded file
                await event.client.send_file(
                    event.chat_id,
                    media_path,
                    caption=f"📥 Downloaded {media_type} by CipherElite userbot"
                )
                
                # Clean up
                if os.path.isfile(media_path):
                    os.remove(media_path)
                elif os.path.isdir(media_path):
                    import shutil
                    shutil.rmtree(media_path, ignore_errors=True)
                    
                await msg.delete()
            except Exception as download_err:
                await msg.edit(f"❌ Download process failed: {str(download_err)}")
            
        except Exception as e:
            await msg.edit(f"❌ Process failed: {str(e)}")

def extract_media_id(url):
    """Extract media ID from Instagram URL"""
    # Extract shortcode from URL
    patterns = [
        r'instagram.com/p/([^/?]+)',      # Regular posts
        r'instagram.com/reel/([^/?]+)',   # Reels
        r'instagram.com/stories/[^/]+/(\d+)'  # Stories
    ]
    
    shortcode = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            shortcode = match.group(1)
            break
            
    if not shortcode:
        return None
        
    return shortcode

async def download_instagram_media(media_id):
    """Download media using authenticated Instagram client"""
    global ig_client
    
    # Create temp file path
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # For reels and posts, we can use the shortcode directly
        try:
            # Try as a regular post/reel using shortcode
            media_pk = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ig_client.media_pk_from_code(media_id)
            )
            
            # Once we have the media_pk, we can get media info
            media_info = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ig_client.media_info(media_pk)
            )
            
            if media_info.media_type == 1:  # Photo
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.photo_download(media_pk, folder=temp_dir)
                )
                return "photo", path
            elif media_info.media_type == 2:  # Video
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.video_download(media_pk, folder=temp_dir)
                )
                return "video", path
            elif media_info.media_type == 8:  # Album
                # For albums, download first item for now
                path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ig_client.album_download(media_pk, folder=temp_dir)
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
            # Try for story - these use numeric IDs directly
            if media_id.isdigit():
                try:
                    path = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: ig_client.story_download(int(media_id), folder=temp_dir)
                    )
                    return "story", path
                except Exception as story_e:
                    raise Exception(f"Failed to download story: {str(story_e)}")
            else:
                raise Exception(f"Failed to process media: {str(e)}")
                
    except Exception as e:
        raise Exception(f"Failed to download: {str(e)}")
