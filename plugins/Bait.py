# =============================================================================
#  CipherElite The Bait v2.0 (Infinite Chat Actions)
#  Author:         CipherElite Dev (@rishabhops)
#
# =============================================================================

import asyncio
import time
from telethon import events
from telethon.tl import functions, types

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

# ==========================================
# BACKGROUND TASK MANAGER
# ==========================================
# key: "<chat_id>_<action>"  ->  {"task": asyncio.Task, "since": float}
BAIT_TASKS = {}

# Explicit raw API actions = version-proof (no string mapping involved)
ACTION_MAP = {
    "typing":    types.SendMessageTypingAction(),
    "recording": types.SendMessageRecordAudioAction(),
    "gaming":    types.SendMessageGamePlayAction(),
    "video":     types.SendMessageRecordVideoAction(),
    "round":     types.SendMessageRecordRoundAction(),
    "photo":     types.SendMessageUploadPhotoAction(progress=1),
    "document":  types.SendMessageUploadDocumentAction(progress=1),
    "location":  types.SendMessageGeoLocationAction(),
    "contact":   types.SendMessageChooseContactAction(),
}

# Newer Telethon layers only
try:
    ACTION_MAP["sticker"] = types.SendMessageChooseStickerAction()
except AttributeError:
    pass

CMD_PATTERN = r"^\.(" + "|".join(ACTION_MAP.keys()) + r")(?: |$)(.*)"

# ==========================================
# HELP MENU INTEGRATION
# ==========================================
def init(client_instance):
    commands = [
        ".typing on/off - Infinite typing status",
        ".recording on/off - Infinite recording voice note status",
        ".gaming on/off - Infinite playing game status",
        ".video on/off - Infinite recording video status",
        ".round on/off - Infinite recording round video status",
        ".photo on/off - Infinite sending photo status",
        ".document on/off - Infinite sending file status",
        ".sticker on/off - Infinite choosing sticker status",
        ".location on/off - Infinite picking location status",
        ".contact on/off - Infinite choosing contact status",
        ".<action> on <seconds> - Timed bait, auto-stops (e.g. .typing on 60)",
        ".baitlist - List all active baits in all chats",
        ".baitstop - Stop all baits in the current chat",
        ".baitstopall - PANIC: stop every bait in every chat",
    ]
    description = (
        "🎣 **The Bait v2.0 (Infinite Actions)**\n"
        "🧠 Psychological trolling tool.\n"
        "🔄 Keeps your status active indefinitely in the background.\n"
        "⏱️ Supports timed auto-stop mode.\n"
        "🛑 Can run in multiple chats simultaneously.\n\n"
    )
    add_handler("bait", commands, description)

# ==========================================
# THE INFINITE LOOP ENGINE (raw API, version-proof)
# ==========================================
async def action_runner(client, chat_id, action, task_key, duration=None):
    """Re-sends the chat action every 4s (Telegram expires it after ~6s)."""
    deadline = (time.time() + duration) if duration else None
    try:
        while True:
            if deadline and time.time() >= deadline:
                break
            await client(functions.messages.SetTypingRequest(
                peer=chat_id, action=action
            ))
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"Bait Error [{task_key}]: {e}")
    finally:
        # Auto-cleanup (timed mode or crash)
        BAIT_TASKS.pop(task_key, None)
        try:
            await client(functions.messages.SetTypingRequest(
                peer=chat_id, action=types.SendMessageCancelAction()
            ))
        except Exception:
            pass

# ==========================================
# COMMAND HANDLER
# ==========================================
@CipherElite.on(events.NewMessage(pattern=CMD_PATTERN, outgoing=True))
@rishabh
async def bait_handler(event):
    action_type = event.pattern_match.group(1).lower()
    args = event.pattern_match.group(2).strip().lower().split()
    state = args[0] if args else ""
    chat_id = event.chat_id

    action = ACTION_MAP[action_type]
    task_key = f"{chat_id}_{action_type}"

    if state == "on":
        if task_key in BAIT_TASKS:
            return await event.reply(f"⚠️ **Already {action_type} infinitely in this chat!**")

        # Optional timed mode:  .typing on 60
        duration = None
        if len(args) > 1 and args[1].isdigit():
            duration = int(args[1])

        task = asyncio.create_task(
            action_runner(event.client, chat_id, action, task_key, duration)
        )
        BAIT_TASKS[task_key] = {"task": task, "since": time.time()}

        await event.delete()  # Stealth mode

    elif state == "off":
        entry = BAIT_TASKS.pop(task_key, None)
        if not entry:
            return await event.reply(f"⚠️ **No infinite {action_type} is running here.**")

        entry["task"].cancel()
        await event.client(functions.messages.SetTypingRequest(
            peer=chat_id, action=types.SendMessageCancelAction()
        ))
        await event.reply(f"🛑 **Infinite {action_type} stopped.**")

    else:
        await event.reply(
            f"❌ **Syntax:** `.{action_type} on`, `.{action_type} on <seconds>` or `.{action_type} off`"
        )

# ==========================================
# LIST ACTIVE BAITS
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"^\.baitlist$", outgoing=True))
@rishabh
async def bait_list(event):
    if not BAIT_TASKS:
        return await event.reply("😴 **No baits running anywhere.**")

    lines = ["🎣 **Active Baits:**\n"]
    for key, entry in BAIT_TASKS.items():
        chat_id, _, action = key.rpartition("_")
        mins = int((time.time() - entry["since"]) // 60)
        lines.append(f"• `{action}` in chat `{chat_id}` — running {mins}m")
    await event.reply("\n".join(lines))

# ==========================================
# STOP ALL IN CURRENT CHAT
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"^\.baitstop$", outgoing=True))
@rishabh
async def stop_all_bait(event):
    chat_id = event.chat_id
    keys = [k for k in BAIT_TASKS if k.startswith(f"{chat_id}_")]

    for key in keys:
        BAIT_TASKS.pop(key)["task"].cancel()

    if keys:
        await event.client(functions.messages.SetTypingRequest(
            peer=chat_id, action=types.SendMessageCancelAction()
        ))
        await event.reply(f"🛑 **Stopped {len(keys)} infinite actions in this chat!**")
    else:
        await event.reply("⚠️ **No bait actions are currently running here.**")

# ==========================================
# GLOBAL PANIC BUTTON
# ==========================================

VERSION = "1.0.0"
CATEGORY = "utilities"
@CipherElite.on(events.NewMessage(pattern=r"^\.baitstopall$", outgoing=True))
@rishabh
async def stop_everything(event):
    if not BAIT_TASKS:
        return await event.reply("⚠️ **No baits running anywhere.**")

    chat_ids = set()
    count = len(BAIT_TASKS)
    for key in list(BAIT_TASKS):
        chat_id, _, _ = key.rpartition("_")
        chat_ids.add(int(chat_id))
        BAIT_TASKS.pop(key)["task"].cancel()

    for cid in chat_ids:
        try:
            await event.client(functions.messages.SetTypingRequest(
                peer=cid, action=types.SendMessageCancelAction()
            ))
        except Exception:
            pass

    await event.reply(f"🛑 **PANIC: Killed {count} baits across {len(chat_ids)} chats!**")
