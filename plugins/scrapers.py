# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    scrapers
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  Commands:       .wiki <query>
#                  .imdb <movie/series>
# =============================================================================

from telethon import events
import aiohttp
import json
import re
import urllib.parse
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "utilities"

def init(client_instance):
    commands = [
        ".wiki <query> - Search Wikipedia",
        ".imdb <query> - Search IMDb"
    ]
    description = "Web scraper utilities for quick lookups"
    add_handler("scrapers", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.wiki(?: |$)(.*)"))
    @rishabh()
    async def wiki_search(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Provide a search term. Example: `.wiki Python programming`")
            return
        if event.is_reply:
            query = (await event.get_reply_message()).text or query
        encoded = urllib.parse.quote(query.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status == 404:
                    await event.reply(f"⚠️ No Wikipedia article found for **{query}**.")
                    return
                if resp.status != 200:
                    await event.reply("⚠️ Wikipedia API error. Try again later.")
                    return
                data = await resp.json()
        title = data.get("title", query)
        extract = data.get("extract", "No summary available.")
        link = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{encoded}")
        description = data.get("description", "")
        text = (
            f"📚 **Wikipedia: {title}**\n"
            f"_{description}_\n\n"
            f"{extract}\n\n"
            f"🔗 [Read more]({link})"
        )
        await event.reply(text, link_preview=False)

    @CipherElite.on(events.NewMessage(pattern=r"\.imdb(?: |$)(.*)"))
    @rishabh()
    async def imdb_search(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.reply("❌ Provide a movie/series name. Example: `.imdb Inception`")
            return
        if event.is_reply:
            query = (await event.get_reply_message()).text or query
        encoded = urllib.parse.quote(query)
        url = f"https://v2.sg.media-imdb.com/suggests/i/{encoded}.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status != 200:
                    await event.reply("⚠️ IMDb search failed. Try again later.")
                    return
                raw = await resp.text()
        try:
            # Response is JSONP wrapped as imdb$<query>({...})
            json_str = raw.split("(", 1)[1].rsplit(")", 1)[0]
            data = json.loads(json_str)
        except Exception:
            await event.reply("⚠️ Could not parse IMDb response.")
            return
        results = data.get("d", [])
        if not results:
            await event.reply(f"⚠️ No IMDb results for **{query}**.")
            return
        # Build inline result list (up to 6)
        lines = [f"🎬 **IMDb results for `{query}`**\n"]
        for item in results[:6]:
            title = item.get("l", "Unknown")
            year = item.get("y", "N/A")
            kind = item.get("qid", item.get("q", "title")).replace("tv", "TV ").replace("movie", "Movie")
            imdb_id = item.get("id", "")
            cast = item.get("s", "")
            link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
            lines.append(
                f"• **{title}** ({year}) — {kind}\n"
                f"  🎭 {cast}\n"
                f"  🔗 {link}\n"
            )
        await event.reply("\n".join(lines), link_preview=False)
