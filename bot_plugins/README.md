# 🤖 CipherElite Bot Plugins

Beautiful and useful plugins for the CipherElite Assistant Bot.

## 📦 Available Plugins

### 1. 🤖 Assistant (`assistant.py`)
**Main assistant bot with core features**

**Commands:**
- `/start` - Welcome message with features
- `/help` - Complete help menu
- `/ping` - Check bot status
- `/stats` - Bot statistics

---

### 2. 🧮 Calculator (`calculator.py`)
**Advanced math calculator**

**Commands:**
- `/calc <expression>` - Calculate math expressions
- Inline: `@bot calc <expression>`

**Examples:**
- `/calc 2+2` → 4
- `/calc 10*5+3` → 53
- `/calc (100-20)/4` → 20
- `/calc 2^8` → 256

---

### 3. 🌐 Translator (`translator.py`)
**Text translation using Google Translate**

**Commands:**
- `/tr <text>` - Translate to English
- `/tr <lang> <text>` - Translate to specific language
- Reply to message with `/tr <lang>` - Translate that message
- Inline: `@bot tr <text>`

**Languages:**
en (English), hi (Hindi), es (Spanish), fr (French), de (German), it (Italian), pt (Portuguese), ru (Russian), ja (Japanese), ko (Korean), zh (Chinese), ar (Arabic)

**Examples:**
- `/tr Hello` → Translation
- `/tr es Hello world` → Spanish translation
- Reply to Hindi text with `/tr en` → English translation

---

### 4. 🌤️ Weather (`weather.py`)
**Real-time weather information**

**Commands:**
- `/weather <city>` - Get weather for city
- Inline: `@bot weather <city>`

**Features:**
- Current temperature
- Humidity percentage
- Wind speed
- Weather condition with emoji

**Examples:**
- `/weather London`
- `/weather New York`
- `/weather Tokyo`

---

### 5. 🎮 Games (`games.py`)
**Fun games and dice**

**Commands:**
- `/dice` - Roll a dice (1-6)
- `/coin` - Flip a coin
- `/8ball <question>` - Magic 8-ball
- `/rps` - Rock Paper Scissors (with buttons)
- Inline: `@bot dice` or `@bot coin`

**Features:**
- Random dice roll
- Coin flip
- Interactive Rock Paper Scissors with buttons
- Magic 8-ball predictions

---

### 6. 💭 Quotes (`quotes.py`)
**Inspiration, jokes, and facts**

**Commands:**
- `/quote` - Random inspirational quote
- `/joke` - Random joke
- `/fact` - Interesting fact
- Inline: `@bot quote` or `@bot joke`

**Content:**
- 15+ inspirational quotes from famous people
- Programming jokes
- Amazing facts

---

### 7. 🤫 Whisper Bot (`whisper_bot.py`)
**Secret message delivery**

**Usage:**
- Use userbot command: `.wspr <user> <text>`
- Bot creates a button that only target user can open
- Messages are cryptographically locked

---

### 8. 📚 Help (`help.py`)
**Beautiful help menu with all commands**

**Commands:**
- `/start` - Welcome message
- `/help` - Complete help menu
- `/ping` - Bot status
- `/stats` - Statistics

---

## 🎯 Features

### Inline Mode Support
Most plugins support inline mode:
```
@YourBot calc 2+2
@YourBot tr Hello
@YourBot weather London
@YourBot dice
@YourBot quote
```

### Beautiful UI
- Clean blockquote design
- Emoji-rich interface
- Responsive buttons
- Mobile-friendly

### Error Handling
- Graceful failures
- Helpful error messages
- Fallback options

---

## 📊 Plugin Structure

Each plugin follows this structure:

```python
def init_bot_plugin(bot, owner_id, owner_name):
    # Register handlers
    @bot.on(events.NewMessage(pattern=r"^/command$"))
    async def command(event):
        # Handler logic
        pass
    
    @bot.on(events.InlineQuery(pattern=r"^command$"))
    async def inline_command(event):
        # Inline handler logic
        pass
    
    print("✅ Plugin loaded")
```

---

## 🚀 Adding New Plugins

1. Create new file in `bot_plugins/` folder
2. Follow the structure above
3. Add to `BOT_CATEGORIES` in `help.py`:

```python
BOT_CATEGORIES = {
    "your_plugin": {
        "icon": "🎨",
        "name": "Your Plugin",
        "desc": "Description"
    },
}
```

4. Restart bot - plugin will auto-load

---

## 💡 Tips

- All commands work in groups and private chats
- Inline mode works in any chat
- Plugins auto-load on bot restart
- Check `/stats` to see all loaded plugins

---

**Made with ❤️ by CipherElite Dev**
