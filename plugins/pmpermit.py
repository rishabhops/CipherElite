# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    pmpermit
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    â€¢ If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    â€¢ You MUST give proper credit to the CipherElite Userbot author:
#        â€“ GitHub:    https://github.com/rishabhops/CipherElite
#        â€“ Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================
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
DB_DIR       = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE      = DB_DIR / "assistant_db.json"


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
        cfg = self.data["config"]
        if not cfg.get("pmpermit_pic"):
            cfg["pmpermit_pic"] = DEFAULT_PMPERMIT_PIC
            self._save()

    def _load(self):
        try:
            if DB_FILE.exists():
                with DB_FILE.open("r", encoding="utf-8") as f:
                    on_disk = json.load(f)
                for k, v in on_disk.items():
                    self.data[k] = v
        except Exception as e:
            logging.error(f"Assistant load error: {e}")

    def _save(self):
        try:
            with DB_FILE.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Assistant save error: {e}")

    async def send_message(self, event, mtype, **kwargs):
        """
        Send a permitâ€flow message. This safely resolves the entity
        for typing actions and sending files to avoid 'could not find entity'.
        """
        # Prepare target entity (User or chat)
        try:
            target = await event.get_sender()
        except Exception:
            target = event.chat_id

        cfg = self.data["config"]
        texts = {
            "introduction": [
                f"ðŸ‘‹ Hi! I'm {cfg['assistant_name']}, {cfg['alive_name']}'s assistant.\n"
                "Please explain briefly why you want to contact them.\n"
                "Type 'ok' to acknowledge."
            ],
            "acknowledgment": [
                "ðŸ‘ Thanks for understanding!\n"
                f"I will notify {cfg['alive_name']}."
            ],
            "warning": [
                "âš ï¸ Warning {warn_count}/{max_warnings}\n"
                "Please wait for approval before messaging again."
            ],
            "approved": [
                "âœ… You are now approved! Feel free to continue."
            ],
            "disapproved": [
                "âŒ Your approval has been revoked."
            ],
            "blocked": [
                "ðŸš« You have been blocked due to repeated messages."
            ],
        }

        lst = texts.get(mtype, [])
        if not lst:
            return

        msg = random.choice(lst).format(**kwargs)

        # Show typing indicator (if possible)
        try:
            async with event.client.action(target, 'typing'):
                await asyncio.sleep(1.0)
        except Exception:
            pass

        # Send with picture on introduction if enabled
        if mtype == "introduction" and cfg.get("use_pic"):
            try:
                await event.client.send_file(
                    target,
                    cfg["pmpermit_pic"],
                    caption=msg
                )
            except Exception:
                await event.reply(msg)
        else:
            await event.reply(msg)

    async def handle_message(self, event):
        # only private chats
        if not event.is_private:
            return

        sender = await event.get_sender()
        uid = str(sender.id)

        # ignore bots and already-approved
        if sender.bot or uid in self.data["approved_users"]:
            return

        text = (event.message.text or "").lower()

        # 1) First-time user â†’ introduction
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

        # 2) Acknowledgment
        if self.data["user_states"].get(uid) == "introduced" and text in ("ok", "okay"):
            self.data["user_states"][uid] = "acknowledged"
            await self.send_message(event, "acknowledgment")
            self._save()
            return

        # 3) Warnings / blocking
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
        ".a / .approve        â€” Approve a user",
        ".da / .disapprove    â€” Revoke approval",
        ".block               â€” Block a user",
        ".listapproved        â€” List approved users",
        ".setpermitpic        â€” Set the permit picture",
        ".togglepermitpic     â€” Enable/disable the picture"
    ]
    add_handler("pmpermit", commands, "Personal Assistant PM Manager")

    @CipherElite.on(events.NewMessage(incoming=True))
    async def _incoming(event):
        await assistant.handle_message(event)

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.(?:a|approve)(?:$|\s)"))
    @rishabh()
    async def _approve(event):
        if event.is_private:
            uid = str(event.chat_id)
        else:
            reply = await event.get_reply_message()
            if not reply:
                return await event.reply("â†ªï¸ Reply to the user to approve.")
            uid = str(reply.sender_id)

        if uid not in assistant.data["approved_users"]:
            assistant.data["approved_users"].append(uid)
        assistant.data["warnings"].pop(uid, None)
        assistant._save()
        await assistant.send_message(event, "approved")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.(?:da|disapprove)(?:$|\s)"))
    @rishabh()
    async def _disapprove(event):
        if event.is_private:
            uid = str(event.chat_id)
        else:
            reply = await event.get_reply_message()
            if not reply:
                return await event.reply("â†ªï¸ Reply to the user to disapprove.")
            uid = str(reply.sender_id)

        assistant.data["approved_users"] = [
            u for u in assistant.data["approved_users"] if u != uid
        ]
        assistant.data["warnings"][uid] = 0
        assistant._save()
        await assistant.send_message(event, "disapproved")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.listapproved$"))
    @rishabh()
    async def _list(event):
        approved = assistant.data["approved_users"]
        if not approved:
            return await event.reply("No users are approved.")
        text = "**Approved Users:**\n"
        for uid in approved:
            info = assistant.data["users"].get(uid, {})
            name = info.get("name", "Unknown")
            text += f"â€¢ {name} (`{uid}`)\n"
        await event.reply(text)

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.setpermitpic(?:\s+.*)?$"))
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
                return await event.reply("âœ… Permit picture set from reply")
            return await event.reply("âŒ Reply to an image.")
        # from URL
        parts = event.text.split(None, 1)
        if len(parts) > 1:
            assistant.data["config"]["pmpermit_pic"] = parts[1].strip()
            assistant.data["config"]["use_pic"] = True
            assistant._save()
            return await event.reply("âœ… Permit picture set from URL")
        await event.reply("âŒ Usage: .setpermitpic <url> or reply to an image")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.togglepermitpic$"))
    @rishabh()
    async def _togglepic(event):
        cfg = assistant.data["config"]
        cfg["use_pic"] = not cfg.get("use_pic", True)
        assistant._save()
        state = "enabled" if cfg["use_pic"] else "disabled"
        await event.reply(f"âœ… Permit picture {state}")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.block(?:$|\s)"))
    @rishabh()
    async def _block(event):
        if event.is_private:
            uid = str(event.chat_id)
        else:
            reply = await event.get_reply_message()
            if not reply:
                return await event.reply("â†ªï¸ Reply to the user to block.")
            uid = str(reply.sender_id)

        assistant.data["approved_users"] = [
            u for u in assistant.data["approved_users"] if u != uid
        ]
        assistant.data["warnings"].pop(uid, None)
        assistant.data["user_states"].pop(uid, None)
        assistant._save()
        await event.client(functions.contacts.BlockRequest(int(uid)))
        await event.reply(f"ðŸš« User `{uid}` has been blocked.")

    return assistant
