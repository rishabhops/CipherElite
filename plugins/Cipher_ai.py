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

# System prompt - Intelligent response length based on question
SYSTEM_PROMPT = """You are Cipher AI, created by @thanosceo for the CipherElite Userbot.

RESPONSE GUIDELINES:
1. **For simple questions** (definitions, quick facts, yes/no): Keep SHORT (1-2 paragraphs)
2. **For complex questions** (how-to, tutorials, guides, code): Provide COMPLETE detailed answer
3. **For list-based questions** (pros/cons, steps, process): Use numbered/bullet points
4. **ALWAYS use **bold** for important keywords and section headers**
5. Avoid unnecessary apologies and disclaimers
6. Use line breaks and formatting for readability
7. Include practical examples when relevant for tutorials/how-to
8. For deployment/setup guides: Provide COMPLETE step-by-step instructions
9. Don't truncate - give full answer, not partial

SMART FORMATTING:
• Simple → 1-2 paragraphs with bold highlights
• Tutorial/How-to → Numbered steps, detailed explanations
• Code → Minimal but complete examples
• Guides → Complete with all necessary details
• Always prioritize completeness over brevity for complex topics"""


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
        """Make request to Google Generative AI with smart response handling"""
        try:
            api_key = ai_config.get_api_key()
            if not api_key:
                return "❌ **API Key not configured!**\n\nUse `.setai <key>` to set up Google Gemini API.\n\n🔗 Get key: https://aistudio.google.com/"
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Format messages for Gemini
            text_input = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            # Allow more tokens for complete responses
            response = model.generate_content(
                text_input,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2000,  # Allow full detailed responses
                    temperature=0.7,
                    top_p=0.9,
                )
            )
            return response.text
            
        except Exception as e:
            return f"❌ **Error:** {str(e)[:100]}"
    
    def estimate_response_type(query):
        """Estimate if question needs short or detailed answer"""
        short_keywords = ["what is", "who is", "when", "where", "how many", "define", "meaning"]
        complex_keywords = ["how to", "deploy", "explain", "tutorial", "guide", "step", "process", "setup", "install", "configure", "build", "create", "write code"]
        
        query_lower = query.lower()
        
        # Check for complex/tutorial questions
        if any(keyword in query_lower for keyword in complex_keywords):
            return "detailed"
        
        # Check if it's a simple question
        if any(keyword in query_lower for keyword in short_keywords):
            return "short"
        
        return "medium"
    
    def format_response(response, response_type):
        """Format response based on type - don't truncate complex answers"""
        response = response.strip()
        
        # Remove common unnecessary phrases only
        unnecessary_phrases = [
            "I'm glad you asked. ",
            "Great question! ",
            "Thank you for asking. ",
            "Let me explain: ",
            "Sure, here's ",
        ]
        
        for phrase in unnecessary_phrases:
            if response.startswith(phrase):
                response = response[len(phrase):]
        
        response = response.strip()
        
        # For short answers, be strict about length
        if response_type == "short" and len(response) > 500:
            sentences = response.split(". ")
            response = ". ".join(sentences[:3]) + "."
        
        # For detailed/complex answers, keep complete response
        # Only add indicator if truly massive
        elif response_type == "detailed" and len(response) > 3500:
            response = response + "\n\n💡 *Response may continue in next message if too long*"
        
        return response
    
    @CipherElite.on(events.NewMessage(pattern=r"\.ai(?:\s+(.*))?"))
    @rishabh()
    async def ai_handler(event):
        """Handle AI queries with intelligent response formatting"""
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
                    "**Simple Questions:**\n"
                    "`.ai What is Python?`\n"
                    "`.ai Who created Bitcoin?`\n\n"
                    "**Complex Questions:**\n"
                    "`.ai How to deploy Cipher Elite?`\n"
                    "`.ai Explain machine learning`\n"
                    "`.ai Write a Python function`"
                )
                return
            
            if len(query) > 2000:
                await event.reply("📝 **Query too long!** Max 2000 characters.")
                return
            
            thinking_msg = await event.reply("🤔 **Cipher AI thinking...**")
            print(f"🤖 Processing AI query: {query[:50]}...")
            
            # Estimate response type
            response_type = estimate_response_type(query)
            print(f"📊 Detected response type: {response_type}")
            
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
                    timeout=35.0
                )
            except asyncio.TimeoutError:
                response = "⏰ **Timeout:** Request took too long. Try again or use `.aiclear` to reset."
            
            if response.startswith("❌"):
                await thinking_msg.edit(response)
                print(f"❌ AI error: {response}")
                return
            
            # Format response intelligently
            response = format_response(response, response_type)
            conversation_history[chat_id].append({"role": "assistant", "content": response})
            
            # Prepare final formatted message based on response type
            if response_type == "short":
                formatted = f"🤖 **Answer:**\n\n{response}"
            
            elif response_type == "detailed":
                formatted = (
                    f"🤖 **Detailed Response:**\n\n"
                    f"{response}\n\n"
                    f"═════════════════════\n"
                    f"📌 **Q:** `{query[:60]}{'...' if len(query) > 60 else ''}`"
                )
            
            else:  # medium
                formatted = (
                    f"🤖 **Cipher AI Response:**\n\n"
                    f"{response}\n\n"
                    f"─────────────────\n"
                    f"💭 Q: `{query[:60]}{'...' if len(query) > 60 else ''}`"
                )
            
            # Handle message splitting for Telegram's 4096 char limit
            if len(formatted) > 4096:
                # Split into multiple messages intelligently
                messages = []
                current_msg = ""
                
                # Split by double newline (paragraphs)
                parts = formatted.split("\n\n")
                
                for part in parts:
                    if len(current_msg) + len(part) + 4 > 4000:
                        if current_msg:
                            messages.append(current_msg.strip())
                        current_msg = part
                    else:
                        current_msg += "\n\n" + part if current_msg else part
                
                if current_msg.strip():
                    messages.append(current_msg.strip())
                
                # Send first message by editing thinking message
                if messages:
                    await thinking_msg.edit(messages[0])
                    
                    # Send remaining messages
                    for msg in messages[1:]:
                        await asyncio.sleep(0.5)
                        await event.reply(msg)
                    
                    print(f"✅ Response sent in {len(messages)} messages ({response_type} response)")
            else:
                await thinking_msg.edit(formatted)
                print(f"✅ AI response sent ({response_type} response, {len(response)} chars)")
            
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

📝 **Smart Response System:**
• Simple questions → Concise answers
• Complex/Tutorials → Complete detailed answers
• Auto-splits long responses

📚 **Commands:**
• `.ai <question>` - Ask AI
• `.aiclear` - Clear history
• `.aiinfo` - Show this info

⚙️ **Setup:**
• `.setai <key>` - Set API key

🔗 **Get Key:** https://aistudio.google.com/"""
        
        await event.reply(info)
    
    print("✅ Cipher AI Plugin initialized (Smart Complete Response System)")
    return True
