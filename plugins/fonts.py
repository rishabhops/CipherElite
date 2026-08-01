# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    fonts
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .fmusical, .ancient, .vapor, .smallcaps, .blackbf,
#                  .bubbles, .tanf, .boxf, .smothtext, .egyptf, .maref,
#                  .handcf, .doublef, .mock, .ghostf, .handsf
# =============================================================================

from telethon import events
import random
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

normalfont = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', "'", ',', '\\', '/', '!', '?']

musicalfont = ['♬', 'ᖲ', '¢', 'ᖱ', '៩', '⨏', '❡', 'Ϧ', 'ɨ', 'ɉ', 'ƙ', 'ɭ', '៣', '⩎', '០', 'ᖰ', 'ᖳ', 'Ʀ', 'ន', 'Ƭ', '⩏', '⩔', 'Ɯ', '✗', 'ƴ', 'Ȥ', '♬', 'ᖲ', '¢', 'ᖱ', '៩', '⨏', '❡', 'Ϧ', 'ɨ', 'ɉ', 'ƙ', 'ɭ', '៣', '⩎', '០', 'ᖰ', 'ᖳ', 'Ʀ', 'ន', 'Ƭ', '⩏', '⩔', 'Ɯ', '✗', 'ƴ', 'Ȥ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', "'", ',', '\\', '/', '!', '?']

ancientfont = ['ꍏ', 'ꌃ', 'ꉓ', 'ꀸ', 'ꍟ', 'ꎇ', 'ꁅ', 'ꃅ', 'ꀤ', 'ꀭ', 'ꀘ', '꒒', 'ꎭ', 'ꈤ', 'ꂦ', 'ᖘ', 'ꆰ', 'ꋪ', 'ꌗ', '꓄', 'ꀎ', 'ᐯ', 'ꅏ', 'ꊼ', 'ꌩ', 'ꁴ', 'ꍏ', 'ꌃ', 'ꉓ', 'ꀸ', 'ꍟ', 'ꎇ', 'ꁅ', 'ꃅ', 'ꀤ', 'ꀭ', 'ꀘ', '꒒', 'ꎭ', 'ꈤ', 'ꂦ', 'ᖘ', 'ꆰ', 'ꋪ', 'ꌗ', '꓄', 'ꀎ', 'ᐯ', 'ꅏ', 'ꊼ', 'ꌩ', 'ꁴ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', "'", ',', '\\', '/', '!', '?']

bubblesfont = 'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

bubblesblackfont = '🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

tantextfont = 'ᎯᏰᏣᎴᏋᎴᎶᏂiᏠᏦlmᏁᏫᎵᏄᖇᎦᎿᏌᏉᏯﾒᎩᏃᎯᏰᏣᎴᏋᎴᎶᏂiᏠᏦlmᏁᏫᎵᏄᖇᎦᎿᏌᏉᏯﾒᎩᏃ1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

littleboxtextfont = '🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

smothtextfont = 'ᗩᗷᑕᗞᗴᖴᏀᕼᏆᒍᏦᏞᗰᑎᝪᑭᑫᖇᔑᎢᑌᐯᗯ᙭ᎩᏃᗩᗷᑕᗞᗴᖴᏀᕼᏆᒍᏦᏞᗰᑎᝪᑭᑫᖇᔑᎢᑌᐯᗯ᙭ᎩᏃ1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

egyptfontfont = 'ค๒ς๔єŦﻮђเןкl๓ภ๏קợгรtยשฬץאzค๒ς๔єŦﻮђเןкl๓ภ๏קợгรtยשฬץאz1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

nightmarefont = '𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

hwcapitalfont = '𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

doubletextfont = 'ᎯℬℂⅅℰℱᎶℋℐᎫᏦℒℳℕᎾℙℚℛЅᏆUᏉᏇXᎽℤᎯℬℂⅅℰℱᎶℋℐᎫᏦℒℳℕᎾℙℚℛЅᏆUᏉᏇXᎽℤ1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

ghostfontfont = '𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'

hwslfont = '𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏1234567890"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~'


