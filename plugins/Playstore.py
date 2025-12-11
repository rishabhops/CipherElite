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
# Check these carefully! GitHub is Case SENSITIVE.
BG_URL_FULL = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/app-full.jpg"
BG_URL_SUGGEST = "https://raw.githubusercontent.com/rishabhops/CipherElite/elite/images/app-suggest.jpg"

# A safer, more direct link for the font
FONT_URL = "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Medium.ttf"
FONT_PATH = "Roboto-Medium.ttf"

# --- Helper Functions ---

def download_file(url, filename):
    """
    Tries to download a file. Returns True if success, False if 404/Error.
    """
    try:
        if os.path.exists(filename):
            return True
        # spoof user agent to avoid some 403 errors
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
    """Draws text, falling back to default font if custom font fails."""
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text=str(text), fill=fill, font=font)

# --- Plugin Init ---

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
            if not query:
                return await event.reply("💡 **Usage:** `.app telegram`")

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
                review = review_tag.text if review_tag else None
                
                downloads_tags = soup.findAll("div", "ClM7O")
                downloads = f"{downloads_tags[1].text} downloads" if downloads_tags and len(downloads_tags) > 1 else None

            except AttributeError:
                return await status.edit("❌ **Not Found:** Could not find that app.")

            # 2. Prepare Assets
            await status.edit("🎨 **Downloading Assets...**")
            
            # --- DEBUGGING DOWNLOADS ---
            font_success = download_file(FONT_URL, FONT_PATH)
            
            target_bg = BG_URL_FULL if (downloads and review) else BG_URL_SUGGEST
            pic_name = "temp_bg.jpg"
            logo_name = "temp_logo.jpg"
            
            bg_success = download_file(target_bg, pic_name)
            icon_success = download_file(app_icon, logo_name)

            if not bg_success:
                # Notify user but continue working
                await event.client.send_message(event.chat_id, f"⚠️ **Warning:** Could not download background image.\n`{target_bg}`\nUsing black background.")

            # 3. Generate Image
            if bg_success:
                background = Image.open(pic_name).resize((1024, 512))
            else:
                # Black background fallback
                background = Image.new("RGBA", (1024, 512), (20, 20, 20, 255))

            thumbmask = Image.new("RGBA", (1024, 512), 0)
            thumbmask.paste(background, (0, 0))

            if icon_success:
                try:
                    logo_img = Image.open(logo_name).convert("RGBA").resize((250, 250))
                    logo_circle = make_circle(logo_img)
                    thumbmask.paste(logo_circle, (680, 100), logo_circle)
                except Exception as e:
                    print(f"Icon Process Error: {e}")

            # Draw Text
            text_draw(thumbmask, fullapp_name[:15], 50, 30, 65, FONT_PATH)
            text_draw(thumbmask, dev_name, 60, 120, 30, FONT_PATH, "red")
            text_draw(thumbmask, f"{rating} / 5", 190, 260, 70, FONT_PATH)
            
            if downloads and review:
                text_draw(thumbmask, review, 80, 420, 35, FONT_PATH)
                text_draw(thumbmask, downloads, 415, 420, 30, FONT_PATH)

            final_path = "playstore_result.png"
            thumbmask.save(final_path)

            # 4. Send
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

            # Cleanup
            for f in [pic_name, logo_name, final_path]:
                if os.path.exists(f):
                    os.remove(f)

        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
