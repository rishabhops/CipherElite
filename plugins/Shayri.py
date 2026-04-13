# =============================================================================
#  CipherElite Master Poet (Shayari Generator)
#  Author:         CipherElite Dev (@rishabhops)
# =============================================================================

import requests
import urllib.parse
from telethon import events

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# THE MASTER POET SYSTEM PROMPT
# ==========================================
SHAYARI_PROMPT = """
You are a legendary, soulful Shayar (Urdu/Hindi poet) like Mirza Ghalib or Rahat Indori.
Your task is to write a deeply emotional, authentic, and beautiful 2-line or 4-line poetry/shayari based on the user's topic.

CRITICAL RULES:
1. QUALITY: It must be genuine poetry. Deep meaning, proper rhythm (kafiya/radeef), and real emotion. NO cringe, NO cheap jokes, NO generic robotic phrases. 
2. FORMAT: ONLY output the shayari lines. Do NOT say "Here is your shayari", do NOT use quotes, do NOT add any intro/outro text.
3. VIBE: Match the emotion perfectly. (e.g., 'love' = romantic/deep, 'broken heart' = painful/melancholic, 'attitude' = savage/royal).
4. EMOJI: Add 1 or 2 relevant emojis at the very end of the shayari.
"""

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".shayari <topic> - Get a Hinglish shayari (e.g., .shayari broken heart)",
        ".hshayari <topic> - Get a pure Hindi shayari (e.g., .hshayari dosti)",
        ".eshayari <topic> - Get an English poetic quote (e.g., .eshayari love)"
    ]
    description = (
        "✍️ **The Master Poet (Shayari)**\n"
        "🎭 Generates deep, authentic, and emotional poetry.\n"
        "🗣️ Supports Hinglish, Hindi, and English.\n"
        "⚡ Perfect rhythm and meaning, no robotic cringe.\n\n"
    )
    add_handler("shayari", commands, description)

# ==========================================
# AI GENERATOR FUNCTION
# ==========================================
def generate_shayari(topic, language):
    """Calls Pollinations AI with the Master Poet prompt."""
    try:
        if language == "Hinglish":
            lang_instruction = "Write STRICTLY in Hinglish (Hindi/Urdu words written in the English alphabet)."
        elif language == "Hindi":
            lang_instruction = "Write STRICTLY in pure Hindi Script (Devanagari - हिंदी)."
        else:
            lang_instruction = "Write STRICTLY in pure, beautiful English poetry."

        full_prompt = f"{SHAYARI_PROMPT}\n\nLanguage Rule: {lang_instruction}\n\nTopic requested by user: {topic}"
        encoded = urllib.parse.quote(full_prompt)
        
        # Using openai model for better poetic nuance instead of mistral
        url = f"https://text.pollinations.ai/{encoded}?model=openai"
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text.strip()
        return "❌ *Kalam toot gayi...* (API Error: Could not generate shayari)."
    except Exception:
        return "❌ *Lafz nahi mil rahe...* (Server Timeout)."

# ==========================================
# COMMAND HANDLERS
# ==========================================

@CipherElite.on(events.NewMessage(pattern=r"^\.shayari(?: |$)(.*)", outgoing=True))
@rishabh
async def hinglish_shayari(event):
    topic = event.pattern_match.group(1).strip()
    if not topic:
        return await event.edit("❌ **Bhai, topic toh batao!**\nExample: `.shayari broken heart` or `.shayari dosti`")
    
    await event.edit("✍️ *Soch raha hoon...*")
    shayari = generate_shayari(topic, "Hinglish")
    await event.edit(f"{shayari}")

@CipherElite.on(events.NewMessage(pattern=r"^\.hshayari(?: |$)(.*)", outgoing=True))
@rishabh
async def hindi_shayari(event):
    topic = event.pattern_match.group(1).strip()
    if not topic:
        return await event.edit("❌ **कृपया विषय बताएं!**\nExample: `.hshayari माँ` or `.hshayari प्यार`")
    
    await event.edit("✍️ *लफ्ज़ पिरो रहा हूँ...*")
    shayari = generate_shayari(topic, "Hindi")
    await event.edit(f"{shayari}")

@CipherElite.on(events.NewMessage(pattern=r"^\.eshayari(?: |$)(.*)", outgoing=True))
@rishabh
async def english_shayari(event):
    topic = event.pattern_match.group(1).strip()
    if not topic:
        return await event.edit("❌ **Please provide a topic!**\nExample: `.eshayari betrayal` or `.eshayari missing you`")
    
    await event.edit("✍️ *Channeling my inner poet...*")
    shayari = generate_shayari(topic, "English")
    await event.edit(f"{shayari}")
