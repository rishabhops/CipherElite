# =============================================================================
#  CipherElite Assistant Bot Plugin
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
#  What it does:
#    a safe maths calculator and a multi-endpoint translator.
#
#  Merged from calculator.py, translator.py so related commands live in one file and share a single
#  init_bot_plugin().
#
#  Thank you for respecting open-source software!
# =============================================================================

import ast
import math
import operator as op
import aiohttp
from telethon import Button, events

# ---------------------------------------------------------------------------
#  calculator.py — module level
# ---------------------------------------------------------------------------

_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}


_FUNCS = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "sqrt": math.sqrt, "cbrt": lambda x: x ** (1 / 3),
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "log10": math.log10, "log2": math.log2,
    "exp": math.exp, "floor": math.floor, "ceil": math.ceil,
    "factorial": math.factorial, "gcd": math.gcd, "degrees": math.degrees,
    "radians": math.radians, "pow": pow,
}


_CONSTS = {
    "pi": math.pi, "e": math.e, "tau": math.tau, "inf": math.inf,
}


MAX_EXPONENT = 1000


MAX_RESULT = 1e18


class CalcError(ValueError):
    """Raised for anything the evaluator refuses to compute."""


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise CalcError("only numbers are allowed")

    # Python 3.7 parses -5 as UnaryOp(USub, 5); 3.8+ folds it into a Constant.
    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.UAdd):
            return +_eval(node.operand)
        if isinstance(node.op, ast.USub):
            return -_eval(node.operand)
        raise CalcError("unsupported unary operator")

    if isinstance(node, ast.BinOp):
        func = _BIN_OPS.get(type(node.op))
        if func is None:
            raise CalcError("unsupported operator")
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise CalcError(f"exponent too large (max {MAX_EXPONENT})")
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
            raise CalcError("division by zero")
        try:
            return func(left, right)
        except (ValueError, OverflowError) as e:
            raise CalcError(str(e)) from None

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise CalcError("only plain function calls are allowed")
        name = node.func.id
        func = _FUNCS.get(name)
        if func is None:
            raise CalcError(f"unknown function `{name}`")
        if node.keywords:
            raise CalcError("keyword arguments are not supported")
        args = [_eval(a) for a in node.args]
        try:
            return func(*args)
        except (ValueError, OverflowError, ZeroDivisionError, TypeError) as e:
            raise CalcError(f"`{name}` failed: {e}") from None

    if isinstance(node, ast.Name):
        if node.id in _CONSTS:
            return _CONSTS[node.id]
        raise CalcError(f"unknown name `{node.id}`")

    # ast.Tuple covers min(1,2,3) style arg lists inside Call already; a bare
    # tuple like (1,2) is not a number.
    raise CalcError("unsupported expression")


def calculate(expression):
    """
    Evaluate a maths expression string. Returns a float/int, or raises CalcError.
    '^' is accepted as a synonym for '**' because the README documents `2^8`.
    """
    text = (expression or "").strip()
    if not text:
        raise CalcError("nothing to calculate")
    if len(text) > 400:
        raise CalcError("expression too long (max 400 characters)")

    # normalise ^ -> ** so 2^8 works, but leave ** alone
    text = text.replace("^", "**")
    # strip a trailing '=' people often type
    text = text.rstrip("=").strip()

    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as e:
        raise CalcError(f"syntax error: {e.msg}") from None

    result = _eval(tree)

    if isinstance(result, complex):
        raise CalcError("complex numbers are not supported")
    if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
        raise CalcError("result is not a finite number")
    if abs(result) > MAX_RESULT:
        raise CalcError("result too large")
    return result


def format_result(value):
    """Render a result without a trailing '.0' for whole numbers."""
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


_HELP = (
    "🧮 **Cipher Elite Calculator**\n\n"
    "**Usage:** `/calc <expression>`\n\n"
    "**Examples:**\n"
    "• `/calc 2+2` → 4\n"
    "• `/calc 10*5+3` → 53\n"
    "• `/calc (100-20)/4` → 20\n"
    "• `/calc 2^8` → 256\n"
    "• `/calc sqrt(144)` → 12\n"
    "• `/calc 15%4` → 3\n\n"
    "**Operators:** `+ - * / // % ^` and parentheses\n"
    "**Functions:** `sqrt cbrt sin cos tan log log10 log2 exp abs round "
    "min max sum floor ceil factorial gcd degrees radians pow`\n"
    "**Constants:** `pi e tau`\n\n"
    "🔒 Runs on a safe AST walker — no `eval()`, no code execution.\n"
    "🤖 **Powered by Cipher Elite**"
)

# ---------------------------------------------------------------------------
#  translator.py — module level
# ---------------------------------------------------------------------------

LANGS = {
    "en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
    "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian",
    "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "ar": "Arabic",
    "bn": "Bengali", "ta": "Tamil", "te": "Telugu", "mr": "Marathi",
    "gu": "Gujarati", "ur": "Urdu", "pa": "Punjabi", "tr": "Turkish",
    "id": "Indonesian", "nl": "Dutch", "pl": "Polish", "vi": "Vietnamese",
}


LANG_ALIASES = {
    "english": "en", "hindi": "hi", "spanish": "es", "french": "fr",
    "german": "de", "italian": "it", "portuguese": "pt", "russian": "ru",
    "japanese": "ja", "korean": "ko", "chinese": "zh", "arabic": "ar",
    "bengali": "bn", "bangla": "bn", "tamil": "ta", "telugu": "te",
    "marathi": "mr", "gujarati": "gu", "urdu": "ur", "punjabi": "pa",
    "turkish": "tr", "indonesian": "id", "dutch": "nl", "polish": "pl",
    "vietnamese": "vi", "auto": "auto",
}


MAX_TEXT = 4000


TIMEOUT = 12


LINGVA_HOSTS = ["lingva.ml", "lingva.garudalinux.org", "lingva.lunar.icu"]


class TranslateError(Exception):
    pass


def _normalise_lang(token):
    """'Hindi' / 'hi' / 'HI' -> 'hi'. Returns None when unrecognised."""
    token = (token or "").strip().lower().replace("_", "-")
    if token in ("auto", "detect"):
        return "auto"
    if token in LANGS:
        return token
    if token in LANG_ALIASES:
        return LANG_ALIASES[token]
    # accept a region subtag such as zh-cn / pt-br
    base = token.split("-")[0]
    if base in LANGS:
        return base
    return None


async def _from_lingva(session, host, source, target, text):
    url = f"https://{host}/api/v1/{source}/{target}/{text}"
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
        if resp.status != 200:
            raise TranslateError(f"{host} returned HTTP {resp.status}")
        data = await resp.json(content_type=None)
    translated = (data or {}).get("translation")
    if not translated:
        raise TranslateError(f"{host} returned an empty translation")
    detected = ((data or {}).get("info") or {}).get("detectedSource")
    # A degraded instance echoes the input and still claims it detected the
    # target language. Trust it only when something actually changed, or when
    # the source really is the language we asked for.
    if translated.strip() == text.strip() and detected and detected != target:
        raise TranslateError(f"{host} echoed the input untranslated")
    return translated, detected


