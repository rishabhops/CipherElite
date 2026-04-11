# =============================================================================
#  CipherElite Assistant Bot Plugin
#
#  Plugin Name:    assistant
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import json
from pathlib import Path
from telethon import events, Button
import html

# Database file path
DB_PATH = Path(__file__).parent.parent / "DB" / "assistant_db.json"

# Global variables
bot_instance = None
owner_user_id = None
owner_display_name = None

def load_database():
    """Load assistant database from JSON file"""
    if DB_PATH.exists():
        try:
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading assistant database: {e}")
    
    # Default database structure
    return {
        "assistant_enabled": False,
        "users": [],
        "user_message_map": {},
        "stats": {
            "total_messages": 0,
            "total_replies": 0
        }
    }

def save_database(db):
    """Save assistant database to JSON file"""
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DB_PATH, 'w') as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Error saving assistant database: {e}")

def add_user(user_id):
    """Add a user to the database safely, auto-repairing if JSON is corrupted"""
    db = load_database()
    
    # Safety Check 1: Ensure 'users' exists
    if "users" not in db:
        db["users"] = []
        
    # Safety Check 2: Auto-repair if the JSON file accidentally saved 'users' as a dict {}
    if isinstance(db["users"], dict):
        print("⚠️ Auto-repairing db['users'] from dict back to list in JSON file...")
        # Convert dictionary keys back into a list
        db["users"] = list(db["users"].keys())
        
    # Safely append now that we are 100% sure it is a list
    if user_id not in db["users"]:
        db["users"].append(user_id)
        save_database(db)
        
    return len(db["users"])

def get_stats():
    """Get bot statistics"""
    db = load_database()
    return {
        "users_count": len(db["users"]),
        "assistant_enabled": db["assistant_enabled"],
        "total_messages": db["stats"]["total_messages"],
        "total_replies": db["stats"]["total_replies"]
    }

def get_bot_plugins_count():
    """Get the number of bot plugins installed"""
    bot_plugins_path = Path(__file__).parent
    return len([
        f for f in bot_plugins_path.glob("*.py")
        if f.stem != "__init__"
    ])

