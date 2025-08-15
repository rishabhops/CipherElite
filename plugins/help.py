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
                # Create direct plugin help message
                plugin_data = CMD_LIST[plugin_name]
                
                help_text = f"🎭 <b>Cipher Elite - {plugin_name.title()} Plugin</b>\n"
                help_text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
                help_text += f"{plugin_data['description']}\n\n"
                help_text += f"<b>📋 Available Commands:</b>\n\n"
                
                # Add commands with proper HTML formatting
                for cmd in plugin_data["commands"]:
                    if isinstance(cmd, str) and cmd.strip():
                        if " - " in cmd:
                            cmd_part, desc_part = cmd.split(" - ", 1)
                            # Escape HTML characters
                            escaped_command = cmd_part.strip().replace('<', '&lt;').replace('>', '&gt;')
                            description = desc_part.strip()
                            
                            help_text += f"• <code>{escaped_command}</code>\n"
                            help_text += f"  <i>{description}</i>\n\n"
                        else:
                            escaped_cmd = cmd.strip().replace('<', '&lt;').replace('>', '&gt;')
                            help_text += f"• <code>{escaped_cmd}</code>\n\n"
                
                help_text += f"🔄 <b>Quick Help:</b> <code>.help {plugin_name}</code>\n"
                help_text += f"📚 <b>All Plugins:</b> <code>.help</code>\n"
                help_text += f"🤖 <b>Powered by Cipher Elite</b>"
                
                await event.reply(help_text, parse_mode='html')
                return
                
            else:
                # Plugin not found - show available plugins
                available_plugins = list(CMD_LIST.keys())
                
                error_text = f"🎭 <b>Cipher Elite Help System</b>\n\n"
                error_text += f"❌ <b>Plugin '{plugin_name}' not found!</b>\n\n"
                error_text += f"📋 <b>Available Plugins:</b>\n"
                
                # Show plugins in rows of 3
                for i in range(0, len(available_plugins), 3):
                    row_plugins = available_plugins[i:i+3]
                    plugin_row = " • ".join([f"<code>{p}</code>" for p in row_plugins])
                    error_text += f"{plugin_row}\n"
                
                error_text += f"\n💡 <b>Usage:</b> <code>.help &lt;plugin_name&gt;</code>\n"
                error_text += f"📚 <b>Example:</b> <code>.help spam</code>\n"
                error_text += f"🔍 <b>All Help:</b> <code>.help</code>"
                
                await event.reply(error_text, parse_mode='html')
                return
        
        # Default behavior - show inline help menu
        try:
            results = await event.client.inline_query(
                f"{Config.TG_BOT_USERNAME}",
                "help"
            )
            await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True
            )
            await event.delete()
        except Exception as e:
            # Fallback if inline query fails
            await event.reply(f"❌ <b>Inline help unavailable. Use <code>.plugins</code> to see all plugins.</b>\n\n"
                            f"<b>Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def list_plugins(event):
        try:
            if not CMD_LIST:
                await event.reply("🎭 <b>Cipher Elite Plugin Manager</b>\n\n"
                                "❌ <b>No plugins loaded yet!</b>\n"
                                "💡 <b>Check your plugin directory and restart bot</b>", parse_mode='html')
                return
            
            total_plugins = len(CMD_LIST)
            total_commands = sum(len(data['commands']) for data in CMD_LIST.values())
            
            plugins_text = f"🎭 <b>Cipher Elite Loaded Plugins</b>\n"
            plugins_text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
            plugins_text += f"📊 <b>Statistics:</b>\n"
            plugins_text += f"⚡ <b>Total Plugins:</b> {total_plugins}\n"
            plugins_text += f"📂 <b>Total Commands:</b> {total_commands}\n\n"
            plugins_text += f"📋 <b>Plugin List:</b>\n\n"
            
            # Sort plugins alphabetically, but put quickhelp first
            sorted_plugins = sorted(CMD_LIST.items(), key=lambda x: (x[0] != 'quickhelp', x))
            
            for plugin_name, plugin_data in sorted_plugins:
                command_count = len(plugin_data['commands'])
                
                # Special formatting for quickhelp
                if plugin_name == 'quickhelp':
                    plugins_text += f"⚡ <b>{plugin_name.title()} (Help System)</b>\n"
                else:
                    plugins_text += f"🔸 <b>{plugin_name.title()}</b>\n"
                    
                plugins_text += f"   📝 {command_count} command{'s' if command_count != 1 else ''}\n"
                plugins_text += f"   🔍 <code>.help {plugin_name}</code>\n\n"
            
            plugins_text += f"💡 <b>Quick Help:</b> <code>.help &lt;plugin_name&gt;</code>\n"
            plugins_text += f"🔍 <b>Search:</b> <code>.findplugin &lt;term&gt;</code>\n"
            plugins_text += f"🤖 <b>Powered by Cipher Elite</b>"
            
            await event.reply(plugins_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"🎭 <b>Plugin Manager Error</b>\n\n"
                            f"❌ <b>Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.findplugin\s+(.+)"))
    @rishabh()
    async def find_plugin(event):
        try:
            search_term = event.pattern_match.group(1).strip().lower()
            
            if not search_term:
                await event.reply("🔍 <b>Cipher Elite Plugin Search</b>\n\n"
                                "❌ <b>Please provide a search term!</b>\n\n"
                                "💡 <b>Usage:</b> <code>.findplugin spam</code>", parse_mode='html')
                return
            
            # Find matching plugins
            matches = []
            for plugin_name in CMD_LIST.keys():
                if search_term in plugin_name.lower():
                    matches.append(plugin_name)
            
            if not matches:
                await event.reply(f"🔍 <b>Cipher Elite Plugin Search</b>\n\n"
                                f"❌ <b>No plugins found matching '{search_term}'</b>\n\n"
                                f"💡 <b>Available plugins:</b> <code>.plugins</code>\n"
                                f"🔍 <b>Try broader search terms</b>", parse_mode='html')
                return
            
            result_text = f"🔍 <b>Search Results for '{search_term}'</b>\n\n"
            
            for plugin_name in sorted(matches):
                command_count = len(CMD_LIST[plugin_name]['commands'])
                plugin_desc = CMD_LIST[plugin_name].get('description', 'No description available')
                
                result_text += f"🔸 <b>{plugin_name.title()}</b>\n"
                result_text += f"   📝 {command_count} command{'s' if command_count != 1 else ''}\n"
                result_text += f"   📄 <i>{plugin_desc[:50]}{'...' if len(plugin_desc) > 50 else ''}</i>\n"
                result_text += f"   🔍 <code>.help {plugin_name}</code>\n\n"
            
            result_text += f"📊 <b>Found {len(matches)} matching plugin{'s' if len(matches) != 1 else ''}</b>\n"
            result_text += f"🤖 <b>Powered by Cipher Elite</b>"
            
            await event.reply(result_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"🔍 <b>Search Error</b>\n\n"
                            f"❌ <b>Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.helpstats"))
    @rishabh()
    async def help_stats(event):
        try:
            if not CMD_LIST:
                await event.reply("📊 <b>No plugin data available</b>", parse_mode='html')
                return
            
            # Exclude quickhelp from stats calculations since it's a help system plugin
            real_plugins = {k: v for k, v in CMD_LIST.items() if k != 'quickhelp'}
            total_plugins = len(real_plugins)
            total_commands = sum(len(data['commands']) for data in real_plugins.values())
            
            # Find plugin with most commands
            max_commands = 0
            max_plugin = ""
            for plugin_name, plugin_data in real_plugins.items():
                cmd_count = len(plugin_data['commands'])
                if cmd_count > max_commands:
                    max_commands = cmd_count
                    max_plugin = plugin_name
            
            # Calculate average commands per plugin
            avg_commands = total_commands / total_plugins if total_plugins > 0 else 0
            
            stats_text = f"📊 <b>Cipher Elite Help Statistics</b>\n"
            stats_text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
            stats_text += f"⚡ <b>Total Plugins:</b> {total_plugins}\n"
            stats_text += f"📂 <b>Total Commands:</b> {total_commands}\n"
            stats_text += f"📈 <b>Average Commands/Plugin:</b> {avg_commands:.1f}\n"
            
            if max_plugin:
                stats_text += f"🏆 <b>Most Commands:</b> {max_plugin.title()} ({max_commands})\n\n"
            
            stats_text += f"🎯 <b>Plugin Categories:</b>\n"
            
            # Categorize plugins by command count
            light_plugins = [p for p, d in real_plugins.items() if len(d['commands']) <= 3]
            medium_plugins = [p for p, d in real_plugins.items() if 4 <= len(d['commands']) <= 7]
            heavy_plugins = [p for p, d in real_plugins.items() if len(d['commands']) >= 8]
            
            stats_text += f"🟢 <b>Light (≤3 cmds):</b> {len(light_plugins)} plugins\n"
            stats_text += f"🟡 <b>Medium (4-7 cmds):</b> {len(medium_plugins)} plugins\n"
            stats_text += f"🔴 <b>Heavy (≥8 cmds):</b> {len(heavy_plugins)} plugins\n\n"
            
            stats_text += f"🔧 <b>Help System Commands:</b>\n"
            stats_text += f"• <code>.help</code> - Interactive help menu\n"
            stats_text += f"• <code>.help &lt;plugin&gt;</code> - Direct plugin help\n"
            stats_text += f"• <code>.plugins</code> - List all plugins\n"
            stats_text += f"• <code>.findplugin &lt;term&gt;</code> - Search plugins\n"
            stats_text += f"• <code>.helpstats</code> - This statistics view\n"
            stats_text += f"• <code>.quickhelp</code> - Quick help guide\n\n"
            stats_text += f"🤖 <b>Powered by Cipher Elite</b>"
            
            await event.reply(stats_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"📊 <b>Stats Error:</b> {str(e)}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.quickhelp"))
    @rishabh()
    async def quick_help_guide(event):
        try:
            guide_text = f"⚡ <b>Cipher Elite Quick Help Guide</b>\n"
            guide_text += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            guide_text += f"🎯 <b>Basic Help Commands:</b>\n"
            guide_text += f"• <code>.help</code> - Full interactive help menu\n"
            guide_text += f"• <code>.help spam</code> - Direct help for spam plugin\n"
            guide_text += f"• <code>.help broadcast</code> - Direct help for broadcast plugin\n\n"
            
            guide_text += f"🔍 <b>Discovery Commands:</b>\n"
            guide_text += f"• <code>.plugins</code> - List all loaded plugins\n"
            guide_text += f"• <code>.findplugin tool</code> - Find plugins containing 'tool'\n"
            guide_text += f"• <code>.helpstats</code> - Detailed help system statistics\n\n"
            
            guide_text += f"💡 <b>Pro Tips:</b>\n"
            guide_text += f"• Use <code>.help &lt;plugin&gt;</code> for instant access to plugin help\n"
            guide_text += f"• Search partial names: <code>.findplugin spa</code> finds spam\n"
            guide_text += f"• All help commands work in any chat\n"
            guide_text += f"• Commands are case-insensitive\n\n"
            
            # Show available plugins excluding quickhelp itself
            available_plugins = [p for p in CMD_LIST.keys() if p != 'quickhelp']
            if available_plugins:
                import random
                sample_plugins = random.sample(available_plugins, min(3, len(available_plugins)))
                guide_text += f"🎲 <b>Try These:</b>\n"
                for plugin in sample_plugins:
                    guide_text += f"• <code>.help {plugin}</code>\n"
                guide_text += "\n"
            
            guide_text += f"📋 <b>Available in Help Menu:</b>\n"
            guide_text += f"Click the <b>Quickhelp</b> button in <code>.help</code> menu\n\n"
            guide_text += f"🤖 <b>Powered by Cipher Elite</b>"
            
            await event.reply(guide_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"⚡ <b>Quick Help Error:</b> {str(e)}", parse_mode='html')
