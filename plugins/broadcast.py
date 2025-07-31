# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    broadcast
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


import asyncio
from telethon import events
from telethon.tl.types import User, Chat, Channel
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    """
    Required initialization function that registers commands and descriptions
    """
    commands = [
        ".gcast <target> [copy] - Broadcast message to all chats/groups/users with Cipher Elite engine"
    ]
    description = "📡 Cipher Elite Broadcast System - Advanced message broadcasting with intelligent targeting"
    add_handler("broadcast", commands, description)  # Short, professional button name

async def register_commands():
    """
    Cipher Elite broadcast system with advanced targeting
    """
    
    class CipherEliteBroadcastEngine:
        def __init__(self):
            self.broadcast_stats = {
                'sent': 0,
                'failed': 0,
                'total': 0
            }
            
        async def get_target_chats(self, client, target_type):
            """Get list of target chats based on type"""
            target_chats = []
            
            async for dialog in client.iter_dialogs():
                entity = dialog.entity
                
                if target_type == "all":
                    target_chats.append(entity)
                elif target_type == "groups":
                    if isinstance(entity, (Chat, Channel)) and not entity.broadcast:
                        target_chats.append(entity)
                elif target_type == "users":
                    if isinstance(entity, User) and not entity.bot:
                        target_chats.append(entity)
            
            return target_chats
        
        async def broadcast_message(self, client, message, target_chats, use_forward=True, status_msg=None):
            """Broadcast message to target chats"""
            self.broadcast_stats = {'sent': 0, 'failed': 0, 'total': len(target_chats)}
            
            for i, chat in enumerate(target_chats):
                try:
                    if use_forward:
                        # Forward the message with tag
                        await client.forward_messages(chat, message)
                    else:
                        # Copy the message content without forward tag
                        if message.text:
                            await client.send_message(chat, message.text)
                        elif message.media:
                            await client.send_file(chat, message.media, caption=message.caption or "")
                    
                    self.broadcast_stats['sent'] += 1
                    
                    # Update status every 10 messages
                    if status_msg and (i + 1) % 10 == 0:
                        progress_percent = int((i + 1) / len(target_chats) * 100)
                        await status_msg.edit(
                            f"🎭 **Cipher Elite Broadcasting**\n\n"
                            f"📡 **Progress:** {progress_percent}%\n"
                            f"✅ **Sent:** {self.broadcast_stats['sent']}\n"
                            f"❌ **Failed:** {self.broadcast_stats['failed']}\n"
                            f"📊 **Total:** {self.broadcast_stats['total']}\n"
                            f"⚡ **Status:** Broadcasting in progress..."
                        )
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.broadcast_stats['failed'] += 1
                    continue
            
            return self.broadcast_stats
    
    # Initialize broadcast engine
    broadcast_engine = CipherEliteBroadcastEngine()
    
    @CipherElite.on(events.NewMessage(pattern=r"\.gcast\s+(.+)"))
    @rishabh()
    async def cipher_elite_broadcast(event):
        try:
            if not event.reply_to_msg_id:
                await event.reply("🎭 **Cipher Elite Broadcast System**\n\n"
                                "❌ **Error:** Please reply to a message to broadcast!\n\n"
                                "**Usage:**\n"
                                "• `.gcast all` - Broadcast to all chats\n"
                                "• `.gcast groups` - Broadcast to groups only\n"
                                "• `.gcast users` - Broadcast to users only\n"
                                "• `.gcast all copy` - Copy without forward tag\n\n"
                                "🤖 **Powered by Cipher Elite**")
                return
            
            # Parse command arguments
            args = event.pattern_match.group(1).split()
            
            if not args:
                await event.reply("❌ **Cipher Elite Error:** Please specify target (all/groups/users)")
                return
            
            target_type = args[0].lower()
            
            if target_type not in ["all", "groups", "users"]:
                await event.reply("🎭 **Cipher Elite Broadcast Error**\n\n"
                                "❌ **Invalid target type!**\n\n"
                                "**Valid targets:**\n"
                                "• `all` - All chats\n"
                                "• `groups` - Groups only\n"
                                "• `users` - Users only\n\n"
                                "**Example:** `.gcast groups copy`")
                return
            
            # Check if copy mode is specified
            use_forward = True
            if len(args) > 1 and args[1].lower() == "copy":
                use_forward = False
            
            # Get replied message
            reply_message = await event.get_reply_message()
            
            if not reply_message:
                await event.reply("❌ **Cipher Elite Error:** Could not get replied message!")
                return
            
            # Initial status message
            status_msg = await event.reply("🎭 **Cipher Elite Broadcast System**\n\n"
                                         f"🎯 **Target:** {target_type.title()}\n"
                                         f"📋 **Mode:** {'Copy' if not use_forward else 'Forward'}\n"
                                         f"🔄 **Status:** Analyzing target chats...\n"
                                         f"⚡ **Engine:** Advanced Broadcasting Algorithm")
            
            # Get target chats
            target_chats = await broadcast_engine.get_target_chats(event.client, target_type)
            
            if not target_chats:
                await status_msg.edit("🎭 **Cipher Elite Broadcast Result**\n\n"
                                     f"❌ **No target chats found for type:** {target_type}\n"
                                     f"💡 **Make sure you have chats of this type**")
                return
            
            await status_msg.edit(f"🎭 **Cipher Elite Broadcasting**\n\n"
                                 f"🎯 **Target:** {target_type.title()}\n"
                                 f"📊 **Found:** {len(target_chats)} chats\n"
                                 f"📋 **Mode:** {'Copy' if not use_forward else 'Forward'}\n"
                                 f"🚀 **Starting broadcast...**\n"
                                 f"⚡ **Status:** Initializing...")
            
            # Start broadcasting
            stats = await broadcast_engine.broadcast_message(
                event.client, 
                reply_message, 
                target_chats, 
                use_forward, 
                status_msg
            )
            
            # Final results
            success_rate = int((stats['sent'] / stats['total']) * 100) if stats['total'] > 0 else 0
            
            result_msg = f"🎭 **Cipher Elite Broadcast Complete**\n\n"
            result_msg += f"📊 **Broadcast Statistics:**\n"
            result_msg += f"✅ **Successfully sent:** {stats['sent']}\n"
            result_msg += f"❌ **Failed:** {stats['failed']}\n"
            result_msg += f"📈 **Success rate:** {success_rate}%\n"
            result_msg += f"🎯 **Total targets:** {stats['total']}\n\n"
            result_msg += f"📋 **Target type:** {target_type.title()}\n"
            result_msg += f"🔧 **Mode:** {'Copy' if not use_forward else 'Forward'}\n\n"
            
            if success_rate >= 90:
                result_msg += f"🔥 **Status:** Excellent broadcast performance!\n"
            elif success_rate >= 70:
                result_msg += f"✅ **Status:** Good broadcast performance\n"
            elif success_rate >= 50:
                result_msg += f"⚠️ **Status:** Average broadcast performance\n"
            else:
                result_msg += f"❌ **Status:** Poor broadcast performance\n"
            
            result_msg += f"🤖 **Powered by Cipher Elite**"
            
            await status_msg.edit(result_msg)
            
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite Broadcast System Error**\n\n"
                            f"❌ **Critical Error:** {str(e)[:100]}...\n"
                            f"💡 **Suggestion:** Try again with valid parameters\n"
                            f"🔧 **Support:** Check your permissions and network")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.bstats"))
    @rishabh()
    async def broadcast_stats(event):
        try:
            # Get chat statistics
            total_chats = 0
            groups_count = 0
            users_count = 0
            channels_count = 0
            
            async for dialog in event.client.iter_dialogs():
                entity = dialog.entity
                total_chats += 1
                
                if isinstance(entity, User) and not entity.bot:
                    users_count += 1
                elif isinstance(entity, Chat):
                    groups_count += 1
                elif isinstance(entity, Channel):
                    if entity.broadcast:
                        channels_count += 1
                    else:
                        groups_count += 1
            
            stats_msg = f"🎭 **Cipher Elite Broadcast Statistics**\n\n"
            stats_msg += f"📊 **Your Chat Distribution:**\n"
            stats_msg += f"👥 **Total chats:** {total_chats}\n"
            stats_msg += f"👤 **Users:** {users_count}\n"
            stats_msg += f"👥 **Groups:** {groups_count}\n"
            stats_msg += f"📢 **Channels:** {channels_count}\n\n"
            stats_msg += f"🎯 **Broadcast Targets:**\n"
            stats_msg += f"• `all` → {total_chats} chats\n"
            stats_msg += f"• `users` → {users_count} users\n"
            stats_msg += f"• `groups` → {groups_count} groups\n\n"
            stats_msg += f"🤖 **Cipher Elite Analytics**"
            
            await event.reply(stats_msg)
            
        except Exception as e:
            await event.reply(f"🎭 **Stats Error:** {str(e)}")
