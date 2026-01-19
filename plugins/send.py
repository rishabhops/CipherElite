from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import os

# ─────────────── INIT ───────────────
def init(client_instance):
    commands = [
        ".send <plugin_name> - Send a plugin file from server"
    ]
    description = "📦 Send Plugin - Send any installed plugin file"
    add_handler("send", commands, description)


# ───────── REGISTER COMMAND ─────────
async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.send\s+(.+)"))
    @rishabh()
    async def send_plugin(event):
        try:
            plugin_name = event.pattern_match.group(1).strip().lower()

            plugin_path = f"./plugins/{plugin_name}.py"

            if not os.path.exists(plugin_path):
                return await event.reply(
                    "🎭 **Cipher Elite – Send Plugin**\n\n"
                    "❌ **Plugin not found!**\n"
                    f"📄 `{plugin_name}.py` does not exist."
                )

            caption = (
                "🎭 **Cipher Elite Plugin Sender**\n\n"
                f"📦 **Plugin:** `{plugin_name}.py`\n"
                f"👤 **Requested by:** {event.sender.first_name}\n\n"
                "⚡ **[Powered by Cipher Elite](https://t.me/cipherelite_support)**"
            )

            await event.client.send_file(
                event.chat_id,
                plugin_path,
                caption=caption,
                force_document=True,
                reply_to=event.reply_to_msg_id or event.id
            )

            await event.delete()

        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ `{str(e)}`"
            )
