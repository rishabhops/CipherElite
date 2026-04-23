# =============================================================================
#  CipherElite Offline Shayari Repository
#  Author:         CipherElite Dev (@rishabhops)
# =============================================================================

import random
from telethon import events

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# SHAYARI REPOSITORY (Add as many as you want here!)
# ==========================================
SHAYARI_DB = {
    "love": [
        "Aapki muskurahat ne hamara hosh uda diya,\nHum akele the, aapne mehfil se mila diya. ❤️",
        "Nazron se nazar mili to baat ho gayi,\nAapki ek hasi se hamari subah, raat ho gayi. 🌹",
        "Zindagi mein aapka aana ek khwab sa lagta hai,\nAapke bina har lamha azaab sa lagta hai. ✨"
    ],
    "sad": [
        "Khamoshi se bikharna aa gaya hai,\nHumein ab khud mein rehna aa gaya hai. 💔",
        "Dard ki mehfil mein ek naya fasaana likhenge,\nTere bina zindagi ka har lamha purana likhenge. 🥀",
        "Jisko chaha tha dil se wo door ho gaya,\nMera dil toot kar choor choor ho gaya. 🌧️"
    ],
    "attitude": [
        "Hukumat wo hi karta hai jiska dilon par raaj hota hai,\nYun to gali ke kutton ke sar pe bhi taj hota hai. 🔥",
        "Hum wo nahi jo duniya ke hisaab se chalein,\nHum wo hain jiske hisaab se duniya chale. 👑",
        "Sher ko shikaar karna sikhaya nahi jata,\nAur humein hamari aukaat yaad dilaya nahi jata. 🦅"
    ],
    "dosti": [
        "Dosti ka rishta sabse pyara hota hai,\nIsme har dard ka sahara hota hai. 🤝",
        "Dost wo nahi jo sirf khushi mein saath de,\nDost wo hai jo rote hue ko hasa de. 🫂",
        "Zindagi ki raahon mein bohot dost milenge,\nPar hum jaisa pagal dost dhoondhte reh jaoge. 😜"
    ],
    "motivational": [
        "Manzil unhi ko milti hai jinke sapno mein jaan hoti hai,\nPankhon se kuch nahi hota, hauslon se udaan hoti hai. 🕊️",
        "Waqt se ladkar jo naseeb badal de,\nInsaan wahi jo apni taqdeer badal de. ⏳"
    ]
}

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    # Dynamically grab the keys from our database to show in the help menu
    available_keys = ", ".join(SHAYARI_DB.keys())
    
    commands = [
        f".shayari <category> - Fetch a random shayari"
    ]
    description = (
        "✍️ **Offline Shayari Repository**\n"
        "🎭 Instant, high-quality, handpicked poetry.\n"
        f"📂 **Available Categories:** `{available_keys}`\n\n"
    )
    add_handler("shayari", commands, description)

# ==========================================
# COMMAND HANDLER
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"^\.shayari(?: |$)(.*)", outgoing=True))
@rishabh
async def random_shayari_handler(event):
    category = event.pattern_match.group(1).strip().lower()
    available_keys = ", ".join(SHAYARI_DB.keys())
    
    # If user didn't type a category or typed an invalid one
    if not category or category not in SHAYARI_DB:
        error_msg = (
            "❌ **Bhai, sahi category batao!**\n\n"
            f"📂 **Available Categories:**\n`{available_keys}`\n\n"
            "📝 **Usage:** `.shayari love` or `.shayari attitude`"
        )
        return await event.edit(error_msg)
    
    # Pick a random shayari from the chosen category
    selected_shayari = random.choice(SHAYARI_DB[category])
    
    # Format and send it
    final_text = (
        f"╭───〔 🎭 **{category.capitalize()} Shayari** 〕───╮\n\n"
        f"**{selected_shayari}**\n\n"
        f"╰───〔 ✍️ **CipherElite** 〕───╯"
    )
    
    await event.edit(final_text)
