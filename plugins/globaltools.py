# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    globaltools
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import json
import os
from pathlib import Path
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

DATA_FILE = Path(__file__).parent.parent / "data" / "globaltools.json"

def load_data():
    """Load global tools data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"gbanned": {}, "gmuted": {}}

def save_data(data):
    """Save global tools data to JSON file"""
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init(client_instance):
    commands = [
        ".gban <reply/username> - Ban user globally in all groups",
        ".ungban <reply/username> - Unban user globally",
        ".gmute <reply/username> - Mute user globally",
        ".ungmute <reply/username> - Unmute user globally",
        ".gkick <reply/username> - Kick user from all groups",
        ".gpromote <reply/username> - Promote user in all admin chats",
        ".gdemote <reply/username> - Demote user in all admin chats",
        ".listgban - List all gbanned users",
        ".gstat <reply/username> - Check if user is gbanned"
    ]
    description = "Global Admin Tools for managing users across all groups"
    add_handler("globaltools", commands, description)

async def get_user_from_event(event):
    """Get user ID and name from reply or username"""
    user_id = None
    user_name = None
    
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        try:
            user = await event.client.get_entity(user_id)
            user_name = user.first_name or "User"
        except:
            user_name = "User"
    else:
        text = event.text.split(maxsplit=1)
        if len(text) > 1:
            try:
                user = await event.client.get_entity(text[1])
                user_id = user.id
                user_name = user.first_name or "User"
            except:
                await event.reply("❌ Invalid username or user not found!")
                return None, None
        else:
            await event.reply("❌ Reply to a user or provide username!")
            return None, None
    
    return user_id, user_name

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.gban"))
    @rishabh()
    async def gban(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        # Get reason
        text_parts = event.text.split(maxsplit=2)
        reason = text_parts[2] if len(text_parts) > 2 else "No reason provided"
        
        data = load_data()
        data["gbanned"][str(user_id)] = {
            "name": user_name,
            "reason": reason
        }
        save_data(data)
        
        msg = await event.reply(f"🔨 **Global Ban Initiated**\n\n👤 User: {user_name} (`{user_id}`)\n📝 Reason: {reason}\n\n⏳ Banning in all groups...")
        
        banned_count = 0
        failed_count = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await event.client(EditBannedRequest(
                        dialog.id,
                        user_id,
                        ChatBannedRights(until_date=None, view_messages=True)
                    ))
                    banned_count += 1
                except:
                    failed_count += 1
        
        await msg.edit(f"✅ **Global Ban Complete**\n\n👤 User: {user_name} (`{user_id}`)\n📝 Reason: {reason}\n\n✔️ Banned in: {banned_count} groups\n❌ Failed: {failed_count} groups")

    @CipherElite.on(events.NewMessage(pattern=r"\.ungban"))
    @rishabh()
    async def ungban(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        data = load_data()
        if str(user_id) not in data["gbanned"]:
            await event.reply(f"❌ {user_name} is not gbanned!")
            return
        
        del data["gbanned"][str(user_id)]
        save_data(data)
        
        msg = await event.reply(f"🔓 **Global Unban Initiated**\n\n👤 User: {user_name} (`{user_id}`)\n\n⏳ Unbanning in all groups...")
        
        unbanned_count = 0
        failed_count = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await event.client(EditBannedRequest(
                        dialog.id,
                        user_id,
                        ChatBannedRights(until_date=None, view_messages=False)
                    ))
                    unbanned_count += 1
                except:
                    failed_count += 1
        
        await msg.edit(f"✅ **Global Unban Complete**\n\n👤 User: {user_name} (`{user_id}`)\n\n✔️ Unbanned in: {unbanned_count} groups\n❌ Failed: {failed_count} groups")

    @CipherElite.on(events.NewMessage(pattern=r"\.gmute"))
    @rishabh()
    async def gmute(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        # Get reason
        text_parts = event.text.split(maxsplit=2)
        reason = text_parts[2] if len(text_parts) > 2 else "No reason provided"
        
        data = load_data()
        data["gmuted"][str(user_id)] = {
            "name": user_name,
            "reason": reason
        }
        save_data(data)
        
        msg = await event.reply(f"🔇 **Global Mute Initiated**\n\n👤 User: {user_name} (`{user_id}`)\n📝 Reason: {reason}\n\n⏳ Muting in all groups...")
        
        muted_count = 0
        failed_count = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await event.client(EditBannedRequest(
                        dialog.id,
                        user_id,
                        ChatBannedRights(until_date=None, send_messages=True)
                    ))
                    muted_count += 1
                except:
                    failed_count += 1
        
        await msg.edit(f"✅ **Global Mute Complete**\n\n👤 User: {user_name} (`{user_id}`)\n📝 Reason: {reason}\n\n✔️ Muted in: {muted_count} groups\n❌ Failed: {failed_count} groups")

    @CipherElite.on(events.NewMessage(pattern=r"\.ungmute"))
    @rishabh()
    async def ungmute(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        data = load_data()
        if str(user_id) not in data["gmuted"]:
            await event.reply(f"❌ {user_name} is not gmuted!")
            return
        
        del data["gmuted"][str(user_id)]
        save_data(data)
        
        msg = await event.reply(f"🔊 **Global Unmute Initiated**\n\n👤 User: {user_name} (`{user_id}`)\n\n⏳ Unmuting in all groups...")
        
        unmuted_count = 0
        failed_count = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await event.client(EditBannedRequest(
                        dialog.id,
                        user_id,
                        ChatBannedRights(until_date=None, send_messages=False)
                    ))
                    unmuted_count += 1
                except:
                    failed_count += 1
        
        await msg.edit(f"✅ **Global Unmute Complete**\n\n👤 User: {user_name} (`{user_id}`)\n\n✔️ Unmuted in: {unmuted_count} groups\n❌ Failed: {failed_count} groups")

    @CipherElite.on(events.NewMessage(pattern=r"\.gkick"))
    @rishabh()
    async def gkick(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        msg = await event.reply(f"👢 **Global Kick Initiated**\n\n👤 User: {user_name} (`{user_id}`)\n\n⏳ Kicking from all groups...")
        
        kicked_count = 0
        failed_count = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    # Kick = ban then unban
                    await event.client.kick_participant(dialog.id, user_id)
                    kicked_count += 1
                except:
                    failed_count += 1
        
        await msg.edit(f"✅ **Global Kick Complete**\n\n👤 User: {user_name} (`{user_id}`)\n\n✔️ Kicked from: {kicked_count} groups\n❌ Failed: {failed_count} groups")

    @CipherElite.on(events.NewMessage(pattern=r"\.gpromote"))
    @rishabh()
    async def gpromote(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        msg = await event.reply(f"👑 **Global Promote Initiated**\n\n👤 User: {user_name} (`{user_id}`)\n\n⏳ Promoting in all admin chats...")
        
        promoted_count = 0
        failed_count = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await event.client.edit_admin(
                        dialog.id,
                        user_id,
                        is_admin=True,
                        title="Admin"
                    )
                    promoted_count += 1
                except:
                    failed_count += 1
        
        await msg.edit(f"✅ **Global Promote Complete**\n\n👤 User: {user_name} (`{user_id}`)\n\n✔️ Promoted in: {promoted_count} chats\n❌ Failed: {failed_count} chats")

    @CipherElite.on(events.NewMessage(pattern=r"\.gdemote"))
    @rishabh()
    async def gdemote(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        msg = await event.reply(f"⬇️ **Global Demote Initiated**\n\n👤 User: {user_name} (`{user_id}`)\n\n⏳ Demoting in all admin chats...")
        
        demoted_count = 0
        failed_count = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await event.client.edit_admin(
                        dialog.id,
                        user_id,
                        is_admin=False
                    )
                    demoted_count += 1
                except:
                    failed_count += 1
        
        await msg.edit(f"✅ **Global Demote Complete**\n\n👤 User: {user_name} (`{user_id}`)\n\n✔️ Demoted in: {demoted_count} chats\n❌ Failed: {failed_count} chats")

    @CipherElite.on(events.NewMessage(pattern=r"\.listgban"))
    @rishabh()
    async def listgban(event):
        data = load_data()
        gbanned = data["gbanned"]
        
        if not gbanned:
            await event.reply("✅ No users are globally banned!")
            return
        
        msg = "📋 **Globally Banned Users**\n\n"
        for user_id, info in gbanned.items():
            msg += f"👤 {info['name']} (`{user_id}`)\n📝 Reason: {info['reason']}\n\n"
        
        await event.reply(msg)

    @CipherElite.on(events.NewMessage(pattern=r"\.gstat"))
    @rishabh()
    async def gstat(event):
        user_id, user_name = await get_user_from_event(event)
        if not user_id:
            return
        
        data = load_data()
        
        is_gbanned = str(user_id) in data["gbanned"]
        is_gmuted = str(user_id) in data["gmuted"]
        
        msg = f"📊 **Global Status**\n\n👤 User: {user_name} (`{user_id}`)\n\n"
        
        if is_gbanned:
            msg += f"🔨 **Status:** Globally Banned\n📝 Reason: {data['gbanned'][str(user_id)]['reason']}\n"
        elif is_gmuted:
            msg += f"🔇 **Status:** Globally Muted\n📝 Reason: {data['gmuted'][str(user_id)]['reason']}\n"
        else:
            msg += "✅ **Status:** Clean (No restrictions)"
        
        await event.reply(msg)
