# =============================================================================
#  CipherElite Userbot Plugin - Personal Assistant PM Manager
#
#  Plugin Name:    pmpermit
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
# =============================================================================

import os
import json
import random
import asyncio
import logging
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
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
    def __init__(self, ai_config):
        self.ai_config = ai_config  # Reference to centralized config
        self.data = {
            "config": {
                "alive_name": os.environ.get("ALIVE_NAME", "Rishabh"),
                "assistant_name": os.environ.get("ASSISTANT_NAME", "CipherAI"),
                "pmpermit_pic": os.environ.get("PMPERMIT_PIC", DEFAULT_PMPERMIT_PIC),
                "use_pic": True,
                "max_warnings": int(os.environ.get("MAX_WARNINGS", 5)),
                "pmpermit_enabled": True,  # global switch (default ON)
            },
            "users": {},
            "warnings": {},
            "approved_users": [],
            "user_states": {},
        }
        self.ai_sessions = {}
        self.model = None

        # 1. Load and safely validate data from JSON
        self._load()

        # 2. Attempt to boot up the AI
        self._init_ai()

        # Ensure default pic exists
        cfg = self.data["config"]
        if not cfg.get("pmpermit_pic"):
            cfg["pmpermit_pic"] = DEFAULT_PMPERMIT_PIC
            self._save()

    def _init_ai(self):
        """Initializes the Gemini model using centralized config."""
        api_key = self.ai_config.get_api_key()  # Get from centralized config
        if not api_key:
            self.model = None
            return False

        try:
            genai.configure(api_key=api_key)
            system_instruction = (
                f"You are an AI gatekeeper named {self.data['config']['assistant_name']} "
                f"managing the Telegram inbox for {self.data['config']['alive_name']}. "
                "Ask the user politely why they are reaching out. "
                "If they provide a valid reason, tell them you will notify the owner. "
                "Keep responses strictly under 40 words."
            )
            self.model = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=system_instruction,
            )
            return True
        except Exception as e:
            logging.error(f"Failed to initialize AI Gatekeeper: {e}")
            self.model = None
            return False

    def _load(self):
        """Loads DB and strictly enforces data types to prevent crashes."""
        try:
            if DB_FILE.exists():
                with DB_FILE.open("r", encoding="utf-8") as f:
                    on_disk = json.load(f)
                for k, v in on_disk.items():
                    # Force these to ALWAYS be dictionaries
                    if k in ["users", "warnings", "user_states"]:
                        self.data[k] = v if isinstance(v, dict) else {}
                    # Force approved users to ALWAYS be a list
                    elif k == "approved_users":
                        self.data[k] = v if isinstance(v, list) else []
                    # Safely update config without overwriting
                    elif k == "config" and isinstance(v, dict):
                        self.data["config"].update(v)
                    else:
                        self.data[k] = v
        except Exception as e:
            logging.error(f"Assistant load error: {e}")

    def _save(self):
        try:
            with DB_FILE.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Assistant save error: {e}")

    async def _log_pm(self, event, sender, message_text: str):
        """Send a log of the user's message to LOG_CHAT_ID."""
        log_chat = getattr(Config, "LOG_CHAT_ID", None)
        if not log_chat:
            return
        try:
            mention = f"[{sender.first_name or 'User'}](tg://user?id={sender.id})"
            text = (
                f"**Incoming PM**\n"
                f"From: {mention} (`{sender.id}`)\n"
                f"Username: @{sender.username or 'N/A'}\n"
                f"Message:\n{message_text or '_empty_'}"
            )
            await event.client.send_message(log_chat, text, link_preview=False)
        except Exception as e:
            logging.error(f"Failed to log PM: {e}")

    async def send_message(self, event, mtype, **kwargs):
        """Fallback non-AI messaging system."""
        try:
            target = await event.get_sender()
        except Exception:
            target = event.chat_id

        cfg = self.data["config"]
        texts = {
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
            "approved": ["✅ You are now approved! Feel free to continue."],
            "disapproved": ["❌ Your approval has been revoked."],
            "blocked": ["🚫 You have been blocked due to repeated messages."],
        }

        lst = texts.get(mtype, [])
        if not lst:
            return

        msg = random.choice(lst).format(**kwargs)

        try:
            async with event.client.action(target, "typing"):
                await asyncio.sleep(1.0)
        except Exception:
            pass

        if mtype == "introduction" and cfg.get("use_pic"):
            try:
                await event.client.send_file(target, cfg["pmpermit_pic"], caption=msg)
            except Exception:
                await event.reply(msg)
        else:
            await event.reply(msg)

    async def handle_message(self, event):
        if not event.is_private:
            return

        # NEW: bypass everything if pmpermit is disabled
        if not self.data["config"].get("pmpermit_enabled", True):
            return

        sender = await event.get_sender()
        uid = str(sender.id)

        # Ignore bots, yourself, and approved users
        if sender.bot or sender.is_self or uid in self.data["approved_users"]:
            return

        text = (event.message.text or "").strip()

        # Log every incoming PM from non-approved users
        await self._log_pm(event, sender, text)

        # 1) First-time user setup
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "name": sender.first_name,
                "username": sender.username,
                "first_seen": datetime.now().isoformat(),
            }
            self.data["user_states"][uid] = "introduced"

            # Ensure the warnings dict has this user initialized
            if uid not in self.data["warnings"]:
                self.data["warnings"][uid] = 0

            self._save()

            # If no AI, send the standard intro immediately
            if not self.model:
                await self.send_message(event, "introduction")
                return

        # 2) Warnings / Blocking mechanism
        self.data["warnings"].setdefault(uid, 0)
        self.data["warnings"][uid] += 1

        if self.data["warnings"][uid] >= self.data["config"]["max_warnings"]:
            await self.send_message(event, "blocked")
            await event.client(functions.contacts.BlockRequest(int(uid)))
            self._save()
            return

        # 3) Route based on AI availability
        if self.model:
            # --- AI GATEKEEPER FLOW ---
            if uid not in self.ai_sessions:
                self.ai_sessions[uid] = self.model.start_chat(history=[])
            try:
                async with event.client.action(event.chat_id, "typing"):
                    response = await self.ai_sessions[uid].send_message_async(text)
                await event.reply(response.text)
            except Exception as e:
                logging.error(f"AI Error: {e}")
                await event.reply("⏳ Processing... please wait for manual approval.")
        else:
            # --- STANDARD NON-AI FLOW ---
            lowered = text.lower()
            if self.data["user_states"].get(uid) == "introduced" and lowered in ("ok", "okay"):
                self.data["user_states"][uid] = "acknowledged"
                await self.send_message(event, "acknowledgment")
                self._save()
                return

            await self.send_message(
                event,
                "warning",
                warn_count=self.data["warnings"][uid],
                max_warnings=self.data["config"]["max_warnings"],
            )
            self._save()


def init(client):
    try:
        from plugins.ai_setup import ai_config  # Import centralized config
    except ImportError:
        print("❌ ERROR: ai_setup.py not found! Please create it first.")
        return False

        # Note: with no ai_setup.py, you can still stub ai_config.get_api_key to return None

    assistant = PersonalAssistant(ai_config)  # Pass config to assistant
    commands = [
        ".a / .approve        — Approve a user",
        ".da / .disapprove    — Revoke approval",
        ".block               — Block a user",
        ".listapproved        — List approved users",
        ".setpermitpic        — Set the permit picture",
        ".togglepermitpic     — Enable/disable the picture",
        ".pmpermit on|off     — Enable/disable PM permit globally",
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

        assistant.data["approved_users"] = [u for u in assistant.data["approved_users"] if u != uid]
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

    @CipherElite.on1)
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

    # Global pmpermit toggle
    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.pmpermit(?:$|\s)(on|off)?"))
    @rishabh()
    async def _toggle_pmpermit(event):
        arg = (event.pattern_match.group(1) or "").lower()
        cfg = assistant.data["config"]

        if arg in ("on", "off"):
            cfg["pmpermit_enabled"] = arg == "on"
            assistant._save()
            state = "enabled ✅" if cfg["pmpermit_enabled"] else "disabled 🚫"
            return await event.reply(f"PM permit is now {state}")

        state = "ON ✅" if cfg.get("pmpermit_enabled", True) else "OFF 🚫"
        await event.reply(f"PM permit is currently {state}\nUsage: `.pmpermit on` or `.pmpermit off`")

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

        assistant.data["approved_users"] = [u for u in assistant.data["approved_users"] if u != uid]
        assistant.data["warnings"].pop(uid, None)
        assistant.data["user_states"].pop(uid, None)
        assistant._save()
        await event.client(functions.contacts.BlockRequest(int(uid)))
        await event.reply(f"🚫 User `{uid}` has been blocked.")

    print(
        f"✅ PM Permit Plugin initialized (pmpermit_enabled={assistant.data['config'].get('pmpermit_enabled', True)})"
    )
    return assistant