async def _from_google_gtx(session, source, target, text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": source, "tl": target, "dt": "t", "q": text}
    async with session.get(url, params=params,
                           timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
        if resp.status != 200:
            raise TranslateError(f"gtx returned HTTP {resp.status}")
        data = await resp.json(content_type=None)
    if not isinstance(data, list) or not data or not isinstance(data[0], list):
        raise TranslateError("gtx returned an unexpected payload")
    parts = [chunk[0] for chunk in data[0] if isinstance(chunk, list) and chunk and chunk[0]]
    translated = "".join(parts).strip()
    if not translated:
        raise TranslateError("gtx returned an empty translation")
    detected = data[2] if len(data) > 2 and isinstance(data[2], str) else None
    return translated, detected


async def translate(text, target="en", source="auto"):
    """
    Translate `text` into `target`. Returns (translated, detected_source, provider).
    Raises TranslateError when every provider fails.
    """
    text = (text or "").strip()
    if not text:
        raise TranslateError("nothing to translate")
    if len(text) > MAX_TEXT:
        raise TranslateError(f"text too long (max {MAX_TEXT} characters)")

    errors = []
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        for host in LINGVA_HOSTS:
            try:
                out, detected = await _from_lingva(session, host, source, target, text)
                return out, detected, host
            except Exception as e:
                errors.append(f"{host}: {str(e)[:60]}")
        try:
            out, detected = await _from_google_gtx(session, source, target, text)
            return out, detected, "google-gtx"
        except Exception as e:
            errors.append(f"gtx: {str(e)[:60]}")

    raise TranslateError(" · ".join(errors[-3:]) or "all providers failed")


def _split_command(arg):
    """
    '/tr <lang> <text>' vs '/tr <text>'.
    Returns (target_lang, text). target_lang is None when the first token is
    not a language, meaning "translate to English".
    """
    arg = (arg or "").strip()
    if not arg:
        return None, ""
    parts = arg.split(None, 1)
    first = parts[0]
    if len(parts) == 2 and _normalise_lang(first):
        return _normalise_lang(first), parts[1].strip()
    return None, arg


def _help():
    codes = " ".join(f"`{c}`" for c in sorted(LANGS))
    return (
        "🌐 **Cipher Elite Translator**\n\n"
        "**Usage:**\n"
        "• `/tr <text>` — translate to English\n"
        "• `/tr <lang> <text>` — translate to a language\n"
        "• Reply to a message with `/tr <lang>`\n"
        "• Inline: `@yourbot tr <text>`\n\n"
        "**Examples:**\n"
        "• `/tr Hello`\n"
        "• `/tr es Hello world`\n"
        "• `/tr hi How are you`\n\n"
        f"**Languages:** {codes}\n\n"
        "🤖 **Powered by Cipher Elite**"
    )

# ---------------------------------------------------------------------------
#  COMMAND REGISTRATION
# ---------------------------------------------------------------------------

def init_bot_plugin(bot, owner_id, owner_name):
    """Register every Tools handler on the assistant bot."""

    # =======================================================================
    #  calculator.py
    # =======================================================================
    """Register the calculator handlers on the assistant bot."""

    @bot.on(events.NewMessage(pattern=r"^/calc(?:\s+([\s\S]*))?$"))
    async def calc_handler(event):
        expression = (event.pattern_match.group(1) or "").strip()

        if not expression:
            await event.reply(_HELP)
            return

        try:
            value = calculate(expression)
        except CalcError as e:
            await event.reply(
                "🧮 **Cipher Elite Calculator**\n\n"
                f"❌ **Cannot calculate that:** {e}\n\n"
                "💡 **Try:** `/calc 2+2`\n"
                "🤖 **Powered by Cipher Elite**"
            )
            return
        except Exception as e:
            await event.reply(
                "🧮 **Cipher Elite Calculator**\n\n"
                f"❌ **Unexpected error:** {str(e)[:160]}\n"
                "🤖 **Powered by Cipher Elite**"
            )
            return

        await event.reply(
            "🧮 **Cipher Elite Calculator**\n\n"
            f"📥 `{expression}`\n"
            f"📤 **{format_result(value)}**\n\n"
            "🤖 **Powered by Cipher Elite**"
        )

    # Inline support: @bot calc 2+2
    # NOTE: plugins/bot.py registers a pattern-less InlineQuery handler guarded
    # by @rishabh_help(), which answers [] for non-owners. This handler still
    # works for the owner and sudo users.
    @bot.on(events.InlineQuery(pattern=r"^calc\s+(.+)"))
    async def calc_inline_handler(event):
        expression = event.pattern_match.group(1).strip()
        try:
            value = calculate(expression)
            text = f"🧮 `{expression}` = **{format_result(value)}**"
            result = event.builder.article(
                title=f"= {format_result(value)}",
                description=f"{expression} = {format_result(value)}",
                text=text,
                buttons=[Button.url("Cipher Elite", "https://github.com/rishabhops/CipherElite")],
            )
            await event.answer([result])
        except CalcError as e:
            await event.answer([event.builder.article(
                title="Cannot calculate",
                description=str(e)[:80],
                text=f"🧮 ❌ {e}",
            )])
        except Exception:
            await event.answer([])

    # =======================================================================
    #  translator.py
    # =======================================================================
    """Register the translator handlers on the assistant bot."""

    @bot.on(events.NewMessage(pattern=r"^/tr(?:\s+([\s\S]*))?$"))
    async def translate_handler(event):
        arg = (event.pattern_match.group(1) or "").strip()
        reply = await event.get_reply_message()

        # /tr with no argument but replying to a message -> translate that message
        if not arg and reply and reply.text:
            target, text = "en", reply.text
        else:
            target, text = _split_command(arg)
            # /tr <lang> while replying -> translate the replied message
            if target and not text and reply and reply.text:
                text = reply.text

        if not text:
            await event.reply(_help())
            return

        target = target or "en"
        await event.reply("🔄 **Translating...**")
        try:
            translated, detected, provider = await translate(text, target)
        except TranslateError as e:
            await event.edit(
                "🌐 **Cipher Elite Translator**\n\n"
                f"❌ **Translation failed.**\n`{str(e)[:200]}`\n\n"
                "💡 Free endpoints rate-limit sometimes — try again in a moment.\n"
                "🤖 **Powered by Cipher Elite**"
            )
            return
        except Exception as e:
            await event.edit(
                "🌐 **Cipher Elite Translator**\n\n"
                f"❌ **Unexpected error:** {str(e)[:160]}\n"
                "🤖 **Powered by Cipher Elite**"
            )
            return

        src_name = LANGS.get(detected, detected or "auto")
        tgt_name = LANGS.get(target, target)
        await event.edit(
            "🌐 **Cipher Elite Translator**\n\n"
            f"**From:** {src_name} → **To:** {tgt_name}\n\n"
            f"{translated}\n\n"
            f"🔗 **Via:** `{provider}`\n"
            "🤖 **Powered by Cipher Elite**",
            link_preview=False,
        )

    # Inline: @bot tr <text>  /  @bot tr es <text>
    # NOTE: plugins/bot.py registers a pattern-less InlineQuery handler guarded
    # by @rishabh_help(), which answers [] for non-owners. This handler still
    # works for the owner and sudo users.
    @bot.on(events.InlineQuery(pattern=r"^tr\s+(.+)"))
    async def translate_inline_handler(event):
        target, text = _split_command(event.pattern_match.group(1))
        target = target or "en"
        try:
            translated, detected, provider = await translate(text, target)
            tgt_name = LANGS.get(target, target)
            result = event.builder.article(
                title=f"→ {tgt_name}: {translated[:60]}",
                description=f"{LANGS.get(detected, detected or 'auto')} → {tgt_name}",
                text=f"🌐 **{tgt_name}**\n\n{translated}\n\n_via {provider}_",
                buttons=[Button.url("Cipher Elite", "https://github.com/rishabhops/CipherElite")],
            )
            await event.answer([result])
        except Exception as e:
            await event.answer([event.builder.article(
                title="Translation failed",
                description=str(e)[:80],
                text=f"🌐 ❌ {str(e)[:200]}",
            )])

    print("✅ Tools Plugin: All handlers registered successfully")
