import os
import asyncio

from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

import youtube_dl

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Ensure downloads folder exists
os.makedirs("./downloads", exist_ok=True)

# Initialize PyTgCalls with your Telethon client
pytgcalls = PyTgCalls(CipherElite)
pytgcalls.start()

def init(client):
    commands = [
        ".play <query>   — Search & play a YouTube audio in VC",
        ".stop           — Stop playback and leave VC"
    ]
    add_handler("vc_music", commands, "Voice Chat Music Plugin")

async def edit_or_reply(event, text):
    try:
        return await event.edit(text)
    except MessageNotModifiedError:
        return await event.reply(text)

@CipherElite.on(events.NewMessage(pattern=r"^\.play (.+)$", outgoing=True))
@rishabh()
async def play(event):
    """Search YouTube, download best audio, and play it in group VC."""
    query = event.pattern_match.group(1).strip()
    chat_id = event.chat_id
    status = await edit_or_reply(event, f"🔎 Searching for `{query}`...")
    # yt-dl options
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True
    }
    # Search & download
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        title = info["title"]
        url = info["webpage_url"]
        filepath = ydl.prepare_filename(info)
        ydl.download([url])
    await status.edit(f"▶️ Now playing: **{title}**")
    # Join VC (or switch stream) and play audio
    await pytgcalls.join_group_call(
        chat_id,
        AudioPiped(filepath, bitrate=48000)
    )

@CipherElite.on(events.NewMessage(pattern=r"^\.stop$", outgoing=True))
@rishabh()
async def stop(event):
    """Stop playback and leave the group VC."""
    chat_id = event.chat_id
    await edit_or_reply(event, "⏹️ Stopping playback and leaving VC...")
    await pytgcalls.leave_group_call(chat_id)
