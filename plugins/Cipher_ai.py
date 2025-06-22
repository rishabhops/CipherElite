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
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "deepseek-ai/deepseek-r1"

# Initialize client
nvidia_client = None
if OPENAI_AVAILABLE and NVIDIA_API_KEY:
    nvidia_client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY
    )

def init(client_instance):
    """Initialize the NVIDIA AI plugin"""
    commands = [
        ".ai <query> - Ask AI using NVIDIA DeepSeek R1 model",
        ".aiset <api_key> - Set NVIDIA API key",
        ".aimodels - List available AI models",
        ".aiconfig - Show current AI configuration",
        ".aiclear - Clear conversation history",
        ".aihelp - Show detailed AI help"
    ]
    description = "NVIDIA AI integration with DeepSeek R1 model for intelligent responses"
    add_handler("nvidia_ai", commands, description)

# Store conversation history per chat
conversation_history = {}

async def get_ai_response(query, chat_id=None, temperature=0.6, top_p=0.7, max_tokens=4096):
    """Get response from NVIDIA AI"""
    try:
        if not nvidia_client:
            return "❌ **Error:** NVIDIA AI client not initialized. Please set API key with `.aiset <key>`"
        
        # Get conversation history for this chat
        if chat_id not in conversation_history:
            conversation_history[chat_id] = []
        
        # Add user message to history
        conversation_history[chat_id].append({"role": "user", "content": query})
        
        # Keep only last 10 messages to avoid token limit
        if len(conversation_history[chat_id]) > 10:
            conversation_history[chat_id] = conversation_history[chat_id][-10:]
        
        # Make API call
        completion = nvidia_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=conversation_history[chat_id],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=False
        )
        
        response = completion.choices[0].message.content
        
        # Add AI response to history
        conversation_history[chat_id].append({"role": "assistant", "content": response})
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            return "❌ **API Key Error:** Please set a valid NVIDIA API key with `.aiset <key>`"
        elif "rate_limit" in error_msg.lower():
            return "⏳ **Rate Limited:** Please wait a moment before making another request"
        elif "quota" in error_msg.lower():
            return "💳 **Quota Exceeded:** Your API quota has been exceeded"
        else:
            return f"❌ **Error:** {error_msg}"

@CipherElite.on(events.NewMessage(pattern=r"\.ai(?:\s+(.*))?"))
@rishabh()
async def ai_handler(event):
    """Handle AI queries"""
    try:
        if not OPENAI_AVAILABLE:
            await event.reply("❌ **Error:** OpenAI library not installed. Install with: `pip install openai`")
            return
        
        query = event.pattern_match.group(1)
        if not query:
            await event.reply("❓ **Usage:** `.ai <your question>`\n\n**Example:** `.ai What is artificial intelligence?`")
            return
        
        # Show typing indicator
        async with event.client.action(event.chat_id, 'typing'):
            # Send "thinking" message
            thinking_msg = await event.reply("🤔 **Thinking...** Please wait while I process your query.")
            
            # Get AI response
            response = await get_ai_response(query, event.chat_id)
            
            # Format response
            formatted_response = f"🤖 **NVIDIA DeepSeek R1 Response:**\n\n{response}\n\n"
            formatted_response += f"💭 **Query:** `{query[:100]}{'...' if len(query) > 100 else ''}`"
            
            # Edit the thinking message with response
            await thinking_msg.edit(formatted_response)
    
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")

@CipherElite.on(events.NewMessage(pattern=r"\.aiset(?:\s+(.*))?"))
@rishabh()
async def aiset_handler(event):
    """Set NVIDIA API key"""
    try:
        api_key = event.pattern_match.group(1)
        if not api_key:
            await event.reply("🔑 **Usage:** `.aiset <your_nvidia_api_key>`\n\n**Note:** Get your API key from NVIDIA NGC")
            return
        
        # Set environment variable
        os.environ["NVIDIA_API_KEY"] = api_key
        
        # Reinitialize client
        global nvidia_client
        nvidia_client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=api_key
        )
        
        await event.reply("✅ **NVIDIA API Key set successfully!**\n\n🔒 Your API key has been configured securely.")
        
        # Delete the message containing API key for security
        await asyncio.sleep(5)
        await event.delete()
        
    except Exception as e:
        await event.reply(f"❌ **Error setting API key:** {str(e)}")

