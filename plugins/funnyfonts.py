# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    funnyfonts
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .str, .zal, .weeb, .downside, .subscript, .superscript
#  Note:           .cp skipped because it conflicts with .cp in carbon.py
# =============================================================================

from telethon import events
import random
import re
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

normiefont = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

weebyfont = ['卂', '乃', '匚', '刀', '乇', '下', '厶', '卄', '工', '丁', '长', '乚', '从', '𠘨', '口', '尸', '㔿', '尺', '丂', '丅', '凵', 'リ', '山', '乂', '丫', '乙']

upsidefont = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', "'", ',', '\\', '/', '!', '?']

downsidefont = ['ɐ', 'q', 'ɔ', 'p', 'ə', 'ɟ', 'ɓ', 'ɥ', 'ı', 'ɾ', 'ʞ', 'l', 'ɯ', 'u', 'o', 'p', 'q', 'ɹ', 's', 'ʇ', 'n', 'ʌ', 'ʍ', 'x', 'ʎ', 'z', '∀', 'B', 'Ↄ', '◖', 'Ǝ', 'Ⅎ', '⅁', 'H', 'I', 'ſ', 'K', '⅂', 'W', 'ᴎ', 'O', 'Ԁ', 'Ό', 'ᴚ', 'S', '⊥', '∩', 'ᴧ', 'M', 'X', '⅄', 'Z', '0', '1', 'ᄅ', 'Ɛ', 'ᔭ', '5', '9', 'Ɫ', '8', '6', '¯', ',', "'", '/', '\\', '¡', '¿']

normaltext = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

subscriptfont = 'ₐBCDₑFGₕᵢⱼₖₗₘₙₒₚQᵣₛₜᵤᵥWₓYZₐᵦ𝒸𝒹ₑ𝒻𝓰ₕᵢⱼₖₗₘₙₒₚᵩᵣₛₜᵤᵥ𝓌ₓᵧ𝓏₁₂₃₄₅₆₇₈₉₀"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

superscriptfont = 'ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᵠᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ¹²³⁴⁵⁶⁷⁸⁹⁰"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

ZALG_LIST = [['̖', ' ̗', ' ̘', ' ̙', ' ̜', ' ̝', ' ̞', ' ̟', ' ̠', ' ̤', ' ̥', ' ̦', ' ̩', ' ̪', ' ̫', ' ̬', ' ̭', ' ̮', ' ̯', ' ̰', ' ̱', ' ̲', ' ̳', ' ̹', ' ̺', ' ̻', ' ̼', ' ͅ', ' ͇', ' ͈', ' ͉', ' ͍', ' ͎', ' ͓', ' ͔', ' ͕', ' ͖', ' ͙', ' ͚', ' '], [' ̍', ' ̎', ' ̄', ' ̅', ' ̿', ' ̑', ' ̆', ' ̐', ' ͒', ' ͗', ' ͑', ' ̇', ' ̈', ' ̊', ' ͂', ' ̓', ' ̈́', ' ͊', ' ͋', ' ͌', ' ̃', ' ̂', ' ̌', ' ͐', ' ́', ' ̋', ' ̏', ' ̽', ' ̉', ' ͣ', ' ͤ', ' ͥ', ' ͦ', ' ͧ', ' ͨ', ' ͩ', ' ͪ', ' ͫ', ' ͬ', ' ͭ', ' ͮ', ' ͯ', ' ̾', ' ͛', ' ͆', ' ̚'], [' ̕', ' ̛', ' ̀', ' ́', ' ͘', ' ̡', ' ̢', ' ̧', ' ̨', ' ̴', ' ̵', ' ̶', ' ͜', ' ͝', ' ͞', ' ͟', ' ͠', ' ͢', ' ̸', ' ̷', ' ͡']]

EMOJIS = ['😂', '😂', '👌', '💞', '👍', '👌', '💯', '🎶', '👀', '😂', '👓', '👏', '👐', '🍕', '💥', '😩', '😏', '😞', '👀', '👅', '😩', '🤒', '😳', '🤯', '😵', '🥵', '🤒', '😠', '😪', '😴', '🤤', '👿', '👽', '😏', '😒', '😣', '🤔', '🤨', '🧐', '😝', '🤪', '🤩', '☺️', '😭', '🥺']


def init(client_instance):
    commands = [
        ".str <text> - Stretch vowels",
        ".zal <text> - Zalgo text",
        ".weeb <text> - Weebify text",
        ".downside <text> - Upside-down text",
        ".subscript <text> - Subscript text",
        ".superscript <text> - Superscript text"
    ]
    description = "More funny font style converters"
    add_handler("funnyfonts", commands, description)

async def register_commands():

    async def _get_text(event):
        text = event.pattern_match.group(1).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        return text

    def _apply_font(text, source, target):
        result = ""
        for ch in text:
            if ch.lower() in source:
                idx = source.index(ch.lower())
                if idx < len(target):
                    result += target[idx]
                else:
                    result += ch
            else:
                result += ch
        return result

    @CipherElite.on(events.NewMessage(pattern=r"\.str(?: |$)([\s\S]*)"))
    @rishabh()
    async def str_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        count = random.randint(3, 10)
        reply = re.sub(r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵаеиоуюяыэё])", (r"\1" * count), text)
        await event.reply(reply)

    @CipherElite.on(events.NewMessage(pattern=r"\.zal(?: |$)([\s\S]*)"))
    @rishabh()
    async def zal_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        reply_text = []
        for ch in text:
            if not ch.isalpha():
                reply_text.append(ch)
                continue
            for _ in range(3):
                randint = random.randint(0, 2)
                if randint == 0:
                    ch = ch.strip() + random.choice(ZALG_LIST[0]).strip()
                elif randint == 1:
                    ch = ch.strip() + random.choice(ZALG_LIST[1]).strip()
                else:
                    ch = ch.strip() + random.choice(ZALG_LIST[2]).strip()
            reply_text.append(ch)
        await event.reply("".join(reply_text))

    @CipherElite.on(events.NewMessage(pattern=r"\.weeb(?: |$)([\s\S]*)"))
    @rishabh()
    async def weeb_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font(text.lower(), normiefont, weebyfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.downside(?: |$)([\s\S]*)"))
    @rishabh()
    async def downside_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font(text.lower(), upsidefont, downsidefont))

    @CipherElite.on(events.NewMessage(pattern=r"\.subscript(?: |$)([\s\S]*)"))
    @rishabh()
    async def subscript_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font(text.lower(), normaltext, subscriptfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.superscript(?: |$)([\s\S]*)"))
    @rishabh()
    async def superscript_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font(text.lower(), normaltext, superscriptfont))
