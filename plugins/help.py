from telethon import events
from config.config import Config
from utils.decorators import rishabh
from plugins.bot import CMD_LIST  # Import the command list

client = None

def init(client_instance):
    global client
    client = client_instance

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
                
                help_text = f"🎭 **Cipher Elite - {plugin_name.title()} Plugin**\n"
                help_text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
                help_text += f"{plugin_data['description']}\n\n"
                help_text += f"**📋 Available Commands:**\n\n"
                
                # Add commands with proper formatting
                for cmd in plugin_data["commands"]:
                    if isinstance(cmd, str) and cmd.strip():
                        if " - " in cmd:
                            cmd_part, desc_part = cmd.split(" - ", 1)
                            # Escape HTML characters
                            escaped_command = cmd_part.strip().replace('<', '&lt;').replace('>', '&gt;')
                            description = desc_part.strip()
                            
                            help_text += f"• `{escaped_command}`\n"
                            help_text += f"  _{description}_\n\n"
                        else:
                            escaped_cmd = cmd.strip().replace('<', '&lt;').replace('>', '&gt;')
                            help_text += f"• `{escaped_cmd}`\n\n"
                
                help_text += f"🔄 **Quick Help:** `.help {plugin_name}`\n"
                help_text += f"📚 **All Plugins:** `.help`\n"
                help_text += f"🤖 **Powered by Cipher Elite**"
                
                await event.reply(help_text, parse_mode='html')
                return
                
            else:
                # Plugin not found - show available plugins
                available_plugins = list(CMD_LIST.keys())
                
                error_text = f"🎭 **Cipher Elite Help System**\n\n"
                error_text += f"❌ **Plugin '{plugin_name}' not found!**\n\n"
                error_text += f"📋 **Available Plugins:**\n"
                
                # Show plugins in rows of 3
                for i in range(0, len(available_plugins), 3):
                    row_plugins = available_plugins[i:i+3]
                    plugin_row = " • ".join([f"`{p}`" for p in row_plugins])
                    error_text += f"{plugin_row}\n"
                
                error_text += f"\n💡 **Usage:** `.help <plugin_name>`\n"
                error_text += f"📚 **Example:** `.help spam`\n"
                error_text += f"🔍 **All Help:** `.help`"
                
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
            await event.reply(f"❌ **Inline help unavailable. Use `.plugins` to see all plugins.**\n\n"
                            f"**Error:** {str(e)}")

    @client.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def list_plugins(event):
        try:
            if not CMD_LIST:
                await event.reply("🎭 **Cipher Elite Plugin Manager**\n\n"
                                "❌ **No plugins loaded yet!**\n"
                                "💡 **Check your plugin directory and restart bot**")
                return
            
            total_plugins = len(CMD_LIST)
            total_commands = sum(len(data['commands']) for data in CMD_LIST.values())
            
            plugins_text = f"🎭 **Cipher Elite Loaded Plugins**\n"
            plugins_text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
            plugins_text += f"📊 **Statistics:**\n"
            plugins_text += f"⚡ **Total Plugins:** {total_plugins}\n"
            plugins_text += f"📂 **Total Commands:** {total_commands}\n\n"
            plugins_text += f"📋 **Plugin List:**\n\n"
            
            # Sort plugins alphabetically and group by type
            sorted_plugins = sorted(CMD_LIST.items(), key=lambda x: x[0])
            
            for plugin_name, plugin_data in sorted_plugins:
                command_count = len(plugin_data['commands'])
                plugins_text += f"🔸 **{plugin_name.title()}**\n"
                plugins_text += f"   📝 {command_count} command{'s' if command_count != 1 else ''}\n"
                plugins_text += f"   🔍 `.help {plugin_name}`\n\n"
            
            plugins_text += f"💡 **Quick Help:** `.help <plugin_name>`\n"
            plugins_text += f"🔍 **Search:** `.findplugin <term>`\n"
            plugins_text += f"🤖 **Powered by Cipher Elite**"
            
            await event.reply(plugins_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"🎭 **Plugin Manager Error**\n\n"
                            f"❌ **Error:** {str(e)}")

    @client.on(events.NewMessage(pattern=r"\.findplugin\s+(.+)"))
    @rishabh()
    async def find_plugin(event):
        try:
            search_term = event.pattern_match.group(1).strip().lower()
            
            if not search_term:
                await event.reply("🔍 **Cipher Elite Plugin Search**\n\n"
                                "❌ **Please provide a search term!**\n\n"
                                "💡 **Usage:** `.findplugin spam`")
                return
            
            # Find matching plugins
            matches = []
            for plugin_name in CMD_LIST.keys():
                if search_term in plugin_name.lower():
                    matches.append(plugin_name)
            
            if not matches:
                await event.reply(f"🔍 **Cipher Elite Plugin Search**\n\n"
                                f"❌ **No plugins found matching '{search_term}'**\n\n"
                                f"💡 **Available plugins:** `.plugins`\n"
                                f"🔍 **Try broader search terms**")
                return
            
            result_text = f"🔍 **Search Results for '{search_term}'**\n\n"
            
            for plugin_name in sorted(matches):
                command_count = len(CMD_LIST[plugin_name]['commands'])
                plugin_desc = CMD_LIST[plugin_name].get('description', 'No description available')
                
                result_text += f"🔸 **{plugin_name.title()}**\n"
                result_text += f"   📝 {command_count} command{'s' if command_count != 1 else ''}\n"
                result_text += f"   📄 _{plugin_desc[:50]}{'...' if len(plugin_desc) > 50 else ''}_\n"
                result_text += f"   🔍 `.help {plugin_name}`\n\n"
            
            result_text += f"📊 **Found {len(matches)} matching plugin{'s' if len(matches) != 1 else ''}**\n"
            result_text += f"🤖 **Powered by Cipher Elite**"
            
            await event.reply(result_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"🔍 **Search Error**\n\n"
                            f"❌ **Error:** {str(e)}")

    @client.on(events.NewMessage(pattern=r"\.helpstats"))
    @rishabh()
    async def help_stats(event):
        try:
            if not CMD_LIST:
                await event.reply("📊 **No plugin data available**")
                return
            
            total_plugins = len(CMD_LIST)
            total_commands = sum(len(data['commands']) for data in CMD_LIST.values())
            
            # Find plugin with most commands
            max_commands = 0
            max_plugin = ""
            for plugin_name, plugin_data in CMD_LIST.items():
                cmd_count = len(plugin_data['commands'])
                if cmd_count > max_commands:
                    max_commands = cmd_count
                    max_plugin = plugin_name
            
            # Calculate average commands per plugin
            avg_commands = total_commands / total_plugins if total_plugins > 0 else 0
            
            stats_text = f"📊 **Cipher Elite Help Statistics**\n"
            stats_text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
            stats_text += f"⚡ **Total Plugins:** {total_plugins}\n"
            stats_text += f"📂 **Total Commands:** {total_commands}\n"
            stats_text += f"📈 **Average Commands/Plugin:** {avg_commands:.1f}\n"
            stats_text += f"🏆 **Most Commands:** {max_plugin.title()} ({max_commands})\n\n"
            
            stats_text += f"🎯 **Plugin Categories:**\n"
            
            # Categorize plugins by command count
            light_plugins = [p for p, d in CMD_LIST.items() if len(d['commands']) <= 3]
            medium_plugins = [p for p, d in CMD_LIST.items() if 4 <= len(d['commands']) <= 7]
            heavy_plugins = [p for p, d in CMD_LIST.items() if len(d['commands']) >= 8]
            
            stats_text += f"🟢 **Light (≤3 cmds):** {len(light_plugins)} plugins\n"
            stats_text += f"🟡 **Medium (4-7 cmds):** {len(medium_plugins)} plugins\n"
            stats_text += f"🔴 **Heavy (≥8 cmds):** {len(heavy_plugins)} plugins\n\n"
            
            stats_text += f"🔧 **Help System Commands:**\n"
            stats_text += f"• `.help` - Interactive help menu\n"
            stats_text += f"• `.help <plugin>` - Direct plugin help\n"
            stats_text += f"• `.plugins` - List all plugins\n"
            stats_text += f"• `.findplugin <term>` - Search plugins\n"
            stats_text += f"• `.helpstats` - This statistics view\n\n"
            stats_text += f"🤖 **Powered by Cipher Elite**"
            
            await event.reply(stats_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"📊 **Stats Error:** {str(e)}")

    @client.on(events.NewMessage(pattern=r"\.quickhelp"))
    @rishabh()
    async def quick_help_guide(event):
        try:
            guide_text = f"⚡ **Cipher Elite Quick Help Guide**\n"
            guide_text += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            guide_text += f"🎯 **Basic Help Commands:**\n"
            guide_text += f"• `.help` - Full interactive help menu\n"
            guide_text += f"• `.help spam` - Direct help for spam plugin\n"
            guide_text += f"• `.help broadcast` - Direct help for broadcast plugin\n\n"
            
            guide_text += f"🔍 **Discovery Commands:**\n"
            guide_text += f"• `.plugins` - List all loaded plugins\n"
            guide_text += f"• `.findplugin tool` - Find plugins containing 'tool'\n"
            guide_text += f"• `.helpstats` - Detailed help system statistics\n\n"
            
            guide_text += f"💡 **Pro Tips:**\n"
            guide_text += f"• Use `.help <plugin>` for instant access to plugin help\n"
            guide_text += f"• Search partial names: `.findplugin spa` finds spam\n"
            guide_text += f"• All help commands work in any chat\n"
            guide_text += f"• Commands are case-insensitive\n\n"
            
            if CMD_LIST:
                # Show 3 random plugins as examples
                import random
                sample_plugins = random.sample(list(CMD_LIST.keys()), min(3, len(CMD_LIST)))
                guide_text += f"🎲 **Try These:**\n"
                for plugin in sample_plugins:
                    guide_text += f"• `.help {plugin}`\n"
                guide_text += "\n"
            
            guide_text += f"🤖 **Powered by Cipher Elite**"
            
            await event.reply(guide_text, parse_mode='html')
            
        except Exception as e:
            await event.reply(f"⚡ **Quick Help Error:** {str(e)}")
