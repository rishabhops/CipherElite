# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    cipher_ai
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • Give proper credit back to the CipherElite Userbot author:
#        – GitHub: https://github.com/rishabhops/CipherElite
#        – Telegram: @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================

import asyncio
import re
from openai import AsyncOpenAI
from openai import OpenAIError, AuthenticationError, RateLimitError
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from vars import ELITE_BOT_USERNAME
import os

# Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "mistralai/mistral-nemotron"

# Initialize OpenAI client
client = AsyncOpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY
)

# Store conversation history per chat
conversation_history = {}

# System prompt to define AI identity and behavior
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Cipher AI, created by @thanosceo for the CipherElite Userbot. Provide short, natural, and accurate answers. Return only the final result without any thinking process, internal deliberations, or <think> blocks. Avoid verbose explanations, technical model details, or markdown unless requested."
}

def init(client):
    """Initialize the NVIDIA AI plugin"""
    commands = [
        f".ai <question> — Ask Cipher AI a question",
        f".aiset <key> — Set NVIDIA API key",
        f".aitest — Test AI connection",
        f".aiclear — Clear conversation history",
        f".aistatus — Show AI status"
    ]
    description = "Interact with Cipher AI powered by NVIDIA API"
    add_handler("cipher_ai", commands, description)
    print("🤖 CIPHER AI Plugin initialized successfully")
    return True

async def make_nvidia_request(messages, temperature=0.6, top_p=0.7, max_tokens=2048):
    """Make async request to NVIDIA API with streaming"""
    try:
        stream = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=True
        )
        
        # Collect streamed response
        response = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        
        # Filter out <think> blocks
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
        return response
        
    except AuthenticationError:
        return "❌ **Authentication Error:** Invalid API key. Use `.aiset <key>` to set a valid key."
    except RateLimitError:
        return "⏳ **Rate Limited:** Too many requests. Please wait a moment."
    except OpenAIError as e:
        return f"❌ **API Error:** {str(e)[:200]}"
    except asyncio.TimeoutError:
        return "⏰ **Timeout Error:** Request took too long. Please try again."
    except Exception as e:
        return f"❌ **Unexpected Error:** {str(e)}"

@CipherElite.on(events.NewMessage(pattern=r"\.ai(?:\s+(.*))?"))
@rishabh()
async def ai_handler(event):
    """Handle AI queries with proper error handling"""
    thinking_msg = None
    try:
        if not NVIDIA_API_KEY:
            await event.reply(f"🔑 **API Key Required!**\n\nUse `{ELITE_BOT_USERNAME} .aiset <your_nvidia_api_key>` to set your NVIDIA API key.\n\n📋 Get your key from: https://build.nvidia.com/")
            return
        
        query = event.pattern_match.group(1)
        if not query:
            await event.reply(f"❓ **Usage:** `{ELITE_BOT_USERNAME} .ai <your question>`\n\n**Examples:**\n• `.ai What is AI?`\n• `.ai Write a Python function`\n• `.ai Explain quantum physics`")
            return
        
        if len(query) > 2000:
            await event.reply("📝 **Query too long!** Please keep your question under 2000 characters.")
            return
        
        thinking_msg = await event.reply("🤔 **Cipher AI is thinking...**")
        print(f"🤖 Processing AI query: {query[:50]}...")
        
        chat_id = event.chat_id
        if chat_id not in conversation_history:
            conversation_history[chat_id] = [SYSTEM_PROMPT]
        
        conversation_history[chat_id].append({"role": "user", "content": query})
        
        if len(conversation_history[chat_id]) > 6:
            conversation_history[chat_id] = [SYSTEM_PROMPT] + conversation_history[chat_id][-5:]
        
        try:
            response = await asyncio.wait_for(
                make_nvidia_request(conversation_history[chat_id]),
                timeout=45.0
            )
            print(f"✅ AI response received: {len(response)} characters")
        except asyncio.TimeoutError:
            response = "⏰ **Request Timeout:** The AI took too long to respond. Try a shorter question."
            print("❌ AI request timed out")
        
        if response.startswith("❌") or response.startswith("⏳"):
            await thinking_msg.edit(response)
            print(f"❌ AI error response: {response[:100]}")
            return
        
        conversation_history[chat_id].append({"role": "assistant", "content": response})
        
        if len(response) > 3500:
            parts = [response[i:i+3500] for i in range(0, len(response), 3500)]
            await thinking_msg.edit(f"🤖 **Cipher AI Response (Part 1/{len(parts)}):**\n\n{parts[0]}")
            for i, part in enumerate(parts[1:], 2):
                await event.reply(f"🤖 **Part {i}/{len(parts)}:**\n\n{part}")
        else:
            formatted_response = f"🤖 **Cipher AI Response:**\n\n{response}\n\n💭 **Query:** `{query[:100]}{'...' if len(query) > 100 else ''}`"
            await thinking_msg.edit(formatted_response)
        
        print(f"✅ AI response sent successfully")
        
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
            await event.reply(f"🔑 **Usage:** `{ELITE_BOT_USERNAME} .aiset <your_nvidia_api_key>`\n\n📋 **Steps:**\n1. Visit https://build.nvidia.com/\n2. Sign up/Login\n3. Generate API key\n4. Use this command to set it")
            return
        
        if len(api_key) < 10:
            await event.reply("❌ **Invalid API key format.** Please check your key.")
            return
        
        os.environ["NVIDIA_API_KEY"] = api_key
        global NVIDIA_API_KEY, client
        NVIDIA_API_KEY = api_key
        client = AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)
        
        success_msg = await event.reply("✅ **API Key set successfully!**\n\n🔒 Your key is now configured.\n🤖 You can now use `.ai <question>` command.")
        print(f"✅ NVIDIA API key set: {api_key[:10]}...")
        
        await asyncio.sleep(5)
        try:
            await event.delete()
            await success_msg.delete()
        except:
            pass
        
    except Exception as e:
        await event.reply(f"❌ **Error setting API key:** {str(e)}")
        print(f"❌ API Key Set Error: {e}")

