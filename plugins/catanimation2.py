# =============================================================================
#  CipherElite Userbot Plugin
#  Ported from CatPlugins-main
#  License: MIT
# =============================================================================

from telethon import events
import asyncio
from collections import deque
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def init(client_instance):
    commands = [".think - Animation", ".lmao - Animation", ".nothappy - Animation", ".clock - Animation", ".muah - Animation", ".heart - Animation", ".gym - Animation", ".earth - Animation", ".moon - Animation", ".smoon - Animation", ".tmoon - Animation"]
    description = "Animation commands from CatPlugins"
    add_handler("catanimation2", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.think$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("think")
            deq = deque(list("🤔🧐🤔🧐🤔🧐"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.lmao$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("lmao")
            deq = deque(list("😂🤣😂🤣😂🤣"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.nothappy$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("nathappy")
            deq = deque(list("😁☹️😁☹️😁☹️😁"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.clock$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("clock")
            deq = deque(list("🕙🕘🕗🕖🕕🕔🕓🕒🕑🕐🕛"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.muah$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("muah")
            deq = deque(list("😗😙😚😚😘"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.heart$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("heart")
            deq = deque(list("❤️🧡💛💚💙💜🖤"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.gym$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("gym")
            deq = deque(list("🏃‍🏋‍🤸‍🏃‍🏋‍🤸‍🏃‍🏋‍🤸‍"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.earth$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("earth")
            deq = deque(list("🌏🌍🌎🌎🌍🌏🌍🌎"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.moon$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("moon")
            deq = deque(list("🌗🌘🌑🌒🌓🌔🌕🌖"))
            for _ in range(48):
                await asyncio.sleep(0.2)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.smoon$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("smoon")
            animation_interval = 0.2
            animation_ttl = range(101)
            await event.edit("smoon..")
            animation_chars = [
                "🌗🌗🌗🌗🌗\n🌓🌓🌓🌓🌓\n🌗🌗🌗🌗🌗\n🌓🌓🌓🌓🌓\n🌗🌗🌗🌗🌗",
                "🌘🌘🌘🌘🌘\n🌔🌔🌔🌔🌔\n🌘🌘🌘🌘🌘\n🌔🌔🌔🌔🌔\n🌘🌘🌘🌘🌘",
                "🌑🌑🌑🌑🌑\n🌕🌕🌕🌕🌕\n🌑🌑🌑🌑🌑\n🌕🌕🌕🌕🌕\n🌑🌑🌑🌑🌑",
                "🌒🌒🌒🌒🌒\n🌖🌖🌖🌖🌖\n🌒🌒🌒🌒🌒\n🌖🌖🌖🌖🌖\n🌒🌒🌒🌒🌒",
                "🌓🌓🌓🌓🌓\n🌗🌗🌗🌗🌗\n🌓🌓🌓🌓🌓\n🌗🌗🌗🌗🌗\n🌓🌓🌓🌓🌓",
                "🌔🌔🌔🌔🌔\n🌘🌘🌘🌘🌘\n🌔🌔🌔🌔🌔\n🌘🌘🌘🌘🌘\n🌔🌔🌔🌔🌔",
                "🌕🌕🌕🌕🌕\n🌑🌑🌑🌑🌑\n🌕🌕🌕🌕🌕\n🌑🌑🌑🌑🌑\n🌕🌕🌕🌕🌕",
                "🌖🌖🌖🌖🌖\n🌒🌒🌒🌒🌒\n🌖🌖🌖🌖🌖\n🌒🌒🌒🌒🌒\n🌖🌖🌖🌖🌖",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 8])


    @CipherElite.on(events.NewMessage(pattern=r"\.tmoon$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("tmoon")
            animation_interval = 0.2
            animation_ttl = range(96)
            await event.edit("tmoon..")
            animation_chars = [
                "🌗",
                "🌘",
                "🌑",
                "🌒",
                "🌓",
                "🌔",
                "🌕",
                "🌖",
                "🌗",
                "🌘",
                "🌑",
                "🌒",
                "🌓",
                "🌔",
                "🌕",
                "🌖",
                "🌗",
                "🌘",
                "🌑",
                "🌒",
                "🌓",
                "🌔",
                "🌕",
                "🌖",
                "🌗",
                "🌘",
                "🌑",
                "🌒",
                "🌓",
                "🌔",
                "🌕",
                "🌖",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 32])