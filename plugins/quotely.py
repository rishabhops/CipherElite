# plugins/quotely.py
"""
🎭 Quotely – turn any replied text message into a stylish sticker.

Commands
────────
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
# 1. Init – register in .help
# ──────────────────────────────────────────────────────────────
def init(_):
    cmds = [
        ".q <reply> - Quote a message",
        ".q r <reply> - Quote a message and its reply",
    ]
    add_handler("quotely", cmds, "🎭 Quotely – quote-sticker generator")


# ──────────────────────────────────────────────────────────────
# 2. Helpers
# ──────────────────────────────────────────────────────────────
def _entities_to_api(msg):
    """Telethon entities → API list."""
    out = []
    if msg.entities:
        for ent in msg.entities:
            out.append(
                {
                    "type": ent.__class__.__name__.lower(),  # bold, mention, url …
                    "offset": ent.offset,
                    "length": ent.length,
                }
            )
    return out


def _generate_quote(payload):
    """Call remote API, write WEBP to disk, return path."""
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
    path = f"Quote_{int(time.time())}.webp"
    with open(path, "wb") as f:
        f.write(base64.b64decode(img_b64))
    return path


# ──────────────────────────────────────────────────────────────
# 3. Command handler
# ──────────────────────────────────────────────────────────────
async def register_commands():
    # Captures optional "r" after .q or .ss
    pattern = r"\.(?:q|ss)(?:\s+(r))?"

    @CipherElite.on(events.NewMessage(pattern=pattern))
    @rishabh()
    async def quotely(event):
        # Must be a reply
        if not event.is_reply:
            return await event.reply(
                "🎭 **Cipher Elite Error**\n\n❌ Reply to a message to quote it."
            )

        reply = await event.get_reply_message()

        # Telethon: text contains caption if present
        if reply.media and not reply.text:
            return await event.reply(
                "🎭 **Cipher Elite Error**\n\n❌ Reply to a *text* message or media with caption."
            )

        want_nested = bool(event.pattern_match.group(1))
        status = await event.reply("🔄 **Generating quote…**")

        # Nested reply (the message *your* replied message was replying to)
        nested_block = {}
        if want_nested and reply.reply_to_msg_id:
            prev = await event.client.get_messages(event.chat_id, reply.reply_to_msg_id)
            if prev and prev.text:
                prev_name = " ".join(
                    filter(None, [prev.sender.first_name, prev.sender.last_name])
                )
                nested_block = {
                    "chatId": prev.sender_id,
                    "entities": _entities_to_api(prev),
                    "name": prev_name,
                    "text": prev.text,
                }

        # Main message block
        sender_name = " ".join(
            filter(None, [reply.sender.first_name, reply.sender.last_name])
        )
        emoji_status = None
        if getattr(reply.sender, "emoji_status", None):
            emoji_status = str(reply.sender.emoji_status.custom_emoji_id)

        payload = [
            {
                "entities": _entities_to_api(reply),
                "avatar": True,
                "from": {
                    "id": reply.sender_id,
                    "name": sender_name,
                    "emoji_status": emoji_status,
                },
                "text": reply.text,
                "replyMessage": nested_block,
            }
        ]

        # Call API
        try:
            webp_path = _generate_quote(payload)
        except Exception as e:
            await status.edit(f"🎭 **Cipher Elite Error**\n\n❌ `{e}`")
            return

        # Send sticker & clean up
        await event.reply(file=webp_path)
        await status.delete()
        os.remove(webp_path)
