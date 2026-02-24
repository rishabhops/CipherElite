# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    Font Changer
#  Author:         @LearningBotsOfficial
#
#  Based On:       CipherElite Userbot Plugin System
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

from telethon import events, Button
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

FONT_CACHE = {}

# ==========================================================
# Iinit → Font Changer Plugin 
# ==========================================================
def init(client_instance):
    commands = [
        ".font <number> <text> -> Convert normal text into stylish font."
        ".fonts <text> → Preview all fonts"
    ]
    description = "^_^ Font Changer -> Convert normal text into stylish Unicode font."
    add_handler("font", commands, description)


# ==========================================================
# Command Handler Registerion
# ==========================================================
async def register_commands():

    FONTS = {

        "font1": {
            "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ",
            "f":"ғ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ",
            "k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ",
            "p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ",
            "u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ"
        },

        "font2": {
            "a":"𝓪","b":"𝓫","c":"𝓬","d":"𝓭","e":"𝓮",
            "f":"𝓯","g":"𝓰","h":"𝓱","i":"𝓲","j":"𝓳",
            "k":"𝓴","l":"𝓵","m":"𝓶","n":"𝓷","o":"𝓸",
            "p":"𝓹","q":"𝓺","r":"𝓻","s":"𝓼","t":"𝓽",
            "u":"𝓾","v":"𝓿","w":"𝔀","x":"𝔁","y":"𝔂","z":"𝔃"
        },

        "font3": {
            "a":"𝕒","b":"𝕓","c":"𝕔","d":"𝕕","e":"𝕖",
            "f":"𝕗","g":"𝕘","h":"𝕙","i":"𝕚","j":"𝕛",
            "k":"𝕜","l":"𝕝","m":"𝕞","n":"𝕟","o":"𝕠",
            "p":"𝕡","q":"𝕢","r":"𝕣","s":"𝕤","t":"𝕥",
            "u":"𝕦","v":"𝕧","w":"𝕨","x":"𝕩","y":"𝕪","z":"𝕫"
        },

        "font4": {
            "a":"𝗮","b":"𝗯","c":"𝗰","d":"𝗱","e":"𝗲",
            "f":"𝗳","g":"𝗴","h":"𝗵","i":"𝗶","j":"𝗷",
            "k":"𝗸","l":"𝗹","m":"𝗺","n":"𝗻","o":"𝗼",
            "p":"𝗽","q":"𝗾","r":"𝗿","s":"𝘀","t":"𝘁",
            "u":"𝘂","v":"𝘃","w":"𝘄","x":"𝘅","y":"𝘆","z":"𝘇"
        },

        "font5": {
            "a":"𝚊","b":"𝚋","c":"𝚌","d":"𝚍","e":"𝚎",
            "f":"𝚏","g":"𝚐","h":"𝚑","i":"𝚒","j":"𝚓",
            "k":"𝚔","l":"𝚕","m":"𝚖","n":"𝚗","o":"𝚘",
            "p":"𝚙","q":"𝚚","r":"𝚛","s":"𝚜","t":"𝚝",
            "u":"𝚞","v":"𝚟","w":"𝚠","x":"𝚡","y":"𝚢","z":"𝚣"
        },

        "font6": {
            "a":"ⓐ","b":"ⓑ","c":"ⓒ","d":"ⓓ","e":"ⓔ",
            "f":"ⓕ","g":"ⓖ","h":"ⓗ","i":"ⓘ","j":"ⓙ",
            "k":"ⓚ","l":"ⓛ","m":"ⓜ","n":"ⓝ","o":"ⓞ",
            "p":"ⓟ","q":"ⓠ","r":"ⓡ","s":"ⓢ","t":"ⓣ",
            "u":"ⓤ","v":"ⓥ","w":"ⓦ","x":"ⓧ","y":"ⓨ","z":"ⓩ"
        },

        "font7": {
            "a":"🄰","b":"🄱","c":"🄲","d":"🄳","e":"🄴",
            "f":"🄵","g":"🄶","h":"🄷","i":"🄸","j":"🄹",
            "k":"🄺","l":"🄻","m":"🄼","n":"🄽","o":"🄾",
            "p":"🄿","q":"🅀","r":"🅁","s":"🅂","t":"🅃",
            "u":"🅄","v":"🅅","w":"🅆","x":"🅇","y":"🅈","z":"🅉"
        },

        "font8": {
            "a":"α","b":"в","c":"¢","d":"∂","e":"є",
            "f":"ƒ","g":"g","h":"н","i":"ι","j":"נ",
            "k":"к","l":"ℓ","m":"м","n":"η","o":"σ",
            "p":"ρ","q":"զ","r":"я","s":"ѕ","t":"т",
            "u":"υ","v":"ν","w":"ω","x":"χ","y":"у","z":"z"
        },

        "font9": {
            "a":"ᵃ","b":"ᵇ","c":"ᶜ","d":"ᵈ","e":"ᵉ",
            "f":"ᶠ","g":"ᵍ","h":"ʰ","i":"ᶦ","j":"ʲ",
            "k":"ᵏ","l":"ˡ","m":"ᵐ","n":"ⁿ","o":"ᵒ",
            "p":"ᵖ","q":"ᵠ","r":"ʳ","s":"ˢ","t":"ᵗ",
            "u":"ᵘ","v":"ᵛ","w":"ʷ","x":"ˣ","y":"ʸ","z":"ᶻ"
        },

        "font10": {
            "a":"ａ","b":"ｂ","c":"ｃ","d":"ｄ","e":"ｅ",
            "f":"ｆ","g":"ｇ","h":"ｈ","i":"ｉ","j":"ｊ",
            "k":"ｋ","l":"ｌ","m":"ｍ","n":"ｎ","o":"ｏ",
            "p":"ｐ","q":"ｑ","r":"ｒ","s":"ｓ","t":"ｔ",
            "u":"ｕ","v":"ｖ","w":"ｗ","x":"ｘ","y":"ｙ","z":"ｚ"
        }
    }

    
    @CipherElite.on(events.NewMessage(pattern=r"\.font(?:\s+(.*))?$"))
    @rishabh()
    async def font_changer(event):
        try:
            args = event.pattern_match.group(1)
    
            # =========================
            # SHOW FONT LIST
            # =========================
            if not args:
                menu = (
                    "🎭 **CipherElite Font Changer**\n\n"
                    "📌 Usage:\n"
                    "`.font <number> <text>`\n\n"
                    "**Available Fonts:**\n"
                    "1 → ᴀʙᴄ\n"
                    "2 → 𝓪𝓫𝓬\n"
                    "3 → 𝕒𝕓𝕔\n"
                    "4 → 𝗮𝗯𝗰\n"
                    "5 → 𝚊𝚋𝚌\n"
                    "6 → ⓐⓑⓒ\n"
                    "7 → 🄰🄱🄲\n"
                    "8 → αв¢\n"
                    "9 → ᵃᵇᶜ\n"
                    "10 → ａｂｃ\n"
                )
                return await event.reply(menu)
    
            # =========================
            # PARSE NUMBER + TEXT
            # =========================
            parts = args.split(maxsplit=1)
    
            if len(parts) < 2:
                return await event.reply("❌ Give font number and text.")
    
            font_number, text = parts
            font_key = f"font{font_number}"
    
            font_map = FONTS.get(font_key)
    
            if not font_map:
                return await event.reply("❌ Invalid font number.")
    
            # =========================
            # CONVERT TEXT
            # =========================
            result = "".join(
                font_map.get(c.lower(), c) for c in text
            )
    
            await event.reply(
                "🎭 **CipherElite Font Result**\n\n"
                f"📝 **Original:** `{text}`\n"
                f"✨ **Styled:** `{result}`"
            )
    
        except Exception as e:
            await event.reply(f"❌ Error: `{e}`")
    
    
    
    @CipherElite.on(events.NewMessage(pattern=r"\.fonts$"))
    @rishabh()
    async def show_fonts(event):
    
        text = (
            "🎭 **Available Fonts — CipherElite**\n\n"
            "1 → ᴀʙᴄ\n"
            "2 → 𝓪𝓫𝓬\n"
            "3 → 𝕒𝕓𝕔\n"
            "4 → 𝗮𝗯𝗰\n"
            "5 → 𝚊𝚋𝚌\n"
            "6 → ⓐⓑⓒ\n"
            "7 → 🄰🄱🄲\n"
            "8 → αв¢\n"
            "9 → ᵃᵇᶜ\n"
            "10 → ａｂｃ\n"
            "📌 Usage:\n"
            "`.font <number> <text>` → Apply font"
        )
        await event.reply(text)
