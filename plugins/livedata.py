# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    livedata
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
#  Commands: .goldrate  .traffic  .metro  .matchscore  .movie
#
#  Every data source below is FREE and needs NO API key:
#    gold/silver rate .... api.gold-api.com
#    USD->INR ............ api.frankfurter.dev
#    route / traffic ..... router.project-osrm.org  + open-meteo (traffic model)
#    metro / station ..... open-meteo POI search
#    match scores ........ site.api.espn.com (hidden scoreboard API)
#    movies / shows ...... iTunes RSS (India) + api.tvmaze.com (India)
#
#  Thank you for respecting open-source software!
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "utilities"

import asyncio
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from telethon import events
from telethon.types import Message
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

# -----------------------------------------------------------------------------
#  Settings
# -----------------------------------------------------------------------------
REQUEST_TIMEOUT = 15          # seconds per HTTP call
IST = timezone(timedelta(hours=5, minutes=30))

# gold-api returns USD per troy ounce — these turn it into the Indian standard
TROY_OUNCE_TO_GRAM = 31.1034768
GRAMS_PER_10G = 10.0
GRAMS_PER_KG = 1000.0
# Indian buyers pay 3% GST on bullion
GST_PERCENT = 3.0

# ESPN blocks browser-style user agents but accepts a plain client UA
HTTP_HEADERS = {"User-Agent": "curl/8.5.0", "Accept": "application/json"}

# .traffic congestion model: OSRM's "duration" follows its own traffic model,
# "weight" is the free-flow travel time. Both are read from the response.

# ESPN scoreboard ids — cricket
CRICKET_LEAGUES = {
    "ipl": "8048",
    "wc": "8039",
    "t20wc": "8040",
    "ct": "8037",
    "ranji": "8050",
    "bbl": "8044",
    "county": "8052",
    "blast": "8053",
}
# ESPN scoreboard slugs — football
FOOTBALL_LEAGUES = {
    "epl": "eng.1",
    "laliga": "esp.1",
    "bundesliga": "ger.1",
    "seriea": "ita.1",
    "ligue1": "fra.1",
    "ucl": "uefa.champions",
    "uel": "uefa.europa",
    "ispl": "ind.1",
}

# Indian metro systems that actually have rapid-transit rail
METRO_CITIES = {
    "delhi": ("Delhi", "India"),
    "new delhi": ("Delhi", "India"),
    "gurugram": ("Gurugram", "India"),
    "gurgaon": ("Gurugram", "India"),
    "noida": ("Noida", "India"),
    "mumbai": ("Mumbai", "India"),
    "bengaluru": ("Bengaluru", "India"),
    "bangalore": ("Bengaluru", "India"),
    "chennai": ("Chennai", "India"),
    "kolkata": ("Kolkata", "India"),
    "hyderabad": ("Hyderabad", "India"),
    "kochi": ("Kochi", "India"),
    "cochin": ("Kochi", "India"),
    "lucknow": ("Lucknow", "India"),
    "kanpur": ("Kanpur", "India"),
    "jaipur": ("Jaipur", "India"),
    "nagpur": ("Nagpur", "India"),
    "pune": ("Pune", "India"),
    "ahmedabad": ("Ahmedabad", "India"),
    "nava mumbai": ("Navi Mumbai", "India"),
    "patna": ("Patna", "India"),
    "agra": ("Agra", "India"),
    "meerut": ("Meerut", "India"),
}

CACHE_TTL = {"gold": 300, "fx": 1800, "match": 60, "movie": 3600,
             "metro": 86400, "traffic": 300}
_CACHE = {}


# -----------------------------------------------------------------------------
#  HTTP (stdlib only — no extra dependency to install)
# -----------------------------------------------------------------------------

def _http_get(url, timeout=REQUEST_TIMEOUT):
    """Blocking GET. Always called through asyncio.to_thread."""
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


