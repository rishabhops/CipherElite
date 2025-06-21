# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    fun_animations
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • Give proper credit back to the CipherElite Userbot author:
#        – GitHub: https://github.com/rishabhops/CipherElite
#        – Telegram: @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

import asyncio
from collections import deque
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Userbot owner's name
DEFAULTUSER = "Elite User"

def init(client):
    """Initialize the fun_animations plugin"""
    commands = [
        ".mind         — Animated brain cleanup sequence",
        ".explode      — Explosive animation with a bang",
        ".dial         — Simulate a call to a VIP",
        ".zap          — Zap someone with a fun animation",
        ".huh          — A confused 'huh?' animation",
        ".pingpong    — Bouncing ball animation",
        ".spiral       — Hypnotic spiral animation",
        ".sweets       — Rotating candy emojis",
        ".badass       — Show off your badass vibe",
        ".charge       — Charge up a device animation"
    ]
    description = "Fun and unique animations for chats"
    add_handler("fun_animations", commands, description)

async def edit_or_reply(event, text):
    """Try to edit the message; if that fails, send a reply"""
    try:
        return await event.edit(text)
    except Exception:
        return await event.reply(text)

@CipherElite.on(events.NewMessage(pattern=r"^\.mind$", outgoing=True))
@rishabh()
async def mind(event):
    """Animated brain cleanup sequence"""
    if event.fwd_from:
        return
    animation_interval = 1
    animation_ttl = range(10)
    event = await edit_or_reply(event, "🧠 Processing...")
    animation_chars = [
        "🧠 MIND RESET ➡️ 🚀\n\n🧠   <(•_•)> 💨",
        "🧠 MIND RESET ➡️ 🚀\n\n🧠 <(•_•)>   💨",
        "🧠 MIND RESET ➡️ 🚀\n\n🧠<(•_•)>     💨",
        "🧠 MIND RESET ➡️ 🚀\n\n(> •_•)>🧠     💨",
        "🧠 MIND RESET ➡️ 🚀\n\n  (> •_•)>🧠   💨",
        "🧠 MIND RESET ➡️ 🚀\n\n    (> •_•)>🧠 💨",
        "🧠 MIND RESET ➡️ 🚀\n\n      (> •_•)>🧠",
        "🧠 MIND RESET ➡️ 🚀\n\n        (> •_•)>",
        "🧠 MIND RESET ➡️ 🚀\n\n         <(•_•)>",
        "🧠 MIND CLEARED! ✨\n\n**(°o°)** Ready to rock!"
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 10])

@CipherElite.on(events.NewMessage(pattern=r"^\.explode$", outgoing=True))
@rishabh()
async def explode(event):
    """Explosive animation with a bang"""
    if event.fwd_from:
        return
    event = await edit_or_reply(event, "💥 Preparing explosion...")
    await event.edit("⬛⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛⬛")
    await asyncio.sleep(0.5)
    await event.edit("💣⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛⬛")
    await asyncio.sleep(0.5)
    await event.edit("⬛⬛⬛⬛\n⬛💣⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛⬛")
    await asyncio.sleep(0.5)
    await event.edit("⬛⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛💣⬛\n⬛⬛⬛⬛")
    await asyncio.sleep(0.5)
    await event.edit("⬛⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛💣")
    await asyncio.sleep(0.5)
    await event.edit("⬛⬛⬛⬛\n⬛⬛⬛⬛\n⬛⬛⬛⬛\n💥💥💥💥")
    await asyncio.sleep(1)
    await event.edit("💥💥💥💥\n💥🔥🔥💥\n💥🔥🔥💥\n💥💥💥💥")
    await asyncio.sleep(0.5)
    await event.edit("💥 **BOOM!** Everything's gone! 😎")

@CipherElite.on(events.NewMessage(pattern=r"^\.dial$", outgoing=True))
@rishabh()
async def dial(event):
    """Simulate a call to a VIP"""
    if event.fwd_from:
        return
    animation_interval = 2
    animation_ttl = range(10)
    event = await edit_or_reply(event, "📞 Dialing a VIP...")
    animation_chars = [
        "`Connecting to Secret Network...`",
        "`Call Initiated.`",
        "`VIP: Who's this?`",
        f"`Me: Yo, it's {DEFAULTUSER}!`",
        "`VIP: Authentication in progress...`",
        "`Call Secured at +91-SECRET-NO`",
        f"`Me: Hey, what's good?`",
        "`VIP: Yo, {DEFAULTUSER}! Been ages!`",
        "`VIP: Gotta run, catch ya later!`",
        "`Call Ended. Stay cool! 😎`"
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 10])

