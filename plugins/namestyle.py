# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    namestyle
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import os
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# =========================
# Character maps (same as before)
# =========================

BOLD_MAP = str.maketrans({
    "A":"𝗔","B":"𝗕","C":"𝗖","D":"𝗗","E":"𝗘","F":"𝗙","G":"𝗚","H":"𝗛","I":"𝗜","J":"𝗝","K":"𝗞","L":"𝗟","M":"𝗠",
    "N":"𝗡","O":"𝗢","P":"𝗣","Q":"𝗤","R":"𝗥","S":"𝗦","T":"𝗧","U":"𝗨","V":"𝗩","W":"𝗪","X":"𝗫","Y":"𝗬","Z":"𝗭",
    "a":"𝗮","b":"𝗯","c":"𝗰","d":"𝗱","e":"𝗲","f":"𝗳","g":"𝗴","h":"𝗵","i":"𝗶","j":"𝗷","k":"𝗸","l":"𝗹","m":"𝗺",
    "n":"𝗻","o":"𝗼","p":"𝗽","q":"𝗾","r":"𝗿","s":"𝘀","t":"𝘁","u":"𝘂","v":"𝘃","w":"𝘄","x":"𝘅","y":"𝘆","z":"𝘇",
    "0":"𝟬","1":"𝟭","2":"𝟮","3":"𝟯","4":"𝟰","5":"𝟱","6":"𝟲","7":"𝟳","8":"𝟴","9":"𝟵"
})

ITALIC_MAP = str.maketrans({
    "A":"𝘈","B":"𝘉","C":"𝘊","D":"𝘋","E":"𝘌","F":"𝘍","G":"𝘎","H":"𝘏","I":"𝘐","J":"𝘑","K":"𝘒","L":"𝘓","M":"𝘔",
    "N":"𝘕","O":"𝘖","P":"𝘗","Q":"𝘘","R":"𝘙","S":"𝘚","T":"𝘛","U":"𝘜","V":"𝘝","W":"𝘞","X":"𝘟","Y":"𝘠","Z":"𝘡",
    "a":"𝘢","b":"𝘣","c":"𝘤","d":"𝘥","e":"𝘦","f":"𝘧","g":"𝘨","h":"𝘩","i":"𝘪","j":"𝘫","k":"𝘬","l":"𝘭","m":"𝘮",
    "n":"𝘯","o":"𝘰","p":"𝘱","q":"𝘲","r":"𝘳","s":"𝘴","t":"𝘵","u":"𝘶","v":"𝘷","w":"𝘸","x":"𝘹","y":"𝘺","z":"𝘻"
})

SCRIPT_MAP = str.maketrans({
    "A":"𝒜","B":"𝐵","C":"𝒞","D":"𝒟","E":"𝐸","F":"𝐹","G":"𝒢","H":"𝐻","I":"𝐼","J":"𝒥","K":"𝒦","L":"𝐿","M":"𝑀",
    "N":"𝒩","O":"𝒪","P":"𝒫","Q":"𝒬","R":"𝑅","S":"𝒮","T":"𝒯","U":"𝒰","V":"𝒱","W":"𝒲","X":"𝒳","Y":"𝒴","Z":"𝒵",
    "a":"𝒶","b":"𝒷","c":"𝒸","d":"𝒹","e":"𝑒","f":"𝒻","g":"𝑔","h":"𝒽","i":"𝒾","j":"𝒿","k":"𝓀","l":"𝓁","m":"𝓂",
    "n":"𝓃","o":"𝑜","p":"𝓅","q":"𝓆","r":"𝓇","s":"𝓈","t":"𝓉","u":"𝓊","v":"𝓋","w":"𝓌","x":"𝓍","y":"𝓎","z":"𝓏"
})

GOTHIC_MAP = str.maketrans({
    "A":"𝔸","B":"𝔹","C":"ℂ","D":"𝔻","E":"𝔼","F":"𝔽","G":"𝔾","H":"ℍ","I":"𝕀","J":"𝕁","K":"𝕂","L":"𝕃","M":"𝕄",
    "N":"ℕ","O":"𝕆","P":"ℙ","Q":"𝔔","R":"ℝ","S":"𝕊","T":"𝕋","U":"𝕌","V":"𝕍","W":"𝕎","X":"𝕏","Y":"𝕐","Z":"ℤ"
})

