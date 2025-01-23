from git import Repo
from git.exc import GitCommandError
import asyncio
import os
import sys
from utils.utils import CipherElite
from vars import Config

UPSTREAM_REPO = "https://github.com/rishabhops/CipherElite_userbot"
BRANCH = "elite"
CHECK_INTERVAL = 60  # Check every hour

def get_version():
    try:
        repo = Repo()
        return repo.head.commit.hexsha
    except:
        return None

async def smart_vars_update():
    # Load existing vars
    from vars import Config as CurrentConfig
    
    # Backup current values
    current_values = {key: value for key, value in vars(CurrentConfig).items() 
                     if not key.startswith('__')}
    
    # Pull updates
    repo.git.pull()
    
    # Import new vars template
    from vars import Config as NewConfig
    
    # Merge old values with new template
    updated_vars = f"""from telethon.tl import types
class Config(object):"""
    
    # Add new vars while keeping old values
    for key, value in vars(NewConfig).items():
        if not key.startswith('__'):
            if key in current_values:
                updated_vars += f"\n    {key} = {repr(current_values[key])}"
            else:
                updated_vars += f"\n    {key} = {repr(value)}"
    
    # Save updated vars
    with open('vars.py', 'w') as f:
        f.write(updated_vars)

async def auto_updater():
    while True:
        try:
            repo = Repo()
            origin = repo.remote('origin')
            
            # Fetch updates
            origin.fetch()
            
            # Check for new version
            current = repo.head.commit
            upstream = repo.refs['origin/main'].commit
            
            if current != upstream:
                # New version detected
                await CipherElite.send_message(
                    Config.LOGGER_GROUP,
                    "🔄 **New Update Detected!**\n\nUpdating and restarting..."
                )
                
                # Smart update vars.py
                await smart_vars_update()
                
                # Pull other updates
                origin.pull()
                
                # Restart bot
                os.execl(sys.executable, sys.executable, "-m", "main")
  

            
        except Exception as e:
            print(f"Auto-update error: {str(e)}")
            if Config.LOGGER_GROUP:
                await CipherElite.send_message(
                    Config.LOGGER_GROUP,
                    f"⚠️ **Update Error:**\n`{str(e)}`"
                )
            
        await asyncio.sleep(CHECK_INTERVAL)

# Initialize updater
def start_updater():
    CipherElite.loop.create_task(auto_updater())
    