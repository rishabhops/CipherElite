# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    nvidia_ai
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
#
#  IMPORTANT:
#    • If you copy, fork or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • Give proper credit back to the CipherElite Userbot author:
#        – GitHub: https://github.com/rishabhops/CipherElite
#        – Telegram: @rishabhops
#
#  Thank you for respecting open‐source software!
# =============================================================================

import os
import asyncio
import aiohttp
import json
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh

# Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "deepseek-ai/deepseek-r1"

# Store conversation history per chat
conversation_history = {}

async def make_nvidia_request(messages, temperature=0.6, top_p=0.7, max_tokens=1024):
    """Make async request to NVIDIA API"""
    try:
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{NVIDIA_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                elif response.status == 401:
                    return "❌ **Authentication Error:** Invalid API key. Use `.aiset <key>` to set a valid key."
                elif response.status == 429:
                    return "⏳ **Rate Limited:** Too many requests. Please wait a moment."
                elif response.status == 403:
                    return "🚫 **Access Denied:** Check your API key permissions."
                else:
                    error_text = await response.text()
                    return f"❌ **API Error ({response.status}):** {error_text[:200]}"
                    
    except asyncio.TimeoutError:
        return "⏰ **Timeout Error:** Request took too long. Please try again."
    except aiohttp.ClientError as e:
        return f"🌐 **Network Error:** {str(e)}"
    except Exception as e:
        return f"❌ **Unexpected Error:** {str(e)}"

@CipherElite.on(events.NewMessage(pattern=r"\.ai(?:\s+(.*))?"))
@rishabh()
async def ai_handler(event):
    """Handle AI queries with proper error handling"""
    thinking_msg = None
    try:
        # Check if API key is set
        if not NVIDIA_API_KEY:
            await event.reply("🔑 **API Key Required!**\n\nUse `.aiset <your_nvidia_api_key>` to set your NVIDIA API key first.\n\n📋 Get your key from: https://build.nvidia.com/")
            return
        
        # Get query
        query = event.pattern_match.group(1)
        if not query:
            await event.reply("❓ **Usage:** `.ai <your question>`\n\n**Examples:**\n• `.ai What is AI?`\n• `.ai Write a Python function`\n• `.ai Explain quantum physics`")
            return
        
        # Limit query length
        if len(query) > 2000:
            await event.reply("📝 **Query too long!** Please keep your question under 2000 characters.")
            return
        
        # Show thinking message
        thinking_msg = await event.reply("🤔 **Processing your query...**\n\n⏳ This may take a few seconds.")
        
        # Get conversation history for this chat
        chat_id = event.chat_id
        if chat_id not in conversation_history:
            conversation_history[chat_id] = []
        
        # Add user message to history
        conversation_history[chat_id].append({"role": "user", "content": query})
        
        # Keep only last 6 messages to avoid token limit
        if len(conversation_history[chat_id]) > 6:
            conversation_history[chat_id] = conversation_history[chat_id][-6:]
        
        # Make API request with timeout
        try:
            response = await asyncio.wait_for(
                make_nvidia_request(conversation_history[chat_id]),
                timeout=45.0  # 45 second total timeout
            )
        except asyncio.TimeoutError:
            response = "⏰ **Request Timeout:** The AI took too long to respond. Please try a shorter question."
        
        # Check if response is an error
        if response.startswith("❌") or response.startswith("⏳") or response.startswith("🚫"):
            await thinking_msg.edit(response)
            return
        
        # Add AI response to history
        conversation_history[chat_id].append({"role": "assistant", "content": response})
        
        # Format and send response
        if len(response) > 3500:  # Telegram message limit
            # Split long responses
            parts = [response[i:i+3500] for i in range(0, len(response), 3500)]
            await thinking_msg.edit(f"🤖 **NVIDIA AI Response (Part 1/{len(parts)}):**\n\n{parts[0]}")
            
            for i, part in enumerate(parts[1:], 2):
                await event.reply(f"🤖 **Part {i}/{len(parts)}:**\n\n{part}")
        else:
            formatted_response = f"🤖 **NVIDIA AI Response:**\n\n{response}\n\n"
            formatted_response += f"💭 **Query:** `{query[:100]}{'...' if len(query) > 100 else ''}`"
            await thinking_msg.edit(formatted_response)
        
        print(f"✅ AI response sent successfully for query: {query[:50]}...")
        
    except Exception as e:
        error_msg = f"❌ **Error:** {str(e)}"
        print(f"❌ AI Handler Error: {e}")
        
        if thinking_msg:
            try:
                await thinking_msg.edit(error_msg)
            except:
                await event.reply(error_msg)
        else:
            await event.reply(error_msg)

@CipherElite.on(events.NewMessage(pattern=r"\.aiset(?:\s+(.*))?"))
@rishabh()
async def aiset_handler(event):
    """Set NVIDIA API key"""
    try:
        api_key = event.pattern_match.group(1)
        if not api_key:
            await event.reply("🔑 **Usage:** `.aiset <your_nvidia_api_key>`\n\n📋 **Steps:**\n1. Visit https://build.nvidia.com/\n2. Sign up/Login\n3. Generate API key\n4. Use this command to set it")
            return
        
        # Basic validation
        if len(api_key) < 10:
            await event.reply("❌ **Invalid API key format.** Please check your key.")
            return
        
        # Set environment variable
        os.environ["NVIDIA_API_KEY"] = api_key
        global NVIDIA_API_KEY
        NVIDIA_API_KEY = api_key
        
        success_msg = await event.reply("✅ **API Key set successfully!**\n\n🔒 Your key is now configured.\n🤖 You can now use `.ai <question>` command.")
        
        # Delete messages for security
        await asyncio.sleep(5)
        try:
            await event.delete()
            await success_msg.delete()
        except:
            pass
        
        print("✅ NVIDIA API key configured successfully")
        
    except Exception as e:
        await event.reply(f"❌ **Error setting API key:** {str(e)}")
        print(f"❌ API Key Set Error: {e}")

@CipherElite.on(events.NewMessage(pattern=r"\.aitest"))
@rishabh()
async def aitest_handler(event):
    """Test AI connection"""
    try:
        if not NVIDIA_API_KEY:
            await event.reply("❌ **No API key set.** Use `.aiset <key>` first.")
            return
        
        test_msg = await event.reply("🧪 **Testing NVIDIA AI connection...**")
        
        # Simple test query
        test_messages = [{"role": "user", "content": "Say 'Hello, I am working!' in exactly those words."}]
        
        response = await asyncio.wait_for(
            make_nvidia_request(test_messages),
            timeout=20.0
        )
        
        if response.startswith("❌") or response.startswith("⏳") or response.startswith("🚫"):
            await test_msg.edit(f"❌ **Test Failed:**\n\n{response}")
        else:
            await test_msg.edit(f"✅ **Test Successful!**\n\n🤖 **AI Response:** {response}\n\n🎉 Your NVIDIA AI is working correctly!")
        
    except Exception as e:
        await event.reply(f"❌ **Test Error:** {str(e)}")
        print(f"❌ AI Test Error: {e}")

@CipherElite.on(events.NewMessage(pattern=r"\.aiclear"))
@rishabh()
async def aiclear_handler(event):
    """Clear conversation history"""
    try:
        chat_id = event.chat_id
        
        if chat_id in conversation_history:
            messages_count = len(conversation_history[chat_id])
            del conversation_history[chat_id]
            await event.reply(f"🗑️ **History cleared!**\n\n📊 Removed `{messages_count}` messages from this chat.")
        else:
            await event.reply("📭 **No history found** for this chat.")
            
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")

@CipherElite.on(events.NewMessage(pattern=r"\.aistatus"))
@rishabh()
async def aistatus_handler(event):
    """Show AI status"""
    try:
        api_status = "✅ Set" if NVIDIA_API_KEY else "❌ Not Set"
        history_count = len(conversation_history)
        total_messages = sum(len(history) for history in conversation_history.values())
        
        status_msg = f"""📊 **NVIDIA AI Status:**

🔑 **API Key:** `{api_status}`
🌐 **Endpoint:** `{NVIDIA_BASE_URL}`
🤖 **Model:** `{DEFAULT_MODEL}`

💾 **Conversation Data:**
• **Active Chats:** `{history_count}`
• **Total Messages:** `{total_messages}`

⚙️ **Commands:**
• `.ai <question>` - Ask AI
• `.aitest` - Test connection
• `.aiclear` - Clear history
• `.aiset <key>` - Set API key

🔗 **Get API Key:** https://build.nvidia.com/"""

        await event.reply(status_msg)
        
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")

print("✅ NVIDIA AI Plugin loaded successfully")