def init(client_instance):
    commands = [
        ".fmusical <text> - Musical font",
        ".ancient <text> - Ancient font",
        ".vapor <text> - Vaporwave font",
        ".smallcaps <text> - Small caps font",
        ".blackbf <text> - Black bubble font",
        ".bubbles <text> - Bubbles font",
        ".tanf <text> - Tan font",
        ".boxf <text> - Box font",
        ".smothtext <text> - Smooth text font",
        ".egyptf <text> - Egypt font",
        ".maref <text> - Nightmare font",
        ".handcf <text> - Handwriting capitals",
        ".doublef <text> - Double font",
        ".mock <text> - SpongeMock text",
        ".ghostf <text> - Ghost font",
        ".handsf <text> - Handwriting font",
    ]
    description = "Text font style converters"
    add_handler("fonts", commands, description)

async def register_commands():

    async def _get_text(event):
        text = event.pattern_match.group(1).strip()
        if event.is_reply:
            text = (await event.get_reply_message()).text or text
        return text

    def _apply_font_list(text, font):
        result = ""
        for ch in text:
            if ch.lower() in normalfont:
                idx = normalfont.index(ch.lower())
                if idx < len(font):
                    result += font[idx]
                else:
                    result += ch
            else:
                result += ch
        return result

    def _apply_font_str(text, font):
        result = ""
        for ch in text:
            if ch.lower() in normalfont:
                idx = normalfont.index(ch.lower())
                if idx < len(font):
                    result += font[idx]
                else:
                    result += ch
            else:
                result += ch
        return result


    @CipherElite.on(events.NewMessage(pattern=r"\.fmusical(?: |$)([\s\S]*)"))
    @rishabh()
    async def fmusical_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, musicalfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.ancient(?: |$)([\s\S]*)"))
    @rishabh()
    async def ancient_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, ancientfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.smallcaps(?: |$)([\s\S]*)"))
    @rishabh()
    async def smallcaps_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, normalfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.blackbf(?: |$)([\s\S]*)"))
    @rishabh()
    async def blackbf_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, bubblesblackfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.bubbles(?: |$)([\s\S]*)"))
    @rishabh()
    async def bubbles_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, bubblesfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.tanf(?: |$)([\s\S]*)"))
    @rishabh()
    async def tanf_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, tantextfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.boxf(?: |$)([\s\S]*)"))
    @rishabh()
    async def boxf_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, littleboxtextfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.smothtext(?: |$)([\s\S]*)"))
    @rishabh()
    async def smothtext_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, smothtextfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.egyptf(?: |$)([\s\S]*)"))
    @rishabh()
    async def egyptf_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, egyptfontfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.maref(?: |$)([\s\S]*)"))
    @rishabh()
    async def maref_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, nightmarefont))

    @CipherElite.on(events.NewMessage(pattern=r"\.handcf(?: |$)([\s\S]*)"))
    @rishabh()
    async def handcf_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, hwcapitalfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.doublef(?: |$)([\s\S]*)"))
    @rishabh()
    async def doublef_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, doubletextfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.ghostf(?: |$)([\s\S]*)"))
    @rishabh()
    async def ghostf_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, ghostfontfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.handsf(?: |$)([\s\S]*)"))
    @rishabh()
    async def handsf_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        await event.reply(_apply_font_str(text, hwslfont))

    @CipherElite.on(events.NewMessage(pattern=r"\.vapor(?: |$)([\s\S]*)"))
    @rishabh()
    async def vapor_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        reply_text = []
        for ch in text:
            if 0x21 <= ord(ch) <= 0x7F:
                reply_text.append(chr(ord(ch) + 0xFEE0))
            elif ord(ch) == 0x20:
                reply_text.append(chr(0x3000))
            else:
                reply_text.append(ch)
        await event.reply("".join(reply_text))

    @CipherElite.on(events.NewMessage(pattern=r"\.mock(?: |$)([\s\S]*)"))
    @rishabh()
    async def mock_cmd(event):
        text = await _get_text(event)
        if not text:
            await event.reply("❌ Give me some text.")
            return
        reply_text = []
        for ch in text:
            if ch.isalpha() and random.randint(0, 1):
                reply_text.append(ch.upper() if ch.islower() else ch.lower())
            else:
                reply_text.append(ch)
        await event.reply("".join(reply_text))
