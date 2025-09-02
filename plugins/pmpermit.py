# =============================================================================
#  CipherElite Userbot Plugin - PM Permit (Fixed Version)
# =============================================================================

import os
import json
import random
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from telethon import events, functions
from telethon.errors import UserAlreadyParticipantError, ChatAdminRequiredError

# Configuration
CIPHER_ELITE_OWNER_ID = 5470956337
DEFAULT_PMPERMIT_PIC = "https://graph.org/file/4d8c8b8b8b8b8b8b8b8b8.jpg"  # Add your default pic URL

# Database setup
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "pmpermit_db.json"

class PersonalAssistant:
    def __init__(self):
        self.data = {
            "config": {
                "alive_name": os.environ.get("ALIVE_NAME", "Master"),
                "assistant_name": os.environ.get("ASSISTANT_NAME", "CipherAI"),
                "pmpermit_pic": os.environ.get("PMPERMIT_PIC", DEFAULT_PMPERMIT_PIC),
                "use_pic": True,
                "max_warnings": int(os.environ.get("MAX_WARNINGS", 3)),
                "enabled": True
            },
            "users": {},
            "warnings": {},
            "approved_users": [],
            "user_states": {},
        }
        self._load()

    def _load(self):
        try:
            if DB_FILE.exists():
                with DB_FILE.open("r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
        except Exception as e:
            print(f"DB Load Error: {e}")

    def _save(self):
        try:
            DB_DIR.mkdir(exist_ok=True)
            with DB_FILE.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"DB Save Error: {e}")

    async def send_permit_message(self, event, message_type, **kwargs):
        """Send PM permit messages"""
        cfg = self.data["config"]
        
        messages = {
            "introduction": f"""🎭 **Hello! I'm {cfg['assistant_name']}**

👋 I'm {cfg['alive_name']}'s Personal Assistant
📝 Please briefly explain why you want to contact them
✅ Type **'ok'** to acknowledge this message

🤖 **Powered by CipherElite**""",

            "acknowledgment": f"""✅ **Thank you for your cooperation!**

📢 I will notify **{cfg['alive_name']}** about your message
⏳ Please wait for approval
🤖 **CipherElite Assistant Active**""",

            "warning": f"""⚠️ **Warning {kwargs.get('warn_count', 1)}/{cfg['max_warnings']}**

🚫 Please wait for approval before messaging again
📵 Unauthorized messages may result in blocking
🛡️ **CipherElite Protection Active**""",

            "owner_greeting": f"""👑 **CIPHER ELITE DEVELOPER DETECTED!** 👑

🎭 **Welcome Master Developer!**
✨ **Auto-approved** with highest privileges
🔥 Thank you for creating **CipherElite**!
💎 **VIP Access Granted Instantly**""",

            "approved": f"""🎉 **APPROVED!** 🎉

✅ You are now authorized to chat
💬 Feel free to continue your conversation
🤖 **CipherElite Access Granted**""",

            "blocked": f"""🔒 **ACCOUNT BLOCKED**

🚫 You have been permanently blocked
⚠️ Reason: Excessive unauthorized messages
🛡️ **CipherElite Security Enforcement**"""
        }

        message = messages.get(message_type, "Unknown message type")
        
        try:
            # Send with picture for introduction and owner greeting
            if message_type in ["introduction", "owner_greeting"] and cfg.get("use_pic"):
                try:
                    await event.client.send_file(
                        event.chat_id,
                        cfg["pmpermit_pic"],
                        caption=message
                    )
                except:
                    await event.reply(message)
            else:
                await event.reply(message)
        except Exception as e:
            print(f"Send message error: {e}")

    def is_approved(self, user_id):
        return str(user_id) in self.data["approved_users"]

    def approve_user(self, user_id):
        uid = str(user_id)
        if uid not in self.data["approved_users"]:
            self.data["approved_users"].append(uid)
        self.data["warnings"].pop(uid, None)
        self._save()

    def disapprove_user(self, user_id):
        uid = str(user_id)
        if uid in self.data["approved_users"]:
            self.data["approved_users"].remove(uid)
        self.data["warnings"][uid] = 0
        self._save()


# Initialize the assistant
assistant = PersonalAssistant()

