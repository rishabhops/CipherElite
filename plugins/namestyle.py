# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    namestyle
#  Author:         rishabh Anand
#  GitHub:         rishabhops
#  Description:    Generate 10 elite display-name variants from text
#  Command:        .namestyle <name>
#                  Reply to any message with .namestyle
# =============================================================================

from telethon import events
from utils.decorators import rishabh_help

# =========================
# Character maps
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
    "A":"𝕬","B":"𝕭","C":"𝕮","D":"𝕯","E":"𝕰","F":"𝕱","G":"𝕲","H":"𝕳","I":"𝕴","J":"𝕵","K":"𝕶","L":"𝕷","M":"𝕸",
    "N":"𝕹","O":"𝕺","P":"𝕻","Q":"𝕼","R":"𝕽","S":"𝕾","T":"𝕿","U":"𝖀","V":"𝖁","W":"𝖂","X":"𝖃","Y":"𝖄","Z":"𝖅",
    "a":"𝖆","b":"𝖇","c":"𝖈","d":"𝖉","e":"𝖊","f":"𝖋","g":"𝖌","h":"𝖍","i":"𝖎","j":"𝖏","k":"𝖐","l":"𝖑","m":"𝖒",
    "n":"𝖓","o":"𝖔","p":"𝖕","q":"𝖖","r":"𝖗","s":"𝖘","t":"𝖙","u":"𝖚","v":"𝖛","w":"𝖜","x":"𝖝","y":"𝖞","z":"𝖟"
})

MONO_MAP = str.maketrans({
    "A":"𝙰","B":"𝙱","C":"𝙲","D":"𝙳","E":"𝙴","F":"𝙵","G":"𝙶","H":"𝙷","I":"𝙸","J":"𝙹","K":"𝙺","L":"𝙻","M":"𝙼",
    "N":"𝙽","O":"𝙾","P":"𝙿","Q":"𝚀","R":"𝚁","S":"𝚂","T":"𝚃","U":"𝚄","V":"𝚅","W":"𝚆","X":"𝚇","Y":"𝚈","Z":"𝚉",
    "a":"𝚊","b":"𝚋","c":"𝚌","d":"𝚍","e":"𝚎","f":"𝚏","g":"𝚐","h":"𝚑","i":"𝚒","j":"𝚓","k":"𝚔","l":"𝚕","m":"𝚖",
    "n":"𝚗","o":"𝚘","p":"𝚙","q":"𝚚","r":"𝚛","s":"𝚜","t":"𝚝","u":"𝚞","v":"𝚟","w":"𝚠","x":"𝚡","y":"𝚢","z":"𝚣",
    "0":"𝟶","1":"𝟷","2":"𝟸","3":"𝟹","4":"𝟺","5":"𝟻","6":"𝟼","7":"𝟽","8":"𝟾","9":"𝟿"
})

CIRCLED_MAP = str.maketrans({
    "A":"Ⓐ","B":"Ⓑ","C":"Ⓒ","D":"Ⓓ","E":"Ⓔ","F":"Ⓕ","G":"Ⓖ","H":"Ⓗ","I":"Ⓘ","J":"Ⓙ","K":"Ⓚ","L":"Ⓛ","M":"Ⓜ",
    "N":"Ⓝ","O":"Ⓞ","P":"Ⓟ","Q":"Ⓠ","R":"Ⓡ","S":"Ⓢ","T":"Ⓣ","U":"Ⓤ","V":"Ⓥ","W":"Ⓦ","X":"Ⓧ","Y":"Ⓨ","Z":"Ⓩ",
    "a":"ⓐ","b":"ⓑ","c":"ⓒ","d":"ⓓ","e":"ⓔ","f":"ⓕ","g":"ⓖ","h":"ⓗ","i":"ⓘ","j":"ⓙ","k":"ⓚ","l":"ⓛ","m":"ⓜ",
    "n":"ⓝ","o":"ⓞ","p":"ⓟ","q":"ⓠ","r":"ⓡ","s":"ⓢ","t":"ⓣ","u":"ⓤ","v":"ⓥ","w":"ⓦ","x":"ⓧ","y":"ⓨ","z":"ⓩ",
    "0":"⓪","1":"①","2":"②","3":"③","4":"④","5":"⑤","6":"⑥","7":"⑦","8":"⑧","9":"⑨"
})

SMALLCAPS_MAP = {
    "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ","f":"ғ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ","k":"ᴋ","l":"ʟ","m":"ᴍ",
    "n":"ɴ","o":"ᴏ","p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ","u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ"
}

# =========================
# Helpers
# =========================

def apply_map(text: str, mapping) -> str:
    if isinstance(mapping, dict):
        return "".join(mapping.get(ch.lower(), ch) if ch.isalpha() and ch.lower() in mapping else ch for ch in text)
    return text.translate(mapping)

def wide_text(text: str) -> str:
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
    return " ".join(text.strip().split())

def generate_name_styles(name: str):
    name = sanitize_name(name)
    return [
        ("Bold", apply_map(name, BOLD_MAP)),
        ("Italic", apply_map(name, ITALIC_MAP)),
        ("Script", apply_map(name, SCRIPT_MAP)),
        ("Gothic", apply_map(name, GOTHIC_MAP)),
        ("Monospace", apply_map(name, MONO_MAP)),
        ("Circled", apply_map(name, CIRCLED_MAP)),
        ("Small Caps", apply_map(name, SMALLCAPS_MAP)),
        ("Wide", wide_text(name)),
        ("Squared", square_wrap(name)),
        ("Elite", dark_wrap(bracket_wrap(sparkle_wrap(name))))
    ]

# =========================
# Help metadata
# =========================

@rishabh_help(
    name="namestyle",
    description="Generate 10 elite display-name styles from input text.",
    usage=".namestyle <name> or reply to a message with .namestyle",
    examples=[".namestyle Rishabh Anand", "reply to a name with .namestyle"]
)
def register_namestyle_help():
    return {
        "namestyle": {
            "commands": [".namestyle <name>"],
            "description": "Create 10 stylish name variants for Telegram display name or bio use."
        }
    }

# =========================
# Main command
# =========================

async def namestyle_handler(event):
    reply = await event.get_reply_message()
    args = event.pattern_match.group(1).strip() if event.pattern_match else ""

    if args:
        raw_name = args
    elif reply and reply.raw_text:
        raw_name = reply.raw_text.strip()
    else:
        await event.edit(
            "<b>❌ Give me a name first.</b>\n\n"
            "<b>Usage:</b> <code>.namestyle Rishabh Anand</code>\n"
            "<b>Or:</b> reply to any message with <code>.namestyle</code>"
        )
        return

    if len(raw_name) > 40:
        await event.edit("<b>❌ Name is too long.</b>\nKeep it under <code>40</code> characters.")
        return

    styles = generate_name_styles(raw_name)

    text = f"<b>✨ NameStyle Generator</b>\n"
    text += f"<b>Input:</b> <code>{raw_name}</code>\n\n"

    for idx, (label, styled) in enumerate(styles, start=1):
        text += f"<b>{idx}. {label}</b>\n<code>{styled}</code>\n\n"

    text += "<b>Tip:</b> Tap and hold to copy any style."

    await event.edit(text, parse_mode="html")

# =========================
# Init / registration
# =========================

def init(client):
    client.add_event_handler(
        namestyle_handler,
        events.NewMessage(outgoing=True, pattern=r"^\.namestyle(?:\s+(.*))?$")
    )
