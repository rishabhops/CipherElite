# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    github_info
#  Created: 17/07/2026
#
#  Usage:          .gh <username>
# =============================================================================

VERSION = "1.0.0"
CATEGORY = "utilities"

import aiohttp
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

GITHUB_API = "https://api.github.com/users/{}"
GITHUB_REPOS_API = "https://api.github.com/users/{}/repos?per_page=100&sort=updated"


def init(client_instance):
    commands = [
        ".gh <username> - Get a GitHub user's public profile info card",
    ]
    description = "🐙 Fetch public GitHub profile info"
    add_handler("github_info", commands, description)


async def fetch_json(session, url):
    try:
        async with session.get(url) as resp:
            if resp.status == 404:
                return None
            if resp.status != 200:
                return {"_error": resp.status}
            return await resp.json()
    except:
        return {"_error": "connection_error"}


def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def format_twitter(handle):
    if handle:
        return f"@{handle}"
    return "Not provided"


async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.gh(?:\s+(.+))?"))
    @rishabh()
    async def github_info(event):
        username = event.pattern_match.group(1)
        if not username:
            await event.reply("❌ Usage: `.gh <username>`")
            return

        username = username.strip().lstrip("@")
        msg = await event.reply(f"🔎 Fetching GitHub info for **{username}**...")

        async with aiohttp.ClientSession(
            headers={"Accept": "application/vnd.github+json", "User-Agent": "CipherElite-Userbot"}
        ) as session:
            profile = await fetch_json(session, GITHUB_API.format(username))

            if profile is None:
                await msg.edit(f"❌ No GitHub user found with username `{username}`.")
                return
            if profile and profile.get("_error"):
                error_msg = {
                    403: "Rate limit exceeded. Try again later.",
                    404: "User not found.",
                    "connection_error": "Failed to connect to GitHub API.",
                }.get(profile["_error"], f"GitHub API error (status {profile['_error']})")
                await msg.edit(f"❌ {error_msg}")
                return

            repos = await fetch_json(session, GITHUB_REPOS_API.format(username))
            if not isinstance(repos, list):
                repos = []

        # Build language stats from public repo list (skip forks)
        lang_count = {}
        total_stars = 0
        for r in repos:
            if r.get("fork"):
                continue
            total_stars += r.get("stargazers_count", 0)
            lang = r.get("language")
            if lang:
                lang_count[lang] = lang_count.get(lang, 0) + 1

        top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:5]
        lang_str = ", ".join(f"{lang} ({count})" for lang, count in top_langs) or "N/A"

        # Extract profile data
        login = profile.get("login")
        name = profile.get("name") or login
        bio = profile.get("bio") or "No bio provided"
        location = profile.get("location") or "Not specified"
        company = profile.get("company") or "Not specified"
        blog = profile.get("blog") or "None"
        twitter = profile.get("twitter_username")
        followers = format_number(profile.get("followers", 0))
        following = format_number(profile.get("following", 0))
        public_repos = profile.get("public_repos", 0)
        public_gists = profile.get("public_gists", 0)
        created_at = profile.get("created_at", "")[:10]
        html_url = profile.get("html_url")
        avatar = profile.get("avatar_url")
        hireable = profile.get("hireable")

        # Build stylish message
        text = (
            f"🐙 **GitHub Profile**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** {name}\n"
            f"🔖 **Username:** `@{login}`\n"
            f"📝 **Bio:** {bio}\n"
            f"📍 **Location:** {location}\n"
            f"🏢 **Company:** {company}\n"
            f"🔗 **Blog/Site:** {blog}\n"
        )
        if twitter:
            text += f"🐦 **Twitter:** @{twitter}\n"

        text += (
            f"\n📊 **Statistics**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 **Followers:** {followers}   |   **Following:** {following}\n"
            f"📦 **Public Repos:** {public_repos}   |   **Gists:** {public_gists}\n"
            f"⭐ **Total Stars (non-fork):** {total_stars}\n"
            f"💻 **Top Languages:** {lang_str}\n"
            f"📅 **Joined:** {created_at}\n"
        )
        if hireable is True:
            text += "✅ **Open to hire:** Yes\n"

        text += (
            f"\n🔗 **Profile:** {html_url}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 **Powered by CipherElite**"
        )

        # Send profile image with the text as caption
        try:
            if avatar:
                await event.reply(text, file=avatar)
                await msg.delete()
            else:
                await msg.edit(text)
        except Exception:
            await msg.edit(text)