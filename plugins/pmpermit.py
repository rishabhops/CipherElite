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
#        – Telegram:  @thanosceo
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

CIPHER_ELITE_OWNER_ID = 5470956337  

# Default PM permit picture
DEFAULT_PMPERMIT_PIC = Config.DEFAULT_PMPERMIT_PIC

# DB setup
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR       = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE      = DB_DIR / "assistant_db.json"


def owner_only():
    """Decorator for CipherElite owner commands"""
    def decorator(func):
        async def wrapper(event):
            if event.sender_id == CIPHER_ELITE_OWNER_ID:
                return await func(event)
            return
        return wrapper
    return decorator


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
        Send a permit‑flow message with enhanced emoji formatting
        """
        try:
            target = await event.get_sender()
        except Exception:
            target = event.chat_id

        cfg = self.data["config"]
        texts = {
            "introduction": [
                f"🎭 **Hello! I'm {cfg['assistant_name']}**\n\n"
                f"👋 I'm {cfg['alive_name']}'s **Personal Assistant**\n"
                f"📝 Please briefly explain why you want to contact them\n"
                f"✅ Type **'ok'** to acknowledge this message\n\n"
                f"🤖 **Powered by CipherElite**",
                
                f"🛡️ **Security Protocol Activated**\n\n"
                f"🤖 Assistant: **{cfg['assistant_name']}**\n"
                f"👤 Master: **{cfg['alive_name']}**\n"
                f"📋 Please state your purpose for contacting\n"
                f"✅ Reply with **'ok'** to proceed\n\n"
                f"🎭 **CipherElite Protection System**"
            ],
            "acknowledgment": [
                f"✅ **Thank you for your cooperation!**\n\n"
                f"📢 I will notify **{cfg['alive_name']}** about your message\n"
                f"⏳ Please wait for approval\n"
                f"🤖 **CipherElite Assistant Active**",
                
                f"👍 **Acknowledgment Received!**\n\n"
                f"📨 **{cfg['alive_name']}** has been notified\n"
                f"⏰ You will be contacted soon\n"
                f"🎭 **CipherElite Security**"
            ],
            "warning": [
                f"⚠️ **Warning {warn_count}/{max_warnings}**\n\n"
                f"🚫 Please **wait for approval** before messaging again\n"
                f"📵 Unauthorized messages may result in blocking\n"
                f"🛡️ **CipherElite Protection Active**",
                
                f"🔔 **Security Alert - Warning {warn_count}/{max_warnings}**\n\n"
                f"⏸️ Please **pause** and wait for response\n"
                f"🚨 Continued messaging will trigger auto-block\n"
                f"🤖 **CipherElite Defense System**"
            ],
            "approved": [
                f"🎉 **APPROVED!** 🎉\n\n"
                f"✅ You are now **authorized** to chat\n"
                f"💬 Feel free to continue your conversation\n"
                f"🤖 **CipherElite Access Granted**",
                
                f"🌟 **Welcome to the Approved List!**\n\n"
                f"🔓 **Full access** has been granted\n"
                f"💫 Enjoy your conversation!\n"
                f"🎭 **CipherElite Premium Access**"
            ],
            "disapproved": [
                f"❌ **Access Revoked**\n\n"
                f"🚫 Your approval has been **removed**\n"
                f"📝 Please request permission again if needed\n"
                f"🛡️ **CipherElite Security**",
                
                f"⛔ **Authorization Cancelled**\n\n"
                f"🔒 Approval status has been **revoked**\n"
                f"💭 Contact admin for re-approval\n"
                f"🤖 **CipherElite Access Control**"
            ],
            "blocked": [
                f"🔒 **ACCOUNT BLOCKED**\n\n"
                f"🚫 You have been **permanently blocked**\n"
                f"⚠️ Reason: **Excessive unauthorized messages**\n"
                f"🛡️ **CipherElite Security Enforcement**",
                
                f"🛑 **SECURITY BREACH - BLOCKED**\n\n"
                f"❌ Multiple warnings **ignored**\n"
                f"🚨 **Automatic block** has been applied\n"
                f"🎭 **CipherElite Defense Protocol**"
            ],
            "owner_greeting": [
                f"👑 **CIPHER ELITE DEVELOPER DETECTED!** 👑\n\n"
                f"🎭 **Welcome Master Developer!**\n"
                f"✨ **Auto-approved** with highest privileges\n"
                f"🔥 Thank you for creating **CipherElite**!\n"
                f"💎 **VIP Access Granted Instantly**\n\n"
                f"🤖 **Your creation serves me well, Master!**",
                
                f"🌟 **THE LEGEND HAS ARRIVED!** 🌟\n\n"
                f"🎖️ **CipherElite Creator** @thanosceo\n"
                f"👑 **Instantly approved** - No questions asked!\n"
                f"🙏 **Thank you** for this amazing userbot\n"
                f"🚀 **CipherElite** is serving perfectly!\n\n"
                f"💫 **Honor to serve the Master Developer!**"
            ]
        }

        lst = texts.get(mtype, [])
        if not lst:
            return

        msg = random.choice(lst).format(**kwargs)

        # Show typing indicator
        try:
            async with event.client.action(target, 'typing'):
                await asyncio.sleep(1.5)
        except Exception:
            pass

        # Send with picture for introduction and owner greeting
        if mtype in ["introduction", "owner_greeting"] and cfg.get("use_pic"):
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
        # Only handle private chats
        if not event.is_private:
            return

        sender = await event.get_sender()
        uid = str(sender.id)

        
        if sender.id == CIPHER_ELITE_OWNER_ID:
            # Auto-approve the owner
            if uid not in self.data["approved_users"]:
                self.data["approved_users"].append(uid)
                self.data["users"][uid] = {
                    "name": sender.first_name or "CipherElite Owner",
                    "username": sender.username or "thanosceo",
                    "first_seen": datetime.now().isoformat(),
                    "special_status": "CIPHER_ELITE_DEVELOPER"
                }
                self.data["warnings"].pop(uid, None)
                self.data["user_states"][uid] = "owner_approved"
                self._save()
                
                # Send special owner greeting
                await self.send_message(event, "owner_greeting")
                return
            else:
                # Owner is already approved, just return (let them chat freely)
                return

        # Ignore bots and already-approved users
        if sender.bot or uid in self.data["approved_users"]:
            return

        text = (event.message.text or "").lower()

        # First-time user → introduction
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "name": sender.first_name or "Unknown",
                "username": sender.username,
                "first_seen": datetime.now().isoformat()
            }
            self.data["user_states"][uid] = "introduced"
            self.data["warnings"][uid] = 0
            await self.send_message(event, "introduction")
            self._save()
            return

        # Acknowledgment
        if self.data["user_states"].get(uid) == "introduced" and text in ("ok", "okay", "yes"):
            self.data["user_states"][uid] = "acknowledged"
            await self.send_message(event, "acknowledgment")
            self._save()
            return

        # Warnings / blocking
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


def init(client_instance):
    """
    Initialize PM Permit with CipherElite owner recognition
    """
    assistant = PersonalAssistant()
    commands = [
        ".a / .approve - ✅ Approve a user for chatting",
        ".da / .disapprove - ❌ Revoke user approval", 
        ".block - 🚫 Block a user permanently",
        ".listapproved - 📋 Show all approved users",
        ".setpermitpic <url> - 🖼️ Set PM permit picture",
        ".togglepermitpic - 🔄 Enable/disable permit picture"
    ]
    description = "🎭 Cipher Elite PM Permit - Advanced personal assistant"
    add_handler("pmpermit", commands, description)

    @CipherElite.on(events.NewMessage(incoming=True))
    async def _incoming(event):
        await assistant.handle_message(event)

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.(?:a|approve)(?:$|\s)"))
    @rishabh()
    async def _approve(event):
        try:
            if event.is_private:
                uid = str(event.chat_id)
            else:
                reply = await event.get_reply_message()
                if not reply:
                    return await event.reply("🎭 **Cipher Elite PM Manager**\n\n"
                                           "❌ **Error:** Reply to a user to approve them\n"
                                           "💡 **Usage:** Reply to user's message with `.a`")
                uid = str(reply.sender_id)

            if uid not in assistant.data["approved_users"]:
                assistant.data["approved_users"].append(uid)
            assistant.data["warnings"].pop(uid, None)
            assistant._save()
            
            await event.reply("🎭 **Cipher Elite Approval System**\n\n"
                            f"✅ **User approved successfully!**\n"
                            f"👤 **User ID:** `{uid}`\n"
                            f"🎉 **They can now chat freely**\n"
                            f"🤖 **Powered by Cipher Elite**")
        except Exception as e:
            await event.reply(f"❌ **Approval error:** {str(e)}")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.(?:da|disapprove)(?:$|\s)"))
    @rishabh()
    async def _disapprove(event):
        try:
            if event.is_private:
                uid = str(event.chat_id)
            else:
                reply = await event.get_reply_message()
                if not reply:
                    return await event.reply("🎭 **Cipher Elite PM Manager**\n\n"
                                           "❌ **Error:** Reply to a user to disapprove them")
                uid = str(reply.sender_id)

            assistant.data["approved_users"] = [
                u for u in assistant.data["approved_users"] if u != uid
            ]
            assistant.data["warnings"][uid] = 0
            assistant._save()
            
            await event.reply("🎭 **Cipher Elite Disapproval System**\n\n"
                            f"❌ **User disapproved!**\n"
                            f"👤 **User ID:** `{uid}`\n"
                            f"🚫 **Access has been revoked**\n"
                            f"🤖 **Powered by Cipher Elite**")
        except Exception as e:
            await event.reply(f"❌ **Disapproval error:** {str(e)}")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.listapproved$"))
    @rishabh()
    async def _list(event):
        try:
            approved = assistant.data["approved_users"]
            if not approved:
                return await event.reply("🎭 **Cipher Elite Approved Users**\n\n"
                                       "📭 **No users are currently approved**\n"
                                       "💡 **Use `.a` to approve users**")
            
            text = "🎭 **Cipher Elite Approved Users**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for i, uid in enumerate(approved, 1):
                info = assistant.data["users"].get(uid, {})
                name = info.get("name", "Unknown")
                username = info.get("username", "No username")
                special = info.get("special_status", "")
                
                if special == "CIPHER_ELITE_DEVELOPER":
                    text += f"👑 **{i}. {name}** (DEVELOPER)\n"
                    text += f"   🆔 `{uid}` | @{username}\n"
                    text += f"   ⭐ **CipherElite Creator**\n\n"
                else:
                    text += f"✅ **{i}. {name}**\n"
                    text += f"   🆔 `{uid}` | @{username}\n\n"
            
            text += f"📊 **Total:** {len(approved)} approved user{'s' if len(approved) != 1 else ''}\n"
            text += f"🤖 **Powered by Cipher Elite**"
            
            await event.reply(text)
        except Exception as e:
            await event.reply(f"❌ **List error:** {str(e)}")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.setpermitpic(?:\s+.*)?$"))
    @rishabh()
    async def _setpic(event):
        try:
            if event.reply_to_msg_id:
                msg = await event.get_reply_message()
                if msg.media:
                    path = await event.client.download_media(msg)
                    assistant.data["config"]["pmpermit_pic"] = path
                    assistant.data["config"]["use_pic"] = True
                    assistant._save()
                    return await event.reply("🎭 **Cipher Elite Picture Manager**\n\n"
                                           "✅ **Permit picture set from reply**\n"
                                           "🖼️ **New image will be used for PM permits**")
                return await event.reply("❌ **Please reply to an image file**")
            
            parts = event.text.split(None, 1)
            if len(parts) > 1:
                assistant.data["config"]["pmpermit_pic"] = parts[1].strip()
                assistant.data["config"]["use_pic"] = True
                assistant._save()
                return await event.reply("🎭 **Cipher Elite Picture Manager**\n\n"
                                       "✅ **Permit picture set from URL**\n"
                                       "🔗 **Image URL has been saved**")
            
            await event.reply("🎭 **Cipher Elite Picture Manager**\n\n"
                            "❌ **Usage:** `.setpermitpic <url>` or reply to image\n"
                            "💡 **Example:** `.setpermitpic https://example.com/pic.jpg`")
        except Exception as e:
            await event.reply(f"❌ **Picture error:** {str(e)}")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.togglepermitpic$"))
    @rishabh()
    async def _togglepic(event):
        try:
            cfg = assistant.data["config"]
            cfg["use_pic"] = not cfg.get("use_pic", True)
            assistant._save()
            state = "✅ **Enabled**" if cfg["use_pic"] else "❌ **Disabled**"
            
            await event.reply("🎭 **Cipher Elite Picture Toggle**\n\n"
                            f"🖼️ **Permit picture:** {state}\n"
                            f"🔄 **Setting updated successfully**\n"
                            f"🤖 **Powered by Cipher Elite**")
        except Exception as e:
            await event.reply(f"❌ **Toggle error:** {str(e)}")

    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.block(?:$|\s)"))
    @rishabh()
    async def _block(event):
        try:
            if event.is_private:
                uid = str(event.chat_id)
            else:
                reply = await event.get_reply_message()
                if not reply:
                    return await event.reply("🎭 **Cipher Elite Block System**\n\n"
                                           "❌ **Error:** Reply to a user to block them")
                uid = str(reply.sender_id)

            # Don't allow blocking the CipherElite owner
            if int(uid) == CIPHER_ELITE_OWNER_ID:
                return await event.reply("👑 **Cannot block CipherElite Developer!**\n\n"
                                       "🛡️ **The creator is protected from blocking**\n"
                                       "🎭 **CipherElite Security Protocol**")

            assistant.data["approved_users"] = [
                u for u in assistant.data["approved_users"] if u != uid
            ]
            assistant.data["warnings"].pop(uid, None)
            assistant.data["user_states"].pop(uid, None)
            assistant._save()
            
            await event.client(functions.contacts.BlockRequest(int(uid)))
            
            await event.reply("🎭 **Cipher Elite Block System**\n\n"
                            f"🛑 **User blocked successfully!**\n"
                            f"👤 **User ID:** `{uid}`\n"
                            f"🚫 **Complete access denied**\n"
                            f"🤖 **Powered by Cipher Elite**")
        except Exception as e:
            await event.reply(f"❌ **Block error:** {str(e)}")

    return assistant

async def register_commands():
    """Register additional commands if needed"""
    pass
