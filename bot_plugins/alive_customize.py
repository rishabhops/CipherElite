# =============================================================================
#  CipherElite Bot Plugin - Alive/Ping Customization
# =============================================================================

from telethon import events, Button

VERSION = "1.0.0"

def init_bot_plugin(bot, owner_id, owner_name):
    """Initialize alive/ping customization bot plugin"""
    
    @bot.on(events.NewMessage(pattern=r"^/alive$"))
    async def alive_customize(event):
        """Alive customization menu"""
        try:
            from plugins.alive import user_config, ALIVE_STYLES
            from config.config import Config
            from telethon import version
            
            # Generate preview text
            uptime = "0:00:00"
            quote = ""
            template = ALIVE_STYLES[user_config.alive_style_index]
            preview_text = template.format(
                name="Preview",
                telethon=version.__version__,
                plugins="60",
                uptime=uptime,
                version=Config.VERSION,
                branch=Config.BRANCH,
                quote=quote,
            )
            
            buttons = [
                [Button.inline("🖼 Change Alive Pic", "bot_alive_changepic")],
                [Button.inline(f"🎨 Style: {user_config.alive_style_index + 1}/5", "bot_alive_nextstyle")],
                [Button.inline(f"{'✅' if user_config.use_pic_for_alive else '❌'} Show Pic", "bot_alive_togglepic")],
                [Button.inline(f"{'✅' if user_config.show_quotes else '❌'} Show Quotes", "bot_alive_togglequotes")],
                [Button.inline("✏️ Custom Text", "bot_alive_customtext")],
                [Button.inline("🔄 Reset to Default", "bot_alive_reset")],
            ]
            
            await event.reply(
                f"⚡ <b>Alive Customization</b>\n\n"
                f"Current Style: <b>{user_config.alive_style_index + 1}/5</b>\n\n"
                f"{preview_text}",
                buttons=buttons,
                parse_mode='html'
            )
        except Exception as e:
            await event.reply(f"❌ **Error:** {e}")
    
    @bot.on(events.NewMessage(pattern=r"^/ping$"))
    async def ping_customize(event):
        """Ping customization menu"""
        try:
            from plugins.alive import user_config, PING_STYLES
            
            # Generate preview text
            uptime = "0:00:00"
            speed = "0"
            template = PING_STYLES[user_config.ping_style_index]
            preview_text = template.format(speed=speed, uptime=uptime)
            
            buttons = [
                [Button.inline("🖼 Change Ping Pic", "bot_ping_changepic")],
                [Button.inline(f"🎨 Style: {user_config.ping_style_index + 1}/5", "bot_ping_nextstyle")],
                [Button.inline(f"{'✅' if user_config.use_pic_for_ping else '❌'} Show Pic", "bot_ping_togglepic")],
                [Button.inline("✏️ Custom Text", "bot_ping_customtext")],
                [Button.inline("🔄 Reset to Default", "bot_ping_reset")],
            ]
            
            await event.reply(
                f"🏓 <b>Ping Customization</b>\n\n"
                f"Current Style: <b>{user_config.ping_style_index + 1}/5</b>\n\n"
                f"{preview_text}",
                buttons=buttons,
                parse_mode='html'
            )
        except Exception as e:
            await event.reply(f"❌ **Error:** {e}")
    
    # -------------------------------------------------------------------------
    # ALIVE CUSTOMIZATION CALLBACKS
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"bot_alive_(.+)"))
    async def alive_callback(event):
        """Handle alive customization callbacks"""
        data = event.data_match.group(1).decode()
        
        try:
            from plugins.alive import user_config, save_config, ALIVE_STYLES
            from config.config import Config
            from telethon import version
            
            if data == "nextstyle":
                user_config.alive_style_index = (user_config.alive_style_index + 1) % len(ALIVE_STYLES)
                save_config()
                await event.answer(f"✅ Style changed to {user_config.alive_style_index + 1}/5", alert=True)
            
            elif data == "togglepic":
                user_config.use_pic_for_alive = not user_config.use_pic_for_alive
                save_config()
                state = "ON" if user_config.use_pic_for_alive else "OFF"
                await event.answer(f"✅ Alive pic {state}", alert=True)
            
            elif data == "togglequotes":
                user_config.show_quotes = not user_config.show_quotes
                save_config()
                state = "ON" if user_config.show_quotes else "OFF"
                await event.answer(f"✅ Quotes {state}", alert=True)
            
            elif data == "reset":
                user_config.alive_style_index = 0
                user_config.custom_alive_text = None
                user_config.alive_pic = Config.DEFAULT_ALIVE_PIC
                user_config.use_pic_for_alive = True
                user_config.show_quotes = True
                save_config()
                await event.answer("✅ Reset to default!", alert=True)
            
            elif data == "changepic":
                await event.answer("📸 Reply to an image with .setalivepic command in userbot", alert=True)
                return
            
            elif data == "customtext":
                await event.answer("✏️ Use .setalivetext <text> command in userbot", alert=True)
                return
            
            # Refresh the menu
            uptime = "0:00:00"
            quote = ""
            template = ALIVE_STYLES[user_config.alive_style_index]
            preview_text = template.format(
                name="Preview",
                telethon=version.__version__,
                plugins="60",
                uptime=uptime,
                version=Config.VERSION,
                branch=Config.BRANCH,
                quote=quote,
            )
            
            buttons = [
                [Button.inline("🖼 Change Alive Pic", "bot_alive_changepic")],
                [Button.inline(f"🎨 Style: {user_config.alive_style_index + 1}/5", "bot_alive_nextstyle")],
                [Button.inline(f"{'✅' if user_config.use_pic_for_alive else '❌'} Show Pic", "bot_alive_togglepic")],
                [Button.inline(f"{'✅' if user_config.show_quotes else '❌'} Show Quotes", "bot_alive_togglequotes")],
                [Button.inline("✏️ Custom Text", "bot_alive_customtext")],
                [Button.inline("🔄 Reset to Default", "bot_alive_reset")],
            ]
            
            await event.edit(
                f"⚡ <b>Alive Customization</b>\n\n"
                f"Current Style: <b>{user_config.alive_style_index + 1}/5</b>\n\n"
                f"{preview_text}",
                buttons=buttons,
                parse_mode='html'
            )
            
        except Exception as e:
            await event.answer(f"❌ Error: {e}", alert=True)
    
    # -------------------------------------------------------------------------
    # PING CUSTOMIZATION CALLBACKS
    # -------------------------------------------------------------------------
    @bot.on(events.CallbackQuery(pattern=r"bot_ping_(.+)"))
    async def ping_callback(event):
        """Handle ping customization callbacks"""
        data = event.data_match.group(1).decode()
        
        try:
            from plugins.alive import user_config, save_config, PING_STYLES
            from config.config import Config
            
            if data == "nextstyle":
                user_config.ping_style_index = (user_config.ping_style_index + 1) % len(PING_STYLES)
                save_config()
                await event.answer(f"✅ Style changed to {user_config.ping_style_index + 1}/5", alert=True)
            
            elif data == "togglepic":
                user_config.use_pic_for_ping = not user_config.use_pic_for_ping
                save_config()
                state = "ON" if user_config.use_pic_for_ping else "OFF"
                await event.answer(f"✅ Ping pic {state}", alert=True)
            
            elif data == "reset":
                user_config.ping_style_index = 0
                user_config.custom_ping_text = None
                user_config.ping_pic = Config.DEFAULT_PING_PIC
                user_config.use_pic_for_ping = True
                save_config()
                await event.answer("✅ Reset to default!", alert=True)
            
            elif data == "changepic":
                await event.answer("📸 Reply to an image with .setpingpic command in userbot", alert=True)
                return
            
            elif data == "customtext":
                await event.answer("✏️ Use .setpingtext <text> command in userbot", alert=True)
                return
            
            # Refresh the menu
            uptime = "0:00:00"
            speed = "0"
            template = PING_STYLES[user_config.ping_style_index]
            preview_text = template.format(speed=speed, uptime=uptime)
            
            buttons = [
                [Button.inline("🖼 Change Ping Pic", "bot_ping_changepic")],
                [Button.inline(f"🎨 Style: {user_config.ping_style_index + 1}/5", "bot_ping_nextstyle")],
                [Button.inline(f"{'✅' if user_config.use_pic_for_ping else '❌'} Show Pic", "bot_ping_togglepic")],
                [Button.inline("✏️ Custom Text", "bot_ping_customtext")],
                [Button.inline("🔄 Reset to Default", "bot_ping_reset")],
            ]
            
            await event.edit(
                f"🏓 <b>Ping Customization</b>\n\n"
                f"Current Style: <b>{user_config.ping_style_index + 1}/5</b>\n\n"
                f"{preview_text}",
                buttons=buttons,
                parse_mode='html'
            )
            
        except Exception as e:
            await event.answer(f"❌ Error: {e}", alert=True)
    
    print("✅ Alive/Ping Customization plugin loaded")
