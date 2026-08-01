# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    sudo
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  Commands:       .sudo / .addsudo <reply|user_id>
#                  .delsudo <reply|user_id>
#                  .listsudo
# =============================================================================

from telethon import events
import json
import os
from datetime import datetime
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh
import vars
import config.config as cfg

VERSION = "1.0.0"
CATEGORY = "admin"

SUDO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sudo_users.json")

def load_sudo_users():
    """Load saved sudo users from JSON into vars.SUDO_USERS / Config.SUDO_USERS."""
    if not os.path.exists(SUDO_FILE):
        return
    try:
        with open(SUDO_FILE, "r") as f:
            data = json.load(f)
        for uid in data.get("users", []):
            uid = int(uid)
            if uid not in vars.SUDO_USERS:
                vars.SUDO_USERS.append(uid)
            if uid not in cfg.Config.SUDO_USERS:
                cfg.Config.SUDO_USERS.append(uid)
    except Exception as e:
        print(f"⚠️ Failed to load sudo users: {e}")

def save_sudo_users():
    """Persist current sudo users to JSON."""
    try:
        users = [int(x) for x in vars.SUDO_USERS]
        with open(SUDO_FILE, "w") as f:
            json.dump({"users": users}, f)
    except Exception as e:
        print(f"⚠️ Failed to save sudo users: {e}")

async def _resolve_user(event):
    """Resolve user from reply or raw input. Returns (user_entity, error_text)."""
    text = event.pattern_match.group(1).strip()
    if event.is_reply:
        msg = await event.get_reply_message()
        try:
            user = await event.client.get_entity(msg.sender_id)
            return user, None
        except Exception as e:
            return None, f"⚠️ Could not resolve user: {e}"
    if text:
        try:
            user = await event.client.get_entity(text)
            return user, None
        except Exception:
            try:
                user = await event.client.get_entity(int(text))
                return user, None
            except Exception as e:
                return None, f"⚠️ Could not resolve user: {e}"
    return None, "❌ Reply to a user or provide a username/ID."

def init(client_instance):
    commands = [
        ".sudo <reply|id> - Add a sudo user",
        ".addsudo <reply|id> - Add a sudo user",
        ".delsudo <reply|id> - Remove a sudo user",
        ".listsudo - List sudo users"
    ]
    description = "Manage sudo users who can use restricted commands"
    add_handler("sudo", commands, description)
    load_sudo_users()

async def register_commands():
    load_sudo_users()

    @CipherElite.on(events.NewMessage(pattern=r"\.(?:sudo|addsudo)(?: |$)(.*)"))
    @rishabh()
    async def add_sudo(event):
        user, err = await _resolve_user(event)
        if err:
            await event.reply(err)
            return
        if user.id == event.sender_id:
            await event.reply("🚫 **You cannot add yourself as sudo.**")
            return
        if user.id in vars.SUDO_USERS:
            await event.reply(f"👤 **{user.first_name}** is already a sudo user.")
            return
        vars.SUDO_USERS.append(user.id)
        cfg.Config.SUDO_USERS.append(user.id)
        save_sudo_users()
        date = datetime.now().strftime("%d %B %Y")
        await event.reply(
            f"✅ **Added to sudo users**\n\n"
            f"👤 **Name:** [{user.first_name}](tg://user?id={user.id})\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"📅 **Added on:** `{date}`"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.delsudo(?: |$)(.*)"))
    @rishabh()
    async def del_sudo(event):
        user, err = await _resolve_user(event)
        if err:
            await event.reply(err)
            return
        if user.id not in vars.SUDO_USERS:
            await event.reply(f"👤 **{user.first_name}** is not a sudo user.")
            return
        vars.SUDO_USERS.remove(user.id)
        cfg.Config.SUDO_USERS.remove(user.id)
        save_sudo_users()
        await event.reply(
            f"✅ **Removed from sudo users**\n\n"
            f"👤 **Name:** [{user.first_name}](tg://user?id={user.id})\n"
            f"🆔 **ID:** `{user.id}`"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.listsudo"))
    @rishabh()
    async def list_sudo(event):
        if not vars.SUDO_USERS:
            await event.reply("📭 **No sudo users configured.**")
            return
        lines = ["🔑 **Sudo Users**\n"]
        for uid in vars.SUDO_USERS:
            try:
                user = await event.client.get_entity(uid)
                name = user.first_name or "Unknown"
                username = f"@{user.username}" if user.username else "N/A"
            except Exception:
                name = "Unknown"
                username = "N/A"
            lines.append(
                f"• [{name}](tg://user?id={uid})\n"
                f"  🆔 `{uid}` | 👤 {username}"
            )
        await event.reply("\n".join(lines))
