# plugins/quotely.py
"""
🎭 Quotely – turn any replied text message into a stylish sticker.
Usage:
  .q    <reply>          ➜ Quote the message you replied to
  .q r <reply>           ➜ Quote it *plus* the message it was replying to
Aliases: .ss and .ss r
"""

import os
import time
import base64
import requests
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

API_URL = "https://bot.lyo.su/quote/generate"


# ──────────────────────────────────────────────────────────────
# ➊ Init: register in .help
# ──────────────────────────────────────────────────────────────
def init(_):
    cmds = [
        ".q <reply> - Quote a message",
        ".q r <reply> - Quote a message and its reply",
    ]
    add_handler("quotely", cmds, "🎭 Quotely – quote-sticker generator")


# ──────────────────────────────────────────────────────────────
# ➋ Helper functions
# ──────────────────────────────────────────────────────────────
def _pyrogram_entities_to_api_entities(msg):
    """Convert Pyrogram entities → API-compatible list."""
    out = []
    if msg.entities:
        for ent in msg.entities:
            out.append(
                {
                    "type": ent.type.name.lower(),
                    "offset": ent.offset,
                    "length": ent.length,
                }
            )
    return out


def _generate_quote(payload):
    """Call remote API, write WEBP, return filename or raise."""
    body = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#260746/#6100c2",
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": payload,
    }
    r = requests.post(API_URL, json=body).json()
    img_b64 = r["result"]["image"]
    filename = f"Quote_{int(time.time())}.webp"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(img_b64))
    return filename


# ──────────────────────────────────────────────────────────────
# ➌ Command handler
# ──────────────────────────────────────────────────────────────
async def register_commands():
    pattern = r"\.(?:q|ss)(?:\s+(r))?"          # captures optional "r"
    help_err = "Reply to a *text* message to quote it."

    @CipherElite.on(events.NewMessage(pattern=pattern))
    @rishabh()
    async def quotely(event):
        if not event.is_reply:
            return await event.reply(f"🎭 **Cipher Elite Error**\n\n❌ {help_err}")

        reply = await event.get_reply_message()

        # Ensure we have text
        if not (reply.text or reply.caption):
            return await event.reply(f"🎭 **Cipher Elite Error**\n\n❌ {help_err}")

        # If media + caption, treat caption as text
        if reply.caption and not reply.text:
            reply.text = reply.caption

        want_reply_of_reply = bool(event.pattern_match.group(1))
        await_msg = await event.reply("🔄 **Generating quote…**")

        # Build optional reply-of-reply block
        reply_msg_block = {}
        if want_reply_of_reply and reply.reply_to_msg_id:
            prev = await event.client.get_messages(event.chat_id, reply.reply_to_msg_id)
            if prev and prev.text:
                prev_name = " ".join(
                    filter(None, [prev.sender.first_name, prev.sender.last_name])
                )
                reply_msg_block = {
                    "chatId": prev.sender_id,
                    "entities": _pyrogram_entities_to_api_entities(prev),
                    "name": prev_name,
                    "text": prev.text,
                }

        # Primary message block
        sender_name = " ".join(filter(None, [reply.sender.first_name, reply.sender.last_name]))
        emoji_status = None
        if getattr(reply.sender, "emoji_status", None):
            emoji_status = str(reply.sender.emoji_status.custom_emoji_id)

        payload = [
            {
                "entities": _pyrogram_entities_to_api_entities(reply),
                "avatar": True,
                "from": {
                    "id": reply.sender_id,
                    "name": sender_name,
                    "emoji_status": emoji_status,
                },
                "text": reply.text,
                "replyMessage": reply_msg_block,
            }
        ]

        # Generate sticker
        try:
            webp_path = _generate_quote(payload)
        except Exception as e:
            await await_msg.edit(f"🎭 **Cipher Elite Error**\n\n❌ `{e}`")
            return

        # Send & clean-up
        await event.reply(file=webp_path)
        await await_msg.delete()
        os.remove(webp_path)
