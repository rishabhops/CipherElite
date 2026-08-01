import asyncio
from telethon import events

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "animations"


def init(client):
    commands = [
        ".gf - Animated GF reply (18+)",
        ".mom - Animated Mom reply (18+)",
    ]
    description = (
        "🔞 **R-Rated Animation Pack**\n"
        "Adult animation replies for 18+ users only."
    )
    add_handler("mom-gf", commands, description)


@CipherElite.on(events.NewMessage(pattern=r"\.gf$", outgoing=True))
@rishabh
async def gf(event):
    if event.fwd_from:
        return

    animation_interval = 5
    animation_ttl = range(0, 21)
    animation_chars = [
        "`Ruk jaa , Abhi teri GF ko Fuck karta hu `",
        "`Making your Gf warm 🔥`",
        "`Pressing her boobs 🤚😘`",
        "`Stimulating her pussy🖕`",
        "`Fingering her pussy 💧😍👅 `",
        "`Asking her to taste my DICK🍌`",
        "`Requested accepted😻💋, Ready to taste my DICK🍌`",
        "`Getting her ready to fuck 👀`",
        "`Your GF Is Ready To Fuck`",
        "`Fucking Your GF😈😈\n\n\nYour GF's Pussy Get Red\nTrying new SEX position to make her Squirt\n\nAlmost Done. 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's Pussy Get White\nShe squirted like a shower💧💦👅\n\nAlmost Done..\n\nFucked Percentage... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's Pussy Get Red\nDoing Extreme SEX with her👄\n\nAlmost Done...\n\nFucked Percentage... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's Pussy Get Red\nWarming her Ass🍑 to Fuck!🍑🍑\n\nAlmost Done....\n\nFucked Percentage... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's ASS🍑 Get Red\nInserted my Penis🍌 in her ASS🍑\n\nAlmost Done.....\n\nFucked Percentage... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's ASS🍑 Get Red\ndoing extreme sex with her\n\nAlmost Done......\n\nFucked Percentage... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's Boobs🤚😘 are Awesome\nPressing her tight Nipples🤚👀\n\nAlmost Done.......\n\nFucked Percentage... 84%\n███████████████████▒▒▒▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's Lips Get Horny\nDoing French Kiss with your GF👄💋\n\nAlmost Done........\n\nFucked Percentage... 89%\n██████████████████████▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's Boobs🤚😘 are Awesome\nI am getting ready to cum in her Mouth👄\n\nAlmost Done.......\n\nFucked Percentage... 90%\n██████████████████████▒▒▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's Boobs🤚😘 are Awesome\nFinally, I have cummed in her Mouth👅👄\n\nAlmost Done.......\n\nFucked Percentage... 96%\n████████████████████████▒ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's is Awesome\nShe is Licking my Dick🍌 in the Awesome Way✊🤛🤛👅👄\n\nAlmost Done.......\n\nFucked Percentage... 100%\n█████████████████████████ `",
        "`Fucking Your GF😈😈\n\n\nYour GF's ASS🍑 Get Red\nCummed On her Mouth👅👄\n\nYour GF got Pleasure\n\nResult: Now I Have 1 More SEX Partner 👍👍`",
    ]

    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 21])


@CipherElite.on(events.NewMessage(pattern=r"\.mom$", outgoing=True))
@rishabh
async def mom(event):
    if event.fwd_from:
        return

    animation_interval = 5
    animation_ttl = range(0, 21)
    animation_chars = [
        "`Ruk jaa , Abhi teri Mom ko Fuck karta hu `",
        "`Making your Mom warm 🔥`",
        "`Pressing her boobs 🤚😘`",
        "`Stimulating her pussy🖕`",
        "`Fingering her pussy 💧😍👅 `",
        "`Asking her to taste my DICK🍌`",
        "`Requested accepted😻💋, Ready to taste my DICK🍌`",
        "`Getting her ready to fuck 👀`",
        "`Your Mom Is Ready To Fuck`",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Pussy Get Red\nTrying new SEX position to make her Squirt\n\nAlmost Done. 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Pussy Get White\nShe squirted like a shower💧💦👅\n\nAlmost Done..\n\nFucked Percentage... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Pussy Get Red\nDoing Extreme SEX with her👄\n\nAlmost Done...\n\nFucked Percentage... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Pussy Get Red\nWarming her Ass🍑 to Fuck!🍑🍑\n\nAlmost Done....\n\nFucked Percentage... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's ASS🍑 Get Red\nInserted my Penis🍌 in her ASS🍑\n\nAlmost Done.....\n\nFucked Percentage... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's ASS🍑 Get Red\ndoing extreme sex with her\n\nAlmost Done......\n\nFucked Percentage... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Boobs🤚😘 are Awesome\nPressing her tight Nipples🤚👀\n\nAlmost Done.......\n\nFucked Percentage... 84%\n███████████████████▒▒▒▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Lips Get Horny\nDoing French Kiss with your Mom👄💋\n\nAlmost Done........\n\nFucked Percentage... 89%\n██████████████████████▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Boobs🤚😘 are Awesome\nI am getting ready to cum in her Mouth👄\n\nAlmost Done.......\n\nFucked Percentage... 90%\n██████████████████████▒▒▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's Boobs🤚😘 are Awesome\nFinally, I have cummed in her Mouth👅👄\n\nAlmost Done.......\n\nFucked Percentage... 96%\n████████████████████████▒ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's is Awesome\nShe is Licking my Dick🍌 in the Awesome Way✊🤛🤛👅👄\n\nAlmost Done.......\n\nFucked Percentage... 100%\n█████████████████████████ `",
        "`Fucking Your Mom😈😈\n\n\nYour Mom's ASS🍑 Get Red\nCummed On her Mouth👅👄\n\nYour Mom got Pleasure\n\nResult: Now I Have 1 More SEX Partner 👍👍`",
    ]

    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 21])
