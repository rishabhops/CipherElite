# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    quotes
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .quote <topic>
#                  .pquote
# =============================================================================

from telethon import events
import aiohttp
import random
from bs4 import BeautifulSoup
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

PROGQUOTES = [
    "Talk is cheap. Show me the code.",
    "Programs must be written for people to read, and only incidentally for machines to execute.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "First, solve the problem. Then, write the code.",
    "Experience is the name everyone gives to their mistakes.",
]

async def extract_quote(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            text = await resp.text()
    soup = BeautifulSoup(text, "html.parser")
    results = []
    for quote in soup.find_all("div", class_="quote"):
        q = quote.find("div", {"class": "quoteText"})
        if q:
            results.append(q.text.replace("\n", " ").strip())
    return results

async def random_quote():
    pgno = random.randint(1, 100)
    url = f"https://www.goodreads.com/quotes?format=html&mobile_xhr=1&page={pgno}"
    results = await extract_quote(url)
    return random.choice(results) if results else "No quote found."

async def search_quotes(query):
    pgno = random.randint(1, 5)
    url = f"https://www.goodreads.com/quotes/search?commit=Search&page={pgno}&q={query.replace(' ', '+')}&utf8=%E2%9C%93"
    results = await extract_quote(url)
    return random.choice(results) if results else "No quote found."

def init(client_instance):
    commands = [
        ".quote <topic> - Random quote from Goodreads",
        ".pquote - Random programming quote"
    ]
    description = "Quote commands from CatPlugins"
    add_handler("quotes", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.quote(?: |$)([\s\S]*)"))
    @rishabh()
    async def quote_cmd(event):
        query = event.pattern_match.group(1).strip()
        if event.is_reply:
            query = (await event.get_reply_message()).text or query
        try:
            result = await search_quotes(query) if query else await random_quote()
        except Exception as e:
            await event.reply(f"⚠️ Error: `{str(e)}`")
            return
        await event.reply(result)

    @CipherElite.on(events.NewMessage(pattern=r"\.pquote$"))
    @rishabh()
    async def pquote_cmd(event):
        await event.reply(random.choice(PROGQUOTES))
