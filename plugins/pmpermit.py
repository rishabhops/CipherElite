import os
import json
import random
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from telethon import events, functions
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from config.config import Config
# Default PM permit picture
DEFAULT_PMPERMIT_PIC = Config.DEFAULT_PMPERMIT_PIC

# DB setup
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "assistant_db.json"


class PersonalAssistant:
    def __init__(self):
        self.data = {
            "config": {
                "alive_name": os.environ.get("ALIVE_NAME", "Master"),
                "assistant_name": os.environ.get("ASSISTANT_NAME", "CipherAI"),
                "pmpermit_pic": os.environ.get("PMPERMIT_PIC", DEFAULT_PMPERMIT_PIC),
                "use_pic": True,
                "max_warnings": int(os.environ.get("MAX_WARNINGS", 5)),
            },
            "users": {},
            "warnings": {},
            "approved_users": [],
            "user_states": {},
        }
        self._load()
        # Ensure we always have a default pic
        cfg = self.data["config"]
        if not cfg.get("pmpermit_pic"):
            cfg["pmpermit_pic"] = DEFAULT_PMPERMIT_PIC
            self._save()

    def _load(self):
        try:
            if DB_FILE.exists():
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    on_disk = json.load(f)
                for k, v in on_disk.items():
                    self.data[k] = v
        except Exception as e:
            logging.error(f"Assistant load error: {e}")

    def _save(self):
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Assistant save error: {e}")

    async def send_message(self, event, mtype, **kwargs):
        cfg = self.data["config"]
        texts = {
            "introduction": [
                f"👋 Hello! I'm {cfg['assistant_name']}, {cfg['alive_name']}'s personal assistant.\n\n"
                f"Please briefly explain why you want to contact {cfg['alive_name']}.\n"
                "Wait for approval before sending multiple messages.\n"
                "Type 'ok' or 'okay' to acknowledge."
            ],
            "acknowledgment": [
                "Thank you for understanding! 🙂\n"
                f"I'll notify {cfg['alive_name']} about your message.\n"
                "Please wait patiently for approval."
            ],
            "warning": [
                "⚠️ **Warning {warn_count}/{max_warnings}**\n\n"
                "Please avoid sending multiple messages.\n"
                f"Wait for {cfg['alive_name']}'s approval.\n"
                "Further messages will increase your warning count."
            ],
            "approved": [
                f"✅ Welcome! You're now approved to message {cfg['alive_name']}.\n"
                "Feel free to continue your conversation."
            ],
            "disapproved": [
                "❌ Your approval has been revoked.\n"
                "You'll need to wait for approval again before sending messages."
            ],
            "blocked": [
                "🚫 You have been blocked due to multiple unauthorized messages."
            ],
        }
        lst = texts.get(mtype, [])
        if not lst:
            return
        msg = random.choice(lst).format(**kwargs)
        # typing action
        async with event.client.action(event.chat_id, 'typing'):
            await asyncio.sleep(1.2)

        # send with pic if intro and enabled
        if mtype == "introduction" and cfg.get("use_pic"):
            await event.client.send_file(
                event.chat_id,
                cfg["pmpermit_pic"],
                caption=msg
            )
        else:
            await event.reply(msg)

    async def handle_message(self, event):
        if not event.is_private:
            return
        sender = await event.get_sender()
        uid = str(sender.id)
        if sender.bot or uid in self.data["approved_users"]:
            return
        text = (event.message.text or "").lower()
        # new user
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "name": sender.first_name,
                "username": sender.username,
                "first_seen": datetime.now().isoformat()
            }
            self.data["user_states"][uid] = "introduced"
            self.data["warnings"][uid] = 0
            await self.send_message(event, "introduction")
            self._save()
            return
        # acknowledgment
        if self.data["user_states"].get(uid) == "introduced" and text in ("ok", "okay", "yes", "sure"):
            self.data["user_states"][uid] = "acknowledged"
            await self.send_message(event, "acknowledgment")
            self._save()
            return
        # warnings
        self.data["warnings"].setdefault(uid, 0)
        self.data["warnings"][uid] += 1
        if self.data["warnings"][uid] >= self.data["config"]["max_warnings"]:
            await self.send_message(event, "blocked")
            await event.client(functions.contacts.BlockRequest(int(uid)))
            self._save()
            return
        await self.send_message(
            event,
            "warning",
            warn_count=self.data["warnings"][uid],
            max_warnings=self.data["config"]["max_warnings"]
        )
        self._save()


