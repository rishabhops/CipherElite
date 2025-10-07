# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    raid
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
from telethon import events, utils
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
import asyncio
import random
import time
import re

CIPHER_ELITE_OWNER = 5470956337

active_raids = {
    "users": {},
    "stats": {},
    "start_time": {},
    "language": {}
}

RAID_BANNER = """
🎭 ═══════════════════════════════════════ 🎭
      𝗖𝗜𝗣𝗛𝗘𝗥 𝗘𝗟𝗜𝗧𝗘 𝗥𝗔𝗜𝗗 𝗦𝗬𝗦𝗧𝗘𝗠 
🎭 ═══════════════════════════════════════ 🎭
"""

HINDI_RAIDS = [
    "🎭 Sab batain bhul jha Mari pakad ke jhull jha 🤣",
    "🔥 TERI MAA KI CHUT ME GHUTKA KHAAKE THOOK DUNGA 🤣",
    "⚔️ TERE BEHEN K CHUT ME CHAKU DAAL KAR CHUT KA KHOON KAR DUGA",
    "🎯 TERI VAHEEN NHI HAI KYA? 9 MAHINE RUK SAGI VAHEEN DETA HU 🤣",
    "🔥 TERE PURE KHANDAN KI AURATO KO RANDI BANA DUNGA 🔥",
    "💰 TERI MAA KO RANDI KHANE ME BECH DUNGA 💰",
    "🎭 उदास क्यों रहते हो तन्हा शाम की तरह आओ मेरा land चूसो देसी आम की तरह",
    "🗡️ TERI BEHEN KA BHOSDA FAAD KE RAKJ DUNGA 🗡️",
    "🐘 TERI MAA KE BHOSDE ME HATHI KA LUND 🐘",
    "🧪 TERI BEHEN KI CHUT ME ZEHER LAGA DUNGA 🧪",
    "💃 TERI MAA KO MERE GHAR PE NANGA NACH KARNA PADEGA 💃",
    "🔨 TERI BEHEN KI GAAND ME SARIYA DAAL DUNGA 🔨",
    "👅 TERE PURE KHANDAN KO MERE TATTE CHATNA PADEGA 👅",
    "💣 TERI MAA KI CHUT ME NUCLEAR BOMB 💣",
    "🧨 TERI BEHEN KE BHOSDE ME DYNAMITE 🧨",
    "🎥 TERI MAA KO JOHNNY SINS SE CHUDWA DUNGA 🎥",
    "👞 TERI FAMILY KO MERE JUTTE CHATNE PADENGE 👞",
    "🔪 TERI MAA KA BHOSDA FAAD DUNGA 🔪",
    "🚀 TERI BEHEN KI CHUT ME ROCKET LAUNCHER 🚀",
    "💼 TERE PURE KHANDAN KO MERE PAAS RANDI BANKE KAAM KARNA PADEGA 💼",
    "🏪 TERI MAA KO GB ROAD PE BECH DUNGA 🏪",
    "🏠 TERI BEHEN KO KOTHE PE BITHA DUNGA 🏠",
    "🚛 TERI MAA KI CHUT ME TANK GHUSA DUNGA 🚛",
    "🤺 TERE BAAP KO TERE SAMNE CHOD DUNGA 🤺",
    "🚁 TERI MAA KE BHOSDE ME HELICOPTER KA PANKHA 🚁",
    "🚇 TERI BEHEN KI CHUT ME METRO CHALWA DUNGA 🚇",
    "👥 TERI MAA KO TERE DOSTO SE CHUDWA DUNGA 👥",
    "🔫 TERI BEHEN KI CHUT ME BANDOOK KI GOLI 🔫",
    "🐕 TERI MAA KO KUTTO SE CHUDWA DUNGA 🐕",
    "👯 TERE PURE KHANDAN KI AURATO KO NANGI KARWA DUNGA 👯",
    "💃 TERI BEHEN KO RANDI BAZAR ME NANGA NACHWA DUNGA 💃",
    "🐷 TERI MAA KE BHOSDE ME SUWAR KA LUND 🐷",
    "🏃 TERE BAAP KO BECH DUNGA CHAKLO PE 🏃",
    "💳 TERI BEHEN KE BHOSDE ME CREDIT CARD 💳",
    "🔧 TERI MAA KI CHUT ME SCREW DRIVER 🔧",
    "🕺 TERE PURE KHANDAN KO MERE LUND PE NACHWA DUNGA 🕺",
    "🏏 TERI BEHEN KI CHUT ME LATHI DAAL DUNGA 🏏",
    "🛏️ TERI MAA KO BISTAR PE LETA DUNGA 🛏️",
    "🔨 TERE BEHEN KE BHOSDE ME HATODA 🔨",
    "🐓 TERI MAA KI CHUT ME MURGA 🐓",
    "🎋 TERE BAAP KI GAAND ME DANDA 🎋",
    "💣 TERI BEHEN KI CHUT ME PIPE BOMB 💣",
    "📱 TERI MAA KO VIRAL KAR DUNGA 📱",
    "🙏 TERE PURE KHANDAN KO MERE PAAS BHIKARI BANKE AANA PADEGA 🙏",
    "🌟 TERI BEHEN KI CHUT ME LASER BEAM 🌟",
    "🛢️ TERI MAA KE BHOSDE ME CYLINDER 🛢️",
    "🕴️ TERE BAAP KO TERE SAMNE NACHWA DUNGA 🕴️",
    "📸 TERI BEHEN KO WEBCAM PE NACHWA DUNGA 📸",
    "🚜 TERI MAA KI CHUT ME BULLDOZER 🚜",
    "👑 TERE PURE KHANDAN KO MERE LUND KI DAS BANA DUNGA 👑",
    "🚀 TERI BEHEN KI GAAND ME ROCKET 🚀",
    "🎥 TERI MAA KO PORNHUB PE VIRAL KAR DUNGA 🎥"
]

ENGLISH_RAIDS = [
    "🔥 I'LL DEMOLISH YOUR FAMILY'S ENTIRE EXISTENCE 🔥",
    "💰 YOUR MOM BECOMES MY ETERNAL SLAVE 💰",
    "🗡️ I'LL SHRED YOUR SISTER'S LIFE TO PIECES 🗡️",
    "🐘 YOUR MOM FACES THE WRATH OF GIANTS 🐘",
    "🧪 I'LL POISON YOUR SISTER'S ENTIRE BLOODLINE 🧪",
    "💃 YOUR MOM DANCES NAKED AT MY COMMAND 💃",
    "🔨 I'LL PIERCE YOUR FAMILY WITH STEEL RODS 🔨",
    "👅 YOUR BLOODLINE SERVES AS MY FOOTREST 👅",
    "💣 NUCLEAR DEVASTATION IN YOUR MOM'S WORLD 💣",
    "🧨 DYNAMITE EXPLOSION IN YOUR SISTER'S LIFE 🧨",
    "🎥 YOUR MOM STARS IN MY ADULT EMPIRE 🎥",
    "👞 YOUR FAMILY LICKS MY BOOTS CLEAN 👞",
    "📜 I NOW OWN YOUR ENTIRE GENERATION 📜",
    "🗑️ YOUR EXISTENCE GETS WIPED FROM EARTH 🗑️",
    "🌳 YOUR FAMILY TREE BURNS TO ASHES 🌳",
    "🏗️ I'LL CRUSH YOUR FAMILY'S REMAINING HONOR 🏗️",
    "🚀 MISSILE STRIKE ON YOUR SISTER'S WORLD 🚀",
    "💼 YOUR FAMILY BECOMES MY SLAVE DYNASTY 💼",
    "🏪 SELLING YOUR MOM TO THE UNDERGROUND 🏪",
    "🏠 YOUR SISTER JOINS THE DARK BUSINESS 🏠",
    "🚛 TANK CRUSHING YOUR MOM'S EXISTENCE 🚛",
    "🤺 DESTROYING YOUR DAD'S REMAINING PRIDE 🤺",
    "🚁 HELICOPTER ASSAULT ON YOUR MOM'S LIFE 🚁",
    "🚇 TRAIN WRECK THROUGH YOUR SISTER'S WORLD 🚇",
    "👥 YOUR MOM SERVICES ALL MY SOLDIERS 👥",
    "🔫 BULLET STORM IN YOUR SISTER'S PARADISE 🔫",
    "🐕 YOUR MOM FACES THE BEAST BATTALION 🐕",
    "👯 STRIPPING YOUR FAMILY WOMEN NAKED 👯",
    "💃 YOUR SISTER DANCES IN HELL'S CHAMBER 💃",
    "🐷 YOUR MOM MEETS THE WILD BEASTS 🐷",
    "🏃 SELLING YOUR DAD TO THE UNDERGROUND 🏃",
    "💳 CREDIT CARD MAXED ON YOUR SISTER 💳",
    "🔧 MECHANICAL TORTURE FOR YOUR MOM 🔧",
    "🕺 YOUR FAMILY DANCES ON MY COMMAND 🕺",
    "🏏 POLICE BATON IN YOUR SISTER'S LIFE 🏏",
    "🛏️ YOUR MOM ON MY EMPEROR'S BED 🛏️",
    "🔨 HAMMER TIME FOR YOUR SISTER 🔨",
    "🐓 COCK FIGHT IN YOUR MOM'S WORLD 🐓",
    "🎋 BAMBOO STRIKE FOR YOUR DAD 🎋",
    "💣 PIPE BOMB IN YOUR SISTER'S EXISTENCE 💣",
    "📱 YOUR MOM GOES VIRAL WORLDWIDE 📱",
    "🙏 YOUR FAMILY BEGS AT MY DOORSTEP 🙏",
    "🌟 LASER BEAM THROUGH YOUR SISTER 🌟",
    "🛢️ GAS CHAMBER FOR YOUR MOM 🛢️",
    "🕴️ YOUR DAD DANCES TO MY TUNES 🕴️",
    "📸 YOUR SISTER ON WORLDWIDE WEBCAM 📸",
    "🚜 BULLDOZER CRUSHING YOUR MOM 🚜",
    "👑 YOUR FAMILY SERVES MY EMPIRE 👑",
    "🚀 ROCKET LAUNCH IN YOUR SISTER'S WORLD 🚀",
    "🎥 YOUR MOM TRENDING ON ADULT SITES 🎥"
]

ACTIVATION_MESSAGE = """
🎭 **CIPHER ELITE RAID ACTIVATED** 🎭

🎯 **Target:** {}
🆔 **Target ID:** `{}`
🗣️ **Language:** {}
⚡ **Deployment:** Instant Reply System
🛡️ **Protection:** Elite Shield Active
✅ **Status:** Operational

🤖 **Powered by CipherElite**
"""

def init(client_instance):
    commands = [
        ".replyraid [hindi/english] [username/userid] - 🎭 Activate raid (reply or use username/ID)",
        ".dreplyraid - ❌ Deactivate active raid system", 
        ".raidinfo - 📊 Display raid statistics and data"
    ]
    description = "🎭 Cipher Elite Raid System - Advanced bilingual raiding with flexible targeting"
    add_handler("raid", commands, description)

async def parse_user_target(event, args):
    """Parse and retrieve user entity from reply, username, or ID"""
    user = None
    
    # Check if replying to a message
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user = await event.client.get_entity(reply.sender_id)
        return user
    
    # Extract username or ID from arguments
    # Remove language keywords first
    target_str = args.replace('hindi', '').replace('english', '').strip()
    
    if not target_str:
        return None
    
    try:
        # Check if it's a numeric ID
        if target_str.isdigit():
            user_id = int(target_str)
            user = await event.client.get_entity(user_id)
        # Check if it's a username (with or without @)
        else:
            # Remove @ if present
            username = target_str.lstrip('@')
            user = await event.client.get_entity(username)
            
    except ValueError as e:
        # Entity not found
        raise ValueError(f"Could not find user: {target_str}")
    except Exception as e:
        raise Exception(f"Error getting user entity: {str(e)}")
    
    return user