MONO_MAP = str.maketrans({
    "A":"𝙰","B":"𝙱","C":"𝙲","D":"𝙳","E":"𝙴","F":"𝙵","G":"𝙶","H":"𝙷","I":"𝙸","J":"𝙹","K":"𝙺","L":"𝙻","M":"𝙼",
    "N":"𝙽","O":"𝙾","P":"𝙿","Q":"𝚀","R":"𝚁","S":"𝚂","T":"𝚃","U":"𝚄","V":"𝚅","W":"𝚆","X":"𝚇","Y":"𝚈","Z":"𝚉"
})

SMALLCAPS_MAP = {
    "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ","f":"ғ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ","k":"ᴋ","l":"ʟ","m":"ᴍ",
    "n":"ɴ","o":"ᴏ","p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ","u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ"
}

def apply_map(text: str, mapping) -> str:
    """Apply Unicode style mapping to text"""
    if isinstance(mapping, dict):
        return "".join(mapping.get(ch.lower(), ch) if ch.isalpha() and ch.lower() in mapping else ch for ch in text)
    return text.translate(mapping)

def wide_text(text: str) -> str:
    """Convert to wide text"""
    return " ".join(list(text))

def sparkle_wrap(text: str) -> str:
    return f"✦ {text} ✦"

def bracket_wrap(text: str) -> str:
    return f"『{text}』"

def dark_wrap(text: str) -> str:
    return f"𓆩{text}𓆪"

def square_wrap(text: str) -> str:
    boxed = {
        "A":"🄰","B":"🄱","C":"🄲","D":"🄳","E":"🄴","F":"🄵","G":"🄶","H":"🄷","I":"🄸","J":"🄹","K":"🄺","L":"🄻","M":"🄼",
        "N":"🄽","O":"🄾","P":"🄿","Q":"🅀","R":"🅁","S":"🅂","T":"🅃","U":"🅄","V":"🅅","W":"🅆","X":"🅇","Y":"🅈","Z":"🅉"
    }
    return "".join(boxed.get(ch.upper(), ch) if ch.isalpha() else ch for ch in text)

def sanitize_name(text: str) -> str:
    """Clean and sanitize input name"""
    return " ".join(text.strip().split())

def generate_name_styles(name: str):
    """Generate 10 elite name styles"""
    name = sanitize_name(name)
    return [
        ("💎 Bold Elite", apply_map(name, BOLD_MAP)),
        ("✍️ Italic Pro", apply_map(name, ITALIC_MAP)),
        ("🖌️ Script Lux", apply_map(name, SCRIPT_MAP)),
        ("🦇 Gothic Dark", apply_map(name, GOTHIC_MAP)),
        ("💻 Mono Code", apply_map(name, MONO_MAP)),
        ("⭕ Circled", apply_map(name, CIRCLED_MAP)),
        ("🔤 Small Caps", apply_map(name, SMALLCAPS_MAP)),
        ("📏 Wide Style", wide_text(name)),
        ("⬜ Squared", square_wrap(name)),
        ("𓆩 Elite 𓆪", dark_wrap(bracket_wrap(sparkle_wrap(name))))
    ]

def init(client_instance):
    """Register plugin with help system"""
    commands = [
        ".namestyle <name> - Generate 10 elite display name styles",
        ".namestyle (reply) - Style replied message text"
    ]
    description = "Generate 10 elite display-name variants for Telegram profiles and bios"
    add_handler("namestyle", commands, description)

async def get_input_text(event):
    """Get text from command args or replied message"""
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.raw_text:
            return reply.raw_text.strip()
    
    text = event.text.split(maxsplit=1)
    if len(text) > 1:
        return text[1].strip()
    
    return None

async def register_commands():
    """Register all namestyle commands"""
    
    @CipherElite.on(events.NewMessage(pattern=r"^\.namestyle(?:\s+(.*))?$"))
    @rishabh()
    async def namestyle(event):
        raw_name = await get_input_text(event)
        
        if not raw_name:
            await event.reply(
                "❌ **Usage:**\n"
                "`.namestyle Rishabh Anand`\n"
                "**OR**\n"
                "Reply to any message with `.namestyle`"
            )
            return
        
        if len(raw_name) > 40:
            await event.reply("❌ **Name too long!** Keep under 40 chars.")
            return
        
        # Generate styles
        styles = generate_name_styles(raw_name)
        
        # Build response
        msg = f"✨ **<b>NameStyle Elite</b>** ✨\n\n"
        msg += f"📝 **Input:** `{raw_name}`\n\n"
        
        for idx, (label, styled) in enumerate(styles, 1):
            msg += f"{idx}. **{label}**\n"
            msg += f"`{styled}`\n\n"
        
        msg += "💡 **Tip:** Long press to copy any style!"
        
        await event.reply(msg)

# Auto-register on import
register_commands()
