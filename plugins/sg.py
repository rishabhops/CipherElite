import asyncio
import re
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl import types
from telethon.tl.functions.contacts import UnblockRequest as unblock

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        "sg <username/userid/reply> - Get name history",
        "sgu <username/userid/reply> - Get username history"
    ]
    description = "Fetch user's name or username history"
    add_handler("sangmata", commands, description)

def sanga_seperator(responses):
    names = []
    usernames = []
    for response in responses:
        response = response.strip()
        # Broader matching for name history
        if any(keyword in response.lower() for keyword in ["name", "first name", "previous name", "changed to"]):
            names.append(response)
        # Broader matching for username history
        if any(keyword in response.lower() for keyword in ["username", "previous username"]):
            usernames.append(response)
    return names, usernames

@CipherElite.on(events.NewMessage(pattern=r"^(?i)sg(u)?$", outgoing=True))
@rishabh()
async def sangmata_cmd(event):
    try:
        cmd = event.pattern_match.group(1)  # 'u' for sgu, None for sg
        
        # Get user input (username, user ID, or reply)
        if event.reply_to_msg_id:
            reply = await event.get_reply_message()
            user = reply.sender_id
        else:
            message_text = event.message.text
            parts = message_text.split(maxsplit=1)
            user = parts[1] if len(parts) > 1 else None

        if not user:
            return await event.reply("❌ Please provide a username, user ID, or reply to a message!")

        try:
            userinfo = await event.client.get_entity(user)
        except Exception as e:
            return await event.reply(f"❌ Could not find the specified user! Error: {str(e)}")

        if not isinstance(userinfo, types.User):
            return await event.reply("❌ Invalid user! Only user accounts are supported.")

        async with event.client.conversation("@SangMata_beta_bot") as conv:
            try:
                await conv.send_message(str(userinfo.id))
            except YouBlockedUserError:
                await event.client(unblock("SangMata_beta_bot"))
                await conv.send_message(str(userinfo.id))

            responses = []
            # Increase timeout to 5 seconds to capture more responses
            while True:
                try:
                    response = await conv.get_response(timeout=5)
                    responses.append(response.text)
                except asyncio.TimeoutError:
                    break
            await event.client.send_read_acknowledge(conv.chat_id)

        # Debug: Log raw responses (optional, remove in production)
        print(f"Raw responses from SangMata: {responses}")

        if not responses:
            return await event.reply("❌ Bot couldn't fetch results. Try again later.")

        if "No records found" in "".join(responses):
            return await event.reply("⚠️ No history found for this user.")

        names, usernames = sanga_seperator(responses)
        
        user_name = f"{userinfo.first_name} {userinfo.last_name or ''}".strip() or "Unknown User"
        
        if cmd == "u":
            output = f"**➜ Username History for {user_name}:**\n" + "\n".join(usernames) if usernames else "No username history found"
        else:
            output = f"**➜ Name History for {user_name}:**\n" + "\n".join(names) if names else "No name history found"
        
        await event.reply(output)

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