@CipherElite.on(events.NewMessage(pattern=r"^\.zap$", outgoing=True))
@rishabh()
async def zap(event):
    """Zap someone with a fun animation"""
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await edit_or_reply(event, "⚡ Reply to a user to zap them!")
        return
    reply_message = await event.get_reply_message()
    replied_user = await event.client(GetFullUserRequest(reply_message.sender_id))
    firstname = replied_user.user.first_name or "Unknown"
    animation_interval = 1
    animation_ttl = range(8)
    await edit_or_reply(event, f"⚡ Zapping {firstname}...")
    animation_chars = [
        "⚡ ZAP! ⚡",
        "🔫===>",
        "🔫=====>",
        "🔫=======>",
        "🔫========>",
        "🔫=========>",
        "🔥 ZAPPED! 🔥",
        f"💥 {firstname} is toast! 😜"
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 8])

@CipherElite.on(events.NewMessage(pattern=r"^\.huh$", outgoing=True))
@rishabh()
async def huh(event):
    """A confused 'huh?' animation"""
    if event.fwd_from:
        return
    animation_interval = 0.7
    animation_ttl = range(5)
    event = await edit_or_reply(event, "🤔 Huh?")
    animation_chars = [
        "🤔 What's that?",
        "🤔 What's going on?",
        "🤔 What's the deal?",
        "🤔 What's up, fam?",
        "😵 Totally lost! 🤷‍♂️"
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 5])

@CipherElite.on(events.NewMessage(pattern=r"^\.pingpong$", outgoing=True))
@rishabh()
async def pingpong(event):
    """Bouncing ball animation"""
    if event.fwd_from:
        return
    animation_interval = 0.3
    animation_ttl = range(12)
    event = await edit_or_reply(event, "🏓 Ping pong!")
    animation_chars = [
        "⬛⬛⬛⬛⬛\n⬛🏓⬛⬛⬛\n⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛\n⬛⬛🏓⬛⬛\n⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛\n⬛⬛⬛🏓⬛\n⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛\n⬛⬛⬛⬛🏓\n⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛🏓\n⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛",
        "⬛⬛⬛🏓⬛\n⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛",
        "⬛⬛🏓⬛⬛\n⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛",
        "⬛🏓⬛⬛⬛\n⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛",
        "🏓⬛⬛⬛⬛\n⬛⬛⬛⬛⬛\n⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛\n🏓⬛⬛⬛⬛\n⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛\n⬛⬛⬛⬛🏓\n⬛⬛⬛⬛⬛",
        "🏓 **PONG!** 🏓"
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 12])

@CipherElite.on(events.NewMessage(pattern=r"^\.spiral$", outgoing=True))
@rishabh()
async def spiral(event):
    """Hypnotic spiral animation"""
    if event.fwd_from:
        return
    animation_interval = 0.4
    animation_ttl = range(10)
    event = await edit_or_reply(event, "🌀 Spiraling...")
    animation_chars = [
        "⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛",
        "⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜",
        "⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛",
        "⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜",
        "⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛",
        "⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜",
        "⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛",
        "⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜",
        "🌀 Hypnotized! 😵",
        "🌀 **SPINNING AWAY!** 🚀"
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 10])

@CipherElite.on(events.NewMessage(pattern=r"^\.sweets$", outgoing=True))
@rishabh()
async def sweets(event):
    """Rotating candy emojis"""
    if event.fwd_from:
        return
    event = await edit_or_reply(event, "🍬 Sweetening things up...")
    deq = deque(list("🍬🍭🍫🧁🍰🎂🍪🍩🍧🍦"))
    for _ in range(50):  # Reduced iterations for performance
        await asyncio.sleep(0.3)
        await event.edit("".join(deq))
        deq.rotate(1)
    await event.edit("🍬 Sweet overload! 😋")

@CipherElite.on(events.NewMessage(pattern=r"^\.badass$", outgoing=True))
@rishabh()
async def badass(event):
    """Show off your badass vibe"""
    if event.fwd_from:
        return
    event = await edit_or_reply(event, "😎 Getting ready...")
    await event.edit("YO")
    await asyncio.sleep(0.3)
    await event.edit("YO, I'M")
    await asyncio.sleep(0.3)
    await event.edit("YO, I'M THE")
    await asyncio.sleep(0.3)
    await event.edit("YO, I'M THE BOSS")
    await asyncio.sleep(0.3)
    await event.edit("YO, I'M THE BOSS HERE")
    await asyncio.sleep(0.3)
    await event.edit(f"😎 {DEFAULTUSER} IS THE BOSS! 🔥")

@CipherElite.on(events.NewMessage(pattern=r"^\.charge$", outgoing=True))
@rishabh()
async def charge(event):
    """Charge up a device animation"""
    if event.fwd_from:
        return
    event = await edit_or_reply(event, "🔋 Charging...")
    txt = "🔋 Quantum Charger Activated...\nDevice: CipherElite Phone\nBattery: "
    percentage = 0
    for _ in range(5):
        await event.edit(txt + f"{percentage}%")
        percentage += 20
        await asyncio.sleep(1)
    await event.edit("🔋 Quantum Charger Done!\nDevice: CipherElite Phone\nBattery: 100% ⚡")
