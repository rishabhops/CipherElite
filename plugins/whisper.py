# =============================================================================
#  CipherElite Inline Whisper (Dual-Client Steganography)
#  Author:         CipherElite Dev (@rishabhops)
# =============================================================================

import uuid
from telethon import events, Button
from telethon.utils import get_display_name

from config.config import Config
from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# IN-MEMORY DATABASE (Whispers don't need to be saved to disk)
# ==========================================
WHISPERS = {}

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".w @username <message> - Send a locked whisper to a specific user",
        ".w <message> - (Reply to someone) Send a locked whisper to them"
    ]
    description = (
        "🤫 **Inline Whisper (Dual-Client)**\n"
        "🔒 Sends a secret message hidden behind an inline button.\n"
        "🛑 Prevents anyone except the target from reading the popup.\n\n"
    )
    add_handler("whisper", commands, description)


# ==========================================
# 1. THE USERBOT HANDLER (Creates the Whisper)
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"^\.w(?: |$)(.*)", outgoing=True))
@rishabh()
async def send_whisper(event):
    bot_username = getattr(Config, "BOT_USERNAME", None)
    if not bot_username:
        return await event.reply("❌ **Error:** Please add `BOT_USERNAME = '@your_bot'` to your config.py!")

    args = event.pattern_match.group(1).strip()
    target_entity = None
    secret_text = ""

    # Check if replied to a user
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        target_entity = await reply_msg.get_sender()
        secret_text = args
    else:
        # Check if typed @username
        parts = args.split(" ", 1)
        if len(parts) < 2:
            return await event.reply("❌ **Syntax Error:** Use `.w @username <message>` or reply to a user with `.w <message>`")
        try:
            target_entity = await event.client.get_entity(parts[0])
            secret_text = parts[1]
        except Exception:
            return await event.reply(f"❌ **Error:** Could not find user `{parts[0]}`. Make sure the username is correct.")

    if not target_entity or not secret_text:
        return await event.reply("❌ **Error:** Please provide a valid user and secret message.")

    target_id = target_entity.id
    target_name = get_display_name(target_entity)
    
    # Generate a unique 8-character ID for this specific whisper
    whisper_id = str(uuid.uuid4())[:8]

    # Store the whisper in memory
    WHISPERS[whisper_id] = {
        "sender": event.sender_id,
        "target": target_id,
        "target_name": target_name,
        "text": secret_text
    }

    status = await event.reply("⏳ **Locking whisper...**")

    # The Userbot secretly queries the Assistant Bot to generate the inline button!
    try:
        results = await event.client.inline_query(bot_username, f"w_{whisper_id}")
        if results:
            # Click the first inline result and send it to the chat
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
            # Delete the original command and status to keep it clean
            await event.delete()
            await status.delete()
        else:
            await status.edit("❌ **Error:** Assistant bot failed to respond. Make sure Inline Mode is enabled in @BotFather!")
    except Exception as e:
        await status.edit(f"❌ **Inline Error:** `{str(e)}`")


# ==========================================
# 2. THE ASSISTANT BOT HANDLERS (Serves the Whisper)
# ==========================================
# We use the exact same initialization function you have in assistant.py 
# so your bot loads these seamlessly!

def init_bot_plugin(bot, owner_id, owner_name):
    
    # A) Intercepts the secret query from the Userbot and builds the button
    @bot.on(events.InlineQuery(pattern=r"^w_(.*)"))
    async def inline_whisper_handler(event):
        whisper_id = event.pattern_match.group(1)
        
        if whisper_id not in WHISPERS:
            return # Ignore if the ID doesn't exist
            
        whisper = WHISPERS[whisper_id]
        builder = event.builder
        
        # This is what everyone in the group will see
        display_text = (
            f"🤫 **A Secret Whisper**\n\n"
            f"👤 **To:** {whisper['target_name']}\n"
            f"🔒 *This message is cryptographically locked. Only the intended recipient can open it.*"
        )
        
        result = builder.article(
            title="Send Secret Whisper",
            description="Click here to deploy the locked message",
            text=display_text,
            buttons=[Button.inline("👁 View Whisper", data=f"w_{whisper_id}")]
        )
        await event.answer([result])

    # B) Triggers the pop-up when someone clicks the button
    @bot.on(events.CallbackQuery(pattern=r"^w_(.*)"))
    async def callback_whisper_handler(event):
        # Decode the bytes ID back to a string
        whisper_id = event.data_match.group(1).decode('utf-8')
        
        if whisper_id not in WHISPERS:
            return await event.answer("🛑 This whisper has expired or memory was wiped!", alert=True)
            
        whisper = WHISPERS[whisper_id]
        
        # Check if the person clicking is the intended target OR the sender
        if event.sender_id == whisper["target"] or event.sender_id == whisper["sender"]:
            # Success! Show the secret message
            await event.answer(f"🤫 Secret Whisper:\n\n{whisper['text']}", alert=True)
        else:
            # Trap! Show the rejection message
            await event.answer(f"🛑 Access Denied!\nThis whisper is exclusively for {whisper['target_name']}.", alert=True)

    print("✅ Whisper Plugin: Bot handlers registered successfully")
