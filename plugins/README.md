
# 🎭 CipherElite Plugin Development Guide

## Basic Plugin Structure

```
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".command <param> - Description of command"
    ]
    description = "🎭 Plugin Name - Brief description"
    add_handler("plugin_name", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.command\s+(.+)"))
    @rishabh()
    async def command_handler(event):
        try:
            param = event.pattern_match.group(1).strip()
            await event.reply("✅ **Success!**")
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
```

## Required Components

### 1. Imports
```
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
```

### 2. Init Function
```
def init(client_instance):
    commands = [
        ".cmd <param> - Description"  # Full syntax with parameters
    ]
    description = "🎭 Plugin - What it does"
    add_handler("short_name", commands, description)  # Keep name short
```

### 3. Command Handler
```
async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.cmd\s+(.+)"))
    @rishabh()
    async def handler(event):
        try:
            # Your logic here
            await event.reply("🎭 **Cipher Elite Result**\n\n✅ Success")
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
```

## Pattern Examples

```
# Basic command
pattern=r"\.command"

# Required parameter
pattern=r"\.command\s+(.+)"

# Optional parameter
pattern=r"\.command\s*(.*)"

# Multiple parameters
pattern=r"\.command\s+(\w+)\s*(.*)"
```

## Message Formatting

```
# Success message
await event.reply("🎭 **Cipher Elite Success**\n\n"
                 "✅ **Result:** Your result here\n"
                 "🤖 **Powered by Cipher Elite**")

# Error message
await event.reply(f"🎭 **Cipher Elite Error**\n\n"
                 f"❌ **Error:** {str(e)}\n"
                 f"💡 **Try again with correct parameters**")

# Status updates
status = await event.reply("🔄 **Processing...**")
await status.edit("✅ **Complete!**")
```

## Complete Example

```
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".reverse <text> - Reverse text with Cipher Elite",
        ".upper <text> - Convert text to uppercase"
    ]
    description = "🎭 Text Tools - Basic text manipulation"
    add_handler("texttools", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.reverse\s+(.+)"))
    @rishabh()
    async def reverse_text(event):
        try:
            text = event.pattern_match.group(1).strip()
            result = text[::-1]
            
            await event.reply("🎭 **Cipher Elite Text Reverser**\n\n"
                            f"📝 **Original:** `{text}`\n"
                            f"🔄 **Reversed:** `{result}`\n"
                            f"✅ **Success!**")
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.upper\s+(.+)"))
    @rishabh()
    async def upper_text(event):
        try:
            text = event.pattern_match.group(1).strip()
            result = text.upper()
            
            await event.reply(f"🎭 **Uppercase Result**\n\n`{result}`")
        except Exception as e:
            await event.reply(f"❌ **Error:** {str(e)}")
```

## Quick Checklist

### ✅ Must Have
- [ ] `init()` function with commands list
- [ ] `register_commands()` async function
- [ ] `@rishabh()` decorator on commands
- [ ] Try/except error handling
- [ ] Command syntax with `<required>` `[optional]` parameters

### ✅ Best Practices
- [ ] Short plugin name for help menu button
- [ ] Cipher Elite branding in messages
- [ ] Clear parameter descriptions
- [ ] Input validation

## Quick Start

1. **Create file:** `plugins/myplugin.py`
2. **Copy template above**
3. **Replace:** plugin name, commands, logic
4. **Test:** Restart bot, use `.help myplugin`
5. **Deploy:** Commands work automatically

Your plugin will appear in `.help` menu and support direct access via `.help myplugin`!
```
