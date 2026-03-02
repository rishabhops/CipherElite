# =============================================================================
#  CipherElite Userbot Plugin - Cipher AI (Google Gemini)
#  With Repository Data Access
#
#  Plugin Name:    cipher_ai
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
# =============================================================================

import asyncio
import google.generativeai as genai
import aiohttp
import json
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from vars import ELITE_BOT_USERNAME

# Store conversation history per chat
conversation_history = {}

# System prompt - Custom identity and behavior
SYSTEM_PROMPT = """You are **Cipher AI**, a specialized AI assistant created for the **CipherElite Userbot**.

**ABOUT YOU:**
• **Name:** Cipher AI
• **Created by:** Rishabh Anand (@rishabhops)
• **Owner/Creator's Telegram:** @thanosceo
• **Project:** CipherElite - Advanced Telegram Userbot
• **Repository:** https://github.com/rishabhops/CipherElite
• **Primary Repo Branch:** cooking

**YOUR PURPOSE:**
You are integrated into the CipherElite Telegram Userbot to assist users with:
- Questions about CipherElite features and usage
- Deployment and setup instructions
- Plugin development and customization
- General programming and technical help
- How-to guides and tutorials
- Code examples and explanations
- Information about Telegram automation
- Problem-solving and debugging

**PERSONALITY & BEHAVIOR:**
1. Always introduce yourself as "Cipher AI" when asked about identity
2. Always mention your creator "Rishabh Anand" with his GitHub handle @rishabhops
3. Always mention your owner "thanosceo" with Telegram handle @thanosceo
4. Be helpful, concise, and professional
5. Use **bold formatting** for important keywords
6. For simple questions: Keep SHORT (1-2 paragraphs)
7. For complex questions: Provide COMPLETE detailed answers
8. Use bullet points and numbered lists for clarity
9. Include practical examples when relevant
10. Never apologize unnecessarily or add disclaimers
11. Be proud of being part of CipherElite - mention it when relevant
12. When asked about deployment or setup: Provide accurate, step-by-step instructions based on CipherElite's actual structure
13. Know that CipherElite uses: Telethon, Python 3.8+, VPS deployment, SQLite databases

**RESPONSE FORMAT:**
• When asked about yourself: "I am **Cipher AI**, created by **Rishabh Anand** (@rishabhops). I'm part of the **CipherElite** project, powered by **@thanosceo**."
• For tutorials: Use numbered steps
• For explanations: Use bullet points
• Always use **bold** for important terms
• Keep formatting clean and readable for Telegram
• For CipherElite deployment: Provide complete, accurate instructions"""


