# ==============================================================================
#  🎭 Cipher Elite - Auto Profile Tools
#  Copyright (C) 2025 by Cipher Elite.
#  All rights reserved.
# ==============================================================================

import asyncio
import os
import urllib.request
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from telethon import functions, events
from telethon.errors import FloodWaitError, RPCError
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# --- Configuration & Assets ---
ASSETS_DIR = "cipher_assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Default Background for Digital PFP (Cyberpunk Style)
DEFAULT_BG = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/1000083995.jpg"
# Cool Digital Font
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/orbitron/Orbitron-Bold.ttf"
FONT_PATH = os.path.join(ASSETS_DIR, "digital.ttf")
PFP_PATH = os.path.join(ASSETS_DIR, "current_pfp.jpg")
BG_PATH = os.path.join(ASSETS_DIR, "bg.jpg")

# --- Global State ---
RUNNING_TASKS = {
    "autoname": False,
    "autobio": False,
    "digitalpfp": False
}

# --- Helper Functions ---

def get_ist_time():
    """Returns the current time in Indian Standard Time (UTC+5:30)."""
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    return ist_now

def download_file(url, filename):
    """Downloads file with User-Agent to prevent 403 errors."""
    try:
        if os.path.exists(filename):
            return True
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        print(f"⚠️ Download Failed: {e}")
        return False

async def notify_user(client, message):
    """Sends a log message to Saved Messages (Me)."""
    try:
        await client.send_message("me", message)
    except:
        pass

def generate_time_pfp():
    """Generates a PFP with the current IST time."""
    # Ensure assets exist
    download_file(FONT_URL, FONT_PATH)
    download_file(DEFAULT_BG, BG_PATH)
    
    # Load Background (Create black fallback if download failed)
    if os.path.exists(BG_PATH):
        img = Image.open(BG_PATH).convert("RGBA").resize((1024, 1024))
    else:
        img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 255))
        
    draw = ImageDraw.Draw(img)
    
    # Calculate Time (IST)
    ist_now = get_ist_time()
    time_str = ist_now.strftime("%H:%M")
    
    # Load Font
    try:
        if os.path.exists(FONT_PATH):
            font = ImageFont.truetype(FONT_PATH, 220)
            small_font = ImageFont.truetype(FONT_PATH, 50)
        else:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw Text (Centered) - Neon Green Color
    draw.text((220, 380), time_str, font=font, fill="#00ffcc")
    
    # Add "Cipher Elite" watermark
    draw.text((340, 650), "CIPHER ELITE", font=small_font, fill="#ffffff")

    img.convert("RGB").save(PFP_PATH)
    return PFP_PATH

# --- Async Loops ---

