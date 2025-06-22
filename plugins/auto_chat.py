# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    auto_chat
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
#        – Telegram: @rishabhops
#
#  Thank you for respecting open-source software!
# =============================================================================

import asyncio
import re
from openai import AsyncOpenAI, OpenAIError, AuthenticationError, RateLimitError
from telethon import events
from telethon.tl.types import User
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

# Store user’s sent messages per private chat (for mimicking style)
user_conversation_history = {}
# Store AI conversation context per chat
ai_conversation_history = {}
# Auto-chat enable/disable state
auto_chat_enabled = False

# System prompt for AI assistant
SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Cipher AI, an assistant for the CipherElite Userbot, created by @rishabhops. Respond in private chats on behalf of the user, mimicking their tone, style, and behavior based on their past messages. Use provided conversation snippets to guide your responses. Keep answers short, natural, and context-aware. Avoid <think> blocks, technical details, or markdown unless requested. Do not respond to bot commands or other bots."
}

def init(client):
    """Initialize the auto_chat plugin"""
    commands = [
        f".autochat — Toggle auto-chat in private chats"
    ]
    description = "Enable/disable Cipher AI to respond in private chats on your behalf"
    add_handler("auto_chat", commands, description)
    print("🤖 Auto Chat Plugin initialized successfully")
    return True

async def make_auto_chat_request(messages, temperature=0.6, top_p=0.7, max_tokens=2048):
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
        return "⏰ **Timeout Error:** Request took too long."
    except Exception as e:
        return f"❌ **Unexpected Error:** {str(e)}"

@CipherElite.on(events.NewMessage(pattern=r"\.autochat"))
@rishabh()
async def autochat_handler(event):
    """Toggle auto-chat feature"""
    global auto_chat_enabled
    auto_chat_enabled = not auto_chat_enabled
    status = "enabled" if auto_chat_enabled else "disabled"
    await event.reply(f"🤖 **Auto Chat {status}!**\n\nCipher AI will {'now' if auto_chat_enabled else 'no longer'} respond in private chats on your behalf.")
    print(f"🤖 Auto Chat {status}")

@CipherElite.on(events.NewMessage(outgoing=True))
async def store_user_message(event):
    """Store user’s outgoing messages in private chats for style mimicking"""
    if not isinstance(event.chat, User):  # Ensure it’s a private chat
        return
    chat_id = event.chat_id
    message = event.raw_text
    
    if not message or message.startswith("."):  # Ignore commands and empty messages
        return
    
    if chat_id not in user_conversation_history:
        user_conversation_history[chat_id] = []
    
    user_conversation_history[chat_id].append(message)
    
    # Keep only last 50 messages per chat
    if len(user_conversation_history[chat_id]) > 50:
        user_conversation_history[chat_id] = user_conversation_history[chat_id][-50:]
    
    print(f"📜 Stored user message in chat {chat_id}: {message[:30]}...")

@CipherElite.on(events.NewMessage(incoming=True))
@rishabh()
async def auto_respond_handler(event):
    """Handle incoming private messages when auto-chat is enabled"""
    if not auto_chat_enabled or not isinstance(event.chat, User):  # Check if enabled and private chat
        return
    
    if event.sender.bot or event.raw_text.startswith("."):  # Ignore bots and commands
        return
    
    if not NVIDIA_API_KEY:
        print("❌ Auto Chat: No API key set")
        return
    
    chat_id = event.chat_id
    query = event.raw_text
    
    if len(query) > 2000:
        await event.reply("📝 **Message too long!** Please keep it under 2000 characters.")
        return
    
    thinking_msg = await event.reply("🤔 **Cipher AI is thinking...**")
    print(f"🤖 Auto Chat: Processing query in chat {chat_id}: {query[:50]}...")
    
    try:
        # Initialize AI conversation history
        if chat_id not in ai_conversation_history:
            ai_conversation_history[chat_id] = [SYSTEM_PROMPT]
        
        # Get user’s past messages for style
        user_style = user_conversation_history.get(chat_id, [])
        style_snippet = "\n".join(user_style[-5:]) if user_style else "No past messages available."
        
        # Add context about user’s style
        style_prompt = {
            "role": "system",
            "content": f"User's recent messages (for style reference):\n{style_snippet}"
        }
        
        # Add current message
        ai_conversation_history[chat_id].append({"role": "user", "content": query})
        
        # Keep only last 6 messages (plus prompts)
        if len(ai_conversation_history[chat_id]) > 6:
            ai_conversation_history[chat_id] = [SYSTEM_PROMPT, style_prompt] + ai_conversation_history[chat_id][-4:]
        else:
            ai_conversation_history[chat_id] = [SYSTEM_PROMPT, style_prompt] + ai_conversation_history[chat_id]
        
        # Make AI request
        response = await asyncio.wait_for(
            make_auto_chat_request(ai_conversation_history[chat_id]),
            timeout=45.0
        )
        print(f"✅ Auto Chat: Response received: {len(response)} characters")
        
        if response.startswith("❌") or response.startswith("⏳"):
            await thinking_msg.edit(response)
            print(f"❌ Auto Chat: Error response: {response[:100]}")
            return
        
        # Store AI response
        ai_conversation_history[chat_id].append({"role": "assistant", "content": response})
        
        # Send response
        if len(response) > 3500:
            parts = [response[i:i+3500] for i in range(0, len(response), 3500)]
            await thinking_msg.edit(parts[0])
            for i, part in enumerate(parts[1:], 2):
                await event.reply(part)
        else:
            await thinking_msg.edit(response)
        
        print(f"✅ Auto Chat: Response sent in chat {chat_id}")
        
    except Exception as e:
        error_msg = f"❌ **Error:** {str(e)}"
        print(f"❌ Auto Chat: Error in chat {chat_id}: {e}")
        try:
            await thinking_msg.edit(error_msg)
        except:
            await event.reply(error_msg)

print("✅ Auto Chat Plugin loaded successfully")