@CipherElite.on(events.NewMessage(pattern=r"\.aitest"))
@rishabh()
async def aitest_handler(event):
    """Test AI connection"""
    try:
        if not NVIDIA_API_KEY:
            await event.reply(f"❌ **No API key set.** Use `{ELITE_BOT_USERNAME} .aiset <key>` first.")
            return
        
        test_msg = await event.reply("🧪 **Testing Cipher AI connection...**")
        print("🧪 Testing NVIDIA AI connection...")
        
        test_messages = [
            SYSTEM_PROMPT,
            {"role": "user", "content": "Say 'Hello, I am Cipher AI!' in exactly those words."}
        ]
        
        response = await asyncio.wait_for(
            make_nvidia_request(test_messages),
            timeout=20.0
        )
        
        if response.startswith("❌") or response.startswith("⏳"):
            await test_msg.edit(f"❌ **Test Failed:**\n\n{response}")
            print(f"❌ AI test failed: {response}")
        else:
            await test_msg.edit(f"✅ **Test Successful!**\n\n🤖 **Cipher AI Response:** {response}\n\n🎉 Your AI is working correctly!")
            print(f"✅ AI test successful: {response}")
        
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
            print(f"🗑️ Cleared {messages_count} messages from chat {chat_id}")
        else:
            await event.reply("📭 **No history found** for this chat.")
            
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")
        print(f"❌ Clear History Error: {e}")

@CipherElite.on(events.NewMessage(pattern=r"\.aistatus"))
@rishabh()
async def aistatus_handler(event):
    """Show AI status"""
    try:
        api_status = "✅ Set" if NVIDIA_API_KEY else "❌ Not Set"
        history_count = len(conversation_history)
        total_messages = sum(len(history) for history in conversation_history.values())
        
        status_msg = f"""📊 **Cipher AI Status:**

🔑 **API Key:** `{api_status}`
🌐 **Endpoint:** `{NVIDIA_BASE_URL}`
🤖 **Model:** `{DEFAULT_MODEL}`

💾 **Conversation Data:**
• **Active Chats:** `{history_count}`
• **Total Messages:** `{total_messages}`

⚙️ **Commands:**
• `{ELITE_BOT_USERNAME} .ai <question>` - Ask Cipher AI
• `{ELITE_BOT_USERNAME} .aitest` - Test connection
• `{ELITE_BOT_USERNAME} .aiclear` - Clear history
• `{ELITE_BOT_USERNAME} .aiset <key>` - Set API key

🔗 **Get API Key:** https://build.nvidia.com/"""
        
        await event.reply(status_msg)
        
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")
        print(f"❌ Status Error: {e}")

print("CIPHER AI Plugin loaded successfully")
