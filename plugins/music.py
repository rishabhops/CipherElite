import os
import uuid
import subprocess
from telethon import events

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# ensure download folder
os.makedirs("downloads", exist_ok=True)

def init(client):
    commands = [
        ".play <query>  — Download & send as voice note (no live VC stream)",
    ]
    add_handler("voice_play", commands, "YouTube-to-VoiceNote Plugin")

async def edit_or_reply(event, text):
    try:
        return await event.edit(text)
    except:
        return await event.reply(text)

@CipherElite.on(events.NewMessage(pattern=r"^\.play (.+)$", outgoing=True))
@rishabh()
async def play_voice_note(event):
    query = event.pattern_match.group(1).strip()
    msg = await edit_or_reply(event, f"🔎 Searching for `{query}`…")
    # download audio
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
    }
    with __import__('youtube_dl').YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
        downloaded_path = ydl.prepare_filename(info)
    # convert to opus voice note
    note_path = f"downloads/{uuid.uuid4().hex}.ogg"
    cmd = [
        "ffmpeg", "-y",
        "-i", downloaded_path,
        "-c:a", "libopus",
        "-b:a", "64k",
        "-vbr", "off",
        note_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # send voice note
    await event.client.send_file(
        event.chat_id,
        note_path,
        voice_note=True,
        reply_to=event.message.id
    )
    # cleanup & finish
    await msg.edit(f"▶️ Sent voice note for **{info['title']}**")
    try:
        os.remove(downloaded_path)
        os.remove(note_path)
    except:
        pass
