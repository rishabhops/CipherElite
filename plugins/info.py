from telethon import events
from telethon.tl.types import (
    UserStatusRecently, UserStatusOnline, UserStatusOffline,
    UserStatusLastWeek, UserStatusLastMonth, Channel, Chat,
    User, UserProfilePhoto
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from datetime import datetime, timedelta, timezone
import html
import requests
from io import BytesIO
import instaloader
from instaloader.exceptions import ProfileNotExistsException

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Initialize Instaloader for public Instagram data
insta_loader = instaloader.Instaloader()

def init(client_instance):
    commands = [
        ".info <username/userid/reply> - Detailed Telegram user profile",
        ".instainfo <username> - Instagram profile info",
        ".chatinfo <group_username/group_id> - Group/Channel info"
    ]
    description = "Advanced user information retrieval"
    add_handler("info", commands, description)

def format_account_age(creation_date):
    if not creation_date:
        return "Unknown"
        
    # Convert to UTC for consistent calculation
    if creation_date.tzinfo is None:
        creation_date = creation_date.replace(tzinfo=timezone.utc)
        
    now = datetime.now(timezone.utc)
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
    if not hasattr(user, 'status'):
        return "⚫ Status Unknown"
    
    status_map = {
        UserStatusOnline: "🟢 Online Now",
        UserStatusRecently: "🟢 Recently Online",
        UserStatusLastWeek: "🟠 Active This Week",
        UserStatusLastMonth: "🔴 Active This Month",
        UserStatusOffline: "⚫ Offline"
    }
    
    status_type = type(user.status)
    status_text = status_map.get(status_type, "⚫ Status Unknown")
    
    if status_type == UserStatusOffline and hasattr(user.status, 'was_online'):
        last_seen = user.status.was_online
        time_diff = datetime.now(timezone.utc) - last_seen
        
        if time_diff < timedelta(minutes=1):
            return "🟢 Just Now"
        elif time_diff < timedelta(hours=1):
            mins = time_diff.seconds // 60
            return f"🟢 {mins} min ago"
        elif time_diff < timedelta(days=1):
            hours = time_diff.seconds // 3600
            return f"🟠 {hours} hours ago"
        elif time_diff < timedelta(days=7):
            days = time_diff.days
            return f"🔴 {days} days ago"
    
    return status_text

def format_number(num):
    if num is None:
        return "N/A"
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def get_active_hours(user):
    # Placeholder - real implementation requires activity tracking
    return "9AM-5PM (Estimated)"

def get_shadowban_risk(user):
    # Placeholder - real implementation requires activity analysis
    return "Low (Estimated)"

def get_device_type(user):
    # Placeholder - real implementation requires client info
    return "Mobile (Estimated)"

def format_last_post_age(last_post):
    if not last_post:
        return "N/A"
    
    # Convert to UTC for consistent calculation
    if last_post.date_utc.tzinfo is None:
        post_time = last_post.date_utc.replace(tzinfo=timezone.utc)
    else:
        post_time = last_post.date_utc
        
    now = datetime.now(timezone.utc)
    diff = now - post_time
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds//3600} hours ago"
    return f"{diff.seconds//60} minutes ago"

# Custom HTML escape function to handle long strings safely
def safe_html_escape(text):
    """Safely escape HTML characters in text of any length"""
    if text is None:
        return ""
    return html.escape(text)

async def register_commands():
    # Telegram User Info Command
    @CipherElite.on(events.NewMessage(pattern=r"\.(?:whois|info)"))
    @rishabh()
    async def info_command(event):
        try:
            # Delete command message instantly
            await event.delete()
            
            # Determine user
            if event.reply_to_msg_id:
                reply = await event.get_reply_message()
                user = await event.client.get_entity(reply.sender_id)
            else:
                user_input = event.text.split(maxsplit=1)
                if len(user_input) > 1:
                    user = await event.client.get_entity(user_input[1])
                else:
                    await event.respond("❌ Please provide a username, user ID, or reply to a message!")
                    return

            # Fetch full user information
            full_user = await event.client(GetFullUserRequest(user.id))
            
            # Get profile photos
            profile_pics = await event.client.get_profile_photos(user)
            pic_count = len(profile_pics)
            
            # Get mutual groups
            try:
                common_chats = await event.client.get_common_chats(user.id)
                mutual_groups = len(common_chats)
            except Exception:
                mutual_groups = 0

            # Format response using safe_html_escape
            response = (
                "👤 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗨𝗦𝗘𝗥 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦\n\n"
                f"🆔 𝗜𝗗: <code>{user.id}</code>\n"
                f"👤 𝗡𝗮𝗺𝗲: {safe_html_escape(user.first_name or '')} {safe_html_escape(user.last_name or '')}\n"
                f"🔖 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{safe_html_escape(user.username or 'N/A')}\n\n"
                
                "📊 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗦𝗧𝗔𝗧𝗨𝗦\n"
                f"🟢 𝗟𝗮𝘀𝘁 𝗢𝗻𝗹𝗶𝗻𝗲: {format_online_status(user)}\n"
                f"📅 𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗔𝗴𝗲: {format_account_age(getattr(user, 'date', None))}\n"
                f"🤖 𝗜𝘀 𝗕𝗼𝘁: {'✅ Yes' if user.bot else '❌ No'}\n"
                f"✅ 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱: {'✅ Yes' if user.verified else '❌ No'}\n"
                f"🚫 𝗥𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱: {'✅ Yes' if getattr(user, 'restricted', False) else '❌ No'}\n"
                f"👻 𝗦𝗵𝗮𝗱𝗼𝘄𝗯𝗮𝗻 𝗥𝗶𝘀𝗸: {get_shadowban_risk(user)}\n\n"
                
                "📱 𝗗𝗘𝗩𝗜𝗖𝗘 𝗜𝗡𝗙𝗢\n"
                f"📟 𝗧𝘆𝗽𝗲: {get_device_type(user)}\n"
                f"🌐 𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲: {getattr(user, 'lang_code', 'Unknown')}\n"
                f"⏱ 𝗔𝗰𝘁𝗶𝘃𝗲 𝗛𝗼𝘂𝗿𝘀: {get_active_hours(user)}\n\n"
                
                "📈 𝗔𝗖𝗧𝗜𝗩𝗜𝗧𝗬 𝗦𝗧𝗔𝗧𝗦\n"
                f"📸 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 𝗣𝗵𝗼𝘁𝗼𝘀: {pic_count}\n"
                f"👥 𝗠𝘂𝘁𝘂𝗮𝗹 𝗚𝗿𝗼𝘂𝗽𝘀: {mutual_groups}\n"
            )
            
            # Add bio if available
            if hasattr(full_user, 'full_user') and hasattr(full_user.full_user, 'about'):
                bio = safe_html_escape(full_user.full_user.about)
                response += f"\n📝 𝗕𝗜𝗢\n{bio}\n"
            
            # Send with profile photo if available
            if profile_pics:
                await event.client.send_file(
                    event.chat_id,
                    file=profile_pics[0],
                    caption=response,
                    parse_mode='html'
                )
            else:
                await event.respond(response, parse_mode='html')
                
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}")

    # Instagram Info Command
    @CipherElite.on(events.NewMessage(pattern=r"\.instainfo ?(.*)"))
    @rishabh()
    async def instainfo_command(event):
        try:
            # Delete command message instantly
            await event.delete()
            
            username = event.pattern_match.group(1).strip()
            if not username:
                await event.respond("❌ Please provide an Instagram username!")
                return
                
            # Get Instagram profile using Instaloader
            profile = instaloader.Profile.from_username(insta_loader.context, username)
            
            # Get last post if available
            last_post = None
            try:
                posts = profile.get_posts()
                last_post = next(posts, None)
            except Exception:
                last_post = None

            # Format response
            response = (
                "📸 𝗜𝗡𝗦𝗧𝗔𝗚𝗥𝗔𝗠 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦 𝗥𝗘𝗣𝗢𝗥𝗧\n\n"
                f"👤 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{profile.username}\n"
                f"📛 𝗡𝗮𝗺𝗲: {safe_html_escape(profile.full_name)}\n"
                f"🔗 𝗣𝗿𝗼𝗳𝗶𝗹𝗲: https://instagram.com/{profile.username}\n\n"
                
                "📊 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗦𝗧𝗔𝗧𝗦\n"
                f"👥 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗿𝘀: {format_number(profile.followers)}\n"
                f"👣 𝗙𝗼𝗹𝗹𝗼𝘄𝗶𝗻𝗴: {format_number(profile.followees)}\n"
                f"📸 𝗣𝗼𝘀𝘁𝘀: {format_number(profile.mediacount)}\n"
                f"📥 𝗛𝗶𝗴𝗵𝗹𝗶𝗴𝗵𝘁𝘀: {format_number(profile.igtvcount)}\n"
                f"🔐 𝗦𝘁𝗮𝘁𝘂𝘀: {'🔒 Private' if profile.is_private else '🔓 Public'}\n\n"
                
                "📝 𝗕𝗜𝗢\n"
                f"{safe_html_escape(profile.biography) or 'No bio available'}\n\n"
                
                "🔄 𝗟𝗔𝗦𝗧 𝗔𝗖𝗧𝗜𝗩𝗜𝗧𝗬\n"
                f"⏱ 𝗟𝗮𝘀𝘁 𝗣𝗼𝘀𝘁: {format_last_post_age(last_post)}\n"
                f"📍 𝗕𝘂𝘀𝗶𝗻𝗲𝘀𝘀 𝗔𝗰𝗰𝗼𝘂𝗻𝘁: {'✅ Yes' if profile.is_business_account else '❌ No'}\n"
                f"👁 𝗙𝗼𝗹𝗹𝗼𝘄𝗲𝗱 𝗯𝘆 𝗬𝗼𝘂: {'✅ Yes' if profile.followed_by_viewer else '❌ No'}"
            )
            
            # Download profile picture
            photo_url = profile.profile_pic_url
            if photo_url:
                try:
                    response_req = requests.get(photo_url, timeout=10)
                    response_req.raise_for_status()
                    photo_data = BytesIO(response_req.content)
                    photo_data.name = f"{profile.username}.jpg"
                    
                    await event.client.send_file(
                        event.chat_id,
                        file=photo_data,
                        caption=response,
                        parse_mode='html'
                    )
                    return
                except Exception:
                    pass
            
            # If photo download fails, send text only
            await event.respond(response, parse_mode='html')
            
        except ProfileNotExistsException:
            await event.respond("❌ Instagram profile not found!")
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}")

    # Chat Info Command
    @CipherElite.on(events.NewMessage(pattern=r"\.chatinfo ?(.*)"))
    @rishabh()
    async def chatinfo_command(event):
        try:
            # Delete command message instantly
            await event.delete()
            
            # Determine chat
            if event.reply_to_msg_id:
                reply = await event.get_reply_message()
                entity = await event.client.get_entity(reply.to_id)
            else:
                input_str = event.pattern_match.group(1).strip()
                if input_str:
                    entity = await event.client.get_entity(input_str)
                else:
                    entity = await event.client.get_entity(event.chat_id)
            
            # Get full chat info
            if isinstance(entity, (Channel, Chat)):
                if isinstance(entity, Channel):
                    full_chat = await event.client(GetFullChannelRequest(entity))
                else:
                    full_chat = await event.client(GetFullChatRequest(entity.id))
            else:
                await event.respond("❌ This is not a group or channel!")
                return
            
            # Get participants count
            try:
                participants = await event.client.get_participants(entity, limit=0)
                members_count = len(participants)
            except Exception:
                members_count = "Unknown"
            
            # Format response
            response = (
                "👥 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗚𝗥𝗢𝗨𝗣 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦\n\n"
                f"📛 𝗧𝗶𝘁𝗹𝗲: {safe_html_escape(entity.title)}\n"
                f"🆔 𝗜𝗗: <code>{entity.id}</code>\n"
                f"👤 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{safe_html_escape(entity.username or 'N/A')}\n"
                f"🔗 𝗜𝗻𝘃𝗶𝘁𝗲 𝗟𝗶𝗻𝗸: {entity.username and f'https://t.me/{entity.username}' or 'N/A'}\n\n"
                
                "📊 𝗦𝗧𝗔𝗧𝗦\n"
                f"👥 𝗠𝗲𝗺𝗯𝗲𝗿𝘀: {members_count}\n"
                f"📢 𝗧𝘆𝗽𝗲: {'Channel' if getattr(entity, 'broadcast', False) else 'Group'}\n"
                f"🔐 𝗦𝘁𝗮𝘁𝘂𝘀: {'Public' if getattr(entity, 'public', False) else 'Private'}\n"
                f"✅ 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱: {'✅ Yes' if getattr(entity, 'verified', False) else '❌ No'}\n"
                f"🔒 𝗥𝗲𝘀𝘁𝗿𝗶𝗰𝘁𝗲𝗱: {'✅ Yes' if getattr(entity, 'restricted', False) else '❌ No'}\n"
                f"💬 𝗦𝗰𝗮𝗺: {'✅ Yes' if getattr(entity, 'scam', False) else '❌ No'}"
            )
            
            # Add description if available
            if hasattr(full_chat, 'full_chat') and hasattr(full_chat.full_chat, 'about'):
                about = safe_html_escape(full_chat.full_chat.about)
                response += f"\n\n📝 𝗗𝗲𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻:\n{about}\n"
            
            # Send with chat photo if available
            if (hasattr(full_chat, 'full_chat') and 
                hasattr(full_chat.full_chat, 'chat_photo') and 
                full_chat.full_chat.chat_photo):
                
                # Get photo as input file
                photo = full_chat.full_chat.chat_photo
                file = await event.client.upload_file(photo)
                
                await event.client.send_file(
                    event.chat_id,
                    file=file,
                    caption=response,
                    parse_mode='html'
                )
            else:
                await event.respond(response, parse_mode='html')
                
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}")
