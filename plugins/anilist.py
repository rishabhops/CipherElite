# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    anilist
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  Commands:       .anime <title>
#                  .manga <title>
#                  .airing
#                  .mal <title>
# =============================================================================

from telethon import events
import aiohttp
import time
from datetime import datetime
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

ANILIST_URL = "https://graphql.anilist.co/"
JIKAN_URL = "https://api.jikan.moe/v4"

ANIME_QUERY = """
query($search: String) {
  Media(search: $search, type: ANIME) {
    id
    title { romaji english native }
    format
    episodes
    status
    duration
    season
    startDate { year month day }
    averageScore
    genres
    description(asHtml: false)
    coverImage { large }
    siteUrl
    studios { nodes { name } }
  }
}
"""

MANGA_QUERY = """
query($search: String) {
  Media(search: $search, type: MANGA) {
    id
    title { romaji english native }
    format
    chapters
    volumes
    status
    startDate { year month day }
    averageScore
    genres
    description(asHtml: false)
    coverImage { large }
    siteUrl
  }
}
"""

AIRING_QUERY = """
query {
  Page(page: 1, perPage: 10) {
    airingSchedules(notYetAired: false, sort: TIME) {
      id
      episode
      airingAt
      timeUntilAiring
      media { title { romaji english } siteUrl }
    }
  }
}
"""

def clean_html(text):
    if not text:
        return ""
    return text.replace("<br>", "\n").replace("<i>", "").replace("</i>", "").replace("<b>", "**").replace("</b>", "**")

def format_date(date):
    if not date:
        return "N/A"
    y = date.get("year") or ""
    m = date.get("month") or ""
    d = date.get("day") or ""
    return f"{y}-{m}-{d}" if y else "N/A"

def init(client_instance):
    commands = [
        ".anime <title> - Search AniList anime",
        ".manga <title> - Search AniList manga",
        ".airing - Show currently airing schedule",
        ".mal <title> - Search MyAnimeList via Jikan"
    ]
    description = "Anime and manga lookup using AniList and Jikan"
    add_handler("anilist", commands, description)