def init_bot_plugin(bot, owner_id, owner_name):
    """Initialize the assistant bot plugin"""
    global bot_instance, owner_user_id, owner_display_name
    
    bot_instance = bot
    owner_user_id = owner_id
    owner_display_name = owner_name
    
    print(f"🤖 Assistant Plugin: Initialized for {owner_name} (ID: {owner_id})")
    
    # -------------------------------------------------------------------------
    # 1. START COMMAND HANDLER
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/start"))
    async def start_handler(event):
        user_id = event.sender_id
        
        # Add user to database (Now 100% safe from dict crashes)
        users_count = add_user(user_id)
        
        # Check if sender is the owner
        if user_id == owner_user_id:
            # Owner start menu
            db = load_database()
            bot_me = await bot.get_me()
            bot_plugins_count = get_bot_plugins_count()
            
            text = (
                f"👑 <b>Welcome Master {owner_display_name}!</b>\n\n"
                f"🤖 <b>Bot:</b> @{bot_me.username}\n"
                f"📦 <b>Bot Plugins:</b> <code>{bot_plugins_count}</code>\n"
                f"👥 <b>Total Users:</b> <code>{users_count}</code>\n"
                f"🔧 <b>Assistant:</b> {'🟢 Enabled' if db['assistant_enabled'] else '🔴 Disabled'}\n\n"
                f"<i>Use the buttons below to manage your assistant bot</i>"
            )
            
            buttons = [
                [Button.inline("📚 Help", b"menu_help")],
                [Button.inline("🤖 Assistant", b"menu_assistant")],
                [Button.inline("📊 Stats", b"menu_stats")],
                [Button.inline("⚙️ Settings", b"menu_settings")],
                [Button.url("💬 Support", "https://t.me/thanosprosss")]
            ]
            
            await event.reply(text, buttons=buttons, parse_mode='html')
        else:
            # Regular user
            db = load_database()
            
            if db["assistant_enabled"]:
                text = (
                    f"👋 <b>Hello!</b>\n\n"
                    f"I am the personal assistant of <b>{owner_display_name}</b>.\n\n"
                    f"📩 Send me any message and I will deliver it to my master.\n"
                    f"💬 They can reply to you directly through me!\n\n"
                    f"<i>Please wait for a response...</i>"
                )
            else:
                text = (
                    f"👋 <b>Hello!</b>\n\n"
                    f"I am the personal assistant of <b>{owner_display_name}</b>.\n\n"
                    f"⚠️ <b>Assistant mode is currently disabled.</b>\n"
                    f"Please check back later!"
                )
            
            await event.reply(text, parse_mode='html')
    
    # -------------------------------------------------------------------------
    # 2. CALLBACK QUERY HANDLER (For inline buttons)
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"menu_(.*)"))
    async def menu_handler(event):
        # Only owner can use these menus
        if event.sender_id != owner_user_id:
            await event.answer("⛔ This is only for the bot owner!", alert=True)
            return
        
        menu = event.data_match.group(1).decode()
        db = load_database()
        
        if menu == "help":
            text = (
                "📚 <b>Bot Commands Help</b>\n\n"
                "<b>Assistant Commands:</b>\n"
                "• <code>/assistant on</code> - Enable assistant mode\n"
                "• <code>/assistant off</code> - Disable assistant mode\n"
                "• <code>/assistant status</code> - Check current status\n\n"
                "<b>General Commands:</b>\n"
                "• <code>/start</code> - Show main menu\n"
                "• <code>/help</code> - Show this help message\n\n"
                "<i>More commands coming soon...</i>"
            )
            buttons = [[Button.inline("◀️ Back", b"menu_main")]]
            await event.edit(text, buttons=buttons, parse_mode='html')
        
        elif menu == "assistant":
            text = (
                "🤖 <b>Assistant Settings</b>\n\n"
                f"<b>Status:</b> {'🟢 Enabled' if db['assistant_enabled'] else '🔴 Disabled'}\n"
                f"<b>Total Messages:</b> <code>{db['stats']['total_messages']}</code>\n"
                f"<b>Total Replies:</b> <code>{db['stats']['total_replies']}</code>\n\n"
                "<b>Features:</b>\n"
                "• Forward user messages to you\n"
                "• Reply to users through the bot\n"
                "• Track multiple conversations\n"
                "• User information with each message\n\n"
                "<i>Use /assistant on|off|status to control</i>"
            )
            
            if db['assistant_enabled']:
                buttons = [
                    [Button.inline("🔴 Disable Assistant", b"assistant_toggle")],
                    [Button.inline("◀️ Back", b"menu_main")]
                ]
            else:
                buttons = [
                    [Button.inline("🟢 Enable Assistant", b"assistant_toggle")],
                    [Button.inline("◀️ Back", b"menu_main")]
                ]
            
            await event.edit(text, buttons=buttons, parse_mode='html')
        
        elif menu == "stats":
            stats = get_stats()
            text = (
                "📊 <b>Bot Statistics</b>\n\n"
                f"👥 <b>Total Users:</b> <code>{stats['users_count']}</code>\n"
                f"💬 <b>Messages Received:</b> <code>{stats['total_messages']}</code>\n"
                f"📤 <b>Replies Sent:</b> <code>{stats['total_replies']}</code>\n"
                f"🔧 <b>Assistant:</b> {'🟢 Enabled' if stats['assistant_enabled'] else '🔴 Disabled'}\n\n"
                f"<b>Uptime:</b> <i>Since bot start</i>\n"
                f"<b>Version:</b> <code>1.0.0</code>\n\n"
                f"<i>Statistics updated in real-time</i>"
            )
            buttons = [[Button.inline("◀️ Back", b"menu_main")]]
            await event.edit(text, buttons=buttons, parse_mode='html')
        
        elif menu == "settings":
            text = (
                "⚙️ <b>General Settings</b>\n\n"
                "<b>Coming Soon:</b>\n"
                "• Auto-response templates\n"
                "• Block/unblock users\n"
                "• Custom welcome messages\n"
                "• Scheduled messages\n"
                "• Analytics reports\n\n"
                "<i>More features in development...</i>"
            )
            buttons = [[Button.inline("◀️ Back", b"menu_main")]]
            await event.edit(text, buttons=buttons, parse_mode='html')
        
        elif menu == "main":
            # Back to main menu
            bot_me = await bot.get_me()
            stats = get_stats()
            bot_plugins_count = get_bot_plugins_count()
            
            text = (
                f"👑 <b>Welcome Master {owner_display_name}!</b>\n\n"
                f"🤖 <b>Bot:</b> @{bot_me.username}\n"
                f"📦 <b>Bot Plugins:</b> <code>{bot_plugins_count}</code>\n"
                f"👥 <b>Total Users:</b> <code>{stats['users_count']}</code>\n"
                f"🔧 <b>Assistant:</b> {'🟢 Enabled' if stats['assistant_enabled'] else '🔴 Disabled'}\n\n"
                f"<i>Use the buttons below to manage your assistant bot</i>"
            )
            
            buttons = [
                [Button.inline("📚 Help", b"menu_help")],
                [Button.inline("🤖 Assistant", b"menu_assistant")],
                [Button.inline("📊 Stats", b"menu_stats")],
                [Button.inline("⚙️ Settings", b"menu_settings")],
                [Button.url("💬 Support", "https://t.me/thanosprosss")]
            ]
            
            await event.edit(text, buttons=buttons, parse_mode='html')
    
    # -------------------------------------------------------------------------
    # 3. ASSISTANT TOGGLE HANDLER
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"assistant_toggle"))
    async def assistant_toggle_handler(event):
        # Only owner can toggle
        if event.sender_id != owner_user_id:
            await event.answer("⛔ This is only for the bot owner!", alert=True)
            return
        
        db = load_database()
        db["assistant_enabled"] = not db["assistant_enabled"]
        save_database(db)
        
        status = "🟢 Enabled" if db["assistant_enabled"] else "🔴 Disabled"
        await event.answer(f"✅ Assistant is now {status}", alert=True)
        
        # Refresh the assistant menu
        text = (
            "🤖 <b>Assistant Settings</b>\n\n"
            f"<b>Status:</b> {status}\n"
            f"<b>Total Messages:</b> <code>{db['stats']['total_messages']}</code>\n"
            f"<b>Total Replies:</b> <code>{db['stats']['total_replies']}</code>\n\n"
            "<b>Features:</b>\n"
            "• Forward user messages to you\n"
            "• Reply to users through the bot\n"
            "• Track multiple conversations\n"
            "• User information with each message\n\n"
            "<i>Use /assistant on|off|status to control</i>"
        )
        
        if db['assistant_enabled']:
            buttons = [
                [Button.inline("🔴 Disable Assistant", b"assistant_toggle")],
                [Button.inline("◀️ Back", b"menu_main")]
            ]
        else:
            buttons = [
                [Button.inline("🟢 Enable Assistant", b"assistant_toggle")],
                [Button.inline("◀️ Back", b"menu_main")]
            ]
        
        await event.edit(text, buttons=buttons, parse_mode='html')
    
    # -------------------------------------------------------------------------
    # 4. ASSISTANT COMMAND HANDLER
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/assistant(?:\s+(.+))?"))
    async def assistant_command_handler(event):
        # Only owner can use this command
        if event.sender_id != owner_user_id:
            await event.reply("⛔ This command is only for the bot owner!")
            return
        
        action = event.pattern_match.group(1)
        db = load_database()
        
        if not action:
            # Show status
            status = "🟢 Enabled" if db["assistant_enabled"] else "🔴 Disabled"
            await event.reply(
                f"🤖 <b>Assistant Status:</b> {status}\n\n"
                f"<b>Commands:</b>\n"
                f"• <code>/assistant on</code> - Enable assistant\n"
                f"• <code>/assistant off</code> - Disable assistant\n"
                f"• <code>/assistant status</code> - Check status",
                parse_mode='html'
            )
            return
        
        action = action.strip().lower()
        
        if action == "on":
            db["assistant_enabled"] = True
            save_database(db)
            await event.reply(
                "✅ <b>Assistant Mode Enabled!</b>\n\n"
                "Users can now send you messages through the bot.\n"
                "You will receive notifications for each message.",
                parse_mode='html'
            )
        
        elif action == "off":
            db["assistant_enabled"] = False
            save_database(db)
            await event.reply(
                "🔴 <b>Assistant Mode Disabled!</b>\n\n"
                "Users will see a message that assistant is currently disabled.",
                parse_mode='html'
            )
        
        elif action == "status":
            status = "🟢 Enabled" if db["assistant_enabled"] else "🔴 Disabled"
            await event.reply(
                f"🤖 <b>Assistant Status:</b> {status}\n\n"
                f"📊 <b>Statistics:</b>\n"
                f"• Messages: <code>{db['stats']['total_messages']}</code>\n"
                f"• Replies: <code>{db['stats']['total_replies']}</code>\n"
                f"• Users: <code>{len(db['users'])}</code>",
                parse_mode='html'
            )
        
        else:
            await event.reply(
                "❌ Invalid action!\n\n"
                "Use: <code>/assistant on|off|status</code>",
                parse_mode='html'
            )
    
    # -------------------------------------------------------------------------
    # 5. USER MESSAGE HANDLER (Forward to owner)
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def user_message_handler(event):
        # Ignore bot commands
        if event.text and event.text.startswith('/'):
            return
        
        # Ignore owner's messages
        if event.sender_id == owner_user_id:
            return
        
        # Check if assistant is enabled
        db = load_database()
        if not db["assistant_enabled"]:
            return
        
        # Get sender info
        try:
            sender = await event.get_sender()
            sender_name = sender.first_name or "Unknown"
            sender_username = f"@{sender.username}" if sender.username else "No username"
            sender_id = sender.id
            
            # Forward message to owner
            forward_text = (
                f"📩 <b>New Message from User</b>\n\n"
                f"👤 <b>Name:</b> {html.escape(sender_name)}\n"
                f"🆔 <b>User ID:</b> <code>{sender_id}</code>\n"
                f"📝 <b>Username:</b> {html.escape(sender_username)}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
            )
            
            # Send the forward to owner
            message_text = html.escape(event.text) if event.text else '[Media/Sticker/Other]'
            forwarded = await bot.send_message(
                owner_user_id,
                forward_text + f"<b>Message:</b> {message_text}",
                parse_mode='html'
            )
            
            # If there's media, forward it too
            if event.photo or event.video or event.document or event.sticker:
                await event.forward_to(owner_user_id)
            
            # Store mapping for replies
            db["user_message_map"][str(forwarded.id)] = sender_id
            db["stats"]["total_messages"] += 1
            save_database(db)
            
            # Confirm to user
            await event.reply(
                "✅ <b>Message sent!</b>\n\n"
                f"Your message has been delivered to <b>{owner_display_name}</b>.\n"
                f"Please wait for a response...",
                parse_mode='html'
            )
            
        except Exception as e:
            print(f"Error forwarding user message: {e}")
    
    # -------------------------------------------------------------------------
    # 6. OWNER REPLY HANDLER (Reply to users)
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(from_users=owner_user_id))
    async def owner_reply_handler(event):
        # Check if this is a reply
        if not event.is_reply:
            return
        
        try:
            # Get the message being replied to
            replied_msg = await event.get_reply_message()
            
            # Check if this message is in our mapping
            db = load_database()
            replied_msg_id = str(replied_msg.id)
            
            if replied_msg_id in db["user_message_map"]:
                # Get the original user ID
                user_id = db["user_message_map"][replied_msg_id]
                
                # Send owner's reply to the user
                reply_message = html.escape(event.text) if event.text else '[Media/Sticker/Other]'
                reply_text = (
                    f"💬 <b>Reply from {html.escape(owner_display_name)}:</b>\n\n"
                    f"{reply_message}"
                )
                
                await bot.send_message(user_id, reply_text, parse_mode='html')
                
                # If there's media in the reply, forward it too
                if event.photo or event.video or event.document or event.sticker:
                    await event.forward_to(user_id)
                
                # Update stats
                db["stats"]["total_replies"] += 1
                save_database(db)
                
                # Confirm to owner
                await event.reply("✅ <b>Reply sent to user!</b>", parse_mode='html')
                
                # Note: We keep the message mapping for potential follow-up conversations
                # A cleanup mechanism can be added later based on message age
        
        except Exception as e:
            print(f"Error handling owner reply: {e}")
    
    # -------------------------------------------------------------------------
    # 7. HELP COMMAND
    # -------------------------------------------------------------------------
    @bot.on(events.NewMessage(pattern=r"^/help"))
    async def help_command_handler(event):
        if event.sender_id == owner_user_id:
            text = (
                "📚 <b>Bot Commands Help</b>\n\n"
                "<b>Assistant Commands:</b>\n"
                "• <code>/assistant on</code> - Enable assistant mode\n"
                "• <code>/assistant off</code> - Disable assistant mode\n"
                "• <code>/assistant status</code> - Check current status\n\n"
                "<b>General Commands:</b>\n"
                "• <code>/start</code> - Show main menu\n"
                "• <code>/help</code> - Show this help message\n\n"
                "<i>More commands coming soon...</i>"
            )
        else:
            text = (
                "📚 <b>Help</b>\n\n"
                "This is a personal assistant bot.\n"
                "Simply send your message and it will be forwarded to the owner.\n\n"
                "Use /start to begin."
            )
        
        await event.reply(text, parse_mode='html')
    
    print("✅ Assistant Plugin: All handlers registered successfully")
