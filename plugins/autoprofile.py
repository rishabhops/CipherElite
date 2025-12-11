# ==============================================================================
#  🎭 Cipher Elite - Auto Profile Tools
#  Copyright (C) 2025 by Cipher Elite.
#  All rights reserved.
# ==============================================================================

import asyncio
import os
import time
import random
import shutil
import urllib.request
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from telethon import functions, events
from telethon.errors import FloodWaitError
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

# --- Global State (Controls the loops) ---
RUNNING_TASKS = {
    "autoname": False,
    "autobio": False,
    "digitalpfp": False
}

# --- Helper Functions ---

def ensure_assets():
    """Downloads necessary fonts and images if missing."""
    if not os.path.exists(FONT_PATH):
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)

def generate_time_pfp():
    """Generates a PFP with the current time overlaid on a cyberpunk bg."""
    ensure_assets()
    
    # Download BG if not exists or reuse
    bg_path = os.path.join(ASSETS_DIR, "bg.jpg")
    if not os.path.exists(bg_path):
        urllib.request.urlretrieve(DEFAULT_BG, bg_path)
    
    img = Image.open(bg_path).convert("RGBA").resize((1024, 1024)) # High quality
    draw = ImageDraw.Draw(img)
    
    # Calculate Time
    current_time = datetime.now().strftime("%H:%M")
    
    # Load Font
    try:
        font = ImageFont.truetype(FONT_PATH, 220)
    except:
        font = ImageFont.load_default()

    # Draw Text (Centered) - Neon Green Color
    # Coordinates tailored for 1024x1024
    draw.text((220, 400), current_time, font=font, fill="#00ffcc")
    
    # Add "Cipher Elite" watermark
    small_font = ImageFont.truetype(FONT_PATH, 50)
    draw.text((360, 650), "CIPHER ELITE", font=small_font, fill="#ffffff")

    img.convert("RGB").save(PFP_PATH)
    return PFP_PATH

# --- Async Loops ---

async def loop_autoname(client):
    """Updates name every minute."""
    while RUNNING_TASKS["autoname"]:
        try:
            time_str = datetime.now().strftime("%H:%M")
            # You can customize the name format here
            new_name = f"⚡ {time_str} | Cipher Elite"
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
        await asyncio.sleep(60)

async def loop_autobio(client, custom_bio):
    """Updates bio every minute."""
    while RUNNING_TASKS["autobio"]:
        try:
            time_str = datetime.now().strftime("%H:%M")
            date_str = datetime.now().strftime("%d-%b")
            # Format: 📅 Date | Bio | ⌚ Time
            new_bio = f"📅 {date_str} | {custom_bio} | ⌚ {time_str}"
            await client(functions.account.UpdateProfileRequest(about=new_bio))
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
        await asyncio.sleep(60)

async def loop_digitalpfp(client):
    """Updates PFP every minute."""
    while RUNNING_TASKS["digitalpfp"]:
        try:
            pfp_file = generate_time_pfp()
            file = await client.upload_file(pfp_file)
            
            # Delete old photos to prevent clutter (keep current)
            # await client(functions.photos.DeletePhotosRequest(
            #     await client.get_profile_photos("me", limit=1)
            # ))
            
            await client(functions.photos.UploadProfilePhotoRequest(file))
            
            # Clean up local file
            if os.path.exists(pfp_file):
                os.remove(pfp_file)
                
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Error in DigitalPFP: {e}")
        
        await asyncio.sleep(60)

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".autoname - Start Time in Name",
        ".autobio <text> - Start Time in Bio",
        ".digitalpfp - Start Cyberpunk Time PFP",
        ".end <task> - Stop a task (autoname, autobio, digitalpfp)"
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
        await event.reply("🎭 **Cipher Elite: AutoName Enabled.**\nName will update every minute.")

    # -------------------------------------------------------------------------
    # 2. AUTO BIO
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.autobio(?:\s+(.+))?"))
    @rishabh()
    async def enable_autobio(event):
        bio_text = event.pattern_match.group(1)
        if not bio_text:
            bio_text = "Cipher Elite User" # Default
            
        if RUNNING_TASKS["autobio"]:
            return await event.reply("⚠️ **AutoBio is already running!** Stop it first to change text.")
        
        RUNNING_TASKS["autobio"] = True
        CipherElite.loop.create_task(loop_autobio(event.client, bio_text))
        await event.reply(f"🎭 **Cipher Elite: AutoBio Enabled.**\nBio set to: `{bio_text}`")

    # -------------------------------------------------------------------------
    # 3. DIGITAL PFP (The Visual One)
    # -------------------------------------------------------------------------
    @CipherElite.on(events.NewMessage(pattern=r"\.digitalpfp$"))
    @rishabh()
    async def enable_digitalpfp(event):
        if RUNNING_TASKS["digitalpfp"]:
            return await event.reply("⚠️ **DigitalPFP is already running!**")
        
        RUNNING_TASKS["digitalpfp"] = True
        CipherElite.loop.create_task(loop_digitalpfp(event.client))
        await event.reply("🎭 **Cipher Elite: Digital PFP Enabled.**\nProfile picture will update every minute with Cyberpunk style.")

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