def register_handlers(client):
    """Register all PM permit handlers"""
    
    @client.on(events.NewMessage(incoming=True))
    async def handle_incoming_pm(event):
        # Only handle private chats
        if not event.is_private or not assistant.data["config"]["enabled"]:
            return

        try:
            sender = await event.get_sender()
            if not sender or sender.bot:
                return
                
            uid = str(sender.id)
            
            # Handle CipherElite owner
            if sender.id == CIPHER_ELITE_OWNER_ID:
                if not assistant.is_approved(sender.id):
                    assistant.data["users"][uid] = {
                        "name": sender.first_name or "CipherElite Owner",
                        "username": sender.username or "thanosceo",
                        "first_seen": datetime.now().isoformat(),
                        "special_status": "CIPHER_ELITE_DEVELOPER"
                    }
                    assistant.approve_user(sender.id)
                    await assistant.send_permit_message(event, "owner_greeting")
                return

            # Skip if already approved
            if assistant.is_approved(sender.id):
                return

            text = (event.message.text or "").lower()

            # First-time user
            if uid not in assistant.data["users"]:
                assistant.data["users"][uid] = {
                    "name": sender.first_name or "Unknown",
                    "username": sender.username or "No username",
                    "first_seen": datetime.now().isoformat()
                }
                assistant.data["user_states"][uid] = "introduced"
                assistant.data["warnings"][uid] = 0
                assistant._save()
                await assistant.send_permit_message(event, "introduction")
                return

            # Handle acknowledgment
            if (assistant.data["user_states"].get(uid) == "introduced" and 
                text in ["ok", "okay", "yes", "k", "fine"]):
                assistant.data["user_states"][uid] = "acknowledged"
                assistant._save()
                await assistant.send_permit_message(event, "acknowledgment")
                return

            # Issue warning or block
            assistant.data["warnings"].setdefault(uid, 0)
            assistant.data["warnings"][uid] += 1
            
            if assistant.data["warnings"][uid] >= assistant.data["config"]["max_warnings"]:
                await assistant.send_permit_message(event, "blocked")
                try:
                    await client(functions.contacts.BlockRequest(sender.id))
                except:
                    pass
                assistant._save()
                return

            await assistant.send_permit_message(
                event, "warning", 
                warn_count=assistant.data["warnings"][uid]
            )
            assistant._save()
            
        except Exception as e:
            print(f"PM Handler Error: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.a(?:pprove)?(?:\s|$)'))
    async def approve_user_cmd(event):
        try:
            if event.is_private:
                user_id = event.chat_id
            else:
                reply = await event.get_reply_message()
                if not reply:
                    await event.reply("❌ Reply to a user's message to approve them")
                    return
                user_id = reply.sender_id

            assistant.approve_user(user_id)
            
            await event.reply(f"""🎭 **CipherElite Approval System**

✅ **User approved successfully!**
👤 **User ID:** `{user_id}`
🎉 **They can now chat freely**""")
            
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.da(?:pprove)?(?:\s|$)'))
    async def disapprove_user_cmd(event):
        try:
            if event.is_private:
                user_id = event.chat_id
            else:
                reply = await event.get_reply_message()
                if not reply:
                    await event.reply("❌ Reply to a user's message to disapprove them")
                    return
                user_id = reply.sender_id

            assistant.disapprove_user(user_id)
            
            await event.reply(f"""🎭 **CipherElite Disapproval System**

❌ **User disapproved!**
👤 **User ID:** `{user_id}`
🚫 **Access has been revoked**""")
            
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.pmpermit(?:\s+(on|off))?$'))
    async def toggle_pmpermit(event):
        try:
            args = event.pattern_match.group(1)
            if args:
                assistant.data["config"]["enabled"] = (args.lower() == "on")
            else:
                assistant.data["config"]["enabled"] = not assistant.data["config"]["enabled"]
            
            assistant._save()
            status = "✅ **Enabled**" if assistant.data["config"]["enabled"] else "❌ **Disabled**"
            
            await event.reply(f"""🎭 **CipherElite PM Permit**

🔄 **Status:** {status}
🤖 **System updated successfully**""")
            
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.listapproved$'))
    async def list_approved_users(event):
        try:
            approved = assistant.data["approved_users"]
            if not approved:
                await event.reply("📭 **No users are currently approved**")
                return
            
            text = "🎭 **CipherElite Approved Users**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for i, uid in enumerate(approved[:10], 1):  # Limit to 10 users
                info = assistant.data["users"].get(uid, {})
                name = info.get("name", "Unknown")
                username = info.get("username", "No username")
                
                if info.get("special_status") == "CIPHER_ELITE_DEVELOPER":
                    text += f"👑 **{i}. {name}** (DEVELOPER)\n"
                else:
                    text += f"✅ **{i}. {name}**\n"
                text += f"   🆔 `{uid}` | @{username}\n\n"
            
            if len(approved) > 10:
                text += f"... and {len(approved) - 10} more users\n\n"
                
            text += f"📊 **Total:** {len(approved)} approved users"
            await event.reply(text)
            
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    print("✅ CipherElite PM Permit handlers registered successfully!")

# Export function for the main bot
def init_pmpermit(client):
    """Initialize PM Permit system"""
    register_handlers(client)
    return assistant
