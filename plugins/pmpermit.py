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
                "gemini_api_key": None  # New field to store the key persistently
            },
            "users": {},
            "warnings": {},
            "approved_users": [],
            "user_states": {},
        }
        self.ai_sessions = {}
        self.model = None
        
        # 1. Load data from JSON first
        self._load()
        
        # 2. If no key in JSON, check environment variables as backup
        if not self.data["config"].get("gemini_api_key"):
            env_key = os.environ.get("GEMINI_API_KEY")
            if env_key:
                self.data["config"]["gemini_api_key"] = env_key
                self._save()

        # 3. Attempt to boot up the AI
        self._init_ai()

        # Ensure default pic exists
        cfg = self.data["config"]
        if not cfg.get("pmpermit_pic"):
            cfg["pmpermit_pic"] = DEFAULT_PMPERMIT_PIC
            self._save()

    def _init_ai(self):
        """Initializes the Gemini model if a valid key exists."""
        api_key = self.data["config"].get("gemini_api_key")
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
                'gemini-2.5-flash',
                system_instruction=system_instruction
            )
            return True
        except Exception as e:
            logging.error(f"Failed to initialize AI Gatekeeper: {e}")
            self.model = None
            return False

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
            async with event.client.action(target, 'typing'):
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

        sender = await event.get_sender()
        uid = str(sender.id)

        # Ignore bots, yourself, and approved users
        if sender.bot or sender.is_self or uid in self.data["approved_users"]:
            return

        text = (event.message.text or "").lower()

        # 1) First-time user setup
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "name": sender.first_name,
                "username": sender.username,
                "first_seen": datetime.now().isoformat()
            }
            self.data["user_states"][uid] = "introduced"
            self.data["warnings"][uid] = 0
            self._save()
            
            # If no AI, send the standard intro immediately
            if not self.model:
                await self.send_message(event, "introduction")
                return

        # 2) Warnings / Blocking mechanism (Applies to both AI and Non-AI)
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
                async with event.client.action(event.chat_id, 'typing'):
                    response = await self.ai_sessions[uid].send_message_async(event.message.text)
                await event.reply(response.text)
            except Exception as e:
                logging.error(f"AI Error: {e}")
                await event.reply("⏳ Processing... please wait for manual approval.")
        else:
            # --- STANDARD NON-AI FLOW ---
            if self.data["user_states"].get(uid) == "introduced" and text in ("ok", "okay"):
                self.data["user_states"][uid] = "acknowledged"
                await self.send_message(event, "acknowledgment")
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
        ".a / .approve        — Approve a user",
        ".da / .disapprove    — Revoke approval",
        ".block               — Block a user",
        ".setai <key>         — Set/Update Gemini API Key",
        ".rmai                — Remove AI Key and revert to standard bot",
        ".listapproved        — List approved users",
    ]
    add_handler("pmpermit", commands, "Personal Assistant PM Manager")

    @CipherElite.on(events.NewMessage(incoming=True))
    async def _incoming(event):
        await assistant.handle_message(event)

    # ... [KEEP YOUR EXISTING .approve, .disapprove, .listapproved, .setpermitpic, .togglepermitpic, .block COMMANDS HERE] ...

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.setai(?:\s+(.+))?$"))
    @rishabh()
    async def _setai(event):
        key = event.pattern_match.group(1)
        if not key:
            return await event.reply("❌ Usage: `.setai <your_gemini_api_key>`")
        
        # Save to DB
        assistant.data["config"]["gemini_api_key"] = key.strip()
        assistant._save()
        
        # Reinitialize live
        success = assistant._init_ai()
        if success:
            await event.reply("✅ Gemini API Key saved! AI Gatekeeper is now **ACTIVE**.")
        else:
            await event.reply("⚠️ Key saved, but AI failed to initialize. Please check the key.")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.rmai$"))
    @rishabh()
    async def _rmai(event):
        assistant.data["config"]["gemini_api_key"] = None
        assistant.model = None
        assistant.ai_sessions.clear()
        assistant._save()
        await event.reply("🛑 AI Gatekeeper disabled. Reverted to standard text bot.")

    return assistant
