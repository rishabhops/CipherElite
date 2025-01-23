from telethon import events
import os
import shutil
from datetime import datetime
from plugins.bot import add_handler
from utils.utils import CipherElite

def init(client_instance):
    commands = [
        ".ls - List files in current directory",
        ".cd <path> - Change directory",
        ".pwd - Show current directory",
        ".mkdir <name> - Create directory",
        ".rm <file/folder> - Remove file or folder",
        ".cp <source> <dest> - Copy file/folder",
        ".mv <source> <dest> - Move file/folder",
        ".size <path> - Get file/folder size",
        ".upload <path> - Upload file to chat",
        ".download - Download file from chat",
        ".rename <new_name> - Rename file",
        ".find <name> - Find files/folders",
        ".zip <folder> - Zip folder",
        ".unzip <file> - Unzip file"
    ]
    description = "Complete file management system 📂"
    add_handler("filemanager", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.ls(?:\s+(.+))?"))
    async def list_dir(event):
        path = event.pattern_match.group(1) or "."
        try:
            files = os.listdir(path)
            msg = "📂 **Directory Contents:**\n\n"
            for f in files:
                full_path = os.path.join(path, f)
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                is_dir = "📁" if os.path.isdir(full_path) else "📄"
                msg += f"{is_dir} `{f}` | {size}B | {modified.strftime('%Y-%m-%d %H:%M')}\n"
            await event.reply(msg)
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.cd (.+)"))
    async def change_dir(event):
        path = event.pattern_match.group(1)
        try:
            os.chdir(path)
            await event.reply(f"📂 **Changed directory to:**\n`{os.getcwd()}`")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.pwd"))
    async def print_pwd(event):
        await event.reply(f"📂 **Current directory:**\n`{os.getcwd()}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.mkdir (.+)"))
    async def make_dir(event):
        name = event.pattern_match.group(1)
        try:
            os.makedirs(name)
            await event.reply(f"📁 **Created directory:**\n`{name}`")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.rm (.+)"))
    async def remove_file(event):
        path = event.pattern_match.group(1)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            await event.reply(f"🗑️ **Removed:**\n`{path}`")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.cp (.+) (.+)"))
    async def copy_file(event):
        source, dest = event.pattern_match.groups()
        try:
            if os.path.isdir(source):
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)
            await event.reply(f"📋 **Copied:**\n`{source}` ➡️ `{dest}`")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.mv (.+) (.+)"))
    async def move_file(event):
        source, dest = event.pattern_match.groups()
        try:
            shutil.move(source, dest)
            await event.reply(f"📦 **Moved:**\n`{source}` ➡️ `{dest}`")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.size (.+)"))
    async def get_size(event):
        path = event.pattern_match.group(1)
        try:
            if os.path.isdir(path):
                size = sum(os.path.getsize(os.path.join(dirpath,filename)) 
                          for dirpath, dirnames, filenames in os.walk(path)
                          for filename in filenames)
            else:
                size = os.path.getsize(path)
            await event.reply(f"📊 **Size of** `{path}`**:**\n`{size}` bytes")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.find (.+)"))
    async def find_files(event):
        name = event.pattern_match.group(1)
        msg = "🔍 **Search Results:**\n\n"
        try:
            for root, dirs, files in os.walk("."):
                for item in dirs + files:
                    if name in item:
                        msg += f"`{os.path.join(root, item)}`\n"
            await event.reply(msg or "❌ No matches found!")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.zip (.+)"))
    async def zip_folder(event):
        folder = event.pattern_match.group(1)
        try:
            shutil.make_archive(folder, 'zip', folder)
            await event.reply(f"🗜️ **Zipped:**\n`{folder}.zip`")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")

    @CipherElite.on(events.NewMessage(pattern=r"\.unzip (.+)"))
    async def unzip_file(event):
        file = event.pattern_match.group(1)
        try:
            shutil.unpack_archive(file)
            await event.reply(f"📂 **Unzipped:**\n`{file}`")
        except Exception as e:
            await event.reply(f"❌ **Error:**\n`{str(e)}`")
            