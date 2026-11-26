# =============================================================================
#  CipherElite The Bait v2.1.0 (Infinite Chat Actions)
#  Author:         CipherElite Dev (@rishabhops)
#
#  Changelog v2.1.0 (26 Nov 2026) — see CHANGELOG-Bait-v2.1.0.md
#  - Fixed orphaned-bait race: a re-started bait is no longer deleted
#    by the old task's cleanup, so .baitlist / .off / .baitstop keep working.
#  - Timed mode now validates its seconds (rejects 0, negative, float
#    and non-numeric values instead of silently going infinite).
#  - A bait that dies (network / FloodWait / bad peer) now tells the
#    user in-chat instead of failing silently.
#  - Commands are now case-insensitive (.Typing works like .typing).
#  - Timed baits stop on time instead of overshooting by up to 4s.
#  - VERSION fixed: 1.0.0 -> 2.1.0, moved to the top of the file.
# =============================================================================

import asyncio
import time
from telethon import events
from telethon.tl import functions, types

from utils.utils import CipherElite
from plugins.bot import add_handler
from utils.decorators import rishabh

VERSION = "2.1.0"
CATEGORY = "utilities"

# Timed bait cap: 24 hours. Anything larger is almost certainly a typo.
MAX_DURATION = 86400

# ==========================================
# BACKGROUND TASK MANAGER
# ==========================================
# key: "<chat_id>_<action>"  ->  {"task": asyncio.Task, "since": float,
#                                 "duration": int | None}
BAIT_TASKS = {}

# Factories, not shared instances: every loop iteration builds a fresh
# TL action object, so concurrent baits never share / mutate one object.
ACTION_FACTORIES = {
    "typing":    lambda: types.SendMessageTypingAction(),
    "recording": lambda: types.SendMessageRecordAudioAction(),
    "gaming":    lambda: types.SendMessageGamePlayAction(),
    "video":     lambda: types.SendMessageRecordVideoAction(),
    "round":     lambda: types.SendMessageRecordRoundAction(),
    "photo":     lambda: types.SendMessageUploadPhotoAction(progress=1),
    "document":  lambda: types.SendMessageUploadDocumentAction(progress=1),
    "location":  lambda: types.SendMessageGeoLocationAction(),
    "contact":   lambda: types.SendMessageChooseContactAction(),
}

# Newer Telethon layers only
try:
    types.SendMessageChooseStickerAction()
    ACTION_FACTORIES["sticker"] = lambda: types.SendMessageChooseStickerAction()
except AttributeError:
    pass

# (?i) = case-insensitive, so .Typing / .TYPING work like .typing
CMD_PATTERN = r"(?i)^\.(" + "|".join(ACTION_FACTORIES.keys()) + r")(?:\s+|$)(.*)"


async def _send_cancel(client, chat_id):
    """Best-effort Cancel action. Never raises."""
    try:
        await asyncio.shield(
            client(functions.messages.SetTypingRequest(
                peer=chat_id, action=types.SendMessageCancelAction()
            ))
        )
    except Exception:
        pass


async def _stop_entry(entry):
    """Cancel one bait task and wait for its cleanup to finish.

    Awaiting matters: without it, the old task's ``finally`` can run
    *after* a new bait with the same key is started (see action_runner).
    """
    task = entry["task"]
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


def _parse_duration(args):
    """Validate the optional seconds after ``on``.

    Returns (duration, error). ``duration`` is None for infinite mode.
    Any bad value returns an error instead of silently going infinite.
    """
    if len(args) <= 1:
        return None, None
    raw = args[1]
    try:
        duration = int(raw)
    except ValueError:
        return None, f"❌ **Seconds galat hain:** `{raw}` — number likho, jaise `.typing on 60`"
    if duration <= 0:
        return None, "❌ **Seconds 0 se bade hone chahiye** — jaise `.typing on 60`"
    if duration > MAX_DURATION:
        return None, f"❌ **Max {MAX_DURATION} seconds (24h)** — usse zyada nahi"
    return duration, None


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
        "🎣 **The Bait v2.1.0 (Infinite Actions)**\n"
        "🧠 Psychological trolling tool.\n"
        "🔄 Keeps your status active indefinitely in the background.\n"
        "⏱️ Supports timed auto-stop mode.\n"
        "🛑 Can run in multiple chats simultaneously.\n\n"
    )
    add_handler("bait", commands, description)