def init(client):
    assistant = PersonalAssistant()
    commands = [
        ".a - Approve a user for PM",
        ".da - Disapprove a user from PM",
        ".block - Block a user",
        ".listapproved - List approved users",
        ".setpermitpic <url/reply> - Set the PM permit picture",
        ".togglepermitpic - Enable/disable the PM permit picture"
    ]
    add_handler("pmpermit", commands, "Personal Assistant PM Manager")

    @CipherElite.on(events.NewMessage(incoming=True))
    async def _incoming(event):
        await assistant.handle_message(event)

    @CipherElite.on(events.NewMessage(pattern=r"\.(a|approve)(?:$|\s)", incoming=True))
    @rishabh()
    async def _approve(event):
        if event.is_private:
            uid = str(event.chat_id)
        else:
            reply = await event.get_reply_message()
            if not reply:
                return await event.reply("↪️ Reply to a user to approve them.")
            uid = str(reply.sender_id)
        if uid not in assistant.data["approved_users"]:
            assistant.data["approved_users"].append(uid)
        assistant.data["warnings"].pop(uid, None)
        assistant._save()
        await assistant.send_message(event, "approved")

    @CipherElite.on(events.NewMessage(pattern=r"\.(da|disapprove)(?:$|\s)", incoming=True))
    @rishabh()
    async def _disapprove(event):
        if event.is_private:
            uid = str(event.chat_id)
        else:
            reply = await event.get_reply_message()
            if not reply:
                return await event.reply("↪️ Reply to a user to disapprove them.")
            uid = str(reply.sender_id)
        assistant.data["approved_users"] = [u for u in assistant.data["approved_users"] if u != uid]
        assistant.data["warnings"][uid] = 0
        assistant._save()
        await assistant.send_message(event, "disapproved")

    @CipherElite.on(events.NewMessage(pattern=r"\.listapproved$", incoming=True))
    @rishabh()
    async def _list(event):
        approved = assistant.data["approved_users"]
        if not approved:
            return await event.reply("No users are currently approved.")
        text = "**Approved Users:**\n\n"
        for uid in approved:
            info = assistant.data["users"].get(uid, {})
            name = info.get("name", "Unknown")
            text += f"• {name} (`{uid}`)\n"
        await event.reply(text)

    @CipherElite.on(events.NewMessage(pattern=r"\.setpermitpic$", incoming=True))
    @rishabh()
    async def _setpic(event):
        # from reply
        if event.reply_to_msg_id:
            msg = await event.get_reply_message()
            if msg.media:
                path = await CipherElite.download_media(msg)
                assistant.data["config"]["pmpermit_pic"] = path
                assistant.data["config"]["use_pic"] = True
                assistant._save()
                return await event.reply("✅ Permit picture set from reply")
            return await event.reply("❌ Reply to an image.")
        # from URL
        parts = event.text.split(None, 1)
        if len(parts) > 1:
            assistant.data["config"]["pmpermit_pic"] = parts[1]
            assistant.data["config"]["use_pic"] = True
            assistant._save()
            return await event.reply("✅ Permit picture set from URL")
        await event.reply("❌ Usage: .setpermitpic <url> or reply to an image")

    @CipherElite.on(events.NewMessage(pattern=r"\.togglepermitpic$", incoming=True))
    @rishabh()
    async def _togglepic(event):
        cfg = assistant.data["config"]
        cfg["use_pic"] = not cfg.get("use_pic", True)
        assistant._save()
        state = "enabled" if cfg["use_pic"] else "disabled"
        await event.reply(f"✅ Permit picture {state}")

    @CipherElite.on(events.NewMessage(pattern=r"\.(block)(?:$|\s)", incoming=True))
    @rishabh()
    async def _block(event):
        if event.is_private:
            uid = str(event.chat_id)
        else:
            reply = await event.get_reply_message()
            if not reply:
                return await event.reply("↪️ Reply to a user to block them.")
            uid = str(reply.sender_id)
        assistant.data["approved_users"] = [
            u for u in assistant.data["approved_users"] if u != uid
        ]
        assistant.data["warnings"].pop(uid, None)
        assistant.data["user_states"].pop(uid, None)
        assistant._save()
        await event.client(functions.contacts.BlockRequest(int(uid)))
        await event.reply(f"🚫 User `{uid}` has been blocked.")

    return assistant
