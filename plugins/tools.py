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
        ".info - Get user info",
        ".sys - System information",
        ".dc - Get DC info",
        ".stats - Bot statistics"
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

    @CipherElite.on(events.NewMessage(pattern=r"\.info"))
    async def info(event):
        if event.is_reply:
            msg = await event.get_reply_message()
            user = await event.client.get_entity(msg.sender_id)
            text = f"""** User Information**

** ID:** `{user.id}`
** First Name:** `{user.first_name}`
** Username:** `@{user.username if user.username else 'None'}`
** Bot:** `{'Yes' if user.bot else 'No'}`
** Verified:** `{'Yes' if user.verified else 'No'}`"""
            await event.reply(text)

    @CipherElite.on(events.NewMessage(pattern=r"\.sys"))
    async def sysinfo(event):
        cpu_freq = psutil.cpu_freq().current
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        
        text = f"""** System Information**

**CPU Frequency:** `{cpu_freq:.2f}MHz`
**CPU Usage:** `{cpu_usage}%`
**RAM Usage:** `{ram_usage}%`
**Disk Usage:** `{disk_usage}%`"""
        await event.reply(text)

    @CipherElite.on(events.NewMessage(pattern=r"\.dc"))
    async def dc(event):
        if event.is_reply:
            msg = await event.get_reply_message()
            user = await event.client.get_entity(msg.sender_id)
        else:
            user = await event.client.get_me()
        
        dc_id = user.photo.dc_id if user.photo else "No profile photo"
        await event.reply(f" **DC ID:** `{dc_id}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.stats"))
    async def stats(event):
        total_users = 0
        total_chats = 0
        async for dialog in event.client.iter_dialogs():
            if dialog.is_user:
                total_users += 1
            else:
                total_chats += 1
                
        text = f"""** Bot Statistics**

** Total Users:** `{total_users}`
** Total Chats:** `{total_chats}`
** Commands Loaded:** `{len(CMD_LIST)}`"""
        await event.reply(text)

# Initialize start time
START_TIME = datetime.now()
