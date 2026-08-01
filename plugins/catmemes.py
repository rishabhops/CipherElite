# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    catmemes
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .cowsay, .slap, .shout, .owo, .clap, .smk, .f, .wish,
#                  .lfy, .gbun, .yes, .no, .maybe
#  Note:           .coin and .decide skipped because they conflict with fun.py
# =============================================================================

from telethon import events
import aiohttp
import random
import re
import asyncio
from urllib.parse import quote
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

UWUS = ["(・`ω´・)", ";;w;;", "owo", "UwU", ">w<", "^w^", "✧w✧", "(ᵘʷᵘ)", "(´・ω・｀)"]

SLAP_TEMPLATES = [
    "{victim} was {hit} with a {item} by {hitter}.",
    "{hitter} {throws} a {item} at {victim} and it {hit} them.",
    "{hitter} casually slaps {victim} with a {item}.",
    "{victim} got {hit} with a {item} by {hitter}.",
    "A {item} was thrown by {hitter} at {victim}.",
]
ITEMS = ["cast iron pan", "large trout", "baseball bat", "cricket bat", "wooden cane", "printer", "shovel", "CRT monitor", "keyboard"]
HIT = ["slapped", "smacked", "bonked", "whacked", "hit", "bopped"]
THROWS = ["throws", "flings", "chucks", "slings"]

COW = r""" \
   \
    \
      ^__^
      (oo)\\_______
      (__)\\       )\\/\\
          ||----w |
          ||     ||"""

def _cowsay(text):
    lines = text.splitlines()
    max_len = max(len(line) for line in lines) if lines else 0
    border = "_" * (max_len + 2)
    bottom = "-" * (max_len + 2)
    body = "\n".join(f"| {line.ljust(max_len)} |" for line in lines)
    return f" {border}\n{body}\n {bottom}\n{COW}"

def init(client_instance):
    commands = [
        ".cowsay <text> - Cowsay text",
        ".slap <user> - Slap a user",
        ".shout <text> - Shout text",
        ".owo <text> - UwUify text",
        ".clap <text> - Clap text",
        ".smk <text> - Add smirk",
        ".f <emoji> - Pay respects",
        ".wish <text> - Wish chance",
        ".lfy <query> - Let me Google that",
        ".gbun <reason> - Fake global ban",
        ".yes, .no, .maybe - Yes/No/Maybe gif"
    ]
    description = "CatPlugins memes and fun commands"
    add_handler("catmemes", commands, description)