async def anilist_request(query, variables):
    async with aiohttp.ClientSession() as session:
        async with session.post(ANILIST_URL, json={"query": query, "variables": variables}, headers={"Content-Type": "application/json"}) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.anime(?: |$)(.*)"))
    @rishabh()
    async def anime_search(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Provide an anime title. Example: `.anime Naruto`")
            return
        if event.is_reply:
            query = (await event.get_reply_message()).text or query
        data = await anilist_request(ANIME_QUERY, {"search": query})
        if not data or data.get("errors"):
            err = data["errors"][0]["message"] if data and data.get("errors") else "AniList API error"
            await event.reply(f"⚠️ {err}")
            return
        media = data["data"]["Media"]
        title = media["title"]["english"] or media["title"]["romaji"] or media["title"]["native"] or "Unknown"
        genres = ", ".join(media.get("genres", [])[:5])
        studios = ", ".join([s["name"] for s in media.get("studios", {}).get("nodes", [])[:3]]) or "N/A"
        desc = clean_html(media.get("description", "No description."))
        text = (
            f"🎌 **Anime:** {title}\n\n"
            f"📺 **Format:** `{media.get('format', 'N/A')}`\n"
            f"📊 **Episodes:** `{media.get('episodes', 'N/A')}` | **Duration:** `{media.get('duration', 'N/A')} min`\n"
            f"📅 **Status:** `{media.get('status', 'N/A')}` | **Season:** `{media.get('season', 'N/A')}`\n"
            f"⭐ **Score:** `{media.get('averageScore', 'N/A')}`\n"
            f"🏢 **Studio:** `{studios}`\n"
            f"🏷 **Genres:** `{genres}`\n"
            f"📆 **Start:** `{format_date(media.get('startDate'))}`\n\n"
            f"📝 {desc[:300]}{'...' if len(desc) > 300 else ''}\n\n"
            f"🔗 [AniList]({media.get('siteUrl')})"
        )
        await event.reply(text, file=media.get("coverImage", {}).get("large"), link_preview=False)

    @CipherElite.on(events.NewMessage(pattern=r"\.manga(?: |$)(.*)"))
    @rishabh()
    async def manga_search(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Provide a manga title. Example: `.manga One Piece`")
            return
        if event.is_reply:
            query = (await event.get_reply_message()).text or query
        data = await anilist_request(MANGA_QUERY, {"search": query})
        if not data or data.get("errors"):
            err = data["errors"][0]["message"] if data and data.get("errors") else "AniList API error"
            await event.reply(f"⚠️ {err}")
            return
        media = data["data"]["Media"]
        title = media["title"]["english"] or media["title"]["romaji"] or media["title"]["native"] or "Unknown"
        genres = ", ".join(media.get("genres", [])[:5])
        desc = clean_html(media.get("description", "No description."))
        text = (
            f"📖 **Manga:** {title}\n\n"
            f"📚 **Format:** `{media.get('format', 'N/A')}`\n"
            f"📊 **Chapters:** `{media.get('chapters', 'N/A')}` | **Volumes:** `{media.get('volumes', 'N/A')}`\n"
            f"📅 **Status:** `{media.get('status', 'N/A')}`\n"
            f"⭐ **Score:** `{media.get('averageScore', 'N/A')}`\n"
            f"🏷 **Genres:** `{genres}`\n"
            f"📆 **Start:** `{format_date(media.get('startDate'))}`\n\n"
            f"📝 {desc[:300]}{'...' if len(desc) > 300 else ''}\n\n"
            f"🔗 [AniList]({media.get('siteUrl')})"
        )
        await event.reply(text, file=media.get("coverImage", {}).get("large"), link_preview=False)

    @CipherElite.on(events.NewMessage(pattern=r"\.airing"))
    @rishabh()
    async def airing_schedule(event):
        data = await anilist_request(AIRING_QUERY, {})
        if not data or data.get("errors"):
            err = data["errors"][0]["message"] if data and data.get("errors") else "AniList API error"
            await event.reply(f"⚠️ {err}")
            return
        schedules = data["data"]["Page"]["airingSchedules"]
        if not schedules:
            await event.reply("📭 No airing schedule data right now.")
            return
        lines = ["📡 **Airing Now**\n"]
        for s in schedules:
            media = s["media"]
            title = media["title"]["english"] or media["title"]["romaji"] or "Unknown"
            airing_at = datetime.fromtimestamp(s["airingAt"]).strftime("%Y-%m-%d %H:%M")
            minutes = int(s["timeUntilAiring"] / 60)
            lines.append(
                f"• **{title}** — Ep `{s['episode']}`\n"
                f"  🕐 {airing_at} UTC ({minutes}m left)\n"
                f"  🔗 [AniList]({media.get('siteUrl')})\n"
            )
        await event.reply("\n".join(lines), link_preview=False)

    @CipherElite.on(events.NewMessage(pattern=r"\.mal(?: |$)(.*)"))
    @rishabh()
    async def mal_search(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Provide a title. Example: `.mal Naruto`")
            return
        if event.is_reply:
            query = (await event.get_reply_message()).text or query
        url = f"{JIKAN_URL}/anime?q={query}&limit=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status != 200:
                    await event.reply("⚠️ Jikan API error. Try again later.")
                    return
                data = await resp.json()
        results = data.get("data", [])
        if not results:
            await event.reply(f"⚠️ No MAL results for **{query}**.")
            return
        anime = results[0]
        title = anime.get("title", "Unknown")
        title_jp = anime.get("title_japanese", "")
        score = anime.get("score", "N/A")
        episodes = anime.get("episodes", "N/A")
        status = anime.get("status", "N/A")
        aired = anime.get("aired", {}).get("string", "N/A")
        rating = anime.get("rating", "N/A")
        genres = ", ".join([g["name"] for g in anime.get("genres", [])])
        synopsis = anime.get("synopsis", "No synopsis.")
        url = anime.get("url", "")
        image = anime.get("images", {}).get("jpg", {}).get("large_image_url", "")
        text = (
            f"🎌 **MyAnimeList:** {title}\n"
            f"_{title_jp}_\n\n"
            f"⭐ **Score:** `{score}` | **Episodes:** `{episodes}`\n"
            f"📅 **Status:** `{status}` | **Aired:** `{aired}`\n"
            f"🔞 **Rating:** `{rating}`\n"
            f"🏷 **Genres:** `{genres}`\n\n"
            f"📝 {synopsis[:400]}{'...' if len(synopsis) > 400 else ''}\n\n"
            f"🔗 [MAL]({url})"
        )
        await event.reply(text, file=image, link_preview=False)
