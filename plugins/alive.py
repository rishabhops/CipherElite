from telethon import version, events
from datetime import datetime
import random
from plugins.bot import add_handler, CMD_LIST
from utils.utils import CipherElite
from utils.decorators import rishabh
from config.config import Config

START_TIME = datetime.now()
def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time
    
# Collection of alive message styles
ALIVE_STYLES = [
    """⚡ 𝘾𝙄𝙋𝙃𝙀𝙍 𝙀𝙇𝙄𝙏𝙀 𝙎𝙔𝙎𝙏𝙀𝙈 ⚡\n\n▰▱▰▱▰▱▰▱▰▱▰▱▰▱\n➺ 𝙈𝘼𝙎𝙏𝙀𝙍: {name}\n➺ 𝙑𝙀𝙍𝙎𝙄𝙊𝙉: 1.0\n➺ 𝙏𝙀𝙇𝙀𝙏𝙃𝙊𝙉: {telethon}\n▰▱▰▱▰▱▰▱▰▱▰▱▰▱\n\n⚔️ 𝙋𝙇𝙐𝙂𝙄𝙉𝙎: {plugins}\n⚔️ 𝙐𝙋𝙏𝙄𝙈𝙀: {uptime}\n⚔️ 𝘽𝙍𝘼𝙉𝘾𝙃: MASTER\n\n▰▱▰▱ ELITE NETWORK ▰▱▰▱""",
    
    """╔══『 CIPHER ELITE 』══╗\n\n◈ CODENAME: {name}\n◈ VERSION: [1.0]\n◈ TELETHON: [{telethon}]\n\n▣ PLUGINS: {plugins}\n▣ UPTIME: {uptime}\n▣ STATUS: OPERATIONAL\n\n╚══『 ELITE FORCE 』══╝""",
    
    # Add all other alive styles here
]

# Collection of ping message styles
PING_STYLES = [
    """⚡ 𝙋𝙄𝙉𝙂 𝙎𝙏𝘼𝙏𝙐𝙎 ⚡\n\n▰▱▰▱▰▱▰▱▰▱▰▱▰▱\n➺ 𝙎𝙋𝙀𝙀𝘿: `{speed}ms`\n➺ 𝙐𝙋𝙏𝙄𝙈𝙀: `{uptime}`\n▰▱▰▱▰▱▰▱▰▱▰▱▰▱""",
    
    """╔══『 PING STATUS 』══╗\n\n◈ SPEED: [{speed}ms]\n◈ UPTIME: [{uptime}]\n\n╚══『 CIPHER ELITE 』══╝""",
    
    # Add all other ping styles here
]

def init(client_instance):
    commands = [".alive - Check bot status", ".ping - Check response time"]
    description = "Shows bot's alive status with random styles 🔥"
    add_handler("alive", commands, description)

async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.alive"))
    @rishabh()
    async def alive(event):
        uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
        
        # Select random alive style
        alive_message = random.choice(ALIVE_STYLES).format(
            name=event.sender.first_name,
            telethon=version.__version__,
            plugins=len(CMD_LIST),
            uptime=uptime
        )
        
        await event.reply(alive_message)

    @CipherElite.on(events.NewMessage(pattern=r"\.ping"))
    @rishabh()
    async def ping(event):
        start = datetime.now()
        msg = await event.reply("**Pong!**")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
        
        # Select random ping style
        ping_message = random.choice(PING_STYLES).format(
            speed=ms,
            uptime=uptime
        )
        
        await msg.edit(ping_message)
        