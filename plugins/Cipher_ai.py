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

# System prompt - Optimized for short, concise responses
SYSTEM_PROMPT = """You are Cipher AI, created by @thanosceo for the CipherElite Userbot.

IMPORTANT RULES:
1. Keep responses SHORT and CONCISE (max 150 words)
2. Use bold text for important words using **word**
3. Use line breaks for readability
4. Never use code blocks unless absolutely necessary
5. Be direct and helpful
6. If asked for code, provide minimal examples only
7. Use emojis sparingly for better formatting

Example response style:
**Topic:** Brief explanation with **bold** highlights
• Point 1
• Point 2
💡 Pro tip if relevant"""


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
        """Make request to Google Generative AI with optimized settings"""
        try:
            api_key = ai_config.get_api_key()
            if not api_key:
                return "❌ **API Key not configured!**\n\nUse `.setai <key>` to set up Google Gemini API.\n\n🔗 Get key: https://aistudio.google.com/"
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Format messages for Gemini
            text_input = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            # Use lower temperature and tokens for shorter responses
            response = model.generate_content(
                text_input,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=150,  # Limit response length
                    temperature=0.7,  # Slightly lower for more focused responses
                    top_p=0.9,
                )
            )
            return response.text
            
        except Exception as e:
            return f"❌ **Error:** {str(e)[:100]}"
    
    @CipherElite.on(events.NewMessage(pattern=r"\.ai(?:\s+(.*))?"))
    @rishabh()
    async def ai_handler(event):
        """Handle AI queries with optimized formatting"""
        try:
            if not ai_config.is_enabled():
                await event.reply(
                    "❌ **API Key Not Set**\n\n"
                    "Use `.setai <your_gemini_api_key>`\n\n"
                    "🔗 Get key: https://aistudio.google.com/"
                )
                return
            
            query = event.pattern_match.group(1)
            if not query:
                await event.reply(
                    "❓ **How to use Cipher AI:**\n\n"
                    "`.ai What is Python?`\n"
                    "`.ai Write a hello world`\n"
                    "`.ai Explain blockchain`\n"
                    "`.ai How does AI work?`"
                )
                return
            
            if len(query) > 2000:
                await event.reply("📝 **Query too long!** Max 2000 characters.")
                return
            
            thinking_msg = await event.reply("🤔 **Cipher AI thinking...**")
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
                    timeout=25.0
                )
            except asyncio.TimeoutError:
                response = "⏰ **Timeout:** Request took too long. Try again."
            
            if response.startswith("❌"):
                await thinking_msg.edit(response)
                print(f"❌ AI error: {response}")
                return
            
            conversation_history[chat_id].append({"role": "assistant", "content": response})
            
            # Optimize response for Telegram display
            response = response.strip()
            
            # If response is still long, summarize it
            if len(response) > 2000:
                response = response[:1900] + "\n\n*[Response truncated - use `.aiclear` and ask again]*"
            
            # Format final response with better styling
            if len(response) > 500:
                # For longer responses, add a separator
                formatted = (
                    f"🤖 **Cipher AI Response:**\n\n"
                    f"{response}\n\n"
                    f"─────────────────\n"
                    f"💭 Q: `{query[:60]}{'...' if len(query) > 60 else ''}`"
                )
            else:
                # For shorter responses, more compact format
                formatted = (
                    f"🤖 **Cipher AI:**\n\n"
                    f"{response}"
                )
            
            await thinking_msg.edit(formatted)
            print(f"✅ AI response sent successfully ({len(response)} chars)")
            
        except Exception as e:
            print(f"❌ AI Handler Error: {e}")
            try:
                await event.reply(f"❌ **Error:** {str(e)[:100]}")
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
            await event.reply(f"🗑️ **Cleared!** {msg_count} messages removed.")
        else:
            await event.reply("📭 **No history** in this chat.")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.aiinfo"))
    @rishabh()
    async def aiinfo_handler(event):
        """Show AI info"""
        is_enabled = ai_config.is_enabled()
        status_emoji = "✅" if is_enabled else "❌"
        
        info = f"""🤖 **Cipher AI - Information**

{status_emoji} **Status:** {'Active' if is_enabled else 'Inactive'}
🔧 **Model:** Gemini 2.5 Flash
🌐 **Provider:** Google AI
💬 **Active Chats:** {len(conversation_history)}

📝 **Commands:**
• `.ai <question>` - Ask AI
• `.aiclear` - Clear history
• `.aiinfo` - Show this info

⚙️ **Setup:**
• `.setai <key>` - Set API key

🔗 **Get Key:** https://aistudio.google.com/"""
        
        await event.reply(info)
    
    print("✅ Cipher AI Plugin initialized (Google Gemini - Optimized)")
    return True
