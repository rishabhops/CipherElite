# =============================================================================
#  CipherElite — Quick Help System  (minimalist edition)
#  Target path:  plugins/quickhelp.py
#
#  Commands:  .help  .help <plugin>  .plugins  .findplugin  .helpstats  .quickhelp
#  Styling inherited from utils/help_ui.py so it matches the inline menu.
# =============================================================================

import asyncio
import random
from telethon import events
from config.config import Config
from utils.decorators import rishabh
from utils import help_ui
from plugins.bot import CMD_LIST  # Shared command registry

client = None


def init(client_instance):
    global client
    client = client_instance

    # Register quickhelp as a pseudo-plugin so it shows in the help menu.
    CMD_LIST["quickhelp"] = {
        "commands": [
            ".help - Interactive help menu with all plugins",
            ".help <plugin> - Direct help for a specific plugin",
            ".plugins - List all loaded plugins with stats",
            ".findplugin <term> - Search plugins by name/keyword",
            ".helpstats - Detailed help-system analytics",
            ".quickhelp - This quick guide",
        ],
        "description": "Cipher Elite help system — complete guide to the help features",
    }

# NOTE: the old add_command() helper was removed. It treated CMD_LIST entries as
# plain lists, but the registry stores dicts ({"commands": [...], "description": ...}).
# Calling it would have corrupted the menu. Use plugins.bot.add_handler() instead.


def _sorted_plugin_names():
    names = list(CMD_LIST.keys())
    names.sort(key=lambda x: (x != 'quickhelp', x))
    return names


