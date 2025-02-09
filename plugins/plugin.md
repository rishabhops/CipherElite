# CipherElite Bot Plugin Development Guide

## Plugin Structure
Every CipherElite plugin should follow this basic structure:

```python
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    """
    Required initialization function that registers commands and descriptions
    """
    commands = [
        ".command1 - Description of command1",
        ".command2 - Description of command2"
    ]
    description = "Plugin description"
    add_handler("plugin_name", commands, description)

async def register_commands():
    """
    Main function where command handlers are defined
    """
    @CipherElite.on(events.NewMessage(pattern=r"\.yourcommand"))
    @rishabh()
    async def your_command_handler(event):
        # Command implementation
        pass
```

## Essential Components

### 1. Imports
```python
from telethon import events  # For event handling
from utils.utils import CipherElite  # Main bot client
from utils.decorators import rishabh  # Command decorator
from plugins.bot import add_handler  # Register commands
```

### 2. Initialization Function
Every plugin must have an `init()` function:
```python
def init(client_instance):
    commands = [
        ".command - Description"
    ]
    description = "Plugin description"
    add_handler("plugin_name", commands, description)
```

### 3. Command Registration
Commands are registered using the `register_commands()` function:
```python
async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.command"))
    @rishabh()
    async def command_handler(event):
        # Command implementation
        pass
```

## Event Handling

### Event Patterns
Commands are triggered using regex patterns:
```python
@CipherElite.on(events.NewMessage(pattern=r"\.yourcommand"))
```

### Event Object
The event object provides access to:
- `event.reply_to_msg_id` - ID of replied message
- `event.pattern_match` - Regex match object
- `event.client` - Bot client instance
- `event.chat_id` - Chat ID where command was used

## Helper Functions

### User Resolution
To get user information:
```python
async def get_user_from_event(event):
    try:
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            user = await event.client.get_entity(reply_message.sender_id)
        else:
            user_input = event.pattern_match.group(1)
            if user_input:
                user = await event.client.get_entity(user_input)
        return user
    except Exception as e:
        await event.reply(f"Error: {e}")
        return None
```

## Best Practices

1. **Error Handling**
```python
try:
    # Your code
except Exception as e:
    await event.reply(f"Error: {str(e)}")
```

2. **Resource Cleanup**
```python
if os.path.exists(temp_file):
    os.remove(temp_file)
```

3. **Command Response**
```python
await event.reply("✅ Operation successful!")
```

## Example Plugin

Here's a simple plugin template:

```python
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".hello - Sends a greeting",
        ".bye - Sends goodbye"
    ]
    description = "Basic greeting plugin"
    add_handler("greetings", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.hello"))
    @rishabh()
    async def hello_handler(event):
        try:
            await event.reply("👋 Hello!")
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.bye"))
    @rishabh()
    async def bye_handler(event):
        try:
            await event.reply("👋 Goodbye!")
        except Exception as e:
            await event.reply(f"Error: {str(e)}")
```

## Important Notes

1. Always use the `@rishabh()` decorator for command handlers
2. Handle exceptions appropriately
3. Clean up temporary files and resources
4. Use meaningful command patterns and descriptions
5. Follow the plugin structure consistently

## Available Utilities

- `CipherElite` - Main bot client instance
- `rishabh()` - Command handler decorator
- `add_handler()` - Register commands and descriptions
- Telethon's event system for command handling
