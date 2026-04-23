# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    words
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".meaning <word> - Get word meaning",
        ".synonym <word> - Get synonyms",
        ".antonym <word> - Get antonyms",
        ".ud <word> - Urban Dictionary definition"
    ]
    description = "Dictionary & Words - Get meanings, synonyms, and more"
    add_handler("words", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.meaning"))
    @rishabh()
    async def meaning(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.meaning <word>`")
            return
        
        word = text[1].strip()
        msg = await event.reply(f"🔍 Searching meaning for **{word}**...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if not data:
                            await msg.edit(f"❌ No definition found for **{word}**")
                            return
                        
                        entry = data[0]
                        meanings_text = f"📖 **Word:** {entry.get('word', word).title()}\n\n"
                        
                        if 'phonetic' in entry and entry['phonetic']:
                            meanings_text += f"🔊 **Pronunciation:** {entry['phonetic']}\n\n"
                        
                        for meaning in entry.get('meanings', [])[:3]:  # Limit to 3 meanings
                            part_of_speech = meaning.get('partOfSpeech', 'Unknown')
                            meanings_text += f"**{part_of_speech.title()}:**\n"
                            
                            for i, definition in enumerate(meaning.get('definitions', [])[:2], 1):  # Limit to 2 definitions per type
                                def_text = definition.get('definition', '')
                                meanings_text += f"{i}. {def_text}\n"
                                
                                if 'example' in definition:
                                    meanings_text += f"   _Example: {definition['example']}_\n"
                            
                            meanings_text += "\n"
                        
                        await msg.edit(meanings_text[:4000])  # Telegram message limit
                    else:
                        await msg.edit(f"❌ Word **{word}** not found!")
        except Exception as e:
            await msg.edit(f"❌ Error fetching meaning: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.synonym"))
    @rishabh()
    async def synonym(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.synonym <word>`")
            return
        
        word = text[1].strip()
        msg = await event.reply(f"🔍 Finding synonyms for **{word}**...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if not data:
                            await msg.edit(f"❌ No synonyms found for **{word}**")
                            return
                        
                        synonyms = []
                        for entry in data:
                            for meaning in entry.get('meanings', []):
                                # Grab from the meaning level (New API Structure)
                                synonyms.extend(meaning.get('synonyms', []))
                                # Grab from the definition level (Old API Structure)
                                for definition in meaning.get('definitions', []):
                                    synonyms.extend(definition.get('synonyms', []))
                        
                        # Filter out empty strings, remove duplicates, and limit
                        synonyms = [s for s in synonyms if s]
                        if synonyms:
                            synonyms = list(set(synonyms))[:20]
                            synonyms_text = f"📝 **Synonyms for {word.title()}:**\n\n"
                            synonyms_text += ", ".join(synonyms)
                            await msg.edit(synonyms_text)
                        else:
                            await msg.edit(f"❌ No synonyms found for **{word}**")
                    else:
                        await msg.edit(f"❌ Word **{word}** not found!")
        except Exception as e:
            await msg.edit(f"❌ Error fetching synonyms: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.antonym"))
    @rishabh()
    async def antonym(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.antonym <word>`")
            return
        
        word = text[1].strip()
        msg = await event.reply(f"🔍 Finding antonyms for **{word}**...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if not data:
                            await msg.edit(f"❌ No antonyms found for **{word}**")
                            return
                        
                        antonyms = []
                        for entry in data:
                            for meaning in entry.get('meanings', []):
                                # Grab from the meaning level (New API Structure)
                                antonyms.extend(meaning.get('antonyms', []))
                                # Grab from the definition level (Old API Structure)
                                for definition in meaning.get('definitions', []):
                                    antonyms.extend(definition.get('antonyms', []))
                        
                        # Filter out empty strings, remove duplicates, and limit
                        antonyms = [a for a in antonyms if a]
                        if antonyms:
                            antonyms = list(set(antonyms))[:20]
                            antonyms_text = f"📝 **Antonyms for {word.title()}:**\n\n"
                            antonyms_text += ", ".join(antonyms)
                            await msg.edit(antonyms_text)
                        else:
                            await msg.edit(f"❌ No antonyms found for **{word}**")
                    else:
                        await msg.edit(f"❌ Word **{word}** not found!")
        except Exception as e:
            await msg.edit(f"❌ Error fetching antonyms: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.ud"))
    @rishabh()
    async def urban_dictionary(event):
        text = event.text.split(maxsplit=1)
        
        if len(text) < 2:
            await event.reply("❌ Usage: `.ud <word>`")
            return
        
        word = text[1].strip()
        msg = await event.reply(f"🔍 Searching Urban Dictionary for **{word}**...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.urbandictionary.com/v0/define?term={word}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if not data.get('list'):
                            await msg.edit(f"❌ No Urban Dictionary definition found for **{word}**")
                            return
                        
                        # Get top definition
                        definition = data['list'][0]
                        
                        ud_text = f"📚 **Urban Dictionary: {word.title()}**\n\n"
                        ud_text += f"**Definition:**\n{definition['definition'][:500]}\n\n"
                        
                        if definition.get('example'):
                            ud_text += f"**Example:**\n{definition['example'][:300]}\n\n"
                        
                        ud_text += f"👍 {definition.get('thumbs_up', 0)} | 👎 {definition.get('thumbs_down', 0)}"
                        
                        await msg.edit(ud_text[:4000])
                    else:
                        await msg.edit(f"❌ Failed to fetch definition from Urban Dictionary")
        except Exception as e:
            await msg.edit(f"❌ Error: {str(e)}")
