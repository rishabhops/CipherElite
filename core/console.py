"""core/console.py — terminal presentation layer.

Kyun alag file: main.py mein banner ke andar fixed-width strings the, jinke
beech runtime values interpolate hote the. Bot ka naam ya version ek character
bhi badla, aur daayin border shift ho gayi. Yahan width runtime par naapi
jaati hai, isliye box hamesha seedha rehta hai.

EMOJI jaan-bujh ke box ke ANDAR nahi rakhe: zyadatar terminal emoji ko
double-width render karta hai lekin Python ka len() unhe 1 ginta hai —
padding turant toot jaati hai. Box ke bahar emoji theek hai.
"""

import os
import re
import sys
import time


# ── colour support detection ──────────────────────────────────────────
# Pipe ya file mein redirect karne par escape codes kachra bante hain,
# isliye sirf asli TTY par colour. NO_COLOR standard bhi respect karte hain.
_USE_COLOUR = (
    sys.stdout.isatty()
    and os.getenv("NO_COLOR") is None
    and os.getenv("TERM") != "dumb"
)


def _c(_code: str) -> str:
    return _code if _USE_COLOUR else ""


RESET = _c("\033[0m")
BOLD = _c("\033[1m")
DIM = _c("\033[2m")

RED = _c("\033[38;5;203m")
GREEN = _c("\033[38;5;114m")
YELLOW = _c("\033[38;5;221m")
BLUE = _c("\033[38;5;75m")
PURPLE = _c("\033[38;5;177m")
CYAN = _c("\033[38;5;80m")
GREY = _c("\033[38;5;245m")

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _width(_s: str) -> int:
    """Colour codes screen par jagah nahi lete — naapte waqt hata do."""
    return len(_ANSI_RE.sub("", _s))


# ── banner ────────────────────────────────────────────────────────────

_ART = r"""

░█████╗░██╗██████╗░██╗░░██╗███████╗██████╗░
██╔══██╗██║██╔══██╗██║░░██║██╔════╝██╔══██╗
██║░░╚═╝██║██████╔╝███████║█████╗░░██████╔╝
██║░░██╗██║██╔═══╝░██╔══██║██╔══╝░░██╔══██╗
╚█████╔╝██║██║░░░░░██║░░██║███████╗██║░░██║
░╚════╝░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝

█▀▀ █░░ █ ▀█▀ █▀▀
██▄ █▄▄ █ ░█░ ██▄
"""


def banner(_name: str, _version: str, _author: str, _handle: str) -> None:
    print()
    for _line in _ART.strip("\n").split("\n"):
        print(f"{PURPLE}{BOLD}{_line}{RESET}")
    print()
    print(f"   {GREY}{_name}{RESET}  {DIM}·{RESET}  {CYAN}v{_version}{RESET}")
    print(f"   {DIM}{_author} · {_handle}{RESET}")
    print()


# ── boxes ─────────────────────────────────────────────────────────────


def box(_title: str, _rows, _colour: str = CYAN) -> None:
    """
    _rows: (label, value) tuples ki list.
    Width sabse lambi line se decide hoti hai — hardcoded nahi.
    """
    _pairs = [(str(_k), str(_v)) for _k, _v in _rows]
    _label_w = max((_width(_k) for _k, _ in _pairs), default=0)
    _body = [f"{GREY}{_k.ljust(_label_w)}{RESET}  {_v}" for _k, _v in _pairs]

    _inner = max([_width(_title)] + [_width(_b) for _b in _body]) + 2
    _pad = lambda _s: _s + " " * (_inner - _width(_s) - 1)

    print(f"{_colour}╭{'─' * _inner}╮{RESET}")
    print(f"{_colour}│{RESET} {_pad(f'{BOLD}{_title}{RESET}')}{_colour}│{RESET}")
    print(f"{_colour}├{'─' * _inner}┤{RESET}")
    for _b in _body:
        print(f"{_colour}│{RESET} {_pad(_b)}{_colour}│{RESET}")
    print(f"{_colour}╰{'─' * _inner}╯{RESET}")


