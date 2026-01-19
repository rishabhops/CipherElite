from telethon import events
import random
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh


# ─────────────── INIT ───────────────
def init(client_instance):
    commands = [
        ".dice - Roll a dice",
        ".coin - Flip a coin",
        ".decide - Yes or No decision",
        ".xogame - Play XO game via inline bot"
    ]
    description = "Fun plugins for games & decisions 🎮✨"
    add_handler("fun", commands, description)


# ───────── REGISTER COMMANDS ─────────
async def register_commands():

    # ── DICE ──
    @CipherElite.on(events.NewMessage(pattern=r"\.dice"))
    @rishabh()
    async def dice(event):
        number = random.randint(1, 6)
        dice_emojis = ["🎲1", "🎲2", "🎲3", "🎲4", "🎲5", "🎲6"]
        await event.reply(f"🎲 {dice_emojis[number-1]} ({number})")

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
