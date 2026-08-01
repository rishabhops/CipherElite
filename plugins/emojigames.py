# =============================================================================
#  CipherElite Userbot Plugin - Emoji Games
#  Ported from CatUserBot
# =============================================================================

import contextlib
from telethon import events
from telethon.tl.types import InputMediaDice

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "fun"

DART_EMOJI = "🎯"
DICE_EMOJI = "🎲"
BALL_EMOJI = "🏀"
FOOT_EMOJI = "⚽"
SLOT_EMOJI = "🎰"
BOWL_EMOJI = "🎳"


def init(client):
    commands = [
        ".dart [1-6] - Throw dart emoji",
        ".dice [1-6] - Roll animated dice",
        ".bb [1-5] - Basketball emoji",
        ".fb [1-5] - Football emoji",
        ".jp [1-64] - Jackpot slot emoji",
        ".bowl [1-6] - Bowling emoji",
    ]
    description = "🎲 Animated emoji games"
    add_handler("emojigames", commands, description)


async def _roll_emoji(event, emoticon, max_value):
    reply_message = event
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
    input_str = event.pattern_match.group(1)
    await event.delete()
    r = await reply_message.reply(file=InputMediaDice(emoticon=emoticon))
    if input_str:
        with contextlib.suppress(BaseException):
            required_number = int(input_str)
            while r.media.value != required_number:
                await r.delete()
                r = await reply_message.reply(file=InputMediaDice(emoticon=emoticon))


@CipherElite.on(events.NewMessage(pattern=r"^\.dart(?:\s+([1-6]))?$", outgoing=True))
@rishabh
async def dart(event):
    await _roll_emoji(event, DART_EMOJI, 6)


@CipherElite.on(events.NewMessage(pattern=r"^\.dice(?:\s+([1-6]))?$", outgoing=True))
@rishabh
async def dice(event):
    await _roll_emoji(event, DICE_EMOJI, 6)


@CipherElite.on(events.NewMessage(pattern=r"^\.bb(?:\s+([1-5]))?$", outgoing=True))
@rishabh
async def basketball(event):
    await _roll_emoji(event, BALL_EMOJI, 5)


@CipherElite.on(events.NewMessage(pattern=r"^\.fb(?:\s+([1-5]))?$", outgoing=True))
@rishabh
async def football(event):
    await _roll_emoji(event, FOOT_EMOJI, 5)


@CipherElite.on(events.NewMessage(pattern=r"^\.jp(?:\s+([1-9]|[1-5][0-9]|6[0-4]))?$", outgoing=True))
@rishabh
async def jackpot(event):
    await _roll_emoji(event, SLOT_EMOJI, 64)


@CipherElite.on(events.NewMessage(pattern=r"^\.bowl(?:\s+([1-6]))?$", outgoing=True))
@rishabh
async def bowling(event):
    await _roll_emoji(event, BOWL_EMOJI, 6)
