from telethon import events
from config.config import Config

client = None
CMD_LIST = {}

def init(client_instance):
    global client
    client = client_instance

def add_command(plugin_name, commands):
    global CMD_LIST
    if plugin_name not in CMD_LIST:
        CMD_LIST[plugin_name] = []
    CMD_LIST[plugin_name].extend(commands)

async def register_commands():
    @client.on(events.NewMessage(pattern=r"\.help"))
    async def help_handler(event):
        results = await event.client.inline_query(
            f"{Config.TG_BOT_USERNAME}",  # Using your bot username
            "help"
        )
        await results[0].click(
            event.chat_id,
            reply_to=event.reply_to_msg_id,
            hide_via=True
        )
        await event.delete()
        