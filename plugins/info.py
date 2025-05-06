from telethon import events
from telethon.tl.types import (
    UserStatusRecently, UserStatusOnline, UserStatusOffline, 
    UserStatusLastWeek, UserStatusLastMonth, Channel, Chat
)
from telethon.tl.functions.users import GetFullUserRequest
from datetime import datetime, timedelta
import html
import os

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".info <username/userid/reply> - Detailed user profile"
    ]
    description = "Advanced user information retrieval"
    add_handler("info", commands, description)

def format_account_age(creation_date):
    now = datetime.now(creation_date.tzinfo)
    age = now - creation_date
    years = age.days // 365
    months = (age.days % 365) // 30
    days = (age.days % 365) % 30
    
    age_str = []
    if years > 0:
        age_str.append(f"{years} year{'s' if years > 1 else ''}")
    if months > 0:
        age_str.append(f"{months} month{'s' if months > 1 else ''}")
    if days > 0:
        age_str.append(f"{days} day{'s' if days > 1 else ''}")
    
    return ", ".join(age_str) if age_str else "Just created"

def format_online_status(user):
    status_icons = {
        UserStatusOnline: "🟢 Online Now",
        UserStatusRecently: "🟡 Recently Online",
        UserStatusLastWeek: "🟠 Active This Week",
        UserStatusLastMonth: "🔴 Active This Month",
        UserStatusOffline: "⚫ Offline"
    }
    
    try:
        status_type = type(user.status)
        base_status = status_icons.get(status_type, "❓ Unknown Status")
        
        if hasattr(user.status, 'was_online') and user.status.was_online:
            last_seen = user.status.was_online
            time_diff = datetime.now(last_seen.tzinfo) - last_seen
            
            if time_diff <= timedelta(minutes=5):
                return "🟢 Online Now"
            elif time_diff <= timedelta(hours=1):
                return f"🟡 Last seen {time_diff.seconds // 60} min ago"
            elif time_diff <= timedelta(days=1):
                return f"🟠 Last seen {time_diff.seconds // 3600} hrs ago"
            else:
                return base_status
        
        return base_status
    except Exception:
        return "❓ Status Unavailable"

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.(?:whois|info)"))
    @rishabh()
    async def whois_command(event):
        try:
            # Determine user
            if event.reply_to_msg_id:
                reply = await event.get_reply_message()
                user = await event.client.get_entity(reply.sender_id)
            else:
                user_input = event.text.split(maxsplit=1)
                user = await event.client.get_entity(user_input[1]) if len(user_input) > 1 else None

            if not user:
                return await event.reply("❌ Please provide a username, user ID, or reply to a message!")

            # Fetch full user information
            full_user = await event.client(GetFullUserRequest(user.id))
            
            # Gather basic details
            first_name = html.escape(user.first_name or "")
            last_name = html.escape(user.last_name or "")
            username = user.username or "None"
            user_id = user.id
            
            # Profile pictures
            profile_pics = await event.client.get_profile_photos(user)
            pic_count = len(profile_pics)
            
            # Mutual groups
            try:
                common_chats = await event.client.get_common_chats(user_id)
                mutual_groups = len(common_chats)
            except Exception:
                mutual_groups = "N/A"
            
            # Advanced information gathering
            info_message = "📋 <b>🔬 Advanced User Profile</b> 🔍\n\n"
            
            # Identity Section
            info_message += "👤 <b>Identity</b>\n"
            info_message += f"• 📛 <b>Full Name:</b> {first_name} {last_name}\n"
            info_message += f"• 🔤 <b>Username:</b> @{username}\n"
            info_message += f"• 🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
            
            # Account Details
            info_message += "🕰 <b>Account Details</b>\n"
            if hasattr(user, 'date') and user.date:
                info_message += f"• 📅 <b>Created:</b> {user.date.strftime('%Y-%m-%d %H:%M')}\n"
                info_message += f"• 🎂 <b>Account Age:</b> {format_account_age(user.date)}\n"
            
            # Status Information
            info_message += "📡 <b>Status</b>\n"
            info_message += f"• 🟢 <b>Online Status:</b> {format_online_status(user)}\n"
            
            # Profile Insights
            info_message += "🖼 <b>Profile Insights</b>\n"
            info_message += f"• 📸 <b>Profile Pictures:</b> {pic_count}\n"
            info_message += f"• 👥 <b>Mutual Groups:</b> {mutual_groups}\n"
            
            # Bio Section
            if hasattr(full_user, 'about') and full_user.about:
                info_message += "\n📝 <b>Bio</b>\n"
                info_message += f"• {html.escape(full_user.about)}\n"
            
            # Additional Checks (if possible)
            info_message += "\n🔒 <b>Privacy Check</b>\n"
            info_message += f"• 🤖 <b>Is Bot:</b> {'Yes' if user.bot else 'No'}\n"
            info_message += f"• 🔐 <b>Verified Account:</b> {'Yes' if user.verified else 'No'}\n"
            
            # Optional Profile Picture
            try:
                if profile_pics:
                    # Send first profile picture along with info
                    await event.client.send_file(
                        event.chat_id, 
                        profile_pics[0], 
                        caption=info_message, 
                        parse_mode='html'
                    )
                else:
                    await event.reply(info_message, parse_mode='html')
            except Exception:
                await event.reply(info_message, parse_mode='html')

        except Exception as e:
            await event.reply(f"❌ Error retrieving user info: {str(e)}")

    # Alias for .info
    @CipherElite.on(events.NewMessage(pattern=r"\.info"))
    async def info_command(event):
        await whois_command(event)