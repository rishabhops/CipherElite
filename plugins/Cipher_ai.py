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
1. **For simple questions** (definitions, quick facts, yes/no): Keep response SHORT (2-3 sentences max)
2. **For complex questions** (how-to, explanations, code): Provide detailed helpful answer
3. **For list-based questions** (pros/cons, steps): Use bullet points
4. **ALWAYS use **bold** for important keywords**
5. Avoid unnecessary fluff and redundant explanations
6. Use line breaks for readability
7. Include practical examples when relevant
8. Don't apologize or add disclaimers unless necessary

SMART FORMATTING:
• Simple answer → 1-2 paragraphs, bold highlights
• Complex answer → Structured with headers, bullets, examples
• Code answers → Keep examples minimal but useful
• Always prioritize clarity over length"""


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
            
            # Allow more tokens for detailed responses but let AI decide length
            response = model.generate_content(
                text_input,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,  # Allow up to 800 tokens for flexibility
                    temperature=0.7,  # Balanced for quality
                    top_p=0.9,
                )
            )
            return response.text
            
        except Exception as e:
            return f"❌ **Error:** {str(e)[:100]}"
    
    def estimate_response_type(query):
        """Estimate if question needs short or detailed answer"""
        short_keywords = ["what is", "who is", "when", "where", "how many", "is ", "does ", "can ", "define", "meaning"]
        complex_keywords = ["how to", "explain", "why", "process", "tutorial", "guide", "write", "create", "build", "difference", "comparison"]
        
        query_lower = query.lower()
        
        # Check if it's a simple question
        if any(keyword in query_lower for keyword in short_keywords):
            if any(keyword in query_lower for keyword in complex_keywords):
                return "medium"  # Both simple and complex indicators
            return "short"
        
        # Check if it's complex
        if any(keyword in query_lower for keyword in complex_keywords):
            return "detailed"
        
        return "medium"  # Default
    
    def format_response(response, response_type):
        """Format response based on type"""
        response = response.strip()
        
        # Remove common unnecessary phrases
        unnecessary_phrases = [
            "I'm glad you asked",
            "Great question",
            "Thank you for asking",
            "I appreciate the question",
            "Let me explain",
            "Sure, I'll help you with",
            "As I mentioned",
            "It's important to note that",
            "I should mention that",
        ]
        
        for phrase in unnecessary_phrases:
            response = response.replace(phrase + ", ", "")
            response = response.replace(phrase + ". ", "")
        
        response = response.strip()
        
        # For very long responses, intelligently truncate
        if response_type == "short" and len(response) > 400:
            # For short answers that became long, truncate first paragraph
            sentences = response.split(". ")
            response = ". ".join(sentences[:2]) + "."
        
        elif response_type == "medium" and len(response) > 1500:
            # For medium answers, keep structure but limit
            response = response[:1400] + "..."
        
        elif response_type == "detailed" and len(response) > 3000:
            # For detailed answers, more lenient
            response = response[:2900] + "\n\n*[Response shortened]*"
        
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
                    "**Simple questions:**\n"
                    "`.ai What is Python?`\n"
                    "`.ai Who created Bitcoin?`\n\n"
                    "**Complex questions:**\n"
                    "`.ai How to learn Python?`\n"
                    "`.ai Explain machine learning`\n"
                    "`.ai Write a hello world program`"
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
                    timeout=30.0
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
            
            # Prepare final formatted message
            if response_type == "short":
                # Compact format for simple answers
                formatted = (
                    f"🤖 **Answer:**\n\n"
                    f"{response}"
                )
            elif response_type == "medium":
                # Standard format
                formatted = (
                    f"🤖 **Cipher AI Response:**\n\n"
                    f"{response}\n\n"
                    f"─────────────────\n"
                    f"💭 Q: `{query[:55]}{'...' if len(query) > 55 else ''}`"
                )
            else:  # detailed
                # Full format for detailed answers
                formatted = (
                    f"🤖 **Cipher AI - Detailed Response:**\n\n"
                    f"{response}\n\n"
                    f"═════════════════════\n"
                    f"📌 **Question:** `{query[:60]}{'...' if len(query) > 60 else ''}`\n"
                    f"💡 Use `.aiclear` to reset history"
                )
            
            # Split if too long for Telegram
            if len(formatted) > 4096:
                # Split into multiple messages
                parts = []
                current_part = ""
                paragraphs = formatted.split("\n\n")
                
                for para in paragraphs:
                    if len(current_part) + len(para) + 2 > 4000:
                        if current_part:
                            parts.append(current_part)
                        current_part = para
                    else:
                        current_part += "\n\n" + para if current_part else para
                
                if current_part:
                    parts.append(current_part)
                
                # Send first part and edit thinking message
                await thinking_msg.edit(parts[0])
                
                # Send remaining parts
                for part in parts[1:]:
                    await asyncio.sleep(0.5)
                    await event.reply(part)
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
• Simple questions → Short answers
• Complex questions → Detailed answers
• Removes unnecessary fluff

📚 **Commands:**
• `.ai <question>` - Ask AI
• `.aiclear` - Clear history
• `.aiinfo` - Show this info

⚙️ **Setup:**
• `.setai <key>` - Set API key

🔗 **Get Key:** https://aistudio.google.com/"""
        
        await event.reply(info)
    
    print("✅ Cipher AI Plugin initialized (Smart Response System)")
    return True