async def register_commands():

    async def _get_text(event):
        text = event.pattern_match.group(1).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        return text

    async def _resolve_user(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            try:
                user = await event.client.get_entity(reply.sender_id)
                return user, reply.sender_id
            except Exception:
                return None, reply.sender_id
        text = event.text.split(maxsplit=1)
        if len(text) < 2:
            return None, None
        try:
            user = await event.client.get_entity(text[1])
            return user, user.id
        except Exception:
            return None, None

    @CipherElite.on(events.NewMessage(pattern=r"\.(\w+)say(?: |$)([\s\S]*)"))
    @rishabh()
    async def cowsay(event):
        arg = event.pattern_match.group(1).lower()
        text = event.pattern_match.group(2).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        if not text:
            await event.reply("❌ Give me some text.")
            return
        if arg == "cow":
            arg = "default"
        await event.reply(f"```\n{_cowsay(text)}\n```")

    @CipherElite.on(events.NewMessage(pattern=r"\.slap(?: |$)([\s\S]*)"))
    @rishabh()
    async def slap(event):
        user, _ = await _resolve_user(event)
        if not user:
            await event.reply("❌ Reply to a user or provide username to slap.")
            return
        me = await event.client.get_me()
        template = random.choice(SLAP_TEMPLATES)
        caption = template.format(
            victim=user.first_name,
            hitter=me.first_name,
            item=random.choice(ITEMS),
            hit=random.choice(HIT),
            throws=random.choice(THROWS)
        )
        await event.reply(caption)

    @CipherElite.on(events.NewMessage(pattern=r"\.shout(?: |$)([\s\S]*)"))
    @rishabh()
    async def shout(event):
        input_str = await _get_text(event)
        if not input_str:
            await event.reply("❌ What should I shout?")
            return
        words = input_str.split()
        msg = ""
        for messagestr in words:
            text = " ".join(messagestr)
            result = [" ".join(text)]
            result.extend(f"{symbol} " + "  " * pos + symbol for pos, symbol in enumerate(text[1:]))
            result = list("\n".join(result))
            result[0] = text[0]
            result = "".join(result)
            msg += "\n" + result
            if len(words) > 1:
                msg += "\n\n----------\n"
        await event.reply(msg)

    @CipherElite.on(events.NewMessage(pattern=r"\.owo(?: |$)([\s\S]*)"))
    @rishabh()
    async def owo(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ UwU no text given!")
            return
        reply = re.sub(r"(r|l)", "w", text)
        reply = re.sub(r"(R|L)", "W", reply)
        reply = re.sub(r"n([aeiou])", r"ny\1", reply)
        reply = re.sub(r"N([aeiouAEIOU])", r"Ny\1", reply)
        reply = re.sub(r"\!+", f" {random.choice(UWUS)}", reply)
        reply = reply.replace("ove", "uv")
        reply += f" {random.choice(UWUS)}"
        await event.reply(reply)

    @CipherElite.on(events.NewMessage(pattern=r"\.clap(?: |$)([\s\S]*)"))
    @rishabh()
    async def clap(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Hah, I don't clap pointlessly!")
            return
        await event.reply("👏 " + text.replace(" ", " 👏 ") + " 👏")

    @CipherElite.on(events.NewMessage(pattern=r"\.smk(?: |$)([\s\S]*)"))
    @rishabh()
    async def smk(event):
        text = await _get_text(event)
        if not text:
            await event.reply("ツ")
            return
        if text == "dele":
            await event.reply(f"{text}te the hellツ")
        else:
            await event.reply(f"{text} ツ")

    @CipherElite.on(events.NewMessage(pattern=r"\.f(?: |$)([\s\S]*)"))
    @rishabh()
    async def f_cmd(event):
        pay = event.pattern_match.group(1).strip()
        if not pay:
            pay = "🌹"
        result = f"{pay * 8}\n{pay * 8}\n{pay * 2}\n{pay * 2}\n{pay * 2}\n{pay * 6}\n{pay * 6}\n{pay * 2}\n{pay * 2}\n{pay * 2}\n{pay * 2}\n{pay * 2}"
        await event.reply(result)

    @CipherElite.on(events.NewMessage(pattern=r"\.wish(?: |$)([\s\S]*)"))
    @rishabh()
    async def wish(event):
        wishtxt = event.pattern_match.group(1).strip()
        if event.is_reply and not wishtxt:
            wishtxt = "your wish"
        chance = random.randint(0, 100)
        if wishtxt:
            await event.reply(f"**Your wish **__{wishtxt}__ **has been cast.** ✨\n\n__Chance of success:__ **{chance}%**")
        else:
            await event.reply("What's your Wish? 😜")

    @CipherElite.on(events.NewMessage(pattern=r"\.lfy(?: |$)([\s\S]*)"))
    @rishabh()
    async def lfy(event):
        query = event.pattern_match.group(1).strip()
        if event.is_reply:
            query = (await event.get_reply_message()).text or query
        if not query:
            await event.reply("❌ Reply to text or give a query to search.")
            return
        url = f"https://da.gd/s?url=https://lmgtfy.com/?q={quote(query)}%26iie=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                short = (await resp.text()).strip()
        if short:
            await event.reply(f"[{query}]({short})\n`Thank me Later 🙃`")
        else:
            await event.reply("⚠️ Could not generate short link.")

    @CipherElite.on(events.NewMessage(pattern=r"\.gbun(?: |$)([\s\S]*)"))
    @rishabh()
    async def gbun(event):
        reason = event.pattern_match.group(1).strip()
        status = await event.reply("**Summoning out le Gungnir ❗️⚜️☠️**")
        await asyncio.sleep(3.5)
        if not event.is_reply:
            await status.edit("`Warning!! User 𝙂𝘽𝘼𝙉𝙉𝙀𝘿 By Admin...\nReason: Potential spammer.`")
            return
        reply = await event.get_reply_message()
        try:
            user = await event.client.get_entity(reply.sender_id)
        except Exception:
            await status.edit("❌ Could not resolve user.")
            return
        firstname = user.first_name
        usname = user.username
        idd = reply.sender_id
        jnl = f"`Warning!! `[{firstname}](tg://user?id={idd})` 𝙂𝘽𝘼𝙉𝙉𝙀𝘿 By Admin...\n\n`**User's Name:** __{firstname}__\n**ID:** `{idd}`\n"
        if usname:
            jnl += f"**Victim's username:** @{usname}\n"
        else:
            jnl += "**Victim's username:** `Doesn't own a username!`\n"
        if reason:
            jnl += f"**Reason:** `{reason}`"
        else:
            jnl += "**Reason:** Potential spammer."
        await status.edit(jnl)

    @CipherElite.on(events.NewMessage(pattern=r"\.(yes|no|maybe)$"))
    @rishabh()
    async def yesno(event):
        decision = event.pattern_match.group(1).lower()
        url = f"https://yesno.wtf/api?force={decision}" if decision != "maybe" else "https://yesno.wtf/api"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        message_id = None
        if event.is_reply:
            message_id = (await event.get_reply_message()).id
        await event.client.send_message(
            event.chat_id, str(data["answer"]).upper(),
            reply_to=message_id, file=data["image"]
        )
        try:
            await event.delete()
        except Exception:
            pass
