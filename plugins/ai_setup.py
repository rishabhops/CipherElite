# =============================================================================
#  CipherElite Userbot Plugin - AI Setup Manager
#
#  Plugin Name:    ai_setup
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  LICENSE:        MIT
# =============================================================================

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# Centralized AI config file
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "DB"
CONFIG_DIR.mkdir(exist_ok=True)
AI_CONFIG_FILE = CONFIG_DIR / "ai_config.json"


class AIConfigManager:
    """Centralized manager for all AI API keys and settings"""
    
    def __init__(self):
        self.config = {
            "gemini_api_key": None,
            "ai_enabled": False,
            "last_updated": None
        }
        self._load()
    
    def _load(self):
        """Load config from file or environment"""
        try:
            if AI_CONFIG_FILE.exists():
                with open(AI_CONFIG_FILE, 'r') as f:
                    on_disk = json.load(f)
                    self.config.update(on_disk)
        except Exception as e:
            print(f"⚠️ AI Config load error: {e}")
        
        # Fallback to environment variable
        if not self.config["gemini_api_key"]:
            env_key = os.environ.get("GEMINI_API_KEY")
            if env_key:
                self.config["gemini_api_key"] = env_key
                self.config["ai_enabled"] = True
                self._save()
    
    def _save(self):
        """Save config to file"""
        try:
            with open(AI_CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ AI Config save error: {e}")
    
    def set_api_key(self, key):
        """Set Gemini API key"""
        self.config["gemini_api_key"] = key.strip() if key else None
        self.config["ai_enabled"] = bool(key)
        self.config["last_updated"] = datetime.now().isoformat()
        self._save()
        # Update environment variable for immediate use
        os.environ["GEMINI_API_KEY"] = key.strip() if key else ""
    
    def get_api_key(self):
        """Get Gemini API key"""
        return self.config.get("gemini_api_key")
    
    def is_enabled(self):
        """Check if AI is enabled"""
        return bool(self.config.get("gemini_api_key"))


# Global instance
ai_config = AIConfigManager()


def init(client):
    """Initialize AI Setup plugin"""
    commands = [
        ".setai <key>      — Set Google Gemini API Key",
        ".rmai             — Remove AI Key",
        ".aistatus         — Show AI configuration status"
    ]
    add_handler("ai_setup", commands, "AI Configuration Manager")
    
    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.setai(?:\s+(.+))?$"))
    @rishabh()
    async def _setai(event):
        """Set Gemini API key"""
        key = event.pattern_match.group(1)
        if not key:
            return await event.reply(
                "❌ **Usage:** `.setai <your_gemini_api_key>`\n\n"
                "📋 Get your key from: https://aistudio.google.com/"
            )
        
        ai_config.set_api_key(key.strip())
        msg = await event.reply(
            "✅ **Gemini API Key saved!**\n\n"
            "🤖 AI is now **ACTIVE** for all plugins.\n"
            "💬 Use `.ai <question>` in Cipher AI\n"
            "🛡️ PM Permit AI Gatekeeper is ready"
        )
        
        # Auto-delete after 5 seconds
        await asyncio.sleep(5)
        try:
            await event.delete()
            await msg.delete()
        except:
            pass
    
    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.rmai$"))
    @rishabh()
    async def _rmai(event):
        """Remove AI key"""
        ai_config.set_api_key(None)
        msg = await event.reply(
            "🛑 **Gemini API Key removed!**\n\n"
            "AI features disabled across all plugins."
        )
        
        await asyncio.sleep(5)
        try:
            await event.delete()
            await msg.delete()
        except:
            pass
    
    @CipherElite.on(events.NewMessage(outgoing=True, pattern=r"\.aistatus$"))
    @rishabh()
    async def _aistatus(event):
        """Show AI status"""
        key = ai_config.get_api_key()
        status = "✅ **Enabled**" if key else "❌ **Disabled**"
        masked_key = f"`{key[:10]}...{key[-5:]}`" if key else "`Not Set`"
        
        status_msg = f"""📊 **AI Configuration Status:**

🔑 **API Key:** {status}
🔐 **Key (Masked):** {masked_key}
🤖 **Provider:** Google Gemini
⚙️ **Used By:** PM Permit & Cipher AI

📝 **Commands:**
• `.setai <key>` - Set API key (same key for all plugins)
• `.rmai` - Remove API key
• `.aistatus` - Show this status

🔗 **Get API Key:** https://aistudio.google.com/

💡 **Note:** Set the API key once and it works across all AI plugins!"""
        
        await event.reply(status_msg)
    
    print("✅ AI Setup Plugin initialized")
    return ai_config
