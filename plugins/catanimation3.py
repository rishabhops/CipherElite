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
    commands = [".star - Animation", ".boxs - Animation", ".rain - Animation", ".deploy - Animation", ".dump - Animation", ".fleaveme - Animation", ".loveu - Animation", ".plane - Animation", ".police - Animation", ".jio - Animation", ".solarsystem - Animation"]
    description = "Animation commands from CatPlugins"
    add_handler("catanimation3", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.star$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("`stars.....`")
            deq = deque(list("🦋✨🦋✨🦋✨🦋✨"))
            for _ in range(48):
                await asyncio.sleep(0.3)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.boxs$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("`boxs...`")
            deq = deque(list("🟥🟧🟨🟩🟦🟪🟫⬛⬜"))
            for _ in range(999):
                await asyncio.sleep(0.3)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.rain$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("`Raining.......`")
            deq = deque(list("🌬☁️🌩🌨🌧🌦🌥⛅🌤"))
            for _ in range(48):
                await asyncio.sleep(0.3)
                await event.edit("".join(deq))
                deq.rotate(1)


    @CipherElite.on(events.NewMessage(pattern=r"\.deploy$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 3
            animation_ttl = range(12)
            event = await event.reply("`Deploying...`")
            mention = f"[{event.sender.first_name}](tg://user?id={event.sender_id})"
            animation_chars = [
                "**Heroku Connecting To Latest Github Build **",
                f"**Build started by user** {mention}",
                f"**Deploy** `535a74f0` **by user** {mention}",
                "**Restarting Heroku Server...**",
                "**State changed from up to starting**",
                "**Stopping all processes with SIGTERM**",
                "**Process exited with** `status 143`",
                "**Starting process with command** `python3 -m userbot`",
                "**State changed from starting to up**",
                "__INFO:Userbot:Logged in as 557667062__",
                "__INFO:Userbot:Successfully loaded all plugins__",
                "**Build Succeeded**",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 12])


    @CipherElite.on(events.NewMessage(pattern=r"\.dump(?:\s|$)([\s\S]*)"))
    @rishabh()
    async def _(event):
            "Animation Command"
            try:
                obj = event.pattern_match.group(1)
                if len(obj) != 3:
                    return await event.reply("`Input length must be 3 or empty`")
                inp = " ".join(obj)
            except IndexError:
                inp = "🥞 🎂 🍫"
            event = await event.reply("`droping....`")
            u, t, g, o, s, n = inp.split(), "🗑", "<(^_^ <)", "(> ^_^)>", "⠀ ", "\n"
            h = [(u[0], u[1], u[2]), (u[0], u[1], ""), (u[0], "", "")]
            for something in reversed(
                [
                    [
                        "".join(x)
                        for x in (
                            f + (s, g, s + s * f.count(""), t),
                            f + (g, s * 2 + s * f.count(""), t),
                            f[:i] + (o, f[i], s * 2 + s * f.count(""), t),
                            f[:i] + (s + s * f.count(""), o, f[i], s, t),
                            f[:i] + (s * 2 + s * f.count(""), o, f[i], t),
                            f[:i] + (s * 3 + s * f.count(""), o, t),
                            f[:i] + (s * 3 + s * f.count(""), g, t),
                        )
                    ]
                    for i, f in enumerate(reversed(h))
                ]
            ):
                for something_else in something:
                    await asyncio.sleep(0.3)
                    await event.edit(something_else)


    @CipherElite.on(events.NewMessage(pattern=r"\.fleaveme$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 1
            animation_ttl = range(10)
            animation_chars = [
                "⬛⬛⬛\n⬛⬛⬛\n⬛⬛⬛",
                "⬛⬛⬛\n⬛🔄⬛\n⬛⬛⬛",
                "⬛⬆️⬛\n⬛🔄⬛\n⬛⬛⬛",
                "⬛⬆️↗️\n⬛🔄⬛\n⬛⬛⬛",
                "⬛⬆️↗️\n⬛🔄➡️\n⬛⬛⬛",
                "⬛⬆️↗️\n⬛🔄➡️\n⬛⬛↘️",
                "⬛⬆️↗️\n⬛🔄➡️\n⬛⬇️↘️",
                "⬛⬆️↗️\n⬛🔄➡️\n↙️⬇️↘️",
                "⬛⬆️↗️\n⬅️🔄➡️\n↙️⬇️↘️",
                "↖️⬆️↗️\n⬅️🔄➡️\n↙️⬇️↘️",
            ]
            event = await event.reply("fleaveme....")
            await asyncio.sleep(2)
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 10])


    @CipherElite.on(events.NewMessage(pattern=r"\.loveu$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.5
            animation_ttl = range(70)
            event = await event.reply("loveu")
            animation_chars = [
                "😀",
                "👩‍🎨",
                "😁",
                "😂",
                "🤣",
                "😃",
                "😄",
                "😅",
                "😊",
                "☺",
                "🙂",
                "🤔",
                "🤨",
                "😐",
                "😑",
                "😶",
                "😣",
                "😥",
                "😮",
                "🤐",
                "😯",
                "😴",
                "😔",
                "😕",
                "☹",
                "🙁",
                "😖",
                "😞",
                "😟",
                "😢",
                "😭",
                "🤯",
                "💔",
                "❤",
                "I Love You❤",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 35])


    @CipherElite.on(events.NewMessage(pattern=r"\.plane$"))
    @rishabh()
    async def _(event):
            "animation command"
            event = await event.reply("Wait for plane...")
            await event.edit("✈-------------")
            await event.edit("-✈------------")
            await event.edit("--✈-----------")
            await event.edit("---✈----------")
            await event.edit("----✈---------")
            await event.edit("-----✈--------")
            await event.edit("------✈-------")
            await event.edit("-------✈------")
            await event.edit("--------✈-----")
            await event.edit("---------✈----")
            await event.edit("----------✈---")
            await event.edit("-----------✈--")
            await event.edit("------------✈-")
            await event.edit("-------------✈")
            await asyncio.sleep(3)


    @CipherElite.on(events.NewMessage(pattern=r"\.police$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.3
            animation_ttl = range(12)
            event = await event.reply("Police")
            mention = f"[{event.sender.first_name}](tg://user?id={event.sender_id})"
            animation_chars = [
                "🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵",
                "🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴",
                "🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵",
                "🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴",
                "🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵",
                "🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴",
                "🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵",
                "🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴",
                "🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵",
                "🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴\n🔵🔵🔵⬜⬜⬜🔴🔴🔴",
                "🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵\n🔴🔴🔴⬜⬜⬜🔵🔵🔵",
                f"{mention} **Police iz Here**",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 12])


    @CipherElite.on(events.NewMessage(pattern=r"\.jio$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 1
            animation_ttl = range(19)
            event = await event.reply("jio network boosting...")
            animation_chars = [
                "`Connecting To JIO NETWORK ....`",
                "`█ ▇ ▆ ▅ ▄ ▂ ▁`",
                "`▒ ▇ ▆ ▅ ▄ ▂ ▁`",
                "`▒ ▒ ▆ ▅ ▄ ▂ ▁`",
                "`▒ ▒ ▒ ▅ ▄ ▂ ▁`",
                "`▒ ▒ ▒ ▒ ▄ ▂ ▁`",
                "`▒ ▒ ▒ ▒ ▒ ▂ ▁`",
                "`▒ ▒ ▒ ▒ ▒ ▒ ▁`",
                "`▒ ▒ ▒ ▒ ▒ ▒ ▒`",
                "*Optimising JIO NETWORK...*",
                "`▒ ▒ ▒ ▒ ▒ ▒ ▒`",
                "`▁ ▒ ▒ ▒ ▒ ▒ ▒`",
                "`▁ ▂ ▒ ▒ ▒ ▒ ▒`",
                "`▁ ▂ ▄ ▒ ▒ ▒ ▒`",
                "`▁ ▂ ▄ ▅ ▒ ▒ ▒`",
                "`▁ ▂ ▄ ▅ ▆ ▒ ▒`",
                "`▁ ▂ ▄ ▅ ▆ ▇ ▒`",
                "`▁ ▂ ▄ ▅ ▆ ▇ █`",
                "**JIO NETWORK Boosted....**",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 19])


    @CipherElite.on(events.NewMessage(pattern=r"\.solarsystem$"))
    @rishabh()
    async def _(event):
            "animation command"
            animation_interval = 0.1
            animation_ttl = range(80)
            event = await event.reply("solarsystem")
            animation_chars = [
                "`◼️◼️◼️◼️◼️\n◼️◼️◼️◼️☀\n◼️◼️🌎◼️◼️\n🌕◼️◼️◼️◼️\n◼️◼️◼️◼️◼️`",
                "`◼️◼️◼️◼️◼️\n🌕◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️☀\n◼️◼️◼️◼️◼️`",
                "`◼️🌕◼️◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️◼️☀◼️`",
                "`◼️◼️◼️🌕◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️☀◼️◼️◼️`",
                "`◼️◼️◼️◼️◼️\n◼️◼️◼️◼️🌕\n◼️◼️🌎◼️◼️\n☀◼️◼️◼️◼️\n◼️◼️◼️◼️◼️`",
                "`◼️◼️◼️◼️◼️\n☀◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️🌕\n◼️◼️◼️◼️◼️`",
                "`◼️☀◼️◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️◼️🌕◼️`",
                "`◼️◼️◼️☀◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️🌕◼️◼️◼️`",
            ]
            for i in animation_ttl:
                await asyncio.sleep(animation_interval)
                await event.edit(animation_chars[i % 8])