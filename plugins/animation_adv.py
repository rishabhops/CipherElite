import asyncio
import random
import time

from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        ".loveu              — Rainbow heart animation",
        ".matrix [sec]       — Matrix rain in text",
        ".hearts <text>      — Bubble hearts around your text",
        ".countdown <n>      — Count down from n to 0",
        ".wave <text>        — Text wave effect"
    ]
    add_handler("animation2", commands, "Advanced Animations")

async def safe_edit(msg, text):
    try:
        await msg.edit(text)
    except MessageNotModifiedError:
        pass

@CipherElite.on(events.NewMessage(pattern=r"^\.loveu$", outgoing=True))
@rishabh()
async def loveu(event):
    hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "💖", "💗", "💓"]
    msg = await event.reply(hearts[0])
    # cycle rainbow hearts then final message
    for i in range(len(hearts) * 3):
        await safe_edit(msg, hearts[i % len(hearts)])
        await asyncio.sleep(0.3)
    await safe_edit(msg, "I ❤️ U")

@CipherElite.on(events.NewMessage(pattern=r"^\.matrix(?:\s+(\d+))?$", outgoing=True))
@rishabh()
async def matrix(event):
    sec = event.pattern_match.group(1)
    total = int(sec) if sec and sec.isdigit() else 5
    width, height = 20, 6
    msg = await event.reply("Loading Matrix…")
    start = time.time()
    while time.time() - start < total:
        frame = ""
        for _ in range(height):
            line = "".join(random.choice(["0", "1", " "]) for _ in range(width))
            frame += line + "\n"
        await safe_edit(msg, f"```{frame}```")
        await asyncio.sleep(0.5)
    await safe_edit(msg, "🔚 Matrix end")

@CipherElite.on(events.NewMessage(pattern=r"^\.hearts\s+([\s\S]+)$", outgoing=True))
@rishabh()
async def hearts(event):
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.reply("❗️ Usage: `.hearts <text>`")
    msg = await event.reply(f"💖 {text} 💖")
    frames = [
        f"💘 {text} 💘",
        f"💕 {text} 💕",
        f"💞 {text} 💞",
        f"💓 {text} 💓",
    ]
    for i in range(len(frames) * 2):
        await safe_edit(msg, frames[i % len(frames)])
        await asyncio.sleep(0.6)
    await safe_edit(msg, f"💖 {text} 💖")

@CipherElite.on(events.NewMessage(pattern=r"^\.countdown\s+(\d+)$", outgoing=True))
@rishabh()
async def countdown(event):
    start_n = int(event.pattern_match.group(1))
    msg = await event.reply(str(start_n))
    for n in range(start_n - 1, -1, -1):
        await asyncio.sleep(1.0)
        await safe_edit(msg, str(n))
    await asyncio.sleep(0.5)
    await safe_edit(msg, "🎉 Boom!")

@CipherElite.on(events.NewMessage(pattern=r"^\.wave\s+([\s\S]+)$", outgoing=True))
@rishabh()
async def wave(event):
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.reply("❗️ Usage: `.wave <text>`")
    msg = await event.reply(text)
    width = len(text) + 4
    direction = 1
    pos = 0
    # two full back-and-forth cycles
    for _ in range(width * 2):
        gap = " " * pos
        await safe_edit(msg, gap + text)
        if pos == width or pos == 0:
            direction *= -1
        pos += direction
        await asyncio.sleep(0.1)
    await safe_edit(msg, text)