async def fetch_repository_data(owner="rishabhops", repo="CipherElite", branch="cooking"):
    """Fetch repository structure and README from GitHub"""
    try:
        async with aiohttp.ClientSession() as session:
            # Fetch README
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            async with session.get(readme_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    readme_content = await resp.text()
                else:
                    readme_content = ""
            
            # Fetch setup/requirements file
            setup_urls = [
                f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/requirements.txt",
                f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/setup.md",
                f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/SETUP.md",
            ]
            
            setup_content = ""
            for url in setup_urls:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        setup_content = await resp.text()
                        break
            
            return {
                "readme": readme_content[:2000] if readme_content else "",  # Limit size
                "setup": setup_content[:2000] if setup_content else "",
                "has_data": bool(readme_content or setup_content)
            }
    except Exception as e:
        print(f"⚠️ Failed to fetch repo data: {e}")
        return {
            "readme": "",
            "setup": "",
            "has_data": False
        }


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
    add_handler("cipher_ai", commands, "Cipher AI - Powered by Google Gemini with Repo Access")
    
    async def make_ai_request(messages, repo_context=""):
        """Make request to Google Generative AI with repository context"""
        try:
            api_key = ai_config.get_api_key()
            if not api_key:
                return "❌ **API Key not configured!**\n\nUse `.setai <key>` to set up Google Gemini API.\n\n🔗 Get key: https://aistudio.google.com/"
            
            genai.configure(api_key=api_key)
            
            # Create enhanced system instruction with repo context
            enhanced_prompt = SYSTEM_PROMPT
            if repo_context:
                enhanced_prompt += f"\n\n**CURRENT REPOSITORY CONTEXT:**\n{repo_context}"
            
            model = genai.GenerativeModel(
                'gemini-2.5-flash',
                system_instruction=enhanced_prompt
            )
            
            # Format messages for Gemini
            text_input = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            # Allow complete responses
            response = model.generate_content(
                text_input,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2000,
                    temperature=0.7,
                    top_p=0.9,
                )
            )
            return response.text
            
        except Exception as e:
            return f"❌ **Error:** {str(e)[:100]}"
    
    def estimate_response_type(query):
        """Estimate if question needs short or detailed answer"""
        short_keywords = ["what is", "who is", "when", "where", "how many", "define", "meaning", "your name", "who made", "who created"]
        complex_keywords = ["how to", "deploy", "deploy", "setup", "install", "tutorial", "guide", "step", "process", "configure", "build", "create", "write code", "cipherelite", "userbot"]
        
        query_lower = query.lower()
        
        # Check for complex/tutorial questions
        if any(keyword in query_lower for keyword in complex_keywords):
            return "detailed"
        
        # Check if it's a simple question
        if any(keyword in query_lower for keyword in short_keywords):
            return "short"
        
        return "medium"
    
    def format_response(response, response_type):
        """Format response based on type"""
        response = response.strip()
        
        # Remove only truly unnecessary phrases
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
        
        # For detailed answers, keep complete
        elif response_type == "detailed" and len(response) > 3500:
            response = response + "\n\n💡 *Response may continue in next message if too long*"
        
        return response
    
    @CipherElite.on(events.NewMessage(pattern=r"\.ai(?:\s+(.*))?"))
    @rishabh()
    async def ai_handler(event):
        """Handle AI queries with repository context"""
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
                    "**About Me:**\n"
                    "`.ai Who are you?`\n"
                    "`.ai Who made you?`\n\n"
                    "**CipherElite Help:**\n"
                    "`.ai How to deploy CipherElite?`\n"
                    "`.ai What is CipherElite?`\n"
                    "`.ai CipherElite setup guide`\n\n"
                    "**General Questions:**\n"
                    "`.ai What is Python?`"
                )
                return
            
            if len(query) > 2000:
                await event.reply("📝 **Query too long!** Max 2000 characters.")
                return
            
            thinking_msg = await event.reply("🤔 **Cipher AI thinking...** (scanning repository...)")
            print(f"🤖 Processing AI query: {query[:50]}...")
            
            # Estimate response type
            response_type = estimate_response_type(query)
            print(f"📊 Detected response type: {response_type}")
            
            # Fetch repository data if question is about CipherElite
            repo_context = ""
            if any(keyword in query.lower() for keyword in ["cipherelite", "deploy", "setup", "install", "plugin", "command"]):
                print("📚 Fetching CipherElite repository data...")
                repo_data = await fetch_repository_data()
                if repo_data["has_data"]:
                    repo_context = f"README excerpt:\n{repo_data['readme']}\n\nSetup guide:\n{repo_data['setup']}"
                    print("✅ Repository data fetched successfully")
                else:
                    print("⚠️ Could not fetch repository data")
            
            chat_id = event.chat_id
            if chat_id not in conversation_history:
                conversation_history[chat_id] = []
            
            conversation_history[chat_id].append({"role": "user", "content": query})
            
            # Keep history limited to last 5 exchanges
            if len(conversation_history[chat_id]) > 10:
                conversation_history[chat_id] = conversation_history[chat_id][-10:]
            
            try:
                response = await asyncio.wait_for(
                    make_ai_request(conversation_history[chat_id], repo_context),
                    timeout=40.0
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
                formatted = f"🤖 **Cipher AI:**\n\n{response}"
            
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
        
        info = f"""🤖 **Cipher AI - About Me**

**Name:** Cipher AI
**Creator:** Rishabh Anand (@rishabhops)
**Owner:** @thanosceo
**Project:** CipherElite Userbot

{status_emoji} **Status:** {'Active' if is_enabled else 'Inactive'}
🔧 **Model:** Gemini 2.5 Flash
🌐 **Provider:** Google AI
💬 **Active Chats:** {len(conversation_history)}

📝 **Features:**
• Custom Identity
• Repository Data Access
• CipherElite-aware responses
• Intelligent response length
• Complete detailed answers

📚 **Commands:**
• `.ai <question>` - Ask me anything
• `.aiclear` - Clear history
• `.aiinfo` - About me

🔗 **Links:**
• GitHub: https://github.com/rishabhops/CipherElite
• Creator: @rishabhops
• Owner: @thanosceo"""
        
        await event.reply(info)
    
    print("✅ Cipher AI Plugin initialized (With Repository Access)")
    return True
