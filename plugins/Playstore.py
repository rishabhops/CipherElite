# ==============================================================================
#  CREDITS:
#  This plugin logic is based on CatUserBot's 'app' plugin.
#  Copyright (C) 2020-2023 by TgCatUB@Github.
#  Source: https://github.com/TgCatUB/catuserbot
# ==============================================================================

import os
import requests
import bs4
import urllib.request
from PIL import Image, ImageDraw, ImageFont
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# --- Constants & Assets ---
BG_URL_1 = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/app-full.jpg"
BG_URL_2 = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/app-suggest.jpg"

# 🔄 CHANGED: Now using standard Roboto-Medium (Google/Android Style)
FONT_URL = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Medium.ttf"
FONT_PATH = "Roboto-Medium.ttf"

# --- Helper Functions (Inlined for Standalone use) ---

def ensure_font():
    """Downloads the font if it doesn't exist."""
    if not os.path.exists(FONT_PATH):
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)

def make_circle(img):
    """Crops an image into a circle."""
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    output = Image.new("RGBA", img.size, (0, 0, 0, 0))
    output.paste(img, (0, 0), mask=mask)
    return output

def text_draw(font_name, font_size, img, text, x, y, fill="white"):
    """Draws text on the image."""
    font = ImageFont.truetype(font_name, font_size)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text=text, fill=fill, font=font)

# --- Plugin Structure ---

def init(client_instance):
    commands = [
        ".app <name> - Search app in Play Store & generate card"
    ]
    description = "🎭 App Store - Search and fetch Android app details"
    add_handler("playstore", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.app(?:\s+(.+))?"))
    @rishabh()
    async def app_search_handler(event):
        try:
            query = event.pattern_match.group(1)
            if not query:
                return await event.reply("💡 **Usage:** `.app <app name>`\nExample: `.app telegram`")

            status = await event.reply(f"🔄 **Searching Play Store for `{query}`...**")
            
            # 1. Scrape Play Store
            final_name = query.replace(" ", "+")
            url = f"https://play.google.com/store/search?q={final_name}&c=apps"
            page = requests.get(url)
            soup = bs4.BeautifulSoup(page.content, "lxml")

            try:
                # Selectors (TgCatUB logic)
                fullapp_name = (soup.find("div", "vWM94c") or soup.find("span", "DdYX5")).text
                dev_name = (soup.find("div", "LbQbAe") or soup.find("span", "wMUdtb")).text
                rating = (soup.find("div", "TT9eCd") or soup.find("span", "w2kbF")).text.replace("star", "")
                
                # Icon handling
                img_tag = soup.find("img", "T75of bzqKMd") or soup.find("img", "T75of stzEZd")
                app_icon = img_tag["src"].split("=s")[0]
                
                # Links
                link_tag = soup.find("a", "Qfxief") or soup.find("a", "Si6A0c Gy4nib")
                app_link = "https://play.google.com" + link_tag["href"]
                dev_link = "https://play.google.com/store/apps/developer?id=" + dev_name.replace(" ", "+")
                
                # Details
                review_tag = soup.find("div", "g1rdde")
                review = review_tag.text if review_tag else None
                
                downloads_tags = soup.findAll("div", "ClM7O")
                downloads = f"{downloads_tags[1].text} downloads" if downloads_tags and len(downloads_tags) > 1 else None

            except AttributeError:
                return await status.edit("❌ **Error:** App not found. Try a specific name.")

            # 2. Image Generation
            await status.edit("🎨 **Generating App Card...**")
            
            # Ensure assets
            ensure_font()
            bg_url = BG_URL_1 if downloads and review else BG_URL_2
            
            pic_name = "temp_app_bg.png"
            logo_name = "temp_app_logo.png"
            
            # Download images
            urllib.request.urlretrieve(app_icon, logo_name)
            urllib.request.urlretrieve(bg_url, pic_name)
            
            # Process Image
            background = Image.open(pic_name).resize((1024, 512))
            thumbmask = Image.new("RGBA", (1024, 512), 0)
            thumbmask.paste(background, (0, 0))

            # Icon processing
            logo_img = Image.open(logo_name).convert("RGBA").resize((250, 250))
            logo_circle = make_circle(logo_img)
            thumbmask.paste(logo_circle, (680, 100), logo_circle)

            # Draw Text
            short_name = fullapp_name[:14] + "..." if len(fullapp_name) > 14 else fullapp_name
            
            text_draw(FONT_PATH, 65, thumbmask, short_name, 50, 30)
            text_draw(FONT_PATH, 30, thumbmask, dev_name, 60, 120, "red")
            text_draw(FONT_PATH, 70, thumbmask, f"{rating} / 5", 190, 260)
            
            if bg_url == BG_URL_1:
                text_draw(FONT_PATH, 35, thumbmask, review or "", 80, 420)
                text_draw(FONT_PATH, 30, thumbmask, downloads or "", 415, 420)

            final_path = "playstore_result.png"
            thumbmask.save(final_path)

            # Cleanup temp files
            if os.path.exists(logo_name): os.remove(logo_name)
            if os.path.exists(pic_name): os.remove(pic_name)

            # 3. Send Response
            caption = (
                f"🎭 **Cipher Elite Play Store**\n\n"
                f"📲 **App:** `{fullapp_name}`\n"
                f"👨‍💻 **Developer:** [{dev_name}]({dev_link})\n"
                f"⭐️ **Rating:** `{rating} ⭐`\n"
                f"📥 **Downloads:** `{downloads or 'N/A'}`\n\n"
                f"🔗 [View in Play Store]({app_link})"
            )
            
            await event.delete()
            await event.client.send_file(
                event.chat_id,
                final_path,
                caption=caption,
                reply_to=event.reply_to_msg_id
            )
            
            if os.path.exists(final_path): os.remove(final_path)

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
