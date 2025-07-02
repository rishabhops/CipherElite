# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    alive
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

import io
import re
import subprocess
import sys
import traceback
import requests
import bs4
from speedtest import Speedtest
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

def init(client_instance):
    """
    Initialize the plugin with command descriptions.
    """
    commands = [
        ".eval <python code> - Execute Python code and get results. Use with caution!",
        ".exec <linux command> - Execute Linux command and get results. Use with caution!",
        ".shell <shell script> - Execute shell script and get results. Use with caution!",
        ".fext <file extension> - Get details of a file extension.",
        ".pypi <package name> - Get details of a package from PyPI.",
        ".speedtest - Test server and client speed."
    ]
    description = "Plugin to execute Python, Linux, and shell scripts, fetch file extension and PyPI package details, and run speed tests."
    add_handler("eval", commands, description)

async def aexec(code, client, event):
    """
    Helper function to execute Python code asynchronously.
    """
    exec(
        "async def __aexec(client, event): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, event)

async def register_commands():
    """
    Register all commands for the plugin.
    """
    @CipherElite.on(events.NewMessage(pattern=r"\.eval(?:\s+(.+))?"))
    @rishabh()
    async def eval_handler(event):
        """
        Execute Python code and return the result.
        """
        try:
            code = event.pattern_match.group(1)
            if not code:
                await event.reply("No Python code provided!")
                return

            reply_to = event.reply_to_msg_id or event.message.id
            elite = await event.reply("`Running...`")

            old_stderr = sys.stderr
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()
            redirected_error = sys.stderr = io.StringIO()
            stdout, stderr, exc = None, None, None

            try:
                await aexec(code, event.client, event)
            except Exception:
                exc = traceback.format_exc()

            stdout = redirected_output.getvalue()
            stderr = redirected_error.getvalue()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            evaluation = exc or stderr or stdout or "Success"
            heading = f"**𝖤𝗏𝖺𝗅:**\n```python\n{code}```\n\n"
            output = f"**𝖮𝗎𝗍𝗉𝗎𝗍:**\n`{evaluation.strip()}`"
            final_output = heading + output

            try:
                await event.client.send_message(event.chat_id, final_output, reply_to=reply_to)
            except Exception as e:
                with io.BytesIO(str.encode(output)) as out_file:
                    out_file.name = "eval.txt"
                    await event.client.send_file(event.chat_id, out_file, caption=heading, reply_to=reply_to)

            await elite.delete()
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.(?:exec|term)(?:\s+(.+))?"))
    @rishabh()
    async def exec_handler(event):
        """
        Execute Linux command and return the result.
        """
        try:
            cmd = event.pattern_match.group(1)
            if not cmd:
                await event.reply("No Linux command provided!")
                return

            reply_to = event.reply_to_msg_id or event.message.id
            elite = await event.reply("`Running...`")

            if "\n" in cmd:
                code = cmd.split("\n")
                output = ""
                for x in code:
                    shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
                    try:
                        process = subprocess.Popen(
                            shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                        output += f"**{x}**\n{process.stdout.read().decode('utf-8')}\n"
                    except Exception as err:
                        output += f"**Error:** `{str(err)}`\n"
            else:
                shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", cmd)
                shell = [s.replace('"', "") for s in shell]
                try:
                    process = subprocess.Popen(
                        shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    output = process.stdout.read().decode("utf-8")
                except Exception as err:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    errors = traceback.format_exception(exc_type, exc_obj, exc_tb)
                    await elite.edit(f"**Error:**\n`{''.join(errors)}`")
                    return

            if not output.strip():
                await elite.edit(f"**𝖮𝗎𝗍𝗉𝗎𝗍:** __𝖭𝗈 𝗈𝗎𝗍𝗉𝗎𝗍!__")
                return

            try:
                await event.client.send_message(
                    event.chat_id,
                    f"**{event.client.me.id}@CipherElite:~$** `{cmd}`\n\n**𝖮𝗎𝗍𝗉𝗎𝗍:**\n```\n{output}```",
                    reply_to=reply_to
                )
            except Exception:
                with io.BytesIO(str.encode(output)) as out_file:
                    out_file.name = "exec.txt"
                    await event.client.send_file(
                        event.chat_id,
                        out_file,
                        caption=f"**{event.client.me.id}@CipherElite:~$** `{cmd}`",
                        reply_to=reply_to
                    )

            await elite.delete()
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.(?:sh|shell)(?:\s+(.+))?"))
    @rishabh()
    async def shell_handler(event):
        """
        Execute shell script and return the result.
        """
        try:
            code = event.pattern_match.group(1)
            if not code:
                await event.reply("No shell script provided!")
                return

            reply_to = event.reply_to_msg_id or event.message.id
            elite = await event.reply("`Executing...`")

            result = subprocess.run(code, shell=True, capture_output=True, text=True)
            output = (result.stdout + result.stderr).strip()
            heading = f"**𝖲𝗁𝖾𝗅𝗅:**\n```sh\n{code}```\n\n"
            output = f"**𝖮𝗎𝗍𝗉𝗎𝗍:**\n`{output}`"
            final_output = heading + output

            try:
                await event.client.send_message(event.chat_id, final_output, reply_to=reply_to)
            except Exception:
                with io.BytesIO(str.encode(output)) as out_file:
                    out_file.name = "elite.txt"
                    await event.client.send_file(event.chat_id, out_file, caption=heading, reply_to=reply_to)

            await elite.delete()
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.fext(?:\s+(.+))?"))
    @rishabh()
    async def fext_handler(event):
        """
        Get details of a file extension.
        """
        try:
            ext = event.pattern_match.group(1)
            if not ext:
                await event.reply("No file extension provided!")
                return

            elite = await event.reply("`Getting information...`")
            BASE_URL = "https://www.fileext.com/file-extension/{0}.html"
            response = requests.get(BASE_URL.format(ext))
            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.content, "html.parser")
                details = soup.find_all("td", {"colspan": "3"})[-1].text
                await elite.edit(f"**𝖥𝗂𝗅𝖾 𝖤𝗑𝗍𝖾𝗇𝗍𝗂𝗈𝗇:** `{ext}`\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:**\n`{details}`")
            else:
                await elite.edit(f"**𝖥𝗂𝗅𝖾 𝖤𝗑𝗍𝖾𝗇𝗍𝗂𝗈𝗇:** `{ext}`\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:**\n`Not Found`")
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.pypi(?:\s+(.+))?"))
    @rishabh()
    async def pypi_handler(event):
        """
        Get details of a PyPI package.
        """
        try:
            package = event.pattern_match.group(1)
            if not package:
                await event.reply("No package name provided!")
                return

            elite = await event.reply("`Getting information...`")
            BASE_URL = "https://pypi.org/pypi/{0}/json"
            response = requests.get(BASE_URL.format(package))
            if response.status_code == 200:
                data = response.json()
                info = data["info"]
                name = info["name"]
                url = info["package_url"]
                version = info["version"]
                summary = info["summary"]
                await elite.edit(f"**𝖯𝖺𝖼𝗄𝖺𝗀𝖾:** [{name}]({url}) (`{version}`)\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:** `{summary}`")
            else:
                await elite.edit(f"**𝖯𝖺𝖼𝗄𝖺𝗀𝖾:** `{package}`\n\n**𝖣𝖾𝗍𝖺𝗂𝗅𝗌:** `Not Found`")
        except Exception as e:
            await event.reply(f"Error: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.speedtest"))
    @rishabh()
    async def speedtest_handler(event):
        """
        Test server and client speed.
        """
        try:
            elite = await event.reply("`Testing speed...`")
            speed = Speedtest()
            speed.get_best_server()
            await elite.edit("`Calculating download speed...`")
            speed.download()
            await elite.edit("`Calculating upload speed...`")
            speed.upload()
            await elite.edit("`Finishing up...`")
            speed.results.share()
            result = speed.results.dict()

            form = """**𝖲𝗉𝖾𝖾𝖽𝖳𝖾𝗌𝗍 𝖱𝖾𝗌𝗎𝗅𝗍𝗌 🍀**

**✧ 𝖨𝖲𝖯:** `{0}, {1}` 
**✧ 𝖯𝗂𝗇𝗀:** `{2}`
**✧ 𝖲𝖾𝗋𝗏𝖾𝗋:** `{3}, {4}`
**✧ 𝖲𝗉𝗈𝗇𝗌𝗈𝗋:** `{5}`
"""
            await event.client.send_file(
                event.chat_id,
                result["share"],
                caption=form.format(
                    result["client"]["isp"],
                    result["client"]["country"],
                    result["ping"],
                    result["server"]["name"],
                    result["server"]["country"],
                    result["server"]["sponsor"],
                ),
                reply_to=event.reply_to_msg_id or event.message.id
            )
            await elite.delete()
        except Exception as e:
            await event.reply(f"Error: {str(e)}")
