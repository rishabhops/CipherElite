# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    games
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .task, .truth, .dare, .game
# =============================================================================

from telethon import events
import aiohttp
import json
import random
import asyncio
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

GAME_CODE = ["ttt", "ttf", "ex", "cf", "rps", "rpsls", "rr", "c", "pc"]
GAME_NAME = [
    "Tic-Tac-Toe",
    "Tic-Tac-Four",
    "Elephant XO",
    "Connect Four",
    "Rock-Paper-Scissors",
    "Rock-Paper-Scissors-Lizard-Spock",
    "Russian Roulette",
    "Checkers",
    "Pool Checkers",
]
GAME = dict(zip(GAME_CODE, GAME_NAME))
CATEGORIES = ["classic", "kids", "party", "hot", "mixed"]

async def get_task(mode, choice):
    url = "https://psycatgames.com/api/tod-v2/"
    data = {
        "id": "truth-or-dare",
        "language": "en",
        "category": CATEGORIES[choice - 1],
        "type": mode,
    }
    headers = {"referer": "https://psycatgames.com/app/truth-or-dare/"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
            result = (await resp.json())["results"]
    return random.choice(result)

async def _send_task(event, taskmode, category):
    cat = int(random.choice(category)) if category else random.choice([1, 2])
    try:
        task = await get_task(taskmode, cat)
        label = "truth" if taskmode == "truth" else "dare"
        await event.reply(f"**The {label} task for you is**\n`{task}`")
    except Exception as e:
        await event.reply(f"⚠️ Error while getting task: `{str(e)}`")

def init(client_instance):
    commands = [
        ".task [category] - Random truth or dare task",
        ".truth [category] - Random truth task",
        ".dare [category] - Random dare task",
        ".game <code> - Play inline games via @inlinegamesbot"
    ]
    description = "Truth/Dare and inline games"
    add_handler("games", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.(task|truth|dare)(?: |$)([1-5]+)?$"))
    @rishabh()
    async def truth_dare_task(event):
        mode = event.pattern_match.group(1)
        category = event.pattern_match.group(2)
        if mode == "task":
            mode = random.choice(["truth", "dare"])
        await _send_task(event, mode, category)

    @CipherElite.on(events.NewMessage(pattern=r"\.game(?: |$)([\s\S]*)"))
    @rishabh()
    async def igame(event):
        if event.is_reply:
            reply_to = (await event.get_reply_message()).id
        else:
            reply_to = None
        code = event.pattern_match.group(1).strip().lower()
        game_list = "\n".join(f"**{i}.** `{code}` :- __{GAME[code]}__" for i, code in enumerate(GAME_CODE, start=1))
        if not code:
            await event.reply(f"**Available Game Codes & Names:**\n\n{game_list}")
            return
        if code not in GAME_CODE:
            await event.reply(f"**Available Game Codes & Names:**\n\n{game_list}")
            return
        await event.reply(f"**Game code `{code}` selected:** __{GAME[code]}__")
        await asyncio.sleep(1)
        try:
            results = await event.client.inline_query("@inlinegamesbot", code)
            await results[GAME_CODE.index(code)].click(event.chat_id, reply_to=reply_to)
            await event.delete()
        except Exception as e:
            await event.reply(f"⚠️ Could not start inline game: `{str(e)}`")
