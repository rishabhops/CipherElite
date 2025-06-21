# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    tools
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================
from telethon import events
import time
import platform
import psutil
from datetime import datetime
from plugins.bot import add_handler
from utils.utils import CipherElite

def init(client_instance):
    commands = [
        ".id - Get user/chat ID",
        ".dc - Get DC info"
    ]
    description = "Useful utility tools for your userbot "
    add_handler("tools", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.id"))
    async def get_id(event):
        if event.is_reply:
            msg = await event.get_reply_message()
            user_id = msg.sender_id
            chat_id = event.chat_id
            await event.reply(f" **User ID:** `{user_id}`\n **Chat ID:** `{chat_id}`")
        else:
            await event.reply(f" **Chat ID:** `{event.chat_id}`")



    @CipherElite.on(events.NewMessage(pattern=r"\.dc"))
    async def dc(event):
        if event.is_reply:
            msg = await event.get_reply_message()
            user = await event.client.get_entity(msg.sender_id)
        else:
            user = await event.client.get_me()
        
        dc_id = user.photo.dc_id if user.photo else "No profile photo"
        await event.reply(f" **DC ID:** `{dc_id}`")


# Initialize start time
START_TIME = datetime.now()
