# =============================================================================
#  CipherElite Userbot Plugin
#  Ported from CatPlugins-main
#  License: MIT
# =============================================================================

from telethon import events
import asyncio
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def init(client_instance):
    commands = [".loading - Animation", ".asquare - Animation", ".up - Animation", ".hart - Animation", ".anim - Animation", ".fnl - Animation", ".monkey - Animation", ".herber - Animation", ".hand - Animation", ".gsg - Animation", ".theart - Animation"]
    description = "Animation commands from CatPlugins"
    add_handler("catanimation5", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.loading$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.3
            animation_ttl = range(20)
            event = await event.reply("▯")
            animation_chars = ["▮", "▯", "▬", "▭", "‎"]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 4])


    @CipherElite.on(events.NewMessage(pattern=r"\.asquare$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.3
            animation_ttl = range(20)
            event = await event.reply("◨")
            animation_chars = ["◧", "◨", "◧", "◨", "‎"]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 4])


    @CipherElite.on(events.NewMessage(pattern=r"\.up$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.3
            animation_ttl = range(20)
            event = await event.reply("╻")
            animation_chars = ["╹", "╻", "╹", "╻", "‎"]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 4])


    @CipherElite.on(events.NewMessage(pattern=r"\.hart$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.5
            animation_ttl = range(20)
            event = await event.reply("❤️")
            animation_chars = ["🖤", "❤️", "🖤", "❤️", "‎"]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 4])


    @CipherElite.on(events.NewMessage(pattern=r"\.anim$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 1
            animation_ttl = range(20)
            event = await event.reply("😢")
            animation_chars = [
                "😁",
                "😧",
                "😡",
                "😢",
                "‎**Repo of catuserbot**",
                "😁",
                "😧",
                "😡",
                "😢",
                "__**[Good to see you guys....]**__(github.com/TgCatUB/catuserbot)",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 10])


    @CipherElite.on(events.NewMessage(pattern=r"\.fnl$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 2
            animation_ttl = range(6)
            event = await event.reply("Hey There....")
            animation_chars = ["😁🏿", "😁🏾", "😁🏽", "😁🏼", "‎😁", "**Good to see you friend....**"]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 6])


    @CipherElite.on(events.NewMessage(pattern=r"\.monkey$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 2
            animation_ttl = range(12)
            event = await event.reply("Hey There....")
            animation_chars = ["🐵", "🙉", "🙈", "🙊", "🖕‎🐵🖕", "**Good to see you friend....**"]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 6])


    @CipherElite.on(events.NewMessage(pattern=r"\.herber$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 2
            animation_ttl = range(10)
            event = await event.reply("Power On......")
            animation_chars = [
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 10%\n\n    ●○○○○○○○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 5.9%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 8.13GB\n    **🔹used:** 33.77GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●●○○○\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 158.98GB\n    **🔹recv:** 146.27GB\n    **🔹sent_packets:** 84518799\n    **🔹recv_packets:** 159720314\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 30%\n\n    ●●●○○○○○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 20.4%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 7.18GB\n    **🔹used:** 28.26GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●●●●●\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 146.27GB\n    **🔹recv:** 124.33GB\n    **🔹sent_packets:** 54635686\n    **🔹recv_packets:** 143565654\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 60%\n\n    ●●●●●●○○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 60.9%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 6.52GB\n    **🔹used:** 35.78GB\n    **🔹total:** 60.0GB\n    \n    ●●●○○○○○○○\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 124.33GB\n    **🔹recv:** 162.48GB\n    **🔹sent_packets:** 25655655\n    **🔹recv_packets:** 165289456\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 100%\n\n    ●●●●●●●●●●\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 100.0%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 9.81GB\n    **🔹used:** 30.11GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●●●●●\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 162.48GB\n    **🔹recv:** 175.75GB\n    **🔹sent_packets:** 56565435\n    **🔹recv_packets:** 135345655\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 70%\n\n    ●●●●●●●○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 80.4%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 5.76GB\n    **🔹used:** 29.35GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●●○○○\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 175.75GB\n    **🔹recv:** 118.55GB\n    **🔹sent_packets:** 36547698\n    **🔹recv_packets:** 185466554\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 60%\n\n    ●●●●●●○○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 62.9%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 8.23GB\n    **🔹used:** 33.32GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●○○○○\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 118.55GB\n    **🔹recv:** 168.65GB\n    **🔹sent_packets:** 24786554\n    **🔹recv_packets:** 156745865\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 30%\n\n    ●●●○○○○○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 30.6%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 9.75GB\n    **🔹used:** 36.54GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●●●●●\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 168.65GB\n    **🔹recv:** 128.35GB\n    **🔹sent_packets:** 56565435\n    **🔹recv_packets:** 1475823589\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 10%\n\n    ●○○○○○○○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 10.2%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 10.20GB\n    **🔹used:** 25.40GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●○○○○\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 128.35GB\n    **🔹recv:** 108.31GB\n    **🔹sent_packets:** 54635686\n    **🔹recv_packets:** 157865426\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 100%\n\n    ●●●●●●●●●●\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 100.0%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 5.25GB\n    **🔹used:** 31.14GB\n    **🔹total:** 60.0GB\n    \n    ●●●●●●●●●●\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 108.31GB\n    **🔹recv:** 167.17GB\n    **🔹sent_packets:** 84518799\n    **🔹recv_packets:** 124575356\n\n\n**===================**\n",
                "**===================**\n      **Server Details**  \n**===================**\n\n\n**=>>>   CPU   <<<=**\n\n    **🔹current_freq:** 2500.09MHz\n    **🔹total_usage:** 70%\n\n    ●●●●●●●○○○\n\n    **🔹cpu core**\n\n        **🔹core_usage:** 76.2%\n        **🔹current_freq:** 2500.09MHz\n        |██████████▉  |\n       \n**=>>>   RAM   <<<=**\n\n    **🔹free:** 8.01GB\n    **🔹used:** 33.27GB\n    **🔹total:** 60.0GB\n    \n    ●●●○○○○○○○\n\n\n**=>>>   DISK   <<<=**\n\n   **🔹free:** 224.12GB\n    **🔹used:** 131.84GB\n    **🔹total:** 375.02GB\n    **🔹usage:** 37.0%\n\n    |████▍        |\n\n\n**=>>>   NETWORK   <<<=**\n\n    **🔹sent:** 167.17GB\n    **🔹recv:** 158.98GB\n    **🔹sent_packets:** 36547698\n    **🔹recv_packets:** 165455856\n\n\n**===================**\n",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 10])


    @CipherElite.on(events.NewMessage(pattern=r"\.hand$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 1
            animation_ttl = range(13)
            event = await event.reply("🖐️")
            animation_chars = [
                "👈",
                "👉",
                "☝️",
                "👆",
                "🖕",
                "👇",
                "✌️",
                "🤞",
                "🖖",
                "🤘",
                "🤙",
                "🖐️",
                "👌",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 13])


    @CipherElite.on(events.NewMessage(pattern=r"\.gsg$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 1
            animation_ttl = range(12)
            event = await event.reply("ContDown....")
            animation_chars = [
                "🔟",
                "9️⃣",
                "8️⃣",
                "7️⃣",
                "6️⃣",
                "5️⃣",
                "4️⃣",
                "3️⃣",
                "2️⃣",
                "1️⃣",
                "0️⃣",
                "🆘",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 12])


    @CipherElite.on(events.NewMessage(pattern=r"\.theart$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.3
            animation_ttl = range(54)
            event = await event.reply("🖤")
            animation_chars = [
                "❤️",
                "🧡",
                "💛",
                "💚",
                "💙",
                "💜",
                "🖤",
                "💘",
                "💝",
                "❤️",
                "🧡",
                "💛",
                "💚",
                "💙",
                "💜",
                "🖤",
                "💘",
                "💝",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 18])