import asyncio
import random

from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        ".animate <text>   — Simulate typing animation",
        ".spinner [sec]    — Show spinner animation"
    ]
    add_handler("animation", commands, "Text & Spinner Animation Plugin")

@CipherElite.on(events.NewMessage(pattern=r"^\.animate\s+([\s\S]+)$", outgoing=True))
@rishabh()
async def animate_text(event):
    # Grab everything after ".animate "
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.reply("❗️ Usage: `.animate <text>`")

    # Send a visible placeholder so we can edit it
    msg = await event.reply("⏳")

    # Type out one char at a time
    for i in range(1, len(text) + 1):
        new = text[:i]
        try:
            await msg.edit(new)
        except MessageNotModifiedError:
            # Happens if new == old; just ignore and continue
            pass
        # small random delay for a “human” feel
        await asyncio.sleep(0.05 + random.random() * 0.1)

    # Pause on the full text for a moment
    await asyncio.sleep(0.5)

@CipherElite.on(events.NewMessage(pattern=r"^\.spinner(?:\s+(\d+))?$", outgoing=True))
@rishabh()
async def spinner(event):
    sec = event.pattern_match.group(1)
    total = int(sec) if sec and sec.isdigit() else 5
    frames = ["|", "/", "—", "\\"]
    msg = await event.reply("⏳ Starting spinner…")

    start = asyncio.get_event_loop().time()
    idx = 0
    while asyncio.get_event_loop().time() - start < total:
        frame = frames[idx % len(frames)]
        try:
            await msg.edit(f"{frame} spinning…")
        except MessageNotModifiedError:
            pass
        idx += 1
        await asyncio.sleep(0.2)

    await msg.edit("✅ Done!")
