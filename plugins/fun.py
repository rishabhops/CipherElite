from telethon import events
import random
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

def init(client_instance):
    commands = [
        ".dice - Roll a dice",
        ".coin - Flip a coin",
        ".decide - Yes or No decision"
    ]
    description = "Fun plugins for entertainment "
    add_handler("fun", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.dice"))
    @rishabh()
    async def dice(event):
        number = random.randint(1, 6)
        dice_emojis = ["", "", "", "", "", ""]
        await event.reply(f" {dice_emojis[number-1]} ({number})")

    @CipherElite.on(events.NewMessage(pattern=r"\.coin"))
    @rishabh()
    async def coin(event):
        coins = ["Heads", "Tails"]
        coin_emoji = ""
        result = random.choice(coins)
        await event.reply(f"{coin_emoji} Coin landed on: **{result}**!")

    @CipherElite.on(events.NewMessage(pattern=r"\.decide"))
    @rishabh()
    async def decide(event):
        decisions = ["Yes", "No", "Maybe", "Definitely", "Never"]
        await event.reply(f" **{random.choice(decisions)}**")
        