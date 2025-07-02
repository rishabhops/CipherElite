import os
import asyncio
from datetime import datetime, timedelta
from telethon import events
import logging
from functools import wraps

from utils.utils import CipherElite
from bot.utils import rishabh, add_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)



@rishabh(pattern=r"^\.log(?:\s+(\d+))?$")
@rishabh()
async def log_command(event):
    """
    Get userbot logs
    Usage: 
    .log - Get last 50 lines
    .log 100 - Get last N lines
    """
    try:
        # Get number of lines (default 50)
        lines_match = event.pattern_match.group(1)
        lines = int(lines_match) if lines_match else 50
        
        # Limit maximum lines to prevent spam
        lines = min(lines, 500)
        
        await send_logs(event, lines)
        
    except Exception as e:
        logger.error(f"Error in log command: {e}")
        await event.reply(f"❌ **Error**: {str(e)}")

async def send_logs(event, lines):
    """Send log entries"""
    try:
        # Common log file locations
        log_files = ['bot.log', 'userbot.log', 'app.log', 'logs/bot.log']
        log_content = ""
        used_file = None
        
        # Find and read log file
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    log_content = ''.join(recent_lines)
                    used_file = log_file
                break
        
        if log_content:
            # Split into chunks if too long
            chunks = split_message(log_content)
            
            await event.reply(
                f"📋 **Logs** (Last {lines} lines)\n"
                f"📁 **File**: `{used_file}`\n"
                f"⏰ **Time**: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            # Send log chunks
            for i, chunk in enumerate(chunks):
                if i < 3:  # Limit to 3 chunks
                    await event.respond(f"```\n{chunk}\n```")
                else:
                    await event.respond(f"📄 **Truncated** ({len(chunks) - 3} more chunks)")
                    break
        else:
            await event.reply("📋 **No logs found**")
            
    except Exception as e:
        logger.error(f"Error sending logs: {e}")
        await event.reply(f"❌ **Error getting logs**: {str(e)}")

def split_message(text, max_length=4000):
    """Split long messages into chunks"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        
        # Find newline break point
        break_point = text.rfind('\n', 0, max_length)
        if break_point == -1:
            break_point = max_length
        
        chunks.append(text[:break_point])
        text = text[break_point:].lstrip('\n')
    
    return chunks

async def auto_clear_logs():
    """Automatically clear old logs every 2 hours"""
    while True:
        try:
            await asyncio.sleep(2 * 60 * 60)  # Wait 2 hours (2 * 60 * 60 seconds)
            
            log_files = ['bot.log', 'userbot.log', 'app.log', 'logs/bot.log']
            cleared_files = []
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        # Get file size
                        file_size = os.path.getsize(log_file)
                        
                        # Only clear if file is larger than 1MB
                        if file_size > 1024 * 1024:  # 1MB
                            # Keep only last 100 lines
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                            
                            # Keep last 100 lines + header
                            keep_lines = lines[-100:] if len(lines) > 100 else lines
                            
                            with open(log_file, 'w', encoding='utf-8') as f:
                                f.write(f"# Auto-cleared on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"# Kept last 100 lines from {len(lines)} total lines\n")
                                f.write("=" * 50 + "\n")
                                f.writelines(keep_lines)
                            
                            cleared_files.append(f"{log_file} ({file_size // 1024}KB)")
                            logger.info(f"Auto-cleared log file: {log_file} (was {file_size // 1024}KB)")
                    
                    except Exception as file_error:
                        logger.error(f"Error clearing {log_file}: {file_error}")
            
            if cleared_files:
                logger.info(f"Auto-cleared {len(cleared_files)} log files: {', '.join(cleared_files)}")
            
        except Exception as e:
            logger.error(f"Error in auto_clear_logs: {e}")
            # Continue the loop even if there's an error
            continue

# Start auto-clear task when plugin loads
async def start_auto_clear():
    """Start the auto-clear background task"""
    try:
        # Start the auto-clear task
        asyncio.create_task(auto_clear_logs())
        logger.info("Auto log clearing started - runs every 2 hours")
    except Exception as e:
        logger.error(f"Failed to start auto-clear task: {e}")

# Register command
add_handler(log_command, "log", "Owner-only: Get userbot logs (.log or .log 100)")

# Start auto-clear when plugin loads
if CipherElite.is_connected():
    asyncio.create_task(start_auto_clear())
else:
    # If not connected yet, start when ready
    @CipherElite.on(events.Raw)
    async def on_ready(event):
        if not hasattr(on_ready, 'started'):
            on_ready.started = True
            await start_auto_clear()

logger.info("Logs plugin loaded - .log command ready, auto-clear every 2h")
