# =============================================================================
#  CipherElite Userbot Plugin - PM Permit (With Themed Defaults)
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

# Configuration with CipherElite themed defaults
CIPHER_ELITE_OWNER_ID = 5470956337

# 🎭 CipherElite Themed Defaults
DEFAULT_ALIVE_NAME = "Cipher Master"
DEFAULT_ASSISTANT_NAME = "CipherElite AI"
DEFAULT_PMPERMIT_PIC = "https://graph.org/file/c7b4d2f4c0b4d2f4c0b4d.jpg"  # Add your CipherElite themed image

# You can also use multiple default pictures and randomly select one
CIPHER_ELITE_PICS = [
    "https://graph.org/file/c7b4d2f4c0b4d2f4c0b4d.jpg",
    "https://graph.org/file/elite-cipher-logo-1.jpg", 
    "https://graph.org/file/cipherelite-banner-1.jpg"
]

# Database setup
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "pmpermit_db.json"

class PersonalAssistant:
    def __init__(self):
        self.data = {
            "config": {
                # 🎭 CipherElite themed defaults with fallbacks
                "alive_name": os.environ.get("ALIVE_NAME") or DEFAULT_ALIVE_NAME,
                "assistant_name": os.environ.get("ASSISTANT_NAME") or DEFAULT_ASSISTANT_NAME,
                "pmpermit_pic": os.environ.get("PMPERMIT_PIC") or DEFAULT_PMPERMIT_PIC,
                "use_pic": True,
                "use_random_pic": False,  # Set to True to randomly select from CIPHER_ELITE_PICS
                "max_warnings": int(os.environ.get("MAX_WARNINGS", 3)),
                "enabled": True,
                "welcome_message": os.environ.get("WELCOME_MESSAGE") or "Welcome to CipherElite Security System! 🎭"
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
                    # Merge loaded data with defaults to ensure new config options exist
                    for key, value in loaded_data.items():
                        if key == "config":
                            self.data[key].update(value)
                        else:
                            self.data[key] = value
        except Exception as e:
            print(f"DB Load Error: {e}")

    def _save(self):
        try:
            DB_DIR.mkdir(exist_ok=True)
            with DB_FILE.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"DB Save Error: {e}")

    def get_pmpermit_pic(self):
        """Get PM permit picture - either fixed or random"""
        if self.data["config"].get("use_random_pic", False):
            return random.choice(CIPHER_ELITE_PICS)
        return self.data["config"]["pmpermit_pic"]

    async def send_permit_message(self, event, message_type, **kwargs):
        """Send PM permit messages with CipherElite theming"""
        cfg = self.data["config"]
        
        # 🎭 CipherElite themed messages with proper defaults
        messages = {
            "introduction": f"""🎭 **Hello! I'm {cfg['assistant_name']}**

👑 I'm **{cfg['alive_name']}'s** Personal Security Assistant
🛡️ **CipherElite Protection System** is now active
📝 Please briefly explain why you want to contact my master
✅ Type **'ok'** or **'acknowledge'** to proceed

🎯 **Powered by CipherElite Userbot**
⚡ **Advanced Security Protocol Engaged**""",

            "acknowledgment": f"""✅ **Acknowledgment Received!**

📢 **{cfg['alive_name']}** has been notified about your message
⏳ Please wait for approval from the **Cipher Master**
🔒 Your request is being processed securely

🎭 **CipherElite Assistant Active**
🤖 **Thank you for your cooperation**""",

            "warning": f"""⚠️ **Security Warning {kwargs.get('warn_count', 1)}/{cfg['max_warnings']}**

🚫 **UNAUTHORIZED MESSAGE DETECTED**
🛡️ Please wait for approval before sending more messages
📵 Continued messaging may result in **automatic blocking**

🎭 **CipherElite Defense System**
⚡ **Protection Level:** Maximum""",

            "owner_greeting": f"""👑 **CIPHER ELITE CREATOR DETECTED!** 👑

🎖️ **Welcome Master Developer @thanosceo!**
✨ **INSTANT VIP ACCESS GRANTED**
🔥 **Thank you for creating CipherElite!**
💎 **All privileges unlocked automatically**

🎭 **It's an honor to serve the legend himself!**
🚀 **CipherElite runs flawlessly thanks to you!**""",

            "approved": f"""🎉 **ACCESS GRANTED!** 🎉

✅ **{cfg['alive_name']}** has approved your request
💬 You are now **authorized** to chat freely
🎯 Welcome to the **CipherElite Network**

🤖 **Enjoy your conversation!**
🎭 **CipherElite Access Control**""",

            "disapproved": f"""❌ **ACCESS REVOKED**

🚫 Your approval has been **withdrawn**
📝 Please contact **{cfg['alive_name']}** for re-approval
🔒 **CipherElite Security Protocol**

🎭 **Thank you for understanding**""",

            "blocked": f"""🛑 **SECURITY BREACH - ACCOUNT BLOCKED**

🚫 **PERMANENTLY BLOCKED** for policy violation
⚠️ **Reason:** Excessive unauthorized messages
🛡️ **CipherElite Anti-Spam System**

🎭 **Security Enforcement Complete**
⚡ **No further contact possible**"""
        }

        message = messages.get(message_type, f"🎭 **CipherElite System Message**\n\nUnknown message type: {message_type}")
        
        try:
            # Add typing effect for realism
            async with event.client.action(event.chat_id, 'typing'):
                await asyncio.sleep(1.5)

            # Send with picture for introduction and owner greeting
            if message_type in ["introduction", "owner_greeting"] and cfg.get("use_pic"):
                try:
                    pic_url = self.get_pmpermit_pic()
                    await event.client.send_file(
                        event.chat_id,
                        pic_url,
                        caption=message
                    )
                except Exception as pic_error:
                    print(f"Picture send failed: {pic_error}")
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
        self.data["user_states"][uid] = "approved"
        self._save()

    def disapprove_user(self, user_id):
        uid = str(user_id)
        if uid in self.data["approved_users"]:
            self.data["approved_users"].remove(uid)
        self.data["warnings"][uid] = 0
        self.data["user_states"][uid] = "disapproved"
        self._save()


# Initialize the assistant
assistant = PersonalAssistant()

def register_handlers(client):
    """Register all PM permit handlers with CipherElite theming"""
    
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
            
            # Handle CipherElite owner with special treatment
            if sender.id == CIPHER_ELITE_OWNER_ID:
                if not assistant.is_approved(sender.id):
                    assistant.data["users"][uid] = {
                        "name": sender.first_name or "CipherElite Creator",
                        "username": sender.username or "thanosceo",
                        "first_seen": datetime.now().isoformat(),
                        "special_status": "CIPHER_ELITE_DEVELOPER",
                        "vip_level": "CREATOR"
                    }
                    assistant.approve_user(sender.id)
                    await assistant.send_permit_message(event, "owner_greeting")
                return

            # Skip if already approved
            if assistant.is_approved(sender.id):
                return

            text = (event.message.text or "").lower().strip()

            # First-time user introduction
            if uid not in assistant.data["users"]:
                assistant.data["users"][uid] = {
                    "name": sender.first_name or "Unknown User",
                    "username": sender.username or "No username",
                    "first_seen": datetime.now().isoformat(),
                    "user_id": uid
                }
                assistant.data["user_states"][uid] = "introduced"
                assistant.data["warnings"][uid] = 0
                assistant._save()
                await assistant.send_permit_message(event, "introduction")
                return

            # Handle acknowledgment with multiple accepted responses
            acknowledgment_words = ["ok", "okay", "yes", "k", "fine", "acknowledge", "understood", "got it", "sure"]
            if (assistant.data["user_states"].get(uid) == "introduced" and 
                any(word in text for word in acknowledgment_words)):
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
                    print(f"🛑 Blocked user {uid} after {assistant.data['warnings'][uid]} warnings")
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

    # Command handlers with CipherElite theming
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.a(?:pprove)?(?:\s|$)'))
    async def approve_user_cmd(event):
        try:
            if event.is_private:
                user_id = event.chat_id
            else:
                reply = await event.get_reply_message()
                if not reply:
                    await event.reply("🎭 **CipherElite Approval System**\n\n❌ **Usage:** Reply to a user's message with `.a` to approve them")
                    return
                user_id = reply.sender_id

            # Don't approve if it's yourself
            if user_id == (await client.get_me()).id:
                await event.reply("🎭 **Cannot approve yourself!**")
                return

            assistant.approve_user(user_id)
            
            await event.reply(f"""🎭 **CipherElite Approval System**
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **User Approved Successfully!**
👤 **User ID:** `{user_id}`
🎯 **Status:** Full access granted
🎉 **They can now chat freely**

⚡ **Powered by CipherElite**""")
            
        except Exception as e:
            await event.reply(f"❌ **CipherElite Error:** {str(e)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.da(?:pprove)?(?:\s|$)'))
    async def disapprove_user_cmd(event):
        try:
            if event.is_private:
                user_id = event.chat_id
            else:
                reply = await event.get_reply_message()
                if not reply:
                    await event.reply("🎭 **CipherElite Disapproval System**\n\n❌ **Usage:** Reply to a user's message with `.da` to disapprove them")
                    return
                user_id = reply.sender_id

            # Don't disapprove the CipherElite owner
            if user_id == CIPHER_ELITE_OWNER_ID:
                await event.reply("👑 **Cannot disapprove the CipherElite Creator!**")
                return

            assistant.disapprove_user(user_id)
            
            await event.reply(f"""🎭 **CipherElite Disapproval System**
━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **User Disapproved!**
👤 **User ID:** `{user_id}`
🚫 **Status:** Access revoked
🔒 **Security level restored**

⚡ **Powered by CipherElite**""")
            
        except Exception as e:
            await event.reply(f"❌ **CipherElite Error:** {str(e)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.pmpermit(?:\s+(on|off|status))?$'))
    async def toggle_pmpermit(event):
        try:
            args = event.pattern_match.group(1)
            
            if args == "status":
                status = "🟢 **Online**" if assistant.data["config"]["enabled"] else "🔴 **Offline**"
                pic_status = "🖼️ **Enabled**" if assistant.data["config"]["use_pic"] else "📝 **Text Only**"
                
                await event.reply(f"""🎭 **CipherElite PM Permit Status**
━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 **System Status:** {status}
📸 **Picture Mode:** {pic_status}
⚠️ **Max Warnings:** {assistant.data["config"]["max_warnings"]}
👥 **Approved Users:** {len(assistant.data["approved_users"])}
👤 **Assistant:** {assistant.data["config"]["assistant_name"]}
👑 **Master:** {assistant.data["config"]["alive_name"]}

⚡ **Powered by CipherElite**""")
                return
                
            if args:
                assistant.data["config"]["enabled"] = (args.lower() == "on")
            else:
                assistant.data["config"]["enabled"] = not assistant.data["config"]["enabled"]
            
            assistant._save()
            status = "🟢 **Activated**" if assistant.data["config"]["enabled"] else "🔴 **Deactivated**"
            
            await event.reply(f"""🎭 **CipherElite PM Permit Control**
━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 **System Status:** {status}
🛡️ **Security Protocol Updated**
⚡ **Changes Applied Successfully**

💡 **Tip:** Use `.pmpermit status` for detailed info""")
            
        except Exception as e:
            await event.reply(f"❌ **CipherElite Error:** {str(e)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.listapproved$'))
    async def list_approved_users(event):
        try:
            approved = assistant.data["approved_users"]
            if not approved:
                await event.reply("""🎭 **CipherElite Approved Users**
━━━━━━━━━━━━━━━━━━━━━━━━━

📭 **No users are currently approved**
💡 **Use `.a` (reply to message) to approve users**
🎯 **CipherElite Protection: Maximum Security**""")
                return
            
            text = "🎭 **CipherElite Approved Users**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for i, uid in enumerate(approved[:10], 1):  # Limit to 10 users
                info = assistant.data["users"].get(uid, {})
                name = info.get("name", "Unknown")
                username = info.get("username", "No username")
                username_display = f"@{username}" if username != "No username" else "No username"
                
                if info.get("special_status") == "CIPHER_ELITE_DEVELOPER":
                    text += f"👑 **{i}. {name}** (CREATOR)\n"
                    text += f"   🆔 `{uid}` | {username_display}\n"
                    text += f"   ⭐ **CipherElite Developer**\n\n"
                else:
                    text += f"✅ **{i}. {name}**\n"
                    text += f"   🆔 `{uid}` | {username_display}\n\n"
            
            if len(approved) > 10:
                text += f"... and **{len(approved) - 10}** more users\n\n"
                
            text += f"📊 **Total Approved:** {len(approved)} user{'s' if len(approved) != 1 else ''}\n"
            text += f"⚡ **Powered by CipherElite**"
            
            await event.reply(text)
            
        except Exception as e:
            await event.reply(f"❌ **CipherElite Error:** {str(e)}")

    # Additional CipherElite themed commands
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.setname\s+(.+)$'))
    async def set_alive_name(event):
        try:
            new_name = event.pattern_match.group(1).strip()
            assistant.data["config"]["alive_name"] = new_name
            assistant._save()
            
            await event.reply(f"""🎭 **CipherElite Name Configuration**
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Master name updated!**
👑 **New Name:** {new_name}
🔄 **All PM messages will now use this name**

⚡ **Powered by CipherElite**""")
            
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.setassistant\s+(.+)$'))
    async def set_assistant_name(event):
        try:
            new_assistant = event.pattern_match.group(1).strip()
            assistant.data["config"]["assistant_name"] = new_assistant
            assistant._save()
            
            await event.reply(f"""🎭 **CipherElite Assistant Configuration**
━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **Assistant name updated!**
🎯 **New Assistant:** {new_assistant}
📝 **PM messages will use this assistant identity**

⚡ **Powered by CipherElite**""")
            
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")

    print("✅ CipherElite PM Permit with themed defaults loaded successfully!")
    print(f"👑 Master: {assistant.data['config']['alive_name']}")
    print(f"🤖 Assistant: {assistant.data['config']['assistant_name']}")

# Export function for the main bot
def init_pmpermit(client):
    """Initialize CipherElite PM Permit system with themed defaults"""
    register_handlers(client)
    print("🎭 CipherElite PM Permit System Initialized!")
    return assistant
