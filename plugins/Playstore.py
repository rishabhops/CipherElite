# ==============================================================================
#  CREDITS:
#  Based on CatUserBot's 'app' plugin.
#  Copyright (C) 2020-2023 by TgCatUB@Github.
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

# --- Constants ---
BG_URL_FULL = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/1765442191944.jpg" 


FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/apache/roboto/static/Roboto-Medium.ttf"
FONT_PATH = "Roboto-Medium.ttf"

# --- Helper Functions ---

def download_file(url, filename):
    try:
        if os.path.exists(filename): return True
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        print(f"⚠️ DOWNLOAD FAILED: {url}\nError: {e}")
        return False

def make_circle(img):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    output = Image.new("RGBA", img.size, (0, 0, 0, 0))
    output.paste(img, (0, 0), mask=mask)
    return output

def text_draw(img, text, x, y, size, font_path=None, fill="white"):
    try:
        font = ImageFont.truetype(font_path, size) if font_path and os.path.exists(font_path) else ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text=str(text), fill=fill, font=font)

# --- Plugin Logic ---

def init(client_instance):
    commands = [".app <name> - Search Play Store"]
    description = "🎭 App Store - Search Android apps"
    add_handler("playstore", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.app(?:\s+(.+))?"))
    @rishabh()
    async def app_search_handler(event):
        try:
            query = event.pattern_match.group(1)
            if not query: return await event.reply("💡 **Usage:** `.app telegram`")
            status = await event.reply(f"🔄 **Searching `{query}`...**")

            # 1. Scrape Play Store
            final_name = query.replace(" ", "+")
            url = f"https://play.google.com/store/search?q={final_name}&c=apps"
            page = requests.get(url)
            soup = bs4.BeautifulSoup(page.content, "lxml")

            try:
                fullapp_name = (soup.find("div", "vWM94c") or soup.find("span", "DdYX5")).text
                dev_name = (soup.find("div", "LbQbAe") or soup.find("span", "wMUdtb")).text
                rating = (soup.find("div", "TT9eCd") or soup.find("span", "w2kbF")).text.replace("star", "")
                img_tag = soup.find("img", "T75of bzqKMd") or soup.find("img", "T75of stzEZd")
                app_icon = img_tag["src"].split("=s")[0]
                link_tag = soup.find("a", "Qfxief") or soup.find("a", "Si6A0c Gy4nib")
                app_link = "https://play.google.com" + link_tag["href"]
                dev_link = "https://play.google.com/store/apps/developer?id=" + dev_name.replace(" ", "+")
                
                review_tag = soup.find("div", "g1rdde")
                review = review_tag.text if review_tag else "N/A"
                downloads_tags = soup.findAll("div", "ClM7O")
                downloads = f"{downloads_tags[1].text}" if downloads_tags and len(downloads_tags) > 1 else "N/A"

            except AttributeError:
                return await status.edit("❌ **Not Found:** Could not find that app.")

            # 2. Download Assets
            await status.edit("🎨 **Generating Card...**")
            download_file(FONT_URL, FONT_PATH)
            
            # Use your new image
            target_bg = BG_URL_FULL
            pic_name = "temp_bg.png"
            logo_name = "temp_logo.png"
            
            bg_success = download_file(target_bg, pic_name)
            icon_success = download_file(app_icon, logo_name)

            # 3. Create Image
            if bg_success:
                background = Image.open(pic_name).resize((1024, 512))
            else:
                background = Image.new("RGBA", (1024, 512), (20, 20, 30, 255))

            thumbmask = Image.new("RGBA", (1024, 512), 0)
            thumbmask.paste(background, (0, 0))

            # --- COORDINATE ADJUSTMENTS FOR YOUR NEW IMAGE ---
            
            # 1. App Icon -> Centered inside the glowing ring on the right
            if icon_success:
                try:
                    logo_img = Image.open(logo_name).convert("RGBA").resize((280, 280)) # Slightly larger for the ring
                    logo_circle = make_circle(logo_img)
                    # Coordinates tailored to the glowing circle in your image
                    thumbmask.paste(logo_circle, (640, 115), logo_circle) 
                except: pass

            # 2. App Name -> Top Left (Dark Area)
            short_name = fullapp_name[:12] + ".." if len(fullapp_name) > 12 else fullapp_name
            text_draw(thumbmask, short_name, 50, 60, 85, FONT_PATH, fill="#b3e5fc") # Light Cyan Text

            # 3. Developer Name -> Below App Name
            text_draw(thumbmask, dev_name[:25], 55, 160, 35, FONT_PATH, fill="#ffffff")

            # 4. Rating -> Bottom Left area
            text_draw(thumbmask, f"{rating} ⭐", 55, 250, 60, FONT_PATH, fill="#ffd700") # Gold Star

            # 5. Stats -> Bottom Left (Aligned)
            text_draw(thumbmask, f"📥 {downloads}", 55, 350, 35, FONT_PATH, fill="#e0f7fa")
            text_draw(thumbmask, f"💬 {review} Reviews", 55, 400, 35, FONT_PATH, fill="#e0f7fa")

            final_path = "playstore_result.png"
            thumbmask.save(final_path)

            # 4. Send
            caption = (
                f"🎭 **Cipher Elite Play Store**\n\n"
                f"📲 **App:** `{fullapp_name}`\n"
                f"👨‍💻 **Developer:** [{dev_name}]({dev_link})\n"
                f"⭐️ **Rating:** `{rating} ⭐`\n"
                f"📥 **Downloads:** `{downloads}`\n\n"
                f"🔗 [View in Play Store]({app_link})"
            )

            await event.delete()
            await event.client.send_file(
                event.chat_id,
                final_path,
                caption=caption,
                reply_to=event.reply_to_msg_id
            )

            # Cleanup
            for f in [pic_name, logo_name, final_path]:
                if os.path.exists(f): os.remove(f)

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