# ==========================================
# THE INFINITE LOOP ENGINE (raw API, version-proof)
# ==========================================
async def action_runner(client, chat_id, action_type, task_key, duration=None):
    """Re-sends the chat action every 4s (Telegram expires it after ~6s)."""
    deadline = (time.time() + duration) if duration else None
    error = None
    try:
        while True:
            if deadline is not None:
                remaining = deadline - time.time()
                if remaining <= 0:
                    break
            else:
                remaining = None
            await client(functions.messages.SetTypingRequest(
                peer=chat_id, action=ACTION_FACTORIES[action_type]()
            ))
            # Sleep at most until the deadline, so a timed bait
            # (e.g. 2s) stops on time instead of overshooting to 4s.
            await asyncio.sleep(4 if remaining is None else min(4, remaining))
    except asyncio.CancelledError:
        raise
    except Exception as e:
        error = e
        print(f"Bait Error [{task_key}]: {e}")
    finally:
        # Only remove OUR OWN entry. If the user stopped this bait and
        # immediately started a new one with the same key, the new
        # task is already stored here — deleting it would orphan the
        # new bait (no .baitlist entry, .off won't stop it).
        current = asyncio.current_task()
        entry = BAIT_TASKS.get(task_key)
        if entry is not None and entry.get("task") is current:
            BAIT_TASKS.pop(task_key, None)
        await _send_cancel(client, chat_id)
        if error is not None:
            # Silent death was the old bug: tell the user in-chat.
            try:
                await client.send_message(
                    chat_id,
                    f"⚠️ **Bait `{action_type}` band ho gaya:** `{error}`\n"
                    f"Dobara chalane ke liye `.{action_type} on` bhejo.",
                )
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

    task_key = f"{chat_id}_{action_type}"

    if state == "on":
        if task_key in BAIT_TASKS:
            return await event.reply(f"⚠️ **Already {action_type} infinitely in this chat!**")

        # Optional timed mode:  .typing on 60
        # Bad seconds are rejected here — never silently infinite.
        duration, error = _parse_duration(args)
        if error:
            return await event.reply(error)

        task = asyncio.create_task(
            action_runner(event.client, chat_id, action_type, task_key, duration)
        )
        BAIT_TASKS[task_key] = {
            "task": task,
            "since": time.time(),
            "duration": duration,
        }

        try:
            await event.delete()  # Stealth mode
        except Exception:
            pass

    elif state == "off":
        entry = BAIT_TASKS.pop(task_key, None)
        if not entry:
            return await event.reply(f"⚠️ **No infinite {action_type} is running here.**")

        await _stop_entry(entry)
        await event.reply(f"🛑 **Infinite {action_type} stopped.**")

    else:
        await event.reply(
            f"❌ **Syntax:** `.{action_type} on`, `.{action_type} on <seconds>` or `.{action_type} off`"
        )

# ==========================================
# LIST ACTIVE BAITS
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"(?i)^\.baitlist\s*$", outgoing=True))
@rishabh
async def bait_list(event):
    if not BAIT_TASKS:
        return await event.reply("😴 **No baits running anywhere.**")

    lines = ["🎣 **Active Baits:**\n"]
    for key, entry in BAIT_TASKS.items():
        chat_id, _, action = key.rpartition("_")
        elapsed = int(time.time() - entry["since"])
        age = f"{elapsed // 60}m" if elapsed >= 60 else f"{elapsed}s"
        extra = ""
        if entry.get("duration"):
            left = max(0, int(entry["duration"] - elapsed))
            extra = f" — {left}s left"
        lines.append(f"• `{action}` in chat `{chat_id}` — running {age}{extra}")
    await event.reply("\n".join(lines))

# ==========================================
# STOP ALL IN CURRENT CHAT
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"(?i)^\.baitstop\s*$", outgoing=True))
@rishabh
async def stop_all_bait(event):
    chat_id = event.chat_id
    keys = [k for k in BAIT_TASKS if k.startswith(f"{chat_id}_")]

    entries = [BAIT_TASKS.pop(key) for key in keys]
    for entry in entries:
        entry["task"].cancel()
    if entries:
        await asyncio.gather(
            *(entry["task"] for entry in entries), return_exceptions=True
        )
        await _send_cancel(event.client, chat_id)
        await event.reply(f"🛑 **Stopped {len(keys)} infinite actions in this chat!**")
    else:
        await event.reply("⚠️ **No bait actions are currently running here.**")

# ==========================================
# GLOBAL PANIC BUTTON
# ==========================================
@CipherElite.on(events.NewMessage(pattern=r"(?i)^\.baitstopall\s*$", outgoing=True))
@rishabh
async def stop_everything(event):
    if not BAIT_TASKS:
        return await event.reply("⚠️ **No baits running anywhere.**")

    chat_ids = set()
    count = len(BAIT_TASKS)
    entries = []
    for key in list(BAIT_TASKS):
        chat_id, _, _ = key.rpartition("_")
        chat_ids.add(int(chat_id))
        entries.append(BAIT_TASKS.pop(key))

    for entry in entries:
        entry["task"].cancel()
    await asyncio.gather(
        *(entry["task"] for entry in entries), return_exceptions=True
    )

    for cid in chat_ids:
        await _send_cancel(event.client, cid)

    await event.reply(f"🛑 **PANIC: Killed {count} baits across {len(chat_ids)} chats!**")
