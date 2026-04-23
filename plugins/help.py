import asyncio
from telethon import events
from config.config import Config
from utils.decorators import rishabh
from plugins.bot import CMD_LIST  # Import the command list

client = None

def init(client_instance):
    global client
    client = client_instance
    
    # Register quickhelp as a "plugin" so it shows up in help menu
    quickhelp_commands = [
        ".help - Show interactive help menu with all plugins",
        ".help <plugin> - Get direct help for specific plugin",
        ".plugins - List all loaded plugins with statistics",
        ".findplugin <term> - Search plugins by name or keyword",
        ".helpstats - Show detailed help system analytics",
        ".quickhelp - Show this quick help guide"
    ]
    
    quickhelp_description = "⚡ Cipher Elite Help System - Complete guide to using the advanced help features"
    
    # Add to CMD_LIST so it appears in help menu
    CMD_LIST["quickhelp"] = {
        "commands": quickhelp_commands,
        "description": quickhelp_description
    }

def add_command(plugin_name, commands):
    global CMD_LIST
    if plugin_name not in CMD_LIST:
        CMD_LIST[plugin_name] = []
    CMD_LIST[plugin_name].extend(commands)

async def register_commands():
    
    @client.on(events.NewMessage(pattern=r"\.help(?:\s+(.+))?"))
    @rishabh()
    async def help_handler(event):
        plugin_name = event.pattern_match.group(1)
        
        # Direct plugin help (.help spam, .help broadcast, etc.)
        if plugin_name:
            plugin_name = plugin_name.strip().lower()
            
            # Check if plugin exists
            if plugin_name in CMD_LIST:
                plugin_data = CMD_LIST[plugin_name]
                
                help_text = f"✦ <b>𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐋𝐈𝐓𝐄 ✦ {plugin_name.upper()}</b>\n"
                help_text += f"⟡ ═════════════════ ⟡\n"
                help_text += f"<i>{plugin_data['description']}</i>\n\n"
                help_text += f"❖ <b>Available Commands:</b>\n\n"
                
                # Add commands with proper HTML formatting
                for cmd in plugin_data["commands"]:
                    if isinstance(cmd, str) and cmd.strip():
                        if " - " in cmd:
                            cmd_part, desc_part = cmd.split(" - ", 1)
                            escaped_command = cmd_part.strip().replace('<', '&lt;').replace('>', '&gt;')
                            description = desc_part.strip()
                            help_text += f" ├ <code>{escaped_command}</code>\n"
                            help_text += f" └ <i>{description}</i>\n\n"
                        else:
                            escaped_cmd = cmd.strip().replace('<', '&lt;').replace('>', '&gt;')
                            help_text += f" ├ <code>{escaped_cmd}</code>\n\n"
                
                help_text += f"⟡ ═════════════════ ⟡\n"
                help_text += f"🔄 <b>Quick Help:</b> <code>.help {plugin_name}</code>\n"
                help_text += f"📚 <b>All Plugins:</b> <code>.help</code>\n"
                
                await event.reply(help_text, parse_mode='html')
                return
                
            else:
                # Plugin not found - show available plugins
                available_plugins = list(CMD_LIST.keys())
                
                error_text = f"✦ <b>𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐋𝐈𝐓𝐄 𝐇𝐄𝐋𝐏</b> ✦\n"
                error_text += f"⟡ ═════════════════ ⟡\n"
                error_text += f"⚠️ <b>Plugin '{plugin_name}' not found!</b>\n\n"
                error_text += f"❖ <b>Available Plugins:</b>\n"
                
                # Show plugins in rows of 3
                for i in range(0, len(available_plugins), 3):
                    row_plugins = available_plugins[i:i+3]
                    plugin_row = " • ".join([f"<code>{p}</code>" for p in row_plugins])
                    error_text += f" {plugin_row}\n"
                
                error_text += f"\n💡 <b>Usage:</b> <code>.help &lt;plugin_name&gt;</code>\n"
                
                await event.reply(error_text, parse_mode='html')
                return
        
        # Default behavior - show inline help menu
        try:
            results = await event.client.inline_query(
                f"{Config.TG_BOT_USERNAME}",
                "help"
            )
            help_msg = await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True
            )
            await event.delete()
            
            # --- START INITIAL 60 SECOND TIMEOUT ---
            async def auto_close_initial():
                await asyncio.sleep(60)
                try:
                    # Fetch the message to see if it was touched
                    msg = await event.client.get_messages(event.chat_id, ids=help_msg.id)
                    # If edit_date is None, the user hasn't clicked any buttons yet
                    if msg and msg.edit_date is None:
                        await msg.edit("<i>⏳ Cipher Elite help session expired.</i>", parse_mode='html', buttons=None)
                except Exception:
                    pass
            
            asyncio.create_task(auto_close_initial())
            # ---------------------------------------
            
        except Exception as e:
            # Fallback if inline query fails
            await event.reply(f"❌ <b>Inline help unavailable.</b>\n\n<b>Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def list_plugins(event):
        try:
            if not CMD_LIST:
                await event.reply("⚠️ <b>No plugins loaded yet!</b>", parse_mode='html')
                return
            
            total_plugins = len(CMD_LIST)
            total_commands = sum(len(data['commands']) for data in CMD_LIST.values())
            
            plugins_text = f"✦ <b>𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐋𝐈𝐓𝐄 𝐏𝐋𝐔𝐆𝐈𝐍𝐒</b> ✦\n"
            plugins_text += f"⟡ ═════════════════ ⟡\n"
            plugins_text += f"⚡ <b>Total Plugins:</b> <code>{total_plugins}</code>\n"
            plugins_text += f"⚙️ <b>Total Commands:</b> <code>{total_commands}</code>\n\n"
            
            sorted_plugins = sorted(CMD_LIST.items(), key=lambda x: (x[0] != 'quickhelp', x))
            
            for plugin_name, plugin_data in sorted_plugins:
                command_count = len(plugin_data['commands'])
                if plugin_name == 'quickhelp':
                    plugins_text += f" 💠 <b>{plugin_name.title()}</b> <code>[{command_count} cmds]</code>\n"
                else:
                    plugins_text += f" ├ <b>{plugin_name.title()}</b> <code>[{command_count} cmds]</code>\n"
            
            plugins_text += f"\n🔍 <b>Search:</b> <code>.findplugin &lt;term&gt;</code>\n"
            
            await event.reply(plugins_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.findplugin\s+(.+)"))
    @rishabh()
    async def find_plugin(event):
        try:
            search_term = event.pattern_match.group(1).strip().lower()
            
            if not search_term:
                await event.reply("⚠️ <b>Please provide a search term!</b>\n<code>.findplugin spam</code>", parse_mode='html')
                return
            
            matches = [p for p in CMD_LIST.keys() if search_term in p.lower()]
            
            if not matches:
                await event.reply(f"⚠️ <b>No plugins found matching '{search_term}'</b>", parse_mode='html')
                return
            
            result_text = f"✦ <b>𝐒𝐄𝐀𝐑𝐂𝐇 𝐑𝐄𝐒𝐔𝐋𝐓𝐒: '{search_term}'</b> ✦\n"
            result_text += f"⟡ ═════════════════ ⟡\n\n"
            
            for plugin_name in sorted(matches):
                command_count = len(CMD_LIST[plugin_name]['commands'])
                plugin_desc = CMD_LIST[plugin_name].get('description', 'No description')
                
                result_text += f"❖ <b>{plugin_name.title()}</b>\n"
                result_text += f" ├ <b>Commands:</b> {command_count}\n"
                result_text += f" ├ <b>Info:</b> <i>{plugin_desc[:40]}...</i>\n"
                result_text += f" └ <b>Help:</b> <code>.help {plugin_name}</code>\n\n"
            
            await event.reply(result_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.helpstats"))
    @rishabh()
    async def help_stats(event):
        try:
            if not CMD_LIST:
                await event.reply("⚠️ <b>No plugin data available</b>", parse_mode='html')
                return
            
            real_plugins = {k: v for k, v in CMD_LIST.items() if k != 'quickhelp'}
            total_plugins = len(real_plugins)
            total_commands = sum(len(data['commands']) for data in real_plugins.values())
            
            max_commands = 0
            max_plugin = ""
            for plugin_name, plugin_data in real_plugins.items():
                cmd_count = len(plugin_data['commands'])
                if cmd_count > max_commands:
                    max_commands = cmd_count
                    max_plugin = plugin_name
            
            avg_commands = total_commands / total_plugins if total_plugins > 0 else 0
            
            stats_text = f"✦ <b>𝐂𝐈𝐏𝐇𝐄𝐑 𝐄𝐋𝐈𝐓𝐄 𝐒𝐓𝐀𝐓𝐒</b> ✦\n"
            stats_text += f"⟡ ═════════════════ ⟡\n"
            stats_text += f"⚡ <b>Total Plugins:</b> <code>{total_plugins}</code>\n"
            stats_text += f"⚙️ <b>Total Commands:</b> <code>{total_commands}</code>\n"
            stats_text += f"📈 <b>Avg Commands/Plugin:</b> <code>{avg_commands:.1f}</code>\n"
            
            if max_plugin:
                stats_text += f"🏆 <b>Heaviest Plugin:</b> {max_plugin.title()} ({max_commands})\n\n"
            
            light_plugins = [p for p, d in real_plugins.items() if len(d['commands']) <= 3]
            medium_plugins = [p for p, d in real_plugins.items() if 4 <= len(d['commands']) <= 7]
            heavy_plugins = [p for p, d in real_plugins.items() if len(d['commands']) >= 8]
            
            stats_text += f"❖ <b>Categories:</b>\n"
            stats_text += f" ├ 🟢 Light (≤3 cmds): {len(light_plugins)}\n"
            stats_text += f" ├ 🟡 Medium (4-7 cmds): {len(medium_plugins)}\n"
            stats_text += f" └ 🔴 Heavy (≥8 cmds): {len(heavy_plugins)}\n"
            
            await event.reply(stats_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.quickhelp"))
    @rishabh()
    async def quick_help_guide(event):
        try:
            guide_text = f"✦ <b>𝐐𝐔𝐈𝐂𝐊 𝐇𝐄𝐋𝐏 𝐆𝐔𝐈𝐃𝐄</b> ✦\n"
            guide_text += f"⟡ ═════════════════ ⟡\n\n"
            
            guide_text += f"🎯 <b>Basic Commands:</b>\n"
            guide_text += f" ├ <code>.help</code> - Interactive menu\n"
            guide_text += f" └ <code>.help spam</code> - Direct plugin help\n\n"
            
            guide_text += f"🔍 <b>Discovery:</b>\n"
            guide_text += f" ├ <code>.plugins</code> - List all\n"
            guide_text += f" ├ <code>.findplugin tool</code> - Search\n"
            guide_text += f" └ <code>.helpstats</code> - System stats\n\n"
            
            available_plugins = [p for p in CMD_LIST.keys() if p != 'quickhelp']
            if available_plugins:
                import random
                sample_plugins = random.sample(available_plugins, min(3, len(available_plugins)))
                guide_text += f"🎲 <b>Try These:</b>\n"
                for plugin in sample_plugins:
                    guide_text += f" ├ <code>.help {plugin}</code>\n"
            
            await event.reply(guide_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {str(e)}", parse_mode='html')