async def register_commands():

    @client.on(events.NewMessage(pattern=r"\.help(?:\s+(.+))?"))
    @rishabh()
    async def help_handler(event):
        plugin_name = event.pattern_match.group(1)

        # ── Direct plugin help: .help spam / .help broadcast ─────────────────
        if plugin_name:
            plugin_name = plugin_name.strip().lower()

            if plugin_name in CMD_LIST:
                text = help_ui.build_plugin_text(plugin_name, CMD_LIST[plugin_name])
                await event.reply(text, parse_mode='html')
                return

            # Plugin not found → show the available ones inside an expandable quote.
            names = _sorted_plugin_names()
            error_text = (
                f"⚠️ <b>'{help_ui.esc(plugin_name)}' not found</b>\n\n"
                f"❖ <b>Available modules</b>\n"
                f"<blockquote expandable>"
            )
            for name in names:
                error_text += f"{help_ui.icon_for(name)} <code>{help_ui.esc(name)}</code>\n"
            error_text += "</blockquote>\n"
            error_text += f"💡 <code>.help &lt;plugin&gt;</code>"
            await event.reply(error_text, parse_mode='html')
            return

        # ── No argument → open the inline menu (bot-side styling) ─────────────
        try:
            results = await event.client.inline_query(f"{Config.TG_BOT_USERNAME}", "help")
            help_msg = await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True,
            )
            await event.delete()

            # Auto-close if untouched after 60s
            async def auto_close_initial():
                await asyncio.sleep(60)
                try:
                    msg = await event.client.get_messages(event.chat_id, ids=help_msg.id)
                    if msg and msg.edit_date is None:
                        await msg.edit(
                            "<i>⏳ Help session expired — dobara <code>.help</code> bhejo</i>",
                            parse_mode='html',
                            buttons=None,
                        )
                except Exception:
                    pass

            asyncio.create_task(auto_close_initial())

        except Exception as e:
            await event.reply(
                f"❌ <b>Inline help unavailable.</b>\n\n<b>Error:</b> {help_ui.esc(str(e))}",
                parse_mode='html',
            )

    @client.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def list_plugins(event):
        try:
            if not CMD_LIST:
                await event.reply("⚠️ <b>No plugins loaded yet!</b>", parse_mode='html')
                return

            names = _sorted_plugin_names()
            total_commands = sum(len(d['commands']) for d in CMD_LIST.values())

            text = (
                f"📦 <b>Plugins</b>   "
                f"<code>{len(names)} modules · {total_commands} cmds</code>\n\n"
                f"<blockquote expandable>"
            )
            for name in names:
                count = len(CMD_LIST[name]['commands'])
                text += f"{help_ui.icon_for(name)} <code>{help_ui.esc(name)}</code>  <b>[{count}]</b>\n"
            text += "</blockquote>\n"
            text += f"🔍 <code>.findplugin &lt;term&gt;</code>"

            await event.reply(text, parse_mode='html')

        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {help_ui.esc(str(e))}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.findplugin\s+(.+)"))
    @rishabh()
    async def find_plugin(event):
        try:
            search_term = event.pattern_match.group(1).strip().lower()
            if not search_term:
                await event.reply(
                    "⚠️ <b>Search term chahiye!</b>\n<code>.findplugin spam</code>",
                    parse_mode='html',
                )
                return

            matches = [p for p in CMD_LIST.keys() if search_term in p.lower()]
            if not matches:
                await event.reply(
                    f"⚠️ <b>Koi plugin nahi mila:</b> <code>{help_ui.esc(search_term)}</code>",
                    parse_mode='html',
                )
                return

            text = (
                f"🔍 <b>Search</b> · <code>{help_ui.esc(search_term)}</code>"
                f"   ·   {len(matches)} found\n\n"
            )
            for name in sorted(matches):
                count = len(CMD_LIST[name]['commands'])
                desc = CMD_LIST[name].get('description', 'No description')
                text += (
                    f"{help_ui.icon_for(name)} <b>{help_ui.esc(name.title())}</b> <code>[{count}]</code>\n"
                    f"<blockquote>{help_ui.esc(desc[:80])}</blockquote>"
                    f"❯ <code>.help {help_ui.esc(name)}</code>\n\n"
                )

            await event.reply(text, parse_mode='html')

        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {help_ui.esc(str(e))}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.helpstats"))
    @rishabh()
    async def help_stats(event):
        try:
            real = {k: v for k, v in CMD_LIST.items() if k != 'quickhelp'}
            if not real:
                await event.reply("⚠️ <b>No plugin data available</b>", parse_mode='html')
                return

            total_plugins = len(real)
            total_commands = sum(len(d['commands']) for d in real.values())
            avg = total_commands / total_plugins if total_plugins else 0

            heaviest = max(real.items(), key=lambda kv: len(kv[1]['commands']))
            heaviest_name, heaviest_count = heaviest[0], len(heaviest[1]['commands'])

            light = [p for p, d in real.items() if len(d['commands']) <= 3]
            medium = [p for p, d in real.items() if 4 <= len(d['commands']) <= 7]
            heavy = [p for p, d in real.items() if len(d['commands']) >= 8]

            text = (
                f"📊 <b>Help Stats</b>\n\n"
                f"<blockquote>"
                f"⚡ <b>{total_plugins}</b> plugins\n"
                f"⚙️ <b>{total_commands}</b> commands\n"
                f"📈 <b>{avg:.1f}</b> avg / plugin\n"
                f"🏆 {help_ui.icon_for(heaviest_name)} "
                f"{help_ui.esc(heaviest_name.title())} <code>({heaviest_count})</code>"
                f"</blockquote>\n"
                f"<blockquote>"
                f"🟢 Light   <code>{help_ui.stat_bar(len(light), total_plugins)}</code>  {len(light)}\n"
                f"🟡 Medium  <code>{help_ui.stat_bar(len(medium), total_plugins)}</code>  {len(medium)}\n"
                f"🔴 Heavy   <code>{help_ui.stat_bar(len(heavy), total_plugins)}</code>  {len(heavy)}"
                f"</blockquote>"
            )

            await event.reply(text, parse_mode='html')

        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {help_ui.esc(str(e))}", parse_mode='html')

    @client.on(events.NewMessage(pattern=r"\.quickhelp"))
    @rishabh()
    async def quick_help_guide(event):
        try:
            text = help_ui.build_quickhelp_text()

            available = [p for p in CMD_LIST.keys() if p != 'quickhelp']
            if available:
                sample = random.sample(available, min(3, len(available)))
                text += f"\n\n🎲 <b>Try these</b>\n<blockquote>"
                for plugin in sample:
                    text += f"{help_ui.icon_for(plugin)} <code>.help {help_ui.esc(plugin)}</code>\n"
                text += "</blockquote>"

            await event.reply(text, parse_mode='html')

        except Exception as e:
            await event.reply(f"❌ <b>Error:</b> {help_ui.esc(str(e))}", parse_mode='html')