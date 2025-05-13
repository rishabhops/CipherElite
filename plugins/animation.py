import asyncio
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client):
    commands = [
        ".animate <text>   — Simulate typing animation",
        ".spinner [sec]    — Show spinner animation"
    ]
    add_handler("animation", commands, "Text & Spinner Animation Plugin")

@CipherElite.on(events.NewMessage(pattern=r"\.animate\s+(.+)", outgoing=True))
@rishabh()
async def animate_text(event):
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.reply("❗️ Usage: `.animate <text>`")

    # send a harmless placeholder so we can edit it
    msg = await event.reply(".")

    # type out one char at a time
    for i in range(1, len(text) + 1):
        await asyncio.sleep(0.1)
        await msg.edit(text[:i])

    # optionally pause on the full text
    await asyncio.sleep(0.5)

@CipherElite.on(events.NewMessage(pattern=r"\.spinner(?:\s+(\d+))?", outgoing=True))
@rishabh()
async def spinner(event):
    sec = event.pattern_match.group(1)
    total = int(sec) if sec and sec.isdigit() else 5
    frames = ["|", "/", "—", "\\"]
    msg = await event.reply("⏳ Starting spinner…")
    start = asyncio.get_event_loop().time()
    idx = 0

    while asyncio.get_event_loop().time() - start < total:
        await asyncio.sleep(0.2)
        frame = frames[idx % len(frames)]
        await msg.edit(f"{frame} spinning…")
        idx += 1

    await msg.edit("✅ Done!")
