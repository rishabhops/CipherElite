from telethon import events
import random
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "animations"


# ─────────────── INIT ───────────────
def init(client_instance):
    commands = [
        ".coin - Flip a coin",
        ".decide - Yes or No decision",
        ".xogame - Play XO game via inline bot"
    ]
    description = "Fun plugins for games & decisions 🎮✨"
    add_handler("fun", commands, description)


# ───────── REGISTER COMMANDS ─────────
async def register_commands():

    # ── COIN ──
    @CipherElite.on(events.NewMessage(pattern=r"\.coin"))
    @rishabh()
    async def coin(event):
        coins = ["Heads", "Tails"]
        coin_emoji = "🪙"
        result = random.choice(coins)
        await event.reply(f"{coin_emoji} Coin landed on: **{result}**!")

    # ── DECIDE ──
    @CipherElite.on(events.NewMessage(pattern=r"\.decide"))
    @rishabh()
    async def decide(event):
        decisions = ["Yes", "No", "Maybe", "Definitely", "Never"]
        await event.reply(f"❓ **{random.choice(decisions)}**")

    # ── XO GAME ──
    @CipherElite.on(events.NewMessage(pattern=r"\.xogame$"))
    @rishabh()
    async def xogame(event):
        try:
            bot_username = "@xobot"
            query = "play"

            result = await event.client.inline_query(bot_username, query)
            await result[0].click(event.chat_id)
            await event.delete()

        except Exception as e:
            await event.reply(f"❌ **Error:** `{str(e)}`")
