# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    zip
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
#.      update on: 25/07/2026 by Marlboro CLOVE 
#  Thank you for respecting open-source software!
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "utilities"

import os
import time
import zipfile
import shutil
from pathlib import Path
from telethon import events
from telethon.types import Message
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".zip - Zip the replied media",
        ".unzip - Unzip the replied zip file",
        ".ls [path] - List files in directory",
        ".mkdir <path> - Create a directory",
        ".rm <path> - Remove a file or directory",
        ".mv <src> <dst> - Move/rename a file",
        ".cp <src> <dst> - Copy a file",
        ".size <path> - Get file/folder size",
        ".storage - Show disk storage info",
        ".findfile <name> - Search for files by name"
    ]
    description = "📦 Archive & File Manager - zip, unzip, and manage files"
    add_handler("zip", commands, description)

def get_size(path):
    """Calculate total size of file or directory in MB"""
    try:
        if os.path.isfile(path):
            return os.path.getsize(path) / (1024 * 1024)
        elif os.path.isdir(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total += os.path.getsize(fp)
            return total / (1024 * 1024)
    except Exception:
        pass
    return 0

def format_size(size_mb):
    """Format size in MB to human readable"""
    if size_mb < 1:
        return f"{size_mb * 1024:.2f} KB"
    elif size_mb < 1024:
        return f"{size_mb:.2f} MB"
    else:
        return f"{size_mb / 1024:.2f} GB"

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.zip"))
    @rishabh()
    async def zip_files(event: Message):
        if not event.reply_to_msg_id:
            return await event.reply("❌ Reply to a message to zip it.")
        
        reply = await event.get_reply_message()
        if not reply.media:
            return await event.reply("❌ Reply to a media message to zip it.")
        
        elite = await event.reply("🔄 Zipping...")
        start = time.time()
        download_path = await reply.download_media(f"temp_{round(time.time())}")

        zip_path = f"zipped_{int(time.time())}.zip"
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(download_path, os.path.basename(download_path))

            await elite.edit("✅ Zipped Successfully. Uploading...")
            await event.reply(
                f"**✓ Zipped in {time.time() - start:.2f}s**\n📦 File size: {format_size(get_size(zip_path))}",
                file=zip_path
            )
        except Exception as e:
            await elite.edit(f"❌ Error: {str(e)}")
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(download_path):
                os.remove(download_path)
            await elite.delete()

    @CipherElite.on(events.NewMessage(pattern=r"\.unzip"))
    @rishabh()
    async def unzip_file(event: Message):
        if not event.reply_to_msg_id:
            return await event.reply("❌ Reply to a message to unzip it.")
        
        reply = await event.get_reply_message()
        if not reply.media:
            return await event.reply("❌ Reply to a zip file to unzip it.")
        
        elite = await event.reply("🔄 Unzipping...")
        start = time.time()
        download_path = await reply.download_media(f"temp_{round(time.time())}")
        
        unzip_dir = f"unzipped_{int(time.time())}"
        os.makedirs(unzip_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(download_path, "r") as zip_file:
                zip_file.extractall(unzip_dir)
            
            await elite.edit("✅ Unzipped Successfully. Uploading files...")
            uploaded = 0
            
            for root, _, files in os.walk(unzip_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        await event.reply(
                            f"📄 **{file}** ({format_size(get_size(file_path))})",
                            file=file_path
                        )
                        uploaded += 1
                    except Exception as e:
                        print(f"Error uploading {file}: {e}")
                    finally:
                        if os.path.exists(file_path):
                            os.remove(file_path)
            
            await elite.edit(f"✅ **Successfully uploaded {uploaded} files in {time.time() - start:.2f}s!**")
        except Exception as e:
            await elite.edit(f"❌ Error: {str(e)}")
        finally:
            shutil.rmtree(unzip_dir, ignore_errors=True)
            if os.path.exists(download_path):
                os.remove(download_path)

    @CipherElite.on(events.NewMessage(pattern=r"\.ls(?:\s+(.+))?"))
    @rishabh()
    async def list_files(event: Message):
        path = event.pattern_match.group(1) or "."
        
        if not os.path.exists(path):
            return await event.reply(f"❌ Path not found: `{path}`")
        
        if not os.path.isdir(path):
            return await event.reply(f"❌ Not a directory: `{path}`")
        
        try:
            items = os.listdir(path)
            if not items:
                return await event.reply(f"📁 Directory is empty: `{path}`")
            
            msg = f"📁 **Directory:** `{os.path.abspath(path)}`\n\n"
            folders = [i for i in items if os.path.isdir(os.path.join(path, i))]
            files = [i for i in items if os.path.isfile(os.path.join(path, i))]
            
            if folders:
                msg += "📂 **Folders:**\n"
                for f in folders[:20]:
                    msg += f"  └ `{f}/`\n"
            
            if files:
                msg += "\n📄 **Files:**\n"
                for f in files[:20]:
                    fpath = os.path.join(path, f)
                    size = format_size(get_size(fpath))
                    msg += f"  └ `{f}` ({size})\n"
            
            if len(items) > 40:
                msg += f"\n*... and {len(items) - 40} more items*"
            
            await event.reply(msg)
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.mkdir\s+(.+)"))
    @rishabh()
    async def make_dir(event: Message):
        path = event.pattern_match.group(1).strip()
        
        try:
            os.makedirs(path, exist_ok=True)
            await event.reply(f"✅ **Directory created:** `{os.path.abspath(path)}`")
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.rm\s+(.+)"))
    @rishabh()
    async def remove_file(event: Message):
        path = event.pattern_match.group(1).strip()
        
        if not os.path.exists(path):
            return await event.reply(f"❌ Path not found: `{path}`")
        
        try:
            if os.path.isfile(path):
                os.remove(path)
                await event.reply(f"✅ **File removed:** `{path}`")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                await event.reply(f"✅ **Directory removed:** `{path}`")
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.mv\s+(.+?)\s+(.+)"))
    @rishabh()
    async def move_file(event: Message):
        src = event.pattern_match.group(1).strip()
        dst = event.pattern_match.group(2).strip()
        
        if not os.path.exists(src):
            return await event.reply(f"❌ Source not found: `{src}`")
        
        try:
            shutil.move(src, dst)
            await event.reply(f"✅ **Moved:** `{src}` → `{dst}`")
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.cp\s+(.+?)\s+(.+)"))
    @rishabh()
    async def copy_file(event: Message):
        src = event.pattern_match.group(1).strip()
        dst = event.pattern_match.group(2).strip()
        
        if not os.path.exists(src):
            return await event.reply(f"❌ Source not found: `{src}`")
        
        try:
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                shutil.copytree(src, dst)
            await event.reply(f"✅ **Copied:** `{src}` → `{dst}`")
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.size\s+(.+)"))
    @rishabh()
    async def file_size(event: Message):
        path = event.pattern_match.group(1).strip()
        
        if not os.path.exists(path):
            return await event.reply(f"❌ Path not found: `{path}`")
        
        try:
            size = get_size(path)
            type_str = "📁 Directory" if os.path.isdir(path) else "📄 File"
            await event.reply(f"✅ **{type_str}:** `{path}`\n📊 **Size:** {format_size(size)}")
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.storage"))
    @rishabh()
    async def storage_info(event: Message):
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            
            msg = (
                "💾 **STORAGE INFO**\n\n"
                f"📊 **Total:** {format_size(total / (1024**2))}\n"
                f"✅ **Used:** {format_size(used / (1024**2))}\n"
                f"🟢 **Free:** {format_size(free / (1024**2))}\n"
                f"📈 **Usage:** {(used / total * 100):.1f}%\n"
            )
            await event.reply(msg)
        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.findfile\s+(.+)"))
    @rishabh()
    async def find_file(event: Message):
        search_term = event.pattern_match.group(1).strip()
        
        elite = await event.reply(f"🔍 Searching for `{search_term}`...")
        results = []
        
        try:
            for root, dirs, files in os.walk("."):
                for file in files:
                    if search_term.lower() in file.lower():
                        file_path = os.path.join(root, file)
                        results.append(file_path)
                        if len(results) >= 20:
                            break
                if len(results) >= 20:
                    break
            
            if not results:
                await elite.edit(f"❌ No files found matching: `{search_term}`")
                return
            
            msg = f"✅ **Found {len(results)} file(s):**\n\n"
            for r in results:
                size = format_size(get_size(r))
                msg += f"📄 `{r}` ({size})\n"
            
            await elite.edit(msg)
        except Exception as e:
            await elite.edit(f"❌ Error: {str(e)}")
