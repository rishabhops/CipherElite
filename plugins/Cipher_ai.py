# =============================================================================
#  CipherElite Userbot Plugin - Cipher AI (Google Gemini)
#
#  Plugin Name:    cipher_ai
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
# =============================================================================

import asyncio
import google.generativeai as genai
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from vars import ELITE_BOT_USERNAME

# Store conversation history per chat
conversation_history = {}

# System prompt
SYSTEM_PROMPT = """You are Cipher AI, created by @thanosceo for the CipherElite Userbot. 
Provide short, natural, and accurate answers. Keep responses concise and helpful.
Avoid verbose explanations unless requested."""


def init(client):
    """Initialize the Cipher AI plugin"""
    try:
        from plugins.ai_setup import ai_config  # Import centralized config
    except ImportError:
        print("❌ ERROR: ai_setup.py not found! Please create it first.")
        return False
    
    commands = [
        f".ai <question>   — Ask Cipher AI a question",
        f".aiclear         — Clear conversation history",
        f".aiinfo          — Show AI info"
    ]
    add_handler("cipher_ai", commands, "Cipher AI - Powered by Google Gemini")
    
    async def make_ai_request(messages):
        """Make request to Google Generative AI"""
        try:
            api_key = ai_config.get_api_key()
            if not api_key:
                return "❌ **API Key not configured!** Use `.setai <key>` to set up Google Gemini API."
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Format messages for Gemini
            text_input = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            response = model.generate_content(text_input)
            return response.text
            
        except Exception as e:
            return f"❌ **Error:** {str(e)[:150]}"
    
    @CipherElite.on(events.NewMessage(pattern=r"\.ai(?:\s+(.*))?"))
    @rishabh()
    async def ai_handler(event):
        """Handle AI queries"""
        try:
            if not ai_config.is_enabled():
                await event.reply(
                    f"❌ **API Key not configured!**\n\n"
                    f"Use `.setai <your_gemini_api_key>` to set up AI.\n\n"
                    f"🔗 Get key from: https://aistudio.google.com/"
                )
                return
            
            query = event.pattern_match.group(1)
            if not query:
                await event.reply(
                    f"❓ **Usage:** `.ai <your question>`\n\n"
                    f"**Examples:**\n"
                    f"• `.ai What is AI?`\n"
                    f"• `.ai Write a Python function`\n"
                    f"• `.ai Explain quantum physics`"
                )
                return
            
            if len(query) > 2000:
                await event.reply("📝 **Query too long!** Keep it under 2000 characters.")
                return
            
            thinking_msg = await event.reply("🤔 **Cipher AI is thinking...**")
            print(f"🤖 Processing AI query: {query[:50]}...")
            
            chat_id = event.chat_id
            if chat_id not in conversation_history:
                conversation_history[chat_id] = []
            
            conversation_history[chat_id].append({"role": "user", "content": query})
            
            # Keep history limited to last 5 exchanges
            if len(conversation_history[chat_id]) > 10:
                conversation_history[chat_id] = conversation_history[chat_id][-10:]
            
            try:
                response = await asyncio.wait_for(
                    make_ai_request(conversation_history[chat_id]),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                response = "⏰ **Timeout:** AI took too long. Try a shorter question."
            
            if response.startswith("❌"):
                await thinking_msg.edit(response)
                print(f"❌ AI error: {response}")
                return
            
            conversation_history[chat_id].append({"role": "assistant", "content": response})
            
            # Split long responses
            if len(response) > 3500:
                parts = [response[i:i+3500] for i in range(0, len(response), 3500)]
                await thinking_msg.edit(
                    f"🤖 **Cipher AI Response (Part 1/{len(parts)}):**\n\n{parts[0]}"
                )
                for i, part in enumerate(parts[1:], 2):
                    await event.reply(f"🤖 **Part {i}/{len(parts)}:**\n\n{part}")
            else:
                formatted = (
                    f"🤖 **Cipher AI Response:**\n\n{response}\n\n"
                    f"💭 **Query:** `{query[:80]}{'...' if len(query) > 80 else ''}`"
                )
                await thinking_msg.edit(formatted)
            
            print(f"✅ AI response sent successfully")
            
        except Exception as e:
            print(f"❌ AI Handler Error: {e}")
            try:
                await event.reply(f"❌ **Error:** {str(e)[:150]}")
            except:
                pass
    
    @CipherElite.on(events.NewMessage(pattern=r"\.aiclear"))
    @rishabh()
    async def aiclear_handler(event):
        """Clear conversation history"""
        chat_id = event.chat_id
        if chat_id in conversation_history:
            msg_count = len(conversation_history[chat_id])
            del conversation_history[chat_id]
            await event.reply(f"🗑️ **Cleared!** Removed `{msg_count}` messages.")
        else:
            await event.reply("📭 **No history** for this chat.")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.aiinfo"))
    @rishabh()
    async def aiinfo_handler(event):
        """Show AI info"""
        info = f"""🤖 **Cipher AI Information:**

✨ **Provider:** Google Generative AI (Gemini)
🔑 **API Status:** {'✅ Configured' if ai_config.is_enabled() else '❌ Not Set'}
🌐 **Model:** gemini-2.5-flash
💬 **Active Chats:** {len(conversation_history)}

📝 **Commands:**
• `.ai <question>` - Ask a question
• `.aiclear` - Clear history
• `.aiinfo` - Show this info
• `.setai <key>` - Set API key (from AI Setup)

🔗 **Links:**
• Get API Key: https://aistudio.google.com/
• Google AI Docs: https://ai.google.dev/"""
        
        await event.reply(info)
    
    print("✅ Cipher AI Plugin initialized (Google Gemini)")
    return True
