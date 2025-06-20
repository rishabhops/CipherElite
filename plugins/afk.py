# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    afk
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
#
#  IMPORTANT:
#    • If you copy, fork or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • Give proper credit back to the CipherElite Userbot author:
#        – GitHub: https://github.com/rishabhops/CipherElite
#        – Telegram: @rishabhops
#
#  Thank you for respecting open‐source software!
# =============================================================================

import os
import random
import time
import asyncio
from datetime import datetime, timedelta
from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaGif
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler


afk_users = {}
afk_mentions = {}
afk_stats = {}

# quotes maked by hellbot team we use concept 
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
            if hasattr(media_msg.media, 'photo'):
                return {'type': 'photo', 'media': media_msg.media}
            elif hasattr(media_msg.media, 'document'):
                doc = media_msg.media.document
                if doc.mime_type.startswith('image/gif') or 'gif' in doc.mime_type:
                    return {'type': 'gif', 'media': media_msg.media}
                elif doc.mime_type.startswith('video/'):
                    return {'type': 'video', 'media': media_msg.media}
                elif doc.mime_type.startswith('audio/'):
                    return {'type': 'audio', 'media': media_msg.media}
                else:
                    return {'type': 'document', 'media': media_msg.media}
        return None
    except Exception as e:
        print(f"Error saving media: {e}")
        return None

async def register_commands():
    """Register all AFK-related commands"""
    
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
    
    # AFK Mention Watcher
    @CipherElite.on(events.NewMessage(incoming=True))
    async def afk_mention_watcher(event):
        """Watch for mentions of AFK users"""
        try:
            # Skip if sender is a bot
            if event.sender_id in afk_users:
                return
            
            # Check if any AFK user is mentioned
            for afk_user_id, afk_data in afk_users.items():
                try:
                    # Get AFK user entity
                    afk_user = await event.client.get_entity(afk_user_id)
                    
                    # Check if mentioned in text or replied to
                    mentioned = False
                    if event.is_reply:
                        reply_msg = await event.get_reply_message()
                        if reply_msg and reply_msg.sender_id == afk_user_id:
                            mentioned = True
                    
                    # Check for username/name mentions in text
                    if event.text and afk_user.username:
                        if f"@{afk_user.username}" in event.text.lower():
                            mentioned = True
                    
                    if mentioned:
                        # Add to mentions list
                        afk_mentions[afk_user_id].append({
                            'from_user': event.sender_id,
                            'chat_id': event.chat_id,
                            'time': time.time(),
                            'message': event.text[:100] + "..." if len(event.text) > 100 else event.text
                        })
                        
                        # Calculate AFK duration
                        afk_duration = int(time.time() - afk_data['time'])
                        
                        # Prepare response
                        quote = random.choice(afk_quotes)
                        response = f"**{quote}**\n\n"
                        response += f"💫 **Reason:** `{afk_data['reason']}`\n"
                        response += f"⏰ **AFK Since:** `{readable_time(afk_duration)}`\n"
                        response += f"🔔 **Mentions:** `{len(afk_mentions[afk_user_id])}`"
                        
                        # Send response with media if available
                        if afk_data['media']:
                            media_info = afk_data['media']
                            if media_info['type'] == 'photo':
                                await event.reply(response, file=media_info['media'])
                            elif media_info['type'] in ['gif', 'video', 'audio', 'document']:
                                await event.reply(response, file=media_info['media'])
                            else:
                                await event.reply(response)
                        else:
                            await event.reply(response)
                        
                        break
                        
                except Exception as e:
                    print(f"Error in mention watcher: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in AFK watcher: {e}")
    
    # AFK Auto-removal watcher
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
