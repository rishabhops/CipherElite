# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    updater
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
#
#  IMPORTANT:
#    • If you copy, fork, or include this plugin in your own bot,
#      you MUST keep this header intact.
#    • You MUST give proper credit to the CipherElite Userbot author:
#        – GitHub:    https://github.com/rishabhops/CipherElite
#        – Telegram:  @thanosceo
#
#  Thank you for respecting open-source software!
# =============================================================================
import os, sys, json, asyncio, aiohttp
from pathlib import Path
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh

# ──────────────────────────────────────────────────────────────
GITHUB_OWNER  = "rishabhops"
GITHUB_REPO   = "CipherElite"
GITHUB_BRANCH = "elite"
API_BASE      = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
RAW_BASE      = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
# ──────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
DB_DIR       = PROJECT_ROOT / "DB"
DB_DIR.mkdir(exist_ok=True)
DB_FILE      = DB_DIR / "updater_db.json"

# ANY files here will be *skipped* by the updater
SKIP_FILES = {
  "vars.py",            # your credentials + IDs
  "config/config.py",   # if you also customize your Config
}

def load_db() -> dict:
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text())
    return {}

def save_db(d: dict):
    DB_FILE.write_text(json.dumps(d, indent=2))

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

async def fetch_full_tree():
    tree_url = f"{API_BASE}/git/trees/{GITHUB_BRANCH}?recursive=1"
    js = await get_json(tree_url)
    return [e for e in js.get("tree", []) if e["type"] == "blob"]

@CipherElite.on(events.NewMessage(pattern=r"\.checkupdate$", outgoing=True))
@rishabh()
async def check_update(event):
    db       = load_db()
    last_sha = db.get("last_sha", "")
    await event.reply("🔍 Checking for updates…")

    branch = await get_json(f"{API_BASE}/branches/{GITHUB_BRANCH}")
    remote_sha = branch["commit"]["sha"]

    if not last_sha:
        # initial import listing
        tree = await fetch_full_tree()
        text = "**Initial import – files you will get:**\n\n"
        for e in tree:
            if e["path"] in SKIP_FILES:
                continue
            text += f"• ADDED   {e['path']}\n"
        return await event.reply(text)

    comp = await get_json(f"{API_BASE}/compare/{last_sha}...{remote_sha}")
    files = comp.get("files", [])
    if not files:
        return await event.reply("✅ Already up-to-date.")

    text = "**Updates available:**\n\n"
    for f in files:
        name = f["filename"]
        if name in SKIP_FILES:
            continue
        text += f"• {f['status'].upper():8} {name} (+{f['additions']}/–{f['deletions']})\n"
    await event.reply(text)

@CipherElite.on(events.NewMessage(pattern=r"\.update$", outgoing=True))
@rishabh()
async def do_update(event):
    db       = load_db()
    last_sha = db.get("last_sha", "")
    msg      = await event.reply("🔄 Fetching updates…")

    branch = await get_json(f"{API_BASE}/branches/{GITHUB_BRANCH}")
    remote_sha = branch["commit"]["sha"]

    # ─── initial import ─────────────────────────────────────────────
    if not last_sha:
        tree = await fetch_full_tree()
        await msg.edit(f"📦 Downloading {len(tree)} files (initial import)…")
        for e in tree:
            rel = e["path"]
            if rel in SKIP_FILES:
                continue
            local = PROJECT_ROOT / rel
            local.parent.mkdir(parents=True, exist_ok=True)
            content = await download_file(rel)
            local.write_bytes(content)
        db["last_sha"] = remote_sha
        save_db(db)
        return await msg.edit(
          "✅ Initial import complete! Variables preserved.\n"
          "Now try .ping and .alive\n"
          "Restarting…"
        )

    # ─── delta update ───────────────────────────────────────────────
    if remote_sha == last_sha:
        return await msg.edit("✅ Already up-to-date.")

    comp = await get_json(f"{API_BASE}/compare/{last_sha}...{remote_sha}")
    files = comp.get("files", [])
    if not files:
        db["last_sha"] = remote_sha
        save_db(db)
        return await msg.edit("ℹ️ No changes detected – marker updated.")

    await msg.edit(f"📄 {len(files)} files changed – downloading…")
    for f in files:
        rel    = f["filename"]
        status = f["status"]
        if rel in SKIP_FILES:
            continue
        local = PROJECT_ROOT / rel
        if status in ("added", "modified", "renamed"):
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(await download_file(rel))
        elif status == "removed" and local.exists():
            local.unlink()

    db["last_sha"] = remote_sha
    save_db(db)

    # final success edit + preserve vars + tip
    await msg.edit(
      "✅ Update successful. Variables untouched.\n"
      "Check .ping and .alive\n"
      "Restarting now…"
    )
    await asyncio.sleep(1.0)
    os.execv(sys.executable, [sys.executable] + sys.argv)

def init(client):
    # no-op so your loader doesn’t complain
    pass
    
