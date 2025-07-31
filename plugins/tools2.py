# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    tools
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

import base64
import datetime
import math
import os
import time
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    """
    Required initialization function that registers commands and descriptions
    """
    commands = [
        ".base64enc <text/reply> - Encode text to base64 string",
        ".base64dec <text/reply> - Decode base64 string to text", 
        ".calc <expression> - Calculate mathematical expressions",
        ".calculate <expression> - Calculate mathematical expressions (alias)",
        ".math <operation> <number> - Perform basic math operations",
        ".unpack <reply to file> - Extract text content from file",
        ".pack <reply to text> [filename] - Save text content as file",
        ".calendar [month/year] - Generate calendar image for specified month/year"
    ]
    description = "🔧 Cipher Elite Tools - Advanced utility tools for encoding, calculations, file operations and calendar generation"
    add_handler("tools", commands, description)

async def register_commands():
    """
    Main function where command handlers are defined
    """
    
    # Available math operations
    math_cmds = ["sin", "cos", "tan", "square", "cube", "sqroot", "factorial", "power"]
    
    @CipherElite.on(events.NewMessage(pattern=r"\.base64enc\s*(.*)"))
    @rishabh()
    async def base64_encode(event):
        try:
            text_input = event.pattern_match.group(1).strip()
            
            # Get text from command or reply
            if text_input:
                text = text_input
            elif event.reply_to_msg_id:
                reply_message = await event.get_reply_message()
                text = reply_message.text or reply_message.caption or ""
            else:
                await event.reply("🎭 **Cipher Elite Base64 Encoder**\n\n"
                                "❌ **Error:** Please provide text to encode!\n\n"
                                "**Usage:** `.base64enc Hello World`\n"
                                "**Or reply** to a message with `.base64enc`")
                return
            
            if not text:
                await event.reply("❌ **Cipher Elite Error:** No text found to encode!")
                return
            
            status_msg = await event.reply("🎭 **Cipher Elite Encoder**\n\n"
                                         "🔄 **Processing:** Encoding to Base64...\n"
                                         "⚡ **Engine:** Advanced Encryption Module")
            
            try:
                encoded = base64.b64encode(text.encode()).decode()
                
                await status_msg.edit(f"🎭 **Cipher Elite Base64 Encoded**\n\n"
                                     f"📝 **Original Text:** `{text[:50]}{'...' if len(text) > 50 else ''}`\n\n"
                                     f"🔐 **Encoded Result:**\n`{encoded}`\n\n"
                                     f"✅ **Status:** Successfully encoded\n"
                                     f"🤖 **Powered by Cipher Elite**")
            except Exception as e:
                await status_msg.edit(f"🎭 **Cipher Elite Encoder Error**\n\n"
                                     f"❌ **Error:** {str(e)}\n"
                                     f"💡 **Try again with valid text**")
                
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.base64dec\s*(.*)"))
    @rishabh()
    async def base64_decode(event):
        try:
            text_input = event.pattern_match.group(1).strip()
            
            # Get text from command or reply
            if text_input:
                text = text_input
            elif event.reply_to_msg_id:
                reply_message = await event.get_reply_message()
                text = reply_message.text or reply_message.caption or ""
            else:
                await event.reply("🎭 **Cipher Elite Base64 Decoder**\n\n"
                                "❌ **Error:** Please provide base64 text to decode!\n\n"
                                "**Usage:** `.base64dec SGVsbG8gV29ybGQ=`\n"
                                "**Or reply** to a message with `.base64dec`")
                return
            
            if not text:
                await event.reply("❌ **Cipher Elite Error:** No text found to decode!")
                return
            
            status_msg = await event.reply("🎭 **Cipher Elite Decoder**\n\n"
                                         "🔄 **Processing:** Decoding from Base64...\n"
                                         "⚡ **Engine:** Advanced Decryption Module")
            
            try:
                decoded = base64.b64decode(text.encode()).decode()
                
                await status_msg.edit(f"🎭 **Cipher Elite Base64 Decoded**\n\n"
                                     f"🔐 **Encoded Text:** `{text[:50]}{'...' if len(text) > 50 else ''}`\n\n"
                                     f"📝 **Decoded Result:**\n`{decoded}`\n\n"
                                     f"✅ **Status:** Successfully decoded\n"
                                     f"🤖 **Powered by Cipher Elite**")
            except Exception as e:
                await status_msg.edit(f"🎭 **Cipher Elite Decoder Error**\n\n"
                                     f"❌ **Error:** Invalid Base64 string\n"
                                     f"💡 **Make sure the text is properly encoded**")
                
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.(calc|calculate)\s+(.+)"))
    @rishabh()
    async def calculator(event):
        try:
            expression = event.pattern_match.group(2).strip()
            
            if not expression:
                await event.reply("🎭 **Cipher Elite Calculator**\n\n"
                                "❌ **Error:** Please provide an expression to calculate!\n\n"
                                "**Usage:** `.calc 2 + 2 * 5`\n"
                                "**Example:** `.calculate (10 + 5) / 3`")
                return
            
            status_msg = await event.reply("🎭 **Cipher Elite Calculator**\n\n"
                                         f"🔢 **Expression:** `{expression}`\n"
                                         f"🔄 **Status:** Calculating...\n"
                                         f"⚡ **Engine:** Advanced Math Processor")
            
            try:
                # Secure evaluation (basic protection)
                allowed_chars = set('0123456789+-*/.() ')
                if not all(c in allowed_chars for c in expression.replace(' ', '')):
                    await status_msg.edit("🎭 **Cipher Elite Calculator Error**\n\n"
                                         "❌ **Error:** Invalid characters in expression\n"
                                         "💡 **Only numbers and +, -, *, /, (, ) are allowed**")
                    return
                
                result = eval(expression)
                
                await status_msg.edit(f"🎭 **Cipher Elite Calculator Result**\n\n"
                                     f"🔢 **Expression:** `{expression}`\n\n"
                                     f"🎯 **Result:** `{result}`\n\n"
                                     f"✅ **Status:** Calculation completed\n"
                                     f"🤖 **Powered by Cipher Elite**")
                                     
            except ZeroDivisionError:
                await status_msg.edit("🎭 **Cipher Elite Calculator Error**\n\n"
                                     "❌ **Error:** Division by zero\n"
                                     "💡 **Cannot divide by zero**")
            except Exception as e:
                await status_msg.edit("🎭 **Cipher Elite Calculator Error**\n\n"
                                     f"❌ **Error:** Invalid expression\n"
                                     f"💡 **Check your syntax and try again**")
                
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.math\s+(\w+)\s+(.+)"))
    @rishabh()
    async def math_operations(event):
        try:
            cmd = event.pattern_match.group(1).lower()
            query = event.pattern_match.group(2).strip()
            
            if cmd not in math_cmds:
                await event.reply(f"🎭 **Cipher Elite Math Engine**\n\n"
                                f"❌ **Unknown operation:** `{cmd}`\n\n"
                                f"**Available operations:**\n"
                                f"`{'`, `'.join(math_cmds)}`\n\n"
                                f"**Usage:** `.math sin 90`")
                return
            
            status_msg = await event.reply("🎭 **Cipher Elite Math Engine**\n\n"
                                         f"🧮 **Operation:** {cmd.upper()}\n"
                                         f"🔢 **Input:** {query}\n"
                                         f"🔄 **Status:** Calculating...\n"
                                         f"⚡ **Engine:** Advanced Mathematical Processor")
            
            try:
                number = float(query)
                
                if cmd == "sin":
                    result = math.sin(math.radians(number))
                elif cmd == "cos":
                    result = math.cos(math.radians(number))
                elif cmd == "tan":
                    result = math.tan(math.radians(number))
                elif cmd == "square":
                    result = number * number
                elif cmd == "cube":
                    result = number * number * number
                elif cmd == "sqroot":
                    if number < 0:
                        await status_msg.edit("🎭 **Cipher Elite Math Error**\n\n"
                                             "❌ **Error:** Cannot calculate square root of negative number")
                        return
                    result = math.sqrt(number)
                elif cmd == "factorial":
                    if number < 0 or number != int(number):
                        await status_msg.edit("🎭 **Cipher Elite Math Error**\n\n"
                                             "❌ **Error:** Factorial only works with non-negative integers")
                        return
                    result = math.factorial(int(number))
                elif cmd == "power":
                    result = math.pow(number, 2)
                
                await status_msg.edit(f"🎭 **Cipher Elite Math Result**\n\n"
                                     f"🧮 **Operation:** {cmd.upper()}\n"
                                     f"🔢 **Input:** `{query}`\n\n"
                                     f"🎯 **Result:** `{result}`\n\n"
                                     f"✅ **Status:** Calculation completed\n"
                                     f"🤖 **Powered by Cipher Elite**")
                                     
            except ValueError:
                await status_msg.edit("🎭 **Cipher Elite Math Error**\n\n"
                                     "❌ **Error:** Invalid number format\n"
                                     "💡 **Please provide a valid number**")
            except Exception as e:
                await status_msg.edit(f"🎭 **Cipher Elite Math Error**\n\n"
                                     f"❌ **Error:** {str(e)}")
                
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.unpack"))
    @rishabh()
    async def unpack_file(event):
        try:
            if not event.reply_to_msg_id:
                await event.reply("🎭 **Cipher Elite File Unpacker**\n\n"
                                "❌ **Error:** Please reply to a file!\n\n"
                                "**Usage:** Reply to any text file with `.unpack`\n"
                                "**Supported:** .txt, .py, .js, .json, .xml, etc.")
                return
            
            reply_message = await event.get_reply_message()
            
            if not reply_message.document:
                await event.reply("❌ **Cipher Elite Error:** Please reply to a file document!")
                return
            
            status_msg = await event.reply("🎭 **Cipher Elite File Unpacker**\n\n"
                                         "📁 **Processing:** Downloading file...\n"
                                         "🔄 **Status:** Extracting content\n"
                                         "⚡ **Engine:** Advanced File Processor")
            
            # Download file to temporary location
            temp_dir = "temp_cipher_elite"
            os.makedirs(temp_dir, exist_ok=True)
            filename = await reply_message.download_media(file=temp_dir)
            
            try:
                with open(filename, "rb") as f:
                    data = f.read()
                
                # Try to decode as text
                try:
                    text_content = data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text_content = data.decode('latin-1')
                    except:
                        await status_msg.edit("🎭 **Cipher Elite File Unpacker Error**\n\n"
                                             "❌ **Error:** File is not a text file\n"
                                             "💡 **Only text files can be unpacked**")
                        return
                
                # Limit message length for Telegram
                max_length = 4000
                if len(text_content) > max_length:
                    text_content = text_content[:max_length] + "\n\n... (Content truncated due to length limit)"
                
                await status_msg.edit(f"🎭 **Cipher Elite File Unpacked**\n\n"
                                     f"📁 **File:** {reply_message.document.attributes[0].file_name if reply_message.document.attributes else 'Unknown'}\n"
                                     f"📊 **Size:** {len(data)} bytes\n\n"
                                     f"📄 **Content:**\n``````\n\n"
                                     f"🤖 **Powered by Cipher Elite**")
                
            except Exception as e:
                await status_msg.edit(f"🎭 **Cipher Elite File Unpacker Error**\n\n"
                                     f"❌ **Error:** Could not read file content\n"
                                     f"💡 **Make sure it's a valid text file**")
            finally:
                # Cleanup
                if os.path.exists(filename):
                    os.remove(filename)
                
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.pack\s*(.*)"))
    @rishabh()
    async def pack_text(event):
        try:
            filename_input = event.pattern_match.group(1).strip()
            
            if not event.reply_to_msg_id:
                await event.reply("🎭 **Cipher Elite Text Packer**\n\n"
                                "❌ **Error:** Please reply to a text message!\n\n"
                                "**Usage:** Reply to any text with `.pack [filename]`\n"
                                "**Example:** `.pack my_script.py`")
                return
            
            reply_message = await event.get_reply_message()
            
            if not reply_message.text:
                await event.reply("❌ **Cipher Elite Error:** Replied message contains no text!")
                return
            
            # Generate filename
            if filename_input:
                filename = filename_input
            else:
                filename = f"cipher_elite_pack_{int(time.time())}.txt"
            
            status_msg = await event.reply("🎭 **Cipher Elite Text Packer**\n\n"
                                         f"📝 **Creating:** {filename}\n"
                                         f"🔄 **Status:** Packing text content...\n"
                                         f"⚡ **Engine:** Advanced File Generator")
            
            try:
                # Create temporary file
                temp_dir = "temp_cipher_elite"
                os.makedirs(temp_dir, exist_ok=True)
                temp_filepath = os.path.join(temp_dir, filename)
                
                with open(temp_filepath, "w", encoding="utf-8") as f:
                    f.write(reply_message.text)
                
                # Send file
                await event.client.send_file(
                    event.chat_id,
                    temp_filepath,
                    caption=f"🎭 **Cipher Elite Text Packed**\n\n"
                           f"📁 **Filename:** `{filename}`\n"
                           f"📊 **Size:** {len(reply_message.text)} characters\n"
                           f"✅ **Status:** Successfully packed\n"
                           f"🤖 **Powered by Cipher Elite**",
                    reply_to=event.reply_to_msg_id
                )
                
                await status_msg.delete()
                
                # Cleanup
                os.remove(temp_filepath)
                
            except Exception as e:
                await status_msg.edit(f"🎭 **Cipher Elite Text Packer Error**\n\n"
                                     f"❌ **Error:** Could not create file\n"
                                     f"💡 **Please try again**")
                
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.calendar\s*(.*)"))
    @rishabh()
    async def generate_calendar(event):
        try:
            query_input = event.pattern_match.group(1).strip()
            
            if not query_input:
                # Use current month and year
                now = datetime.datetime.now()
                year = now.year
                month = now.month
            else:
                if "/" in query_input:
                    try:
                        month_str, year_str = query_input.split("/")
                        month = int(month_str)
                        year = int(year_str)
                        
                        if month < 1 or month > 12:
                            await event.reply("🎭 **Cipher Elite Calendar Error**\n\n"
                                            "❌ **Error:** Invalid month! Use 1-12\n\n"
                                            "**Usage:** `.calendar 12/2024`")
                            return
                    except ValueError:
                        await event.reply("🎭 **Cipher Elite Calendar**\n\n"
                                        "❌ **Error:** Invalid format!\n\n"
                                        "**Usage:** `.calendar 12/2024`\n"
                                        "**Example:** `.calendar 1/2025`")
                        return
                else:
                    await event.reply("🎭 **Cipher Elite Calendar**\n\n"
                                    "❌ **Error:** Invalid format!\n\n"
                                    "**Usage:** `.calendar 12/2024`\n"
                                    "**Or use:** `.calendar` for current month")
                    return
            
            status_msg = await event.reply("🎭 **Cipher Elite Calendar Generator**\n\n"
                                         f"📅 **Generating:** {month}/{year}\n"
                                         f"🔄 **Status:** Creating calendar...\n"
                                         f"⚡ **Engine:** Advanced Calendar System")
            
            try:
                # Simple text calendar (since we don't have the image creation function)
                import calendar
                cal = calendar.month(year, month)
                month_name = calendar.month_name[month]
                
                calendar_text = f"🎭 **Cipher Elite Calendar**\n\n"
                calendar_text += f"📅 **{month_name} {year}**\n\n"
                calendar_text += f"``````\n\n"
                calendar_text += f"✅ **Generated successfully**\n"
                calendar_text += f"🤖 **Powered by Cipher Elite**"
                
                await status_msg.edit(calendar_text)
                
            except Exception as e:
                await status_msg.edit(f"🎭 **Cipher Elite Calendar Error**\n\n"
                                     f"❌ **Error:** Could not generate calendar\n"
                                     f"💡 **Please check the month/year values**")
                
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**\n\n"
                            f"❌ **Error:** {str(e)}")