async def loop_autoname(client):
    """Updates name every minute (IST)."""
    while RUNNING_TASKS["autoname"]:
        try:
            ist_now = get_ist_time()
            time_str = ist_now.strftime("%H:%M")
            new_name = f"⚡ {time_str} | Cipher Elite"
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
        except FloodWaitError as e:
            await notify_user(client, f"⏳ **FloodWait in AutoName:** Sleeping for {e.seconds}s.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            await notify_user(client, f"❌ **AutoName Error:** {str(e)}\nStopping task.")
            RUNNING_TASKS["autoname"] = False
        await asyncio.sleep(60)

async def loop_autobio(client, custom_bio):
    """Updates bio every minute (IST)."""
    while RUNNING_TASKS["autobio"]:
        try:
            ist_now = get_ist_time()
            time_str = ist_now.strftime("%H:%M")
            date_str = ist_now.strftime("%d-%b")
            new_bio = f"📅 {date_str} | {custom_bio} | ⌚ {time_str} (IST)"
            await client(functions.account.UpdateProfileRequest(about=new_bio))
        except FloodWaitError as e:
            await notify_user(client, f"⏳ **FloodWait in AutoBio:** Sleeping for {e.seconds}s.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            await notify_user(client, f"❌ **AutoBio Error:** {str(e)}\nStopping task.")
            RUNNING_TASKS["autobio"] = False
        await asyncio.sleep(60)

async def loop_digitalpfp(client):
    """Updates PFP every minute (IST)."""
    while RUNNING_TASKS["digitalpfp"]:
        try:
            pfp_file = generate_time_pfp()
            
            if os.path.exists(pfp_file):
                file = await client.upload_file(pfp_file)
                # Explicitly calling UploadProfilePhotoRequest
                await client(functions.photos.UploadProfilePhotoRequest(
                    file=file,
                    # video=None,
                    # video_start_ts=None
                ))
                
                # Cleanup
                os.remove(pfp_file)
            else:
                await notify_user(client, "⚠️ **Digital PFP Error:** Generated image file not found.")
                
        except FloodWaitError as e:
            RUNNING_TASKS["digitalpfp"] = False
            await notify_user(client, f"🛑 **Digital PFP Stopped:** FloodWait detected ({e.seconds}s). Too many updates!")
            break # Stop loop to prevent ban
            
        except RPCError as e:
            await notify_user(client, f"❌ **Telegram API Error:** {str(e)}\nTask stopped.")
            RUNNING_TASKS["digitalpfp"] = False
            break
            
        except Exception as e:
            await notify_user(client, f"❌ **Digital PFP Crash:** {str(e)}")
            # We don't break here, might be a temporary network glitch
            
        await asyncio.sleep(60)

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".autoname - Start Time in Name (IST)",
        ".autobio <text> - Start Time in Bio (IST)",
        ".digitalpfp - Start Cyberpunk Time PFP (IST)",
        ".end <task> - Stop a task"
    ]
    description = "🎭 Profile Tools - Automate your profile identity"
    add_handler("autoprofile", commands, description)

async def register_commands():
    
    # -------------------------------------------------------------------------
    # 1. AUTO NAME
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.autoname$"))
    @rishabh()
    async def enable_autoname(event):
        if RUNNING_TASKS["autoname"]:
            return await event.reply("⚠️ **AutoName is already running!**")
        
        RUNNING_TASKS["autoname"] = True
        CipherElite.loop.create_task(loop_autoname(event.client))
        await event.reply("🎭 **Cipher Elite: AutoName Enabled (IST).**\nName will update every minute.")

    # -------------------------------------------------------------------------
    # 2. AUTO BIO
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.autobio(?:\s+(.+))?"))
    @rishabh()
    async def enable_autobio(event):
        bio_text = event.pattern_match.group(1)
        if not bio_text:
            bio_text = "Cipher Elite User"
            
        if RUNNING_TASKS["autobio"]:
            return await event.reply("⚠️ **AutoBio is already running!** Stop it first to change text.")
        
        RUNNING_TASKS["autobio"] = True
        CipherElite.loop.create_task(loop_autobio(event.client, bio_text))
        await event.reply(f"🎭 **Cipher Elite: AutoBio Enabled (IST).**\nBio set to: `{bio_text}`")

    # -------------------------------------------------------------------------
    # 3. DIGITAL PFP
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.digitalpfp$"))
    @rishabh()
    async def enable_digitalpfp(event):
        if RUNNING_TASKS["digitalpfp"]:
            return await event.reply("⚠️ **DigitalPFP is already running!**")
        
        # Trigger an initial check
        status = await event.reply("🔄 **Starting Digital PFP (IST)...**")
        
        try:
            # 1. Test Generation
            test_path = generate_time_pfp()
            if not os.path.exists(test_path):
                return await status.edit("❌ **Error:** Image generation failed. Check permissions.")
            
            # 2. Test Upload (Initial Run)
            file = await event.client.upload_file(test_path)
            await event.client(functions.photos.UploadProfilePhotoRequest(file=file))
            
            # 3. Start Loop
            RUNNING_TASKS["digitalpfp"] = True
            CipherElite.loop.create_task(loop_digitalpfp(event.client))
            await status.edit("🎭 **Cipher Elite: Digital PFP Active.**\nProfile updated successfully. Loop started.")
            
        except FloodWaitError as e:
            await status.edit(f"❌ **FloodWait:** You are changing PFP too fast. Wait {e.seconds} seconds.")
        except Exception as e:
            await status.edit(f"❌ **Error starting PFP:** {str(e)}")

    # -------------------------------------------------------------------------
    # 4. END TASKS
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.end\s+(.+)"))
    @rishabh()
    async def end_task(event):
        task_name = event.pattern_match.group(1).lower().strip()
        
        if task_name in RUNNING_TASKS:
            if RUNNING_TASKS[task_name]:
                RUNNING_TASKS[task_name] = False
                await event.reply(f"🛑 **Stopped {task_name} successfully.**")
            else:
                await event.reply(f"⚠️ **{task_name} was not running.**")
        else:
            await event.reply("❌ **Invalid task.** Use: `autoname`, `autobio`, or `digitalpfp`.")