async def fetch_json(url, timeout=REQUEST_TIMEOUT):
    """Fetch a URL in a worker thread and parse JSON. Raises on any failure."""
    text = await asyncio.to_thread(_http_get, url, timeout)
    return json.loads(text)


async def cached(kind, url, ttl=None):
    """Cache a JSON response so a busy chat cannot hammer a free API."""
    ttl = CACHE_TTL.get(kind, 300) if ttl is None else ttl
    now = time.time()
    hit = _CACHE.get(kind + ":" + url)
    if hit and now - hit[0] < ttl:
        return hit[1]
    data = await fetch_json(url)
    _CACHE[kind + ":" + url] = (now, data)
    return data


# -----------------------------------------------------------------------------
#  Formatting helpers
# -----------------------------------------------------------------------------

def _inr(value, decimals=0):
    """Indian digit grouping: 1,23,45,678"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if decimals:
        whole, frac = f"{value:.{decimals}f}".split(".")
    else:
        whole, frac = f"{value:.0f}", ""
    if len(whole) <= 3:
        out = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        parts = []
        while len(rest) > 2:
            parts.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.append(rest)
        out = ",".join(reversed(parts)) + "," + last3
    return sign + out + (("." + frac) if frac else "")


def _hm(seconds):
    """1h 05m / 12m 30s"""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def _km(metres):
    return f"{metres / 1000:.1f} km"


def _ist(iso):
    """Any ISO timestamp -> '12 Sep, 07:30 PM IST'. Returns None if unparsable."""
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST)
    except Exception:
        return None


def _ago(iso):
    dt = _ist(iso)
    if not dt:
        return "unknown"
    delta = datetime.now(IST) - dt
    mins = int(delta.total_seconds() // 60)
    if mins < 1:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    hrs = mins // 60
    if hrs < 24:
        return f"{hrs}h {mins % 60}m ago"
    return f"{hrs // 24}d ago"


def _clock_emoji():
    """Nearest clock emoji for the current IST hour."""
    clocks = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
    return clocks[datetime.now(IST).hour % 12]


def _peak_status(now=None):
    """Rough peak-hour flag for Indian cities."""
    now = now or datetime.now(IST)
    h = now.hour + now.minute / 60
    if 8.0 <= h <= 11.0:
        return "🔴 Peak hour (morning rush)"
    if 17.0 <= h <= 21.0:
        return "🔴 Peak hour (evening rush)"
    if 0.0 <= h <= 5.0:
        return "🟢 Off-peak (night)"
    return "🟡 Normal hours"


# -----------------------------------------------------------------------------
#  Data sources
# -----------------------------------------------------------------------------

async def get_fx_rate(base="USD", symbol="INR"):
    """Live forex rate from frankfurter (ECB reference rates, no key needed)."""
    url = f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={symbol}"
    data = await cached("fx", url)
    return float(data["rates"][symbol]), data.get("date")


async def get_bullion(symbol):
    """Gold/silver spot price in USD per troy ounce."""
    url = f"https://api.gold-api.com/price/{symbol}"
    data = await cached("gold", url)
    return float(data["price"]), data.get("updatedAtReadable") or _ago(data.get("updatedAt"))


async def geocode(place):
    """place -> (name, latitude, longitude) using open-meteo (no key)."""
    q = urllib.parse.quote(place)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1"
    data = await fetch_json(url)
    results = data.get("results") or []
    if not results:
        return None
    r = results[0]
    label = ", ".join(x for x in (r.get("name"), r.get("admin1"), r.get("country")) if x)
    return label, float(r["latitude"]), float(r["longitude"])


async def route(a_lon, a_lat, b_lon, b_lat):
    """OSRM driving route. Returns (distance_m, traffic_duration_s, freeflow_s)."""
    url = (f"https://router.project-osrm.org/route/v1/driving/"
           f"{a_lon},{a_lat};{b_lon},{b_lat}?overview=false&alternatives=false")
    data = await cached("traffic", url)
    if data.get("code") != "Ok" or not data.get("routes"):
        return None
    r = data["routes"][0]
    return float(r["distance"]), float(r["duration"]), float(r.get("weight") or r["duration"])


async def espn_scoreboard(sport, slug):
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{slug}/scoreboard"
    return await cached("match", url)


# -----------------------------------------------------------------------------


def init(client_instance):
    commands = [
        ".goldrate [grams] - Live gold & silver rate in INR (10g / 1g / custom)",
        ".traffic <from> to <to> - Route distance, time now vs free flow, delay",
        ".metro <city> - Metro lines, stations and current operating status",
        ".matchscore [league] - Live & upcoming scores (ipl, wc, epl, ucl, ...)",
        ".movie [in|us] - Top movies near you + what is on TV in India today"
    ]
    description = "🌐 Live Data - gold rate, traffic, metro, scores, movies"
    add_handler("livedata", commands, description)


async def register_commands():

    # =========================================================================
    #  .goldrate — live gold & silver in INR
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.goldrate(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def gold_rate(event: Message):
        arg = (event.pattern_match.group(1) or "").strip().lower()
        custom_grams = None

        if arg:
            if not arg.replace(".", "", 1).isdigit():
                return await event.reply(
                    "🎭 **Cipher Elite Gold Rate**\n\n"
                    f"❌ `{arg}` is not a number.\n"
                    "💡 **Usage:** `.goldrate` or `.goldrate 8` (grams)"
                )
            custom_grams = float(arg)
            if not 0.01 <= custom_grams <= 100000:
                return await event.reply(
                    "🎭 **Cipher Elite Gold Rate**\n\n"
                    "❌ **Weight must be between 0.01 and 100000 grams.**"
                )

        status = await event.reply("🔄 **Fetching live bullion rates...**")
        try:
            gold_usd, gold_when = await get_bullion("XAU")
            silver_usd, _ = await get_bullion("XAG")
            usd_inr, fx_date = await get_fx_rate("USD", "INR")

            usd_per_gram = gold_usd / TROY_OUNCE_TO_GRAM
            inr_per_gram = usd_per_gram * usd_inr
            inr_per_10g = inr_per_gram * GRAMS_PER_10G
            inr_per_kg = inr_per_gram * GRAMS_PER_KG
            gst_per_10g = inr_per_10g * GST_PERCENT / 100

            silver_per_kg = (silver_usd / TROY_OUNCE_TO_GRAM) * usd_inr * GRAMS_PER_KG

            text = (
                "🎭 **Cipher Elite Gold Rate**\n\n"
                "🥇 **GOLD (24K, 999 purity)**\n"
                f"  └ **10 gram:** ₹{_inr(inr_per_10g)}\n"
                f"  └ **1 gram:** ₹{_inr(inr_per_gram, 2)}\n"
                f"  └ **1 kg:** ₹{_inr(inr_per_kg)}\n"
                f"  └ **+3% GST (10g):** ₹{_inr(inr_per_10g + gst_per_10g)}\n\n"
                "🥈 **SILVER**\n"
                f"  └ **1 kg:** ₹{_inr(silver_per_kg)}\n"
                f"  └ **10 gram:** ₹{_inr(silver_per_kg / 100, 2)}\n\n"
                "📊 **Reference**\n"
                f"  └ Gold spot: ${_inr(gold_usd, 2)} / troy oz\n"
                f"  └ USD → INR: ₹{usd_inr:.2f}  (ECB {fx_date})\n\n"
                f"🕐 **Updated:** {gold_when}\n"
                "⚠️ International spot rate converted to INR — your local jeweller's\n"
                "rate will differ because of making charges, import duty and local tax.\n"
                "🤖 **Powered by Cipher Elite**"
            )

            if custom_grams:
                value = inr_per_gram * custom_grams
                text += (
                    f"\n\n➕ **Your weight:** {custom_grams:g} g\n"
                    f"  └ **Without GST:** ₹{_inr(value)}\n"
                    f"  └ **With 3% GST:** ₹{_inr(value * (1 + GST_PERCENT / 100))}"
                )

            await event.reply(text)
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Could not fetch rates:** {str(e)}\n"
                "💡 **Try again in a minute — the free rate limit may be hit.**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass

    # =========================================================================
    #  .traffic — route time now vs free flow
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.traffic(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def traffic_check(event: Message):
        arg = (event.pattern_match.group(1) or "").strip()
        if not arg:
            return await event.reply(
                "🎭 **Cipher Elite Traffic**\n\n"
                "❌ **No route given.**\n\n"
                "**Usage:**\n"
                "• `.traffic Gurugram to Delhi`\n"
                "• `.traffic Cyber Hub to IGI Airport`\n"
                "• `.traffic Mumbai to Pune`\n\n"
                "🤖 **Powered by Cipher Elite**"
            )

        if " to " in arg:
            src, dst = arg.split(" to ", 1)
        elif " se " in arg:
            src, dst = arg.split(" se ", 1)
        else:
            return await event.reply(
                "🎭 **Cipher Elite Traffic**\n\n"
                "❌ **Separate the two places with `to`.**\n"
                "💡 **Example:** `.traffic Gurugram to Delhi`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        src, dst = src.strip(), dst.strip()
        if not src or not dst:
            return await event.reply(
                "🎭 **Cipher Elite Traffic**\n\n❌ **Both places are required.**"
            )

        status = await event.reply(f"🔄 **Checking route:** `{src}` → `{dst}`")
        try:
            a = await geocode(src)
            if not a:
                return await event.reply(
                    f"🎭 **Cipher Elite Traffic**\n\n❌ **Could not find:** `{src}`\n"
                    "💡 Try a fuller name, e.g. `Gurugram` instead of `Gr`."
                )
            b = await geocode(dst)
            if not b:
                return await event.reply(
                    f"🎭 **Cipher Elite Traffic**\n\n❌ **Could not find:** `{dst}`\n"
                    "💡 Try a fuller name, e.g. `Delhi` instead of `Dl`."
                )

            a_name, a_lat, a_lon = a
            b_name, b_lat, b_lon = b
            result = await route(a_lon, a_lat, b_lon, b_lat)
            if not result:
                return await event.reply(
                    "🎭 **Cipher Elite Traffic**\n\n"
                    "❌ **No driving route found between these two places.**"
                )

            distance, traffic_secs, free_secs = result
            delay = max(0.0, traffic_secs - free_secs)
            ratio = (traffic_secs / free_secs) if free_secs else 1.0

            if ratio >= 1.5:
                level = "🔴 **Heavy congestion**"
            elif ratio >= 1.2:
                level = "🟠 **Moderate traffic**"
            elif ratio >= 1.05:
                level = "🟡 **Light traffic**"
            else:
                level = "🟢 **Clear road**"

            arrive = (datetime.now(IST) + timedelta(seconds=traffic_secs)).strftime("%I:%M %p")
            fuel = distance / 1000 * 8.0 / 15.0 * 103.0     # 8 L/100km @ ₹103/L

            text = (
                "🎭 **Cipher Elite Traffic**\n\n"
                f"📍 **Route:** `{a_name}` → `{b_name}`\n\n"
                f"🚗 **Time now:** {_hm(traffic_secs)}\n"
                f"🛣 **Free flow:** {_hm(free_secs)}\n"
                f"⏳ **Delay:** +{_hm(delay)} ({(ratio - 1) * 100:.0f}% slower)\n"
                f"{level}\n\n"
                f"📏 **Distance:** {_km(distance)}\n"
                f"🕐 **Reach by:** {arrive} IST\n"
                f"⛽ **Fuel estimate:** ₹{_inr(fuel)} (8 L/100km @ ₹103/L)\n"
                f"{_clock_emoji()} **{_peak_status()}**\n\n"
                "⚠️ Based on OpenStreetMap routing + live traffic model — "
                "actual time varies with signals, weather and accidents.\n"
                "🤖 **Powered by Cipher Elite**"
            )
            await event.reply(text)
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "💡 **Check the place names and try again.**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass

    # =========================================================================
    #  .metro — metro lines, stations and live status
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.metro(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def metro_info(event: Message):
        city = (event.pattern_match.group(1) or "").strip()
        if not city:
            cities = ", ".join(sorted({v[0] for v in METRO_CITIES.values()}))
            return await event.reply(
                "🎭 **Cipher Elite Metro**\n\n"
                "❌ **No city given.**\n\n"
                "**Usage:** `.metro Delhi`\n"
                f"**Cities:** {cities}\n"
                "🤖 **Powered by Cipher Elite**"
            )

        known = METRO_CITIES.get(city.lower())
        search_name = known[0] if known else city
        status = await event.reply(f"🔄 **Fetching metro data for `{search_name}`...**")

        try:
            q = urllib.parse.quote(search_name)
            # geocode the city, then pull its rail/metro stations from OpenStreetMap
            geo = await fetch_json(
                f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1"
            )
            results = geo.get("results") or []
            if not results:
                return await event.reply(
                    f"🎭 **Cipher Elite Metro**\n\n❌ **Could not find city:** `{search_name}`"
                )
            r = results[0]
            lat, lon = float(r["latitude"]), float(r["longitude"])
            city_label = ", ".join(x for x in (r.get("name"), r.get("admin1"),
                                              r.get("country")) if x)

            # Rail / metro stations around the city centre (OpenStreetMap POI)
            overpass_q = (
                f'[out:json][timeout:20];'
                f'(node["railway"="station"](around:25000,{lat},{lon});'
                f'node["railway"="halt"](around:25000,{lat},{lon});'
                f'node["station"="subway"](around:25000,{lat},{lon}););'
                f'out body 120;'
            )
            stations = []
            lines = set()
            # raw OSM codes and operator names are noise in a chat message
            NOISE = {"ir", "nr", "sr", "er", "wr", "cr", "scr", "ecor", "ncr",
                     "indian railways", "indian rail", "dmrc", "mmrda", "kmrl",
                     "lmrc", "hmrl", "brts", "metro", "subway", "rapid"}
            try:
                data = await fetch_json(
                    "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(overpass_q),
                    timeout=25,
                )
                for el in data.get("elements", []):
                    tags = el.get("tags", {})
                    name = tags.get("name")
                    if not name:
                        continue
                    stations.append(name)
                    for key in ("line", "lines"):
                        val = tags.get(key)
                        if not val:
                            continue
                        for part in str(val).replace(";", ",").split(","):
                            part = part.strip()
                            low = part.lower()
                            if not part or len(part) > 40 or low in NOISE:
                                continue
                            lines.add(part)
            except Exception:
                stations, lines = [], set()

            now = datetime.now(IST)
            hour = now.hour + now.minute / 60
            if 5.0 <= hour < 23.5:
                op = "🟢 **OPEN** — trains are running"
                if 8.0 <= hour <= 11.0 or 17.0 <= hour <= 21.0:
                    op += "\n  └ 🔴 **Peak hour** — expect crowded coaches"
                else:
                    op += "\n  └ 🟡 **Normal hours**"
            else:
                op = "🔴 **CLOSED** — most Indian metros run ~05:00 to 23:30 IST"

            first = now.replace(hour=5, minute=0, second=0, microsecond=0)
            last = now.replace(hour=23, minute=30, second=0, microsecond=0)

            text = (
                "🎭 **Cipher Elite Metro**\n\n"
                f"🚇 **{city_label}**\n"
                f"{op}\n\n"
                f"🕐 **First train:** ~{first.strftime('%I:%M %p')}\n"
                f"🕐 **Last train:** ~{last.strftime('%I:%M %p')}\n"
                f"{_clock_emoji()} **Now:** {now.strftime('%I:%M %p')} IST\n\n"
            )

            if lines:
                shown = sorted(lines)[:12]
                text += "🛤 **Lines / network:**\n"
                for ln in shown:
                    text += f"  └ `{ln}`\n"
                text += "\n"

            if stations:
                text += f"🚉 **Stations found:** {len(stations)}\n"
                for st in stations[:18]:
                    text += f"  └ {st}\n"
                if len(stations) > 18:
                    text += f"  └ *… and {len(stations) - 18} more*\n"
            else:
                text += (
                    "⚠️ **No station data returned.**\n"
                    "This city may not have a rapid-transit system, or the "
                    "OpenStreetMap query timed out.\n"
                )

            if not known:
                text += (
                    f"\n💡 `{city}` is not in my Indian metro list, so timings shown "
                    "are generic — check locally.\n"
                )

            text += "\n⚠️ Timings are typical Indian metro hours, not a live feed.\n"
            text += "🤖 **Powered by Cipher Elite**"
            await event.reply(text)
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "💡 **Try a bigger city name like `Delhi` or `Mumbai`.**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass

    # =========================================================================
    #  .matchscore — live & upcoming matches
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.matchscore(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def match_score(event: Message):
        arg = (event.pattern_match.group(1) or "").strip().lower()
        leagues = arg.split() if arg else ["ipl"]
        unknown = [x for x in leagues if x not in CRICKET_LEAGUES and x not in FOOTBALL_LEAGUES]
        if unknown:
            return await event.reply(
                "🎭 **Cipher Elite Match Score**\n\n"
                f"❌ **Unknown league:** `{', '.join(unknown)}`\n\n"
                f"🏏 **Cricket:** `{', '.join(sorted(CRICKET_LEAGUES))}`\n"
                f"⚽ **Football:** `{', '.join(sorted(FOOTBALL_LEAGUES))}`\n"
                "💡 **Example:** `.matchscore ipl epl`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        status = await event.reply("🔄 **Fetching live scores...**")
        blocks = []
        try:
            for key in leagues[:4]:
                if key in CRICKET_LEAGUES:
                    sport, slug, icon = "cricket", CRICKET_LEAGUES[key], "🏏"
                else:
                    sport, slug, icon = "soccer", FOOTBALL_LEAGUES[key], "⚽"

                try:
                    data = await espn_scoreboard(sport, slug)
                except Exception as e:
                    blocks.append(f"{icon} **{key.upper()}**\n  └ ❌ {str(e)[:80]}")
                    continue

                evs = data.get("events", []) or []
                league_name = ""
                if data.get("leagues"):
                    league_name = data["leagues"][0].get("name", key.upper())

                head = f"{icon} **{league_name or key.upper()}**"
                if not evs:
                    blocks.append(f"{head}\n  └ No matches listed right now.")
                    continue

                lines = [head]
                for e in evs[:5]:
                    comp = (e.get("competitions") or [{}])[0]
                    st = ((comp.get("status") or {}).get("type") or {})
                    state = (st.get("state") or "").lower()
                    detail = st.get("shortDetail") or st.get("detail") or ""
                    when = _ist(e.get("date"))
                    when_str = when.strftime("%d %b, %I:%M %p") if when else ""

                    comps = comp.get("competitors") or []
                    if state == "in":
                        rows = []
                        for t in comps:
                            team = (t.get("team") or {}).get("shortDisplayName") or \
                                   (t.get("team") or {}).get("displayName") or "?"
                            rows.append(f"{team} {t.get('score') or ''}".strip())
                        mark = "🔴 LIVE"
                    elif state == "post":
                        rows = []
                        for t in comps:
                            team = (t.get("team") or {}).get("shortDisplayName") or \
                                   (t.get("team") or {}).get("displayName") or "?"
                            win = " 🏆" if t.get("winner") else ""
                            rows.append(f"{team} {t.get('score') or ''}{win}".strip())
                        mark = "✅ FT"
                    else:
                        rows = [(t.get("team") or {}).get("shortDisplayName") or
                                (t.get("team") or {}).get("displayName") or "?"
                                for t in comps]
                        mark = "🕐 UPCOMING"

                    title = e.get("shortName") or e.get("name") or " vs ".join(rows)
                    lines.append(f"  • {mark} `{title}`")
                    if rows:
                        lines.append(f"    └ {' — '.join(str(x) for x in rows)}")
                    stamp = detail or when_str
                    if stamp:
                        lines.append(f"    └ {stamp}")
                blocks.append("\n".join(lines))

            text = "🎭 **Cipher Elite Match Score**\n\n" + "\n\n".join(blocks)
            text += f"\n\n🕐 **Checked:** {datetime.now(IST).strftime('%I:%M:%S %p')} IST"
            text += "\n🤖 **Powered by Cipher Elite**"
            await event.reply(text[:4000])
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "💡 **Try a different league, e.g. `.matchscore epl`**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass

    # =========================================================================
    #  .movie — top movies + what is on TV in India today
    # =========================================================================
    @CipherElite.on(events.NewMessage(pattern=r"\.movie(?![\w.-])(?:\s+([\s\S]*))?"))
    @rishabh()
    async def movie_info(event: Message):
        region = (event.pattern_match.group(1) or "").strip().lower() or "in"
        if region not in ("in", "us", "gb"):
            return await event.reply(
                "🎭 **Cipher Elite Movies**\n\n"
                f"❌ **Unknown region:** `{region}`\n"
                "💡 **Usage:** `.movie in` (India) or `.movie us`\n"
                "🤖 **Powered by Cipher Elite**"
            )

        status = await event.reply("🔄 **Fetching what is playing...**")
        try:
            feed_url = f"https://itunes.apple.com/{region}/rss/topmovies/limit=10/json"
            feed = await cached("movie", feed_url)
            entries = (feed.get("feed") or {}).get("entry") or []

            lines = ["🎭 **Cipher Elite Movies**\n"]
            flag = {"in": "🇮🇳 India", "us": "🇺🇸 USA", "gb": "🇬🇧 UK"}[region]
            lines.append(f"🎬 **Top movies right now — {flag}**\n")

            if entries:
                for i, e in enumerate(entries[:10], 1):
                    name = (e.get("im:name") or {}).get("label", "?")
                    genre = ((e.get("category") or {}).get("attributes") or {}).get("label", "")
                    price = (e.get("im:price") or {}).get("label", "")
                    extra = "  •  ".join(x for x in (genre, price) if x)
                    lines.append(f"{i}. **{name}**" + (f"\n    └ {extra}" if extra else ""))
            else:
                lines.append("  └ ❌ No chart data returned.")

            # what is airing in India today (free, no key)
            try:
                today = datetime.now(IST).strftime("%Y-%m-%d")
                tv = await cached("movie", f"https://api.tvmaze.com/schedule?country=IN&date={today}")
                if tv:
                    lines.append(f"\n📺 **On TV in India today ({today})**\n")
                    seen = set()
                    count = 0
                    for ep in tv:
                        show = (ep.get("show") or {}).get("name")
                        if not show or show in seen:
                            continue
                        seen.add(show)
                        net = ((ep.get("network") or {}).get("name")) or \
                              ((ep.get("webChannel") or {}).get("name")) or ""
                        when = ep.get("airtime") or ""
                        lines.append(f"  • **{show}**" +
                                     (f" — {when}" if when else "") +
                                     (f" `{net}`" if net else ""))
                        count += 1
                        if count >= 10:
                            break
            except Exception:
                lines.append("\n📺 TV schedule unavailable right now.")

            lines.append("\n⚠️ Charts are from iTunes/Apple TV and TVMaze — "
                         "for cinema showtimes check BookMyShow.")
            lines.append("🤖 **Powered by Cipher Elite**")
            await event.reply("\n".join(lines)[:4000])
        except Exception as e:
            await event.reply(
                "🎭 **Cipher Elite Error**\n\n"
                f"❌ **Error:** {str(e)}\n"
                "💡 **Try again in a minute.**"
            )
        finally:
            try:
                await status.delete()
            except Exception:
                pass
