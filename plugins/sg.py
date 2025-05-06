from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl import types
from telethon.tl.functions.contacts import UnblockRequest as unblock
import asyncio

from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    commands = [
        ".sg <username/userid/reply> - Get name history",
        ".sgu <username/userid/reply> - Get username history"
    ]
    description = "Fetch user's name or username history"
    add_handler("sangmata", commands, description)

def sanga_seperator(responses):
    names = []
    usernames = []
    for response in responses:
        if "Previous name" in response or "First name" in response:
            names.append(response.strip())
        if "Previous username" in response or "Username" in response:
            usernames.append(response.strip())
    return names, usernames

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.sg(u)?"))
    @rishabh()
    async def sangmata_cmd(event):
        try:
            cmd = event.pattern_match.group(1)
            
            if event.reply_to_msg_id:
                reply = await event.get_reply_message()
                user = reply.sender_id
            else:
                user_input = event.pattern_match.group(0).split(maxsplit=1)
                user = user_input[1] if len(user_input) > 1 else None

            if not user:
                return await event.reply("❌ Please provide a username, user ID, or reply to a message!")

            try:
                userinfo = await event.client.get_entity(user)
            except Exception:
                return await event.reply("❌ Could not find the specified user!")

            if not isinstance(userinfo, types.User):
                return await event.reply("❌ Invalid user!")

            async with event.client.conversation("@SangMata_beta_bot") as conv:
                try:
                    await conv.send_message(str(userinfo.id))
                except YouBlockedUserError:
                    await event.client(unblock("SangMata_beta_bot"))
                    await conv.send_message(str(userinfo.id))

                responses = []
                while True:
                    try:
                        response = await conv.get_response(timeout=2)
                        responses.append(response.text)
                    except asyncio.TimeoutError:
                        break
                await event.client.send_read_acknowledge(conv.chat_id)

            if not responses:
                return await event.reply("❌ Bot couldn't fetch results")
            
            if "No records found" in "".join(responses):
                return await event.reply("⚠️ No history found for this user")

            names, usernames = sanga_seperator(responses)
            
            user_name = f"{userinfo.first_name} {userinfo.last_name or ''}".strip()
            
            if cmd == "u":
                output = f"**➜ Username History for {user_name}:**\n" + "\n".join(usernames) if usernames else "No username history found"
            else:
                output = f"**➜ Name History for {user_name}:**\n" + "\n".join(names) if names else "No name history found"
            
            await event.reply(output)

        except Exception as e:
            await event.reply(f"❌ Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.sgu"))
    async def username_history(event):
        await sangmata_cmd(event)