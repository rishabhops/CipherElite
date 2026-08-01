# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    meme
#  Created: 17/07/2026
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "animations"

import aiohttp
import os
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import asyncio

MEME_API = "https://meme-api.com/gimme"
DEFAULT_SUBS = ["memes", "dankmemes", "wholesomememes", "ProgrammerHumor", "indianmemes", "me_irl"]


def init(client_instance):
    commands = [
        ".meme - Get a random meme (auto-detects Image/GIF/Video)",
        ".meme <subreddit> - Get a meme from a specific subreddit",
        ".meme <count> - Get multiple memes (e.g., .meme 5)",
        ".meme <subreddit> <count> - Get memes from a subreddit",
    ]
    description = "😂 Fetch random memes from Reddit"
    add_handler("meme", commands, description)


async def fetch_meme(session, sub=None, count=1):
    """Fetch memes from meme-api.com"""
    if sub:
        url = f"{MEME_API}/{sub.strip()}/{count}" if count > 1 else f"{MEME_API}/{sub.strip()}"
    else:
        url = f"{MEME_API}/{count}" if count > 1 else MEME_API

    async with session.get(url) as resp:
        if resp.status != 200:
            return None, f"❌ Couldn't fetch memes (status {resp.status})."
        data = await resp.json()
        if data.get("code") == 404 or not data.get("url") and not data.get("memes"):
            return None, f"❌ No memes found for `{sub}`. Check the subreddit name."
        return data, None


def detect_media_type(url):
    """Detect if the URL is an image, GIF, or video based on extension"""
    if not url:
        return "📄 Unknown"
    url_lower = url.lower()
    if url_lower.endswith(('.gif', '.gifv')) or 'gif' in url_lower:
        return "🎬 GIF"
    elif url_lower.endswith(('.mp4', '.webm', '.mov', '.avi')):
        return "🎥 Video"
    elif url_lower.endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
        return "🖼️ Image"
    else:
        return "📄 Unknown"


def format_meme_caption(meme, index=None):
    """Format a single meme's caption with style"""
    title = meme.get("title", "Meme")
    subreddit = meme.get("subreddit", "unknown")
    ups = meme.get("ups", 0)
    awards = meme.get("awards", 0)
    post_link = meme.get("postLink", "")
    nsfw = meme.get("nsfw", False)
    spoiler = meme.get("spoiler", False)
    url = meme.get("url", "")
    media_type = detect_media_type(url)

    # Emojis based on content
    nsfw_tag = "🔞 " if nsfw else ""
    spoiler_tag = "🔄 " if spoiler else ""

    if index:
        caption = f"📸 **Meme #{index}**\n"
    else:
        caption = f"😂 **{title}**\n"

    caption += (
        f"{media_type}  |  📌 **r/{subreddit}**"
        f"  |  ⬆️ {ups}"
    )
    if awards:
        caption += f"  |  🎁 {awards}"
    caption += f"\n🔗 {post_link}\n"
    caption += f"─── · ─── · ─── · ───\n"
    caption += f"{nsfw_tag}{spoiler_tag}🤖 **Powered by CipherElite**"
    return caption


async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.meme(?:\s+(.+))?"))
    @rishabh()
    async def meme_cmd(event):
        args = event.pattern_match.group(1)
        sub = None
        count = 1

        if args:
            parts = args.strip().split()
            # Check if first arg is a number or subreddit
            try:
                count = int(parts[0])
                sub = None
                if len(parts) > 1:
                    sub = parts[1]
                    count = int(parts[0]) if parts[0].isdigit() else 1
            except ValueError:
                sub = parts[0]
                if len(parts) > 1:
                    try:
                        count = int(parts[1])
                    except:
                        count = 1

        if count > 10:
            await event.reply("❌ You can only request up to 10 memes at once.")
            return

        msg = await event.reply("😂 Fetching memes..." if count == 1 else f"😂 Fetching {count} memes...")

        async with aiohttp.ClientSession() as session:
            data, error = await fetch_meme(session, sub, count)
            if error:
                await msg.edit(error)
                return

        if count == 1:
            meme = data
            if meme.get("nsfw"):
                await msg.edit("⚠️ Meme is NSFW. Use `.meme` with a different subreddit.")
                return
            caption = format_meme_caption(meme)
            image_url = meme.get("url")
            try:
                if image_url:
                    await event.reply(caption, file=image_url)
                    await msg.delete()
                else:
                    await msg.edit(f"{caption}\n\n(Image URL not available)")
            except Exception as e:
                await msg.edit(f"{caption}\n\n(Couldn't load media, link: {image_url})\nError: {str(e)}")
        else:
            memes = data.get("memes", [])
            if not memes:
                await msg.edit("❌ No memes found.")
                return

            # Send each meme as separate message
            sent = 0
            for idx, meme in enumerate(memes, 1):
                if meme.get("nsfw"):
                    continue  # skip NSFW
                caption = format_meme_caption(meme, idx)
                image_url = meme.get("url")
                try:
                    await event.reply(caption, file=image_url)
                    await asyncio.sleep(0.5)  # small delay to avoid flood
                    sent += 1
                except Exception as e:
                    await event.reply(f"{caption}\n\n(Media link: {image_url})\nError: {str(e)}")
                    await asyncio.sleep(0.5)
                if sent >= count:
                    break
            await msg.delete()
            if sent == 0:
                await event.reply("❌ No valid memes found (all were NSFW or failed to load).")