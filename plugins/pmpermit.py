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
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @rishabhops
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
from openai import AsyncOpenAI, OpenAIError, AuthenticationError, RateLimitError
from telethon import events, functions
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from config.config import Config
from vars import ELITE_BOT_USERNAME

# Default PM permit picture
DEFAULT_PMPERMIT_PIC = Config.DEFAULT_PMPERMIT_PIC

# DB setup
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "assistant_db.json"

# AI Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", getattr(Config, "NVIDIA_API_KEY", ""))
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "mistralai/mistral-nemotron"

# Initialize OpenAI client
if not NVIDIA_API_KEY:
    logging.warning("NVIDIA_API_KEY not set. AI features will use static messages.")
client = AsyncOpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY or "dummy_key"  # Fallback to avoid client initialization errors
)

# AI System Prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Cipher AI, the personal assistant for the CipherElite Userbot, created by @rishabhops. Respond in private chats to manage PM permissions, acting as a polite gatekeeper. Generate short, natural, and context-aware messages tailored to the sender’s input and profile (e.g., name, username). Avoid <think> blocks, technical details, or markdown. Maintain a professional yet friendly tone, and request acknowledgment (e.g., 'Type ok to proceed')."
}

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

    async def generate_ai_message(self, mtype, sender, user_message=None, **kwargs):
        """Generate AI-driven message using Cipher AI"""
        if not NVIDIA_API_KEY:
            return None

        cfg = self.data["config"]
        context = {
            "assistant_name": cfg["assistant_name"],
            "alive_name": cfg["alive_name"],
            "sender_name": sender.first_name or "Unknown",
            "sender_username": sender.username or "None",
            "max_warnings": cfg["max_warnings"],
            "warn_count": kwargs.get("warn_count", 0),
        }

        if mtype == "introduction":
            prompt = f"Generate a polite introduction message for {context['sender_name']} (@{context['sender_username']}) contacting {context['alive_name']}. Ask why they’re messaging and request 'ok' to proceed. Keep it short and friendly."
            if user_message:
                prompt += f" Their message: '{user_message}'."
        elif mtype == "acknowledgment":
            prompt = f"Generate a brief acknowledgment message thanking {context['sender_name']} (@{context['sender_username']}) for responding. Notify them that {context['alive_name']} will be informed."
        elif mtype == "warning":
            prompt = f"Generate a warning message for {context['sender_name']} (@{context['sender_username']}), warning {context['warn_count']}/{context['max_warnings']}. Politely ask them to wait for approval."
        else:
            return None

        try:
            stream = await client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    SYSTEM_PROMPT,
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                top_p=0.7,
                max_tokens=512,
                stream=True
            )
            response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            return response
        except Exception as e:
            logging.error(f"AI message generation error: {e}")
            return None

    async def send_message(self, event, mtype, **kwargs):
        """Send a permit-flow message with AI or static fallback"""
        try:
            target = await event.get_sender()
        except Exception:
            target = event.chat_id

        cfg = self.data["config"]
        static_texts = {
            "introduction": [
                f"👋 Hi! I'm {cfg['assistant_name']}, {cfg['alive_name']}'s assistant.\n"
                "Please explain briefly why you want to contact them.\n"
                "Type 'ok' to acknowledge."
            ],
            "acknowledgment": [
                "👍 Thanks for understanding!\n"
                f"I will notify {cfg['alive_name']}."
            ],
            "warning": [
                "⚠️ Warning {warn_count}/{max_warnings}\n"
                "Please wait for approval before messaging again."
            ],
            "approved": [
                "✅ You are now approved! Feel free to continue."
            ],
            "disapproved": [
                "❌ Your approval has been revoked."
            ],
            "blocked": [
                "🚫 You have been blocked due to repeated messages."
            ],
        }

        sender = await event.get_sender()
        user_message = event.message.text or ""
        ai_msg = await self.generate_ai_message(mtype, sender, user_message, **kwargs)

        msg = ai_msg if ai_msg else random.choice(static_texts.get(mtype, [""])).format(**kwargs)

        try:
            async with event.client.action(target, 'typing'):
                await asyncio.sleep(1.0)
        except Exception:
            pass

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
        if not event.is_private:
            return

        sender = await event.get_sender()
        uid = str(sender.id)

        if sender.bot or uid in self.data["approved_users"]:
            return

        text = (event.message.text or "").lower()

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

        if self.data["user_states"].get(uid) == "introduced" and text in ("ok", "okay"):
            self.data["user_states"][uid] = "acknowledged"
            await self.send_message(event, "acknowledgment")
            self._save()
            return

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
        f".a / .approve — Approve a user",
        f".da / .disapprove — Revoke approval",
        f".block — Block a user",
        f".listapproved — List approved users",
        f".setpermitpic — Set the permit picture",
        f".togglepermitpic — Enable/disable the picture"
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
                return await event.reply("↪️ Reply to the user to approve.")
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
                return await event.reply("↪️ Reply to the user to disapprove.")
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
            text += f"• {name} (`{uid}`)\n"
        await event.reply(text)

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.setpermitpic(?:\s+.*)?$"))
    @rishabh()
    async def _setpic(event):
        if event.reply_to_msg_id:
            msg = await event.get_reply_message()
            if msg.media:
                path = await CipherElite.download_media(msg)
                assistant.data["config"]["pmpermit_pic"] = path
                assistant.data["config"]["use_pic"] = True
                assistant._save()
                return await event.reply("✅ Permit picture set from reply")
            return await event.reply("❌ Reply to an image.")
        parts = event.text.split(None, 1)
        if len(parts) > 1:
            assistant.data["config"]["pmpermit_pic"] = parts[1].strip()
            assistant.data["config"]["use_pic"] = True
            assistant._save()
            return await event.reply("✅ Permit picture set from URL")
        await event.reply("❌ Usage: .setpermitpic <url> or reply to an image")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.togglepermitpic$"))
    @rishabh()
    async def _togglepic(event):
        cfg = assistant.data["config"]
        cfg["use_pic"] = not cfg.get("use_pic", True)
        assistant._save()
        state = "enabled" if cfg["use_pic"] else "disabled"
        await event.reply(f"✅ Permit picture {state}")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.block(?:$|\s)"))
    @rishabh()
    async def _block(event):
        if event.is_private:
            uid = str(event.chat_id)
        else:
            reply = await event.get_reply_message()
            if not reply:
                return await event.reply("↪️ Reply to the user to block.")
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

print("✅ PM Permit Plugin loaded successfully")
