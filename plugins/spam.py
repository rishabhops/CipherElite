import asyncio
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    """
    Required initialization function that registers commands and descriptions
    """
    commands = [
        ".spam <count> <message> - Spam message multiple times with Cipher Elite power",
        ".dspam <count> <delay> <message> - Spam with custom delay between messages",
        ".mspam <count> <reply to media> - Spam media/files multiple times",
        ".stopspam - Stop all active spam tasks in current chat",
        ".listspam - Show all active spam operations across chats"
    ]
    description = "💥 Cipher Elite Spam Engine - Advanced message spamming with military precision"
    add_handler("spam", commands, description)

async def register_commands():
    """
    Cipher Elite spam system with advanced task management
    """
    
    # Global spam task tracker
    cipher_spam_tasks = {}
    
    class CipherEliteSpamEngine:
        def __init__(self):
            self.active_operations = {}
            self.spam_stats = {
                'total_sent': 0,
                'active_tasks': 0,
                'completed_operations': 0
            }
        
        async def execute_spam_operation(self, client, chat_id, message_content=None, 
                                       count=1, reply_to=None, delay=0, media_msg=None, 
                                       stop_event=None, operation_type="text"):
            """Execute spam operation with Cipher Elite precision"""
            sent_count = 0
            
            for i in range(count):
                if stop_event and stop_event.is_set():
                    break
                
                try:
                    if operation_type == "media" and media_msg:
                        # Forward media message
                        await client.forward_messages(chat_id, media_msg)
                    else:
                        # Send text message
                        await client.send_message(
                            chat_id,
                            message_content,
                            reply_to=reply_to
                        )
                    
                    sent_count += 1
                    self.spam_stats['total_sent'] += 1
                    
                    # Add delay if specified
                    if delay > 0:
                        await asyncio.sleep(delay)
                    else:
                        # Minimal delay to prevent rate limiting
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    print(f"❌ Cipher Elite Spam Error: {e}")
                    continue
            
            # Cleanup task
            try:
                if stop_event:
                    stop_event.set()
                task_list = cipher_spam_tasks.get(chat_id, [])
                if stop_event in task_list:
                    task_list.remove(stop_event)
                if not task_list:
                    cipher_spam_tasks.pop(chat_id, None)
                    
                self.spam_stats['completed_operations'] += 1
                    
            except Exception:
                pass
            
            return sent_count
    
    # Initialize spam engine
    spam_engine = CipherEliteSpamEngine()
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spam\s+(\d+)\s+(.+)"))
    @rishabh()
    async def cipher_elite_spam(event):
        try:
            count = int(event.pattern_match.group(1))
            message_content = event.pattern_match.group(2).strip()
            
            if count <= 0 or count > 500:
                await event.reply("🎭 **Cipher Elite Spam Engine**\n\n"
                                "❌ **Invalid count!** Use 1-500\n"
                                "💡 **Usage:** `.spam 10 Hello World`")
                return
            
            if not message_content:
                await event.reply("❌ **Cipher Elite Error:** Please provide message content!")
                return
            
            chat_id = event.chat_id
            reply_to = event.reply_to_msg_id
            
            # Create stop event for this operation
            stop_event = asyncio.Event()
            
            # Add to active tasks
            if chat_id in cipher_spam_tasks:
                cipher_spam_tasks[chat_id].append(stop_event)
            else:
                cipher_spam_tasks[chat_id] = [stop_event]
            
            # Show operation status
            status_msg = await event.reply(f"🎭 **Cipher Elite Spam Engine**\n\n"
                                         f"💥 **Operation:** TEXT SPAM\n"
                                         f"🎯 **Target:** Current Chat\n"
                                         f"📊 **Count:** {count} messages\n"
                                         f"⚡ **Status:** Initializing spam protocol...\n"
                                         f"🔥 **Message:** `{message_content[:30]}{'...' if len(message_content) > 30 else ''}`")
            
            # Delete command message
            await event.delete()
            
            # Execute spam operation
            sent_count = await spam_engine.execute_spam_operation(
                event.client,
                chat_id,
                message_content=message_content,
                count=count,
                reply_to=reply_to,
                delay=0,
                stop_event=stop_event,
                operation_type="text"
            )
            
            # Update status with results
            await status_msg.edit(f"🎭 **Cipher Elite Spam Complete**\n\n"
                                 f"💥 **Operation:** TEXT SPAM\n"
                                 f"✅ **Sent:** {sent_count}/{count} messages\n"
                                 f"🎯 **Success Rate:** {int((sent_count/count)*100)}%\n"
                                 f"🔥 **Status:** OPERATION COMPLETE\n"
                                 f"🤖 **Powered by Cipher Elite**")
            
            # Auto-delete status after 10 seconds
            await asyncio.sleep(10)
            await status_msg.delete()
            
        except ValueError:
            await event.reply("🎭 **Cipher Elite Spam Error**\n\n"
                            "❌ **Invalid number format!**\n"
                            "💡 **Usage:** `.spam 10 Hello World`")
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite Spam System Error**\n\n"
                            f"❌ **Error:** {str(e)[:100]}...")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.dspam\s+(\d+)\s+(\d+\.?\d*)\s+(.+)"))
    @rishabh()
    async def cipher_elite_delay_spam(event):
        try:
            count = int(event.pattern_match.group(1))
            delay = float(event.pattern_match.group(2))
            message_content = event.pattern_match.group(3).strip()
            
            if count <= 0 or count > 200:
                await event.reply("🎭 **Cipher Elite Delay Spam Engine**\n\n"
                                "❌ **Invalid count!** Use 1-200 for delay spam\n"
                                "💡 **Usage:** `.dspam 10 2.5 Hello World`")
                return
            
            if delay < 0 or delay > 60:
                await event.reply("❌ **Invalid delay!** Use 0-60 seconds")
                return
            
            chat_id = event.chat_id
            reply_to = event.reply_to_msg_id
            
            # Create stop event
            stop_event = asyncio.Event()
            
            if chat_id in cipher_spam_tasks:
                cipher_spam_tasks[chat_id].append(stop_event)
            else:
                cipher_spam_tasks[chat_id] = [stop_event]
            
            # Calculate estimated completion time
            estimated_time = int(count * (delay + 0.1))
            
            status_msg = await event.reply(f"🎭 **Cipher Elite Delay Spam Engine**\n\n"
                                         f"💥 **Operation:** DELAY SPAM\n"
                                         f"📊 **Count:** {count} messages\n"
                                         f"⏱️ **Delay:** {delay}s between messages\n"
                                         f"🕐 **Estimated Time:** ~{estimated_time}s\n"
                                         f"⚡ **Status:** Precision timing protocol active...")
            
            await event.delete()
            
            # Execute delay spam
            sent_count = await spam_engine.execute_spam_operation(
                event.client,
                chat_id,
                message_content=message_content,
                count=count,
                reply_to=reply_to,
                delay=delay,
                stop_event=stop_event,
                operation_type="text"
            )
            
            await status_msg.edit(f"🎭 **Cipher Elite Delay Spam Complete**\n\n"
                                 f"💥 **Operation:** DELAY SPAM\n"
                                 f"✅ **Sent:** {sent_count}/{count} messages\n"
                                 f"⏱️ **Delay Used:** {delay}s\n"
                                 f"🎯 **Success Rate:** {int((sent_count/count)*100)}%\n"
                                 f"🔥 **Status:** PRECISION OPERATION COMPLETE\n"
                                 f"🤖 **Powered by Cipher Elite**")
            
            await asyncio.sleep(10)
            await status_msg.delete()
            
        except ValueError:
            await event.reply("🎭 **Cipher Elite Delay Spam Error**\n\n"
                            "❌ **Invalid format!**\n"
                            "💡 **Usage:** `.dspam 10 2.5 Hello World`\n"
                            "📝 **Format:** count delay(seconds) message")
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)[:100]}...")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.mspam\s+(\d+)"))
    @rishabh()
    async def cipher_elite_media_spam(event):
        try:
            count = int(event.pattern_match.group(1))
            
            if not event.reply_to_msg_id:
                await event.reply("🎭 **Cipher Elite Media Spam Engine**\n\n"
                                "❌ **Error:** Please reply to a media message!\n\n"
                                "💡 **Usage:** Reply to any image/video/file with `.mspam 10`\n"
                                "🎯 **Supported:** Images, Videos, Documents, Stickers")
                return
            
            if count <= 0 or count > 100:
                await event.reply("❌ **Invalid count!** Use 1-100 for media spam")
                return
            
            reply_message = await event.get_reply_message()
            
            if not reply_message.media:
                await event.reply("❌ **No media found in replied message!**")
                return
            
            chat_id = event.chat_id
            
            # Create stop event
            stop_event = asyncio.Event()
            
            if chat_id in cipher_spam_tasks:
                cipher_spam_tasks[chat_id].append(stop_event)
            else:
                cipher_spam_tasks[chat_id] = [stop_event]
            
            # Determine media type
            media_type = "Unknown"
            if reply_message.photo:
                media_type = "Image"
            elif reply_message.video:
                media_type = "Video"
            elif reply_message.document:
                media_type = "Document"
            elif reply_message.sticker:
                media_type = "Sticker"
            
            status_msg = await event.reply(f"🎭 **Cipher Elite Media Spam Engine**\n\n"
                                         f"💥 **Operation:** MEDIA SPAM\n"
                                         f"📸 **Media Type:** {media_type}\n"
                                         f"📊 **Count:** {count} times\n"
                                         f"⚡ **Status:** Media replication protocol active...")
            
            await event.delete()
            
            # Execute media spam
            sent_count = await spam_engine.execute_spam_operation(
                event.client,
                chat_id,
                count=count,
                media_msg=reply_message,
                stop_event=stop_event,
                operation_type="media"
            )
            
            await status_msg.edit(f"🎭 **Cipher Elite Media Spam Complete**\n\n"
                                 f"💥 **Operation:** MEDIA SPAM\n"
                                 f"📸 **Type:** {media_type}\n"
                                 f"✅ **Sent:** {sent_count}/{count} media files\n"
                                 f"🎯 **Success Rate:** {int((sent_count/count)*100)}%\n"
                                 f"🔥 **Status:** MEDIA REPLICATION COMPLETE\n"
                                 f"🤖 **Powered by Cipher Elite**")
            
            await asyncio.sleep(10)
            await status_msg.delete()
            
        except ValueError:
            await event.reply("❌ **Invalid number format!**")
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite Media Spam Error**\n\n"
                            f"❌ **Error:** {str(e)[:100]}...")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.stopspam"))
    @rishabh()
    async def cipher_elite_stop_spam(event):
        try:
            chat_id = event.chat_id
            
            if chat_id not in cipher_spam_tasks or not cipher_spam_tasks[chat_id]:
                await event.reply("🎭 **Cipher Elite Spam Control**\n\n"
                                "❌ **No active spam operations in this chat**\n"
                                "💡 **All operations already completed or stopped**")
                return
            
            # Stop all operations in this chat
            active_count = len(cipher_spam_tasks[chat_id])
            
            for stop_event in cipher_spam_tasks[chat_id]:
                stop_event.set()
            
            # Clear the task list
            cipher_spam_tasks.pop(chat_id, None)
            
            chat_name = "Current Chat"
            try:
                chat = await event.get_chat()
                chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Current Chat'))
            except:
                pass
            
            status_msg = await event.reply(f"🎭 **Cipher Elite Operation Terminated**\n\n"
                                         f"🛑 **Action:** EMERGENCY STOP\n"
                                         f"🎯 **Target:** {chat_name}\n"
                                         f"📊 **Stopped:** {active_count} active operation(s)\n"
                                         f"✅ **Status:** ALL SPAM OPERATIONS TERMINATED\n\n"
                                         f"🤖 **Cipher Elite Security Protocol**")
            
            await asyncio.sleep(5)
            await status_msg.delete()
            await event.delete()
            
        except Exception as e:
            await event.reply(f"❌ **Stop spam error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.listspam"))
    @rishabh()
    async def cipher_elite_list_spam(event):
        try:
            if not cipher_spam_tasks:
                await event.reply("🎭 **Cipher Elite Spam Monitor**\n\n"
                                "✅ **No active spam operations detected**\n"
                                "🛡️ **All systems clear**\n"
                                "📊 **Status:** IDLE MODE")
                return
            
            list_msg = f"🎭 **Cipher Elite Active Operations**\n\n"
            list_msg += f"📊 **Global Spam Statistics:**\n"
            list_msg += f"⚡ **Total Sent:** {spam_engine.spam_stats['total_sent']} messages\n"
            list_msg += f"🔄 **Completed Ops:** {spam_engine.spam_stats['completed_operations']}\n\n"
            list_msg += f"🎯 **Active Operations by Chat:**\n"
            
            for chat_id, task_list in cipher_spam_tasks.items():
                if task_list:  # Only show chats with active tasks
                    try:
                        chat = await event.client.get_entity(chat_id)
                        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', f'Chat {chat_id}'))
                    except:
                        chat_name = f"Chat ID: {chat_id}"
                    
                    list_msg += f"🔸 **{chat_name}**\n"
                    list_msg += f"   📍 **Chat ID:** `{chat_id}`\n"
                    list_msg += f"   ⚡ **Active Tasks:** {len(task_list)}\n\n"
            
            list_msg += f"🤖 **Cipher Elite Monitoring System**"
            
            await event.reply(list_msg)
            
        except Exception as e:
            await event.reply(f"❌ **List spam error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spamstats"))
    @rishabh()
    async def cipher_elite_spam_stats(event):
        try:
            active_chats = len(cipher_spam_tasks)
            total_active_tasks = sum(len(tasks) for tasks in cipher_spam_tasks.values())
            
            stats_msg = f"🎭 **Cipher Elite Spam Engine Statistics**\n\n"
            stats_msg += f"📊 **Performance Metrics:**\n"
            stats_msg += f"⚡ **Total Messages Sent:** {spam_engine.spam_stats['total_sent']:,}\n"
            stats_msg += f"🔄 **Completed Operations:** {spam_engine.spam_stats['completed_operations']}\n"
            stats_msg += f"🎯 **Active Chats:** {active_chats}\n"
            stats_msg += f"📈 **Active Tasks:** {total_active_tasks}\n\n"
            
            if active_chats > 0:
                stats_msg += f"🔥 **Status:** HIGH ACTIVITY\n"
            else:
                stats_msg += f"✅ **Status:** STANDBY MODE\n"
            
            stats_msg += f"🤖 **Cipher Elite Analytics**"
            
            await event.reply(stats_msg)
            
        except Exception as e:
            await event.reply(f"❌ **Stats error:** {str(e)}")