@CipherElite.on(events.NewMessage(pattern=r"\.aimodels"))
@rishabh()
async def aimodels_handler(event):
    """List available AI models"""
    try:
        models_info = """🤖 **Available NVIDIA AI Models:**

**🧠 DeepSeek Models:**
• `deepseek-ai/deepseek-r1` - Advanced reasoning model (Default)
• `deepseek-ai/deepseek-coder` - Code generation specialist
• `deepseek-ai/deepseek-chat` - General conversation model

**⚡ Other Models:**
• `meta/llama-3.1-8b-instruct` - Meta's Llama model
• `microsoft/phi-3-medium-4k-instruct` - Microsoft's Phi-3
• `mistralai/mixtral-8x7b-instruct-v0.1` - Mistral's Mixtral

**📊 Current Settings:**
• **Model:** `deepseek-ai/deepseek-r1`
• **Temperature:** `0.6`
• **Top P:** `0.7`
• **Max Tokens:** `4096`

**💡 Note:** Currently using DeepSeek R1 for best reasoning capabilities."""

        await event.reply(models_info)
        
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")

@CipherElite.on(events.NewMessage(pattern=r"\.aiconfig"))
@rishabh()
async def aiconfig_handler(event):
    """Show AI configuration"""
    try:
        api_key_status = "✅ Set" if NVIDIA_API_KEY else "❌ Not Set"
        client_status = "✅ Ready" if nvidia_client else "❌ Not Ready"
        
        config_info = f"""⚙️ **NVIDIA AI Configuration:**

**🔑 API Key:** `{api_key_status}`
**🤖 Client:** `{client_status}`
**🌐 Base URL:** `{NVIDIA_BASE_URL}`
**📱 Model:** `{DEFAULT_MODEL}`

**💾 Conversation History:**
• **Active Chats:** `{len(conversation_history)}`
• **Total Messages:** `{sum(len(history) for history in conversation_history.values())}`

**🔧 Settings:**
• **Temperature:** `0.6` (Creativity level)
• **Top P:** `0.7` (Response diversity)
• **Max Tokens:** `4096` (Response length limit)

**📋 Status:** {'🟢 Ready to use' if nvidia_client else '🔴 Setup required'}"""

        await event.reply(config_info)
        
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")

@CipherElite.on(events.NewMessage(pattern=r"\.aiclear"))
@rishabh()
async def aiclear_handler(event):
    """Clear conversation history"""
    try:
        chat_id = event.chat_id
        
        if chat_id in conversation_history:
            messages_count = len(conversation_history[chat_id])
            del conversation_history[chat_id]
            await event.reply(f"🗑️ **Conversation history cleared!**\n\n📊 Removed `{messages_count}` messages from this chat's history.")
        else:
            await event.reply("📭 **No conversation history found** for this chat.")
            
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")

@CipherElite.on(events.NewMessage(pattern=r"\.aihelp"))
@rishabh()
async def aihelp_handler(event):
    """Show detailed AI help"""
    try:
        help_text = """🆘 **NVIDIA AI Plugin Help**

**🚀 Quick Start:**
1. Get API key from NVIDIA NGC
2. Set key: `.aiset <your_api_key>`
3. Ask questions: `.ai <your_question>`

**📋 Commands:**
• `.ai <query>` - Ask AI anything
• `.aiset <key>` - Set NVIDIA API key
• `.aimodels` - List available models
• `.aiconfig` - Show configuration
• `.aiclear` - Clear chat history
• `.aihelp` - Show this help

**💡 Usage Examples:**
• `.ai What is quantum computing?`
• `.ai Write a Python function to sort a list`
• `.ai Explain the theory of relativity`
• `.ai Create a poem about technology`

**🔧 Features:**
• **Conversation Memory** - Remembers context within each chat
• **Multiple Models** - Access to various NVIDIA AI models
• **Smart Responses** - Advanced reasoning with DeepSeek R1
• **Secure API** - Your API key is stored securely

**⚠️ Important Notes:**
• API key is required for functionality
• Conversation history is kept per chat
• Rate limits may apply based on your NVIDIA plan
• API key messages are auto-deleted for security

**🔗 Get API Key:**
Visit: https://build.nvidia.com/explore/discover"""

        await event.reply(help_text)
        
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")

# Auto-response feature (optional)
@CipherElite.on(events.NewMessage(pattern=r"\.aiauto"))
@rishabh()
async def aiauto_handler(event):
    """Toggle auto AI responses"""
    try:
        await event.reply("🔄 **Auto AI Response feature coming soon!**\n\nThis will allow automatic AI responses to specific triggers.")
    except Exception as e:
        await event.reply(f"❌ **Error:** {str(e)}")
