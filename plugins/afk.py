# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    afk
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
import random
import time
import asyncio
from datetime import datetime, timedelta
from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageEntityMention, MessageEntityMentionName
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

afk_users = {}
afk_mentions = {}
afk_stats = {}

# Quotes made by Hellbot team, improved with emojis
afk_quotes = [
    "🚶‍♂️ Taking a break, be back soon!",
    "⏳ AFK - Away From the Keyboard momentarily.",
    "🔜 Stepped away, but I'll return shortly.",
    "👋 Gone for a moment, not forgotten.",
    "🌿 Taking a breather, back in a bit.",
    "📵 Away for a while, feel free to leave a message!",
    "⏰ On a short break, back shortly.",
    "🌈 Away from the screen, catching a breath.",
    "💤 Offline for a moment, but still here in spirit.",
    "🚀 Exploring the real world, back in a moment!",
    "🍵 Taking a tea break, back shortly!",
    "🌙 Resting my keyboard, back after a short nap.",
    "🚶‍♀️ Stepping away for a moment of peace.",
    "🎵 AFK but humming along, back shortly!",
    "🌞 Taking a sunshine break, back soon!",
    "🌊 Away, catching some waves of relaxation.",
    "🚪 Temporarily closed, be back in a bit!",
    "🌸 Taking a moment to smell the digital roses.",
    "🍃 Stepped into the real world for a while.",
    "🎮 Leveling up in the real world, back soon!",
    "📚 Reading some offline content, brb!",
    "🏃‍♂️ Running some errands, back in a flash!",
    "🍕 Gone for a quick bite, back shortly!",
    "🛀 Refreshing myself, back in a moment!"
]

def init(client_instance):
    """Initialize the AFK plugin"""
    commands = [
        ".afk [reason] - Set yourself as AFK with optional reason",
        ".afkstats - View your AFK statistics",
        ".unafk - Manually remove AFK status",
        ".afkquote - Get a random AFK quote",
        ".afkhelp - Show detailed AFK help"
    ]
    description = "Advanced AFK (Away From Keyboard) system with media support, statistics, and auto-responses"
    add_handler("afk", commands, description)

def readable_time(seconds):
    """Convert seconds to human readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''}"

async def save_media(event, media_msg):
    """Save media file and return file info"""
    try:
        if media_msg.media:
            if isinstance(media_msg.media, MessageMediaPhoto):
                return {'type': 'photo', 'media': media_msg.media}
            elif isinstance(media_msg.media, MessageMediaDocument):
                doc = media_msg.media.document
                if doc.mime_type and 'gif' in doc.mime_type:
                    return {'type': 'gif', 'media': media_msg.media}
                elif doc.mime_type and doc.mime_type.startswith('video/'):
                    return {'type': 'video', 'media': media_msg.media}
                elif doc.mime_type and doc.mime_type.startswith('audio/'):
                    return {'type': 'audio', 'media': media_msg.media}
                else:
                    return {'type': 'document', 'media': media_msg.media}
        return None
    except Exception as e:
        print(f"Error saving media: {e}")
        return None

@CipherElite.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?"))
@rishabh()
async def afk_handler(event):
    """Set AFK status"""
    try:
        user_id = event.sender_id
        
        # Check if already AFK
        if user_id in afk_users:
            await event.reply("🙄 **You're already AFK!** Use `.unafk` to remove AFK status.")
            return
        
        # Get reason from command
        reason = event.pattern_match.group(1) if event.pattern_match.group(1) else "Not specified"
        
        # Check for replied media
        media_info = None
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            media_info = await save_media(event, reply_msg)
        
        # Set AFK status
        afk_time = time.time()
        afk_users[user_id] = {
            'reason': reason,
            'time': afk_time,
            'media': media_info,
            'chat_id': event.chat_id
        }
        
        # Initialize mentions counter
        if user_id not in afk_mentions:
            afk_mentions[user_id] = []
        
        # Update stats
        if user_id not in afk_stats:
            afk_stats[user_id] = {'total_times': 0, 'total_duration': 0}
        afk_stats[user_id]['total_times'] += 1
        
        # Send confirmation
        await event.reply(f"🫡 **Going AFK!** \n\n**📝 Reason:** `{reason}`\n**⏰ Time:** `{datetime.now().strftime('%H:%M:%S')}`\n\n*I'll notify you when someone mentions you!*")
        
    except Exception as e:
        await event.reply(f"❌ **Error setting AFK:** `{str(e)}`")

@CipherElite.on(events.NewMessage(pattern=r"\.unafk"))
@rishabh()
async def unafk_handler(event):
    """Manually remove AFK status"""
    try:
        user_id = event.sender_id
        
        if user_id not in afk_users:
            await event.reply("🤷‍♂️ **You're not AFK!**")
            return
        
        # Calculate AFK duration
        afk_data = afk_users[user_id]
        duration = int(time.time() - afk_data['time'])
        
        # Update stats
        afk_stats[user_id]['total_duration'] += duration
        
        # Remove AFK status
        del afk_users[user_id]
        
        # Show mentions count
        mentions_count = len(afk_mentions.get(user_id, []))
        if mentions_count > 0:
            afk_mentions[user_id] = []  # Clear mentions
        
        await event.reply(f"🫡 **Welcome back!** \n\n**⌚ AFK Duration:** `{readable_time(duration)}`\n**💬 Mentions received:** `{mentions_count}`")
        
    except Exception as e:
        await event.reply(f"❌ **Error removing AFK:** `{str(e)}`")

@CipherElite.on(events.NewMessage(pattern=r"\.afkstats"))
@rishabh()
async def afkstats_handler(event):
    """Show AFK statistics"""
    try:
        user_id = event.sender_id
        
        if user_id not in afk_stats:
            await event.reply("📊 **No AFK statistics found!** \n\nYou haven't used AFK yet.")
            return
        
        stats = afk_stats[user_id]
        current_afk = afk_users.get(user_id)
        
        stats_text = f"📊 **Your AFK Statistics**\n\n"
        stats_text += f"🔢 **Total AFK sessions:** `{stats['total_times']}`\n"
        stats_text += f"⏱️ **Total AFK time:** `{readable_time(stats['total_duration'])}`\n"
        
        if current_afk:
            current_duration = int(time.time() - current_afk['time'])
            stats_text += f"🟢 **Currently AFK:** `Yes`\n"
            stats_text += f"⏰ **Current session:** `{readable_time(current_duration)}`\n"
            stats_text += f"📝 **Current reason:** `{current_afk['reason']}`"
        else:
            stats_text += f"🔴 **Currently AFK:** `No`"
        
        await event.reply(stats_text)
        
    except Exception as e:
        await event.reply(f"❌ **Error getting stats:** `{str(e)}`")

@CipherElite.on(events.NewMessage(pattern=r"\.afkquote"))
@rishabh()
async def afkquote_handler(event):
    """Get a random AFK quote"""
    try:
        quote = random.choice(afk_quotes)
        await event.reply(f"💭 **Random AFK Quote:**\n\n{quote}")
    except Exception as e:
        await event.reply(f"❌ **Error getting quote:** `{str(e)}`")

@CipherElite.on(events.NewMessage(pattern=r"\.afkhelp"))
@rishabh()
async def afkhelp_handler(event):
    """Show detailed AFK help"""
    try:
        help_text = """🆘 **AFK Plugin Help**

**Commands:**
• `.afk [reason]` - Set AFK status with optional reason
• `.afkstats` - View your AFK statistics  
• `.unafk` - Manually remove AFK status
• `.afkquote` - Get a random AFK quote
• `.afkhelp` - Show this help message

**Features:**
• 🖼️ **Media Support** - Reply to any media while setting AFK
• 📊 **Statistics** - Track your AFK usage and duration
• 🔔 **Mention Tracking** - Get notified when mentioned while AFK
• 🎯 **Auto Return** - Automatically removes AFK when you send a message
• 🎨 **Random Quotes** - Beautiful random quotes when someone mentions you

**Usage Examples:**
• `.afk` - Set AFK without reason
• `.afk Taking a break` - Set AFK with reason
• `.afk` (reply to image) - Set AFK with image

**Tips:**
• AFK automatically removes when you send any message
• Include 'afk' in your message to avoid auto-removal
• Your AFK stats are saved and tracked over time"""
        await event.reply(help_text)
    except Exception as e:
        await event.reply(f"❌ **Error showing help:** `{str(e)}`")

@CipherElite.on(events.NewMessage(incoming=True))
async def afk_watcher(event):
    """AFK Auto-responder for private and group messages"""
    try:
        # Skip if sender is in AFK (don't respond to other AFK users)
        if event.sender_id in afk_users:
            return
            
        # Get the bot/userbot owner ID (the one who can be AFK)
        bot_owner_id = (await event.client.get_me()).id
        
        # Check if the bot owner is AFK
        if bot_owner_id not in afk_users:
            return
            
        afk_data = afk_users[bot_owner_id]
        should_respond = False
        
        # PRIVATE CHAT: Always respond if someone messages you privately
        if event.is_private:
            should_respond = True
            
        # GROUP CHAT: Respond if mentioned or replied to
        else:
            # Check if replied to your message
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                if reply_msg and reply_msg.sender_id == bot_owner_id:
                    should_respond = True
            
            # Check for username or mention
            if not should_respond and event.text:
                try:
                    me = await event.client.get_me()
                    # Check for username mention
                    if me.username and f"@{me.username}" in event.text.lower():
                        should_respond = True
                    # Check for entity mention (e.g., by name or ID)
                    if not should_respond and event.entities:
                        for entity in event.entities:
                            if isinstance(entity, (MessageEntityMention, MessageEntityMentionName)):
                                if isinstance(entity, MessageEntityMentionName) and entity.user_id == bot_owner_id:
                                    should_respond = True
                                elif isinstance(entity, MessageEntityMention):
                                    # Extract the mentioned text and check if it matches the username
                                    mention_text = event.text[entity.offset:entity.offset + entity.length]
                                    if me.username and mention_text.lower() == f"@{me.username.lower()}":
                                        should_respond = True
                except Exception as e:
                    print(f"Error checking mentions: {e}")
        
        if should_respond:
            # Add to mentions
            if bot_owner_id not in afk_mentions:
                afk_mentions[bot_owner_id] = []
                
            afk_mentions[bot_owner_id].append({
                'from_user': event.sender_id,
                'chat_id': event.chat_id,
                'time': time.time(),
                'message': event.text[:100] + "..." if event.text and len(event.text) > 100 else (event.text or "Media")
            })
            
            # Calculate AFK duration
            afk_duration = int(time.time() - afk_data['time'])
            
            # Get sender name
            try:
                sender = await event.get_sender()
                sender_name = getattr(sender, 'first_name', 'User') or 'User'
            except:
                sender_name = "Someone"
            
            # Create response
            quote = random.choice(afk_quotes)
            
            response = f"**{quote}**\n\n"
            response += f"💫 **Reason:** `{afk_data['reason']}`\n"
            response += f"⏰ **AFK Duration:** `{readable_time(afk_duration)}`\n"
            
            if event.is_private:
                response += f"📱 **Auto-reply to:** `{sender_name}`\n"
            else:
                response += f"👤 **Mentioned by:** `{sender_name}`\n"
                
            response += f"🔔 **Total interactions:** `{len(afk_mentions[bot_owner_id])}`"
            
            # Send response
            try:
                if afk_data.get('media'):
                    await event.reply(response, file=afk_data['media']['media'])
                else:
                    await event.reply(response)
                    
                print(f"✅ AFK response sent to {sender_name} ({'Private' if event.is_private else 'Group'})")
                
            except Exception as e:
                print(f"❌ Error sending AFK response: {e}")
                
    except Exception as e:
        print(f"❌ Error in AFK watcher: {e}")

@CipherElite.on(events.NewMessage(outgoing=True))
async def afk_auto_remove(event):
    """Automatically remove AFK when user sends a message"""
    try:
        user_id = event.sender_id
        
        if user_id in afk_users:
            # Don't remove if message contains 'afk'
            if event.text and 'afk' in event.text.lower():
                return
            
            # Calculate duration
            afk_data = afk_users[user_id]
            duration = int(time.time() - afk_data['time'])
            
            # Update stats
            afk_stats[user_id]['total_duration'] += duration
            
            # Get mentions count
            mentions_count = len(afk_mentions.get(user_id, []))
            
            # Remove AFK status
            del afk_users[user_id]
            
            # Clear mentions
            if user_id in afk_mentions:
                afk_mentions[user_id] = []
            
            # Send welcome back message
            welcome_msg = f"🫡 **Welcome back to the virtual world!**\n\n"
            welcome_msg += f"⌚ **AFK Duration:** `{readable_time(duration)}`\n"
            welcome_msg += f"💬 **Mentions received:** `{mentions_count}`"
            
            try:
                await event.reply(welcome_msg)
                # Delete the welcome message after 10 seconds
                await asyncio.sleep(10)
                await event.client.delete_messages(event.chat_id, event.id + 1)
            except:
                pass
        
    except Exception as e:
        print(f"Error in auto-remove: {e}")