def blockquote(_lines, _title: str = None, _colour: str = CYAN, _bar: str = "▌") -> None:
    """
    Terminal blockquote: left bar with optional title.
    _lines: string list ya (label, value) tuples.
    """
    _body = []
    for _line in _lines:
        if isinstance(_line, (tuple, list)) and len(_line) == 2:
            _k, _v = str(_line[0]), str(_line[1])
            _body.append(f"{GREY}{_k}{RESET}  {_v}")
        else:
            _body.append(str(_line))

    _max = max([_width(_b) for _b in _body], default=0)
    if _title:
        _max = max(_max, _width(_title))

    if _title:
        _pad = " " * (_max - _width(_title))
        print(f"{_colour}{_bar}{RESET} {BOLD}{_colour}{_title}{RESET}{_pad}")
        print(f"{_colour}{_bar}{RESET}")

    for _b in _body:
        _pad = " " * (_max - _width(_b))
        print(f"{_colour}{_bar}{RESET} {_b}{_pad}")


def panel(_title: str, _rows, _colour: str = CYAN) -> None:
    """Top/bottom ruled panel with blockquote-style bar."""
    _pairs = [(str(_k), str(_v)) for _k, _v in _rows]
    _label_w = max((_width(_k) for _k, _ in _pairs), default=0)
    _body = [f"{GREY}{_k.ljust(_label_w)}{RESET}  {_v}" for _k, _v in _pairs]
    _max = max([_width(_title)] + [_width(_b) for _b in _body])
    _r = "─" * (_max + 2)

    print(f"{_colour}┌{_r}┐{RESET}")
    print(f"{_colour}│{RESET} {BOLD}{_title}{RESET}{' ' * (_max - _width(_title))} {_colour}│{RESET}")
    print(f"{_colour}├{_r}┤{RESET}")
    for _b in _body:
        _pad = " " * (_max - _width(_b))
        print(f"{_colour}│{RESET} {_b}{_pad} {_colour}│{RESET}")
    print(f"{_colour}└{_r}┘{RESET}")


def rule(_text: str = "", _colour: str = GREY) -> None:
    _w = min(os.get_terminal_size().columns if sys.stdout.isatty() else 60, 60)
    if not _text:
        print(f"{_colour}{'─' * _w}{RESET}")
        return
    _left = 3
    _right = max(0, _w - _left - _width(_text) - 2)
    print(f"{_colour}{'─' * _left} {BOLD}{_text}{RESET}{_colour} "
          f"{'─' * _right}{RESET}")


# ── status lines ──────────────────────────────────────────────────────

_STEPS = {}


def step(_key: str, _text: str) -> None:
    """Kaam shuru — baad mein ok()/fail() isi key par timing chhaap dega."""
    _STEPS[_key] = time.monotonic()
    print(f"  {YELLOW}◌{RESET} {_text}{DIM}…{RESET}", flush=True)


def _elapsed(_key: str) -> str:
    _t0 = _STEPS.pop(_key, None)
    if _t0 is None:
        return ""
    return f"  {DIM}{time.monotonic() - _t0:.2f}s{RESET}"


def ok(_text: str, _key: str = None) -> None:
    print(f"  {GREEN}●{RESET} {_text}{_elapsed(_key) if _key else ''}")


def fail(_text: str, _key: str = None) -> None:
    print(f"  {RED}●{RESET} {_text}{_elapsed(_key) if _key else ''}")


def warn(_text: str) -> None:
    print(f"  {YELLOW}▲{RESET} {_text}")


def info(_text: str) -> None:
    print(f"  {BLUE}·{RESET} {_text}")


# ── logging formatter ─────────────────────────────────────────────────


class ColourFormatter:
    """
    logging.Formatter ka replacement nahi — usko wrap karta hai, taaki
    file handler plain text likhta rahe aur sirf console rangeen ho.
    """

    _LEVEL = {
        "DEBUG": (GREY, "debug"),
        "INFO": (BLUE, "info "),
        "WARNING": (YELLOW, "warn "),
        "ERROR": (RED, "error"),
        "CRITICAL": (RED + BOLD, "crit "),
    }

    def __init__(self, _name: str):
        self._name = _name

    def __call__(self):
        import logging

        _outer = self

        class _F(logging.Formatter):
            def format(self, _r):
                _col, _lvl = _outer._LEVEL.get(_r.levelname, (GREY, _r.levelname))
                _ts = time.strftime("%H:%M:%S", time.localtime(_r.created))
                return (
                    f"{DIM}{_ts}{RESET} "
                    f"{_col}{_lvl}{RESET} "
                    f"{GREY}{_outer._name}{RESET}  "
                    f"{_r.getMessage()}"
                )

        return _F()
