# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    xiaomi
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .firmware, .vendor, .xspecs, .fastboot, .recovery, .pb, .of
# =============================================================================

from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "utilities"

COMMANDS = {
    "firmware": "latest MIUI firmware",
    "vendor": "latest MIUI vendor",
    "xspecs": "device specs",
    "fastboot": "latest MIUI fastboot",
    "recovery": "latest MIUI recovery",
    "pb": "latest PBRP",
    "of": "latest OrangeFox recovery",
}

def init(client_instance):
    commands = [f".{cmd} <codename> - {desc}" for cmd, desc in COMMANDS.items()]
    description = "Xiaomi firmware/specs via @XiaomiGeeksBot"
    add_handler("xiaomi", commands, description)

async def register_commands():
    for cmd, desc in COMMANDS.items():
        @CipherElite.on(events.NewMessage(pattern=rf"\.{cmd}(?: |$)([\s\S]*)"))
        @rishabh()
        async def xiaomi_cmd(event, cmd=cmd):
            link = event.pattern_match.group(1).strip()
            if not link:
                await event.reply(f"❌ Provide a device codename. Example: `.{cmd} whyred`")
                return
            status = await event.reply("```Processing```")
            try:
                async with event.client.conversation("@XiaomiGeeksBot") as conv:
                    response = conv.wait_event(
                        events.NewMessage(incoming=True, from_users=774181428)
                    )
                    await conv.send_message(f"/{cmd} {link}")
                    respond = await response
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await status.delete()
                    await event.client.forward_messages(event.chat_id, respond.message)
            except YouBlockedUserError:
                await status.edit("```Unblock @XiaomiGeeksBot plox```")
            except Exception as e:
                await status.edit(f"⚠️ Error: `{str(e)}`")
