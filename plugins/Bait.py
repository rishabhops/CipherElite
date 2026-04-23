# =============================================================================
#  CipherElite The Bait (Infinite Chat Actions)
#  Author:         CipherElite Dev (@rishabhops)
# =============================================================================

import asyncio
from telethon import events

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# BACKGROUND TASK MANAGER
# ==========================================
# We store active background tasks here so we can stop them later
BAIT_TASKS = {}

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".typing on/off - Infinite typing status",
        ".recording on/off - Infinite recording voice note status",
        ".gaming on/off - Infinite playing game status",
        ".baitstop - Instantly stops all active actions in the current chat"
    ]
    description = (
        "🎣 **The Bait (Infinite Actions)**\n"
        "🧠 Psychological trolling tool.\n"
        "🔄 Keeps your status active indefinitely in the background.\n"
        "🛑 Can run in multiple chats simultaneously.\n\n"
    )
    add_handler("bait", commands, description)

# ==========================================
# THE INFINITE LOOP ENGINE
# ==========================================
async def action_runner(client, chat_id, action_str):
    """Runs infinitely in the background to keep the status alive."""
    try:
        # Telethon's action context manager handles the API requests automatically
        async with client.action(chat_id, action_str):
            while True:
                # Keep the context block alive forever until cancelled
                await asyncio.sleep(5)
    except asyncio.CancelledError:
        # Raised when we turn the bait off
        pass
    except Exception as e:
        print(f"Bait Error: {e}")

# ==========================================
# COMMAND HANDLER
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"^\.(typing|recording|gaming)(?: |$)(.*)", outgoing=True))
@rishabh
async def bait_handler(event):
    action_type = event.pattern_match.group(1).lower()
    state = event.pattern_match.group(2).strip().lower()
    chat_id = event.chat_id

    # Map our commands to actual Telethon API action strings
    action_map = {
        "typing": "typing",
        "recording": "record-audio",
        "gaming": "play-game"
    }
    
    telethon_action = action_map[action_type]
    task_key = f"{chat_id}_{action_type}"

    if state == "on":
        if task_key in BAIT_TASKS:
            return await event.reply(f"⚠️ **I am already {action_type} infinitely in this chat!**")
            
        # Create an infinite background task
        task = asyncio.create_task(action_runner(event.client, chat_id, telethon_action))
        BAIT_TASKS[task_key] = task
        
        await event.delete() # Delete the command to be extra stealthy
        
    elif state == "off":
        if task_key not in BAIT_TASKS:
            return await event.reply(f"⚠️ **No infinite {action_type} is running here.**")
            
        # Kill the background task
        BAIT_TASKS[task_key].cancel()
        del BAIT_TASKS[task_key]
        
        # Telethon needs a "cancel" action to clear the status immediately from others' screens
        await event.client.action(chat_id, 'cancel')
        await event.reply(f"🛑 **Infinite {action_type} stopped.**")
        
    else:
        await event.reply(f"❌ **Syntax Error:** Use `.{action_type} on` or `.{action_type} off`")


@CipherElite.on(events.NewMessage(pattern=r"^\.baitstop$", outgoing=True))
@rishabh
async def stop_all_bait(event):
    """A panic button to kill all fake actions in the current chat."""
    chat_id = event.chat_id
    stopped = 0
    
    # Find all tasks running in this specific chat and kill them
    tasks_to_remove = []
    for key, task in BAIT_TASKS.items():
        if key.startswith(f"{chat_id}_"):
            task.cancel()
            tasks_to_remove.append(key)
            stopped += 1
            
    for key in tasks_to_remove:
        del BAIT_TASKS[key]
        
    if stopped > 0:
        await event.client.action(chat_id, 'cancel')
        await event.reply(f"🛑 **Stopped {stopped} infinite actions in this chat!**")
    else:
        await event.reply("⚠️ **No bait actions are currently running here.**")