@CipherElite.on(events.NewMessage)
async def handle_all_messages(event):
    if event.sender_id in active_raids["users"]:
        try:
            sender = await event.get_sender()
            name = sender.first_name if sender and sender.first_name else "Target"
            
            response = f"[{name}](tg://user?id={event.sender_id}) "
            
            lang = active_raids["language"].get(event.sender_id, "english")
            messages = HINDI_RAIDS if lang == "hindi" else ENGLISH_RAIDS
            
            response += random.choice(messages)
            
            await event.reply(response)
            active_raids["stats"][event.sender_id] += 1
            
        except Exception as e:
            lang = active_raids["language"].get(event.sender_id, "english")
            response = f"[User](tg://user?id={event.sender_id}) "
            response += random.choice(HINDI_RAIDS if lang == "hindi" else ENGLISH_RAIDS)
            await event.reply(response)
            active_raids["stats"][event.sender_id] += 1

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r".replyraid(?: |$)(.*)"))
    @rishabh()
    async def activate_raid(event):
        try:
            args = event.pattern_match.group(1).lower()
            lang = "hindi" if "hindi" in args else "english"
            
            # Try to get user from reply or arguments
            user = await parse_user_target(event, args)
            
            if not user:
                await event.reply("🎭 **Cipher Elite Raid System**"
                                "❌ **Error:** No target specified!"
                                "💡 **Usage Options:**"
                                "• Reply to user's message: `.replyraid hindi`"
                                "• Use username: `.replyraid hindi @username`"
                                "• Use user ID: `.replyraid english 123456789`"
                                "🗣️ **Languages:** `hindi` or `english` (default: english)")
                return
            
            # Check if target is the bot owner
            if user.id == CIPHER_ELITE_OWNER:
                await event.reply("🎭 **Cipher Elite Security Protocol**"
                                "🛡️ **Access Denied:** You Cannot target my developer Rishabh"
                                "🔒 **Security Level:** Maximum Protection Active"
                                "⚠️ **Status:** Operation Blocked by Elite Shield")
                return
            
            # Check if already raiding this user
            if user.id in active_raids["users"]:
                await event.reply("🎭 **Cipher Elite Raid System**"
                                f"⚠️ **Already raiding:** {utils.get_display_name(user)}"
                                f"💡 **Tip:** Use `.dreplyraid` to stop the current raid first")
                return
            
            # Activate raid
            active_raids["users"][user.id] = True
            active_raids["stats"][user.id] = 0
            active_raids["start_time"][user.id] = time.time()
            active_raids["language"][user.id] = lang
            
            user_mention = f"[{utils.get_display_name(user)}](tg://user?id={user.id})"
            
            activation_msg = RAID_BANNER + ACTIVATION_MESSAGE.format(
                user_mention,
                user.id,
                lang.upper()
            )
            
            await event.reply(activation_msg)
            
        except ValueError as e:
            await event.reply(f"🎭 **Cipher Elite System Error**"
                            f"❌ **Error:** {str(e)}"
                            f"💡 **Tip:** Make sure the username/ID exists and is accessible")
        except Exception as e:
            await event.reply(f"🎭 **Cipher Elite System Error**"
                            f"❌ **Error:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r".raidinfo"))
    @rishabh()
    async def raid_info(event):
        try:
            info = f"{RAID_BANNER}🎭 **ACTIVE RAID STATISTICS**"
            
            if not active_raids["users"]:
                return await event.reply("🎭 **Cipher Elite Raid Monitor**"
                                       "❌ **No active raids detected**"
                                       "💡 **Use `.replyraid` to start raiding**"
                                       "📊 **All systems are idle**")
                
            for user_id in active_raids["users"]:
                try:
                    user = await event.client.get_entity(user_id)
                    duration = time.time() - active_raids["start_time"][user_id]
                    hits = active_raids["stats"][user_id]
                    lang = active_raids["language"][user_id]
                    
                    info += f"🎯 **Target:** {utils.get_display_name(user)}"
                    info += f"🗣️ **Language:** {lang.upper()}"
                    info += f"💥 **Hits Delivered:** {hits}"
                    info += f"⏱️ **Duration:** {int(duration)}s"
                    info += f"🆔 **User ID:** `{user_id}`"
                    info += f"🔥 **Status:** Active Raid"
                except Exception:
                    info += f"🎯 **Target ID:** `{user_id}`"
                    info += f"⚠️ **Status:** Entity unavailable"
                
            info += f"🤖 **Powered by CipherElite Raid System**"
            await event.reply(info)
        except Exception as e:
            await event.reply(f"🎭 **Raid Info Error:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r".dreplyraid(?: |$)(.*)"))
    @rishabh()
    async def deactivate_raid(event):
        try:
            args = event.pattern_match.group(1).strip()
            user_id = None
            
            # Check if replying to a message
            if event.reply_to_msg_id:
                reply = await event.get_reply_message()
                user_id = reply.sender_id
            # Check if username/ID provided
            elif args:
                try:
                    if args.isdigit():
                        user_id = int(args)
                    else:
                        username = args.lstrip('@')
                        user = await event.client.get_entity(username)
                        user_id = user.id
                except Exception:
                    await event.reply("🎭 **Cipher Elite Raid System**"
                                    "❌ **Error:** Could not find specified user"
                                    "💡 **Check username/ID and try again**")
                    return
            
            if not user_id:
                await event.reply("🎭 **Cipher Elite Raid Deactivation**"
                                "❌ **Error:** No target specified!"
                                "💡 **Usage Options:**"
                                "• Reply to user's message: `.dreplyraid`"
                                "• Use username: `.dreplyraid @username`"
                                "• Use user ID: `.dreplyraid 123456789`")
                return
            
            if user_id in active_raids["users"]:
                final_hits = active_raids["stats"][user_id]
                duration = int(time.time() - active_raids["start_time"][user_id])
                
                del active_raids["users"][user_id]
                del active_raids["stats"][user_id]
                del active_raids["start_time"][user_id]
                del active_raids["language"][user_id]
                
                await event.reply("🎭 **CIPHER ELITE RAID DEACTIVATED** 🎭"
                                f"✅ **Successfully Stopped**"
                                f"💥 **Total Hits:** {final_hits}"
                                f"⏱️ **Duration:** {duration}s"
                                f"🛡️ **Elite Shield:** Restored"
                                f"🤖 **Powered by CipherElite**")
            else:
                await event.reply("🎭 **Cipher Elite Raid System**"
                                "❌ **No active raid found for this user**"
                                "💡 **Target is not currently being raided**")
                                
        except Exception as e:
            await event.reply(f"🎭 **Deactivation Error:** {str(e)}")
