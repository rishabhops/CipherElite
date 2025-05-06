import os
import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURE THESE
GITHUB_OWNER  = "rishabhops"
GITHUB_REPO   = "CipherElite"
GITHUB_BRANCH = "elite"
# ──────────────────────────────────────────────────────────────────────────────

RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
COMPARE_API = API_BASE + "/compare"

# Where to persist last‐seen SHA
PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR       = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE      = DB_DIR / "updater_db.json"

def load_db() -> dict:
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    return {}

def save_db(d: dict):
    DB_FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")

async def get_json(url: str):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

async def download_file(relpath: str) -> bytes:
    url = f"{RAW_BASE}/{relpath}"
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            resp.raise_for_status()
            return await resp.read()

@CipherElite.on(events.NewMessage(pattern=r"\.checkupdate$", incoming=True))
@rishabh()
async def check_update(event):
    """
    .checkupdate — show which files/lines would change if you updated.
    """
    db = load_db()
    last_sha = db.get("last_sha", "")
    await event.reply("🔍 Checking GitHub for updates…")
    # get current head SHA
    branch = await get_json(f"{API_BASE}/branches/{GITHUB_BRANCH}")
    remote_sha = branch["commit"]["sha"]

    if remote_sha == last_sha:
        return await event.reply("✅ Already up-to-date on GitHub.")

    # compare
    comp = await get_json(f"{COMPARE_API}/{last_sha}...{remote_sha}")
    files = comp.get("files", [])
    if not files:
        return await event.reply("ℹ️ No file changes reported.")

    text = "**Updates available:**\n\n"
    for f in files:
        status = f["status"]    # added, removed, modified, renamed
        name   = f["filename"]
        additions = f["additions"]
        deletions = f["deletions"]
        text += f"• {status.upper():8} {name} (+{additions}/–{deletions})\n"
    await event.reply(text)

@CipherElite.on(events.NewMessage(pattern=r"\.update$", incoming=True))
@rishabh()
async def do_update(event):
    """
    .update — fetch only changed files from GitHub, write them, then restart.
    """
    db = load_db()
    last_sha = db.get("last_sha", "")
    msg = await event.reply("🔄 Checking for updates…")

    # fetch current head
    branch = await get_json(f"{API_BASE}/branches/{GITHUB_BRANCH}")
    remote_sha = branch["commit"]["sha"]

    if remote_sha == last_sha:
        return await msg.edit("✅ Already up-to-date on GitHub.")

    # compare base…head
    comp = await get_json(f"{COMPARE_API}/{last_sha}...{remote_sha}")
    files = comp.get("files", [])

    if not files:
        # no files? still update stored SHA
        db["last_sha"] = remote_sha
        save_db(db)
        return await msg.edit("ℹ️ Nothing changed — just updated internal marker.")

    await msg.edit(f"📄 {len(files)} files to update, fetching…")
    # apply each change
    for f in files:
        rel = f["filename"]
        status = f["status"]
        local_path = PROJECT_ROOT / rel
        if status in ("modified", "added", "renamed"):
            # download new content
            content = await download_file(rel)
            # ensure dir exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(content)
        elif status == "removed":
            if local_path.exists():
                local_path.unlink()

    # update stored SHA
    db["last_sha"] = remote_sha
    save_db(db)

    await msg.edit("✅ Files updated, restarting…")
    # small delay for edit to go through
    await asyncio.sleep(1.0)
    os.execv(sys.executable, [sys.executable] + sys.argv)
