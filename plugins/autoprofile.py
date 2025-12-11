# ==============================================================================
#  🎭 Cipher Elite - Auto Profile Tools
#  Copyright (C) 2025 by Cipher Elite.
#  All rights reserved.
# ==============================================================================

import asyncio
import os
import ssl
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


USER_BG_URL = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/1000083995.jpg"


BACKUP_BG_URL = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1024&q=80"

# Font (Roboto Black)
FONT_URL = "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Black.ttf"
FONT_PATH = os.path.join(ASSETS_DIR, "bold.ttf")
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
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    return ist_now

def download_file(url, filename):
    """Downloads file with Strong SSL Bypass & User-Agent."""
    try:
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return True
            
        # Create unverified context to bypass SSL errors
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        print(f"⚠️ Download Failed for {url}: {e}")
        return False

async def notify_user(client, message):
    try:
        await client.send_message("me", message)
    except:
        pass

def generate_time_pfp():
    """Generates a PFP with the current IST time."""
    
    # 1. Try to download User Image
    if not download_file(USER_BG_URL, BG_PATH):
        # 2. If Failed, Download Backup Image
        print("User image failed. Downloading backup...")
        download_file(BACKUP_BG_URL, BG_PATH)
    
    download_file(FONT_URL, FONT_PATH)
    
    # Load Background
    if os.path.exists(BG_PATH):
        img = Image.open(BG_PATH).convert("RGBA").resize((1024, 1024))
    else:
        # Last Resort: Dark Blue (Better than black)
        img = Image.new("RGBA", (1024, 1024), (10, 10, 30, 255))
        
    draw = ImageDraw.Draw(img)
    ist_now = get_ist_time()
    time_str = ist_now.strftime("%H:%M")
    
    # Load Font
    try:
        font = ImageFont.truetype(FONT_PATH, 400) if os.path.exists(FONT_PATH) else ImageFont.load_default()
        small_font = ImageFont.truetype(FONT_PATH, 70) if os.path.exists(FONT_PATH) else ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw Time - CENTERED with OUTLINE
    draw.text(
        (512, 512), 
        time_str, 
        font=font, 
        fill="#00ffcc", 
        anchor="mm", 
        stroke_width=15, 
        stroke_fill="black"
    )
    
    # Draw Watermark
    draw.text(
        (512, 850), 
        "CIPHER ELITE", 
        font=small_font, 
        fill="#ffffff", 
        anchor="mm",
        stroke_width=5,
        stroke_fill="black"
    )

    img.convert("RGB").save(PFP_PATH)
    return PFP_PATH

# --- Async Loops ---

async def loop_autoname(client):
    while RUNNING_TASKS["autoname"]:
        try:
            ist_now = get_ist_time()
            time_str = ist_now.strftime("%H:%M")
            new_name = f"⚡ {time_str} | Cipher Elite"
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
        except FloodWaitError as e:
            await notify_user(client, f"⏳ AutoName FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
        await asyncio.sleep(60)

async def loop_autobio(client, custom_bio):
    while RUNNING_TASKS["autobio"]:
        try:
            ist_now = get_ist_time()
            time_str = ist_now.strftime("%H:%M")
            date_str = ist_now.strftime("%d-%b")
            new_bio = f"📅 {date_str} | {custom_bio} | ⌚ {time_str} (IST)"
            await client(functions.account.UpdateProfileRequest(about=new_bio))
        except FloodWaitError as e:
            await notify_user(client, f"⏳ AutoBio FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
        await asyncio.sleep(60)

async def loop_digitalpfp(client):
    while RUNNING_TASKS["digitalpfp"]:
        try:
            pfp_file = generate_time_pfp()
            if os.path.exists(pfp_file):
                file = await client.upload_file(pfp_file)
                await client(functions.photos.UploadProfilePhotoRequest(file=file))
                os.remove(pfp_file)
            else:
                await notify_user(client, "⚠️ PFP Gen Error")
        except FloodWaitError as e:
            await notify_user(client, f"🛑 PFP Stopped: FloodWait {e.seconds}s")
            RUNNING_TASKS["digitalpfp"] = False
            break
        except Exception as e:
            await notify_user(client, f"❌ PFP Error: {str(e)}")
        await asyncio.sleep(60)

# --- Plugin Init ---

def init(client_instance):
    commands = [
        ".autoname - Start Time in Name",
        ".autobio <text> - Start Time in Bio",
        ".digitalpfp - Start Bold Time PFP",
        ".end <task> - Stop task"
    ]
    description = "🎭 Profile Tools - Auto Updates"
    add_handler("autoprofile", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.autoname$"))
    @rishabh()
    async def enable_autoname(event):
        if RUNNING_TASKS["autoname"]: return await event.reply("⚠️ Running")
        RUNNING_TASKS["autoname"] = True
        CipherElite.loop.create_task(loop_autoname(event.client))
        await event.reply("🎭 **AutoName Started**")

    @CipherElite.on(events.NewMessage(pattern=r"\.autobio(?:\s+(.+))?"))
    @rishabh()
    async def enable_autobio(event):
        bio_text = event.pattern_match.group(1) or "Cipher Elite"
        if RUNNING_TASKS["autobio"]: return await event.reply("⚠️ Running")
        RUNNING_TASKS["autobio"] = True
        CipherElite.loop.create_task(loop_autobio(event.client, bio_text))
        await event.reply(f"🎭 **AutoBio Started:** `{bio_text}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.digitalpfp$"))
    @rishabh()
    async def enable_digitalpfp(event):
        if RUNNING_TASKS["digitalpfp"]: return await event.reply("⚠️ Running")
        status = await event.reply("🔄 **Starting PFP...**")
        
        # Cleanup old buggy file if it exists
        if os.path.exists(BG_PATH): os.remove(BG_PATH)
        
        try:
            test_path = generate_time_pfp()
            if not os.path.exists(test_path): return await status.edit("❌ Gen Error")
            file = await event.client.upload_file(test_path)
            await event.client(functions.photos.UploadProfilePhotoRequest(file=file))
            RUNNING_TASKS["digitalpfp"] = True
            CipherElite.loop.create_task(loop_digitalpfp(event.client))
            await status.edit("🎭 **Digital PFP Started**\nIf your image is missing, a backup Cyberpunk image was used.")
        except FloodWaitError as e:
            await status.edit(f"❌ FloodWait: {e.seconds}s")
        except Exception as e:
            await status.edit(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.end\s+(.+)"))
    @rishabh()
    async def end_task(event):
        task = event.pattern_match.group(1).lower().strip()
        if task in RUNNING_TASKS:
            RUNNING_TASKS[task] = False
            await event.reply(f"🛑 Stopped {task}")
        else:
            await event.reply("❌ Invalid task")
