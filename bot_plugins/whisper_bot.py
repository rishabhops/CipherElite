from telethon import events, Button
# Import the shared memory from the Userbot plugin
from plugins.whisper import WHISPERS

def init_bot_plugin(bot, owner_id, owner_name):
    
    # 1. Intercepts the secret query from the Userbot and builds the button
    @bot.on(events.InlineQuery(pattern=r"^w_(.*)"))
    async def inline_whisper_handler(event):
        whisper_id = event.pattern_match.group(1)
        
        if whisper_id not in WHISPERS:
            return
            
        whisper = WHISPERS[whisper_id]
        builder = event.builder
        
        display_text = (
            f"🤫 **A Secret Whisper**\n\n"
            f"👤 **To:** {whisper['target_name']}\n"
            f"🔒 *This message is cryptographically locked. Only the intended recipient can open it.*"
        )
        
        result = builder.article(
            title="Send Secret Whisper",
            description="Deploy the locked message",
            text=display_text,
            buttons=[Button.inline("👁 View Whisper", data=f"w_{whisper_id}")]
        )
        await event.answer([result])

    # 2. Triggers the pop-up when someone clicks the button
    @bot.on(events.CallbackQuery(pattern=r"^w_(.*)"))
    async def callback_whisper_handler(event):
        whisper_id = event.data_match.group(1).decode('utf-8')
        
        if whisper_id not in WHISPERS:
            return await event.answer("🛑 This whisper has expired or memory was wiped!", alert=True)
            
        whisper = WHISPERS[whisper_id]
        
        # Check if clicker is the target or the sender
        if event.sender_id == whisper["target"] or event.sender_id == whisper["sender"]:
            await event.answer(f"🤫 Secret Whisper:\n\n{whisper['text']}", alert=True)
        else:
            await event.answer(f"🛑 Access Denied!\nThis whisper is exclusively for {whisper['target_name']}.", alert=True)

    print("✅ Whisper Bot Handlers Registered!")
