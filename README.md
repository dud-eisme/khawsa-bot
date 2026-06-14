# khawsa-bot 🥣

A Discord bot built for the **r/surat** community server — handles onboarding, moderation, and community engagement, with a locally-flavored "Surti attitude" personality running through every interaction.

## Features

**Onboarding**
- Automatically assigns member/bot roles on join
- Sends a DM'd getting-started guide plus a public welcome message with randomized flavor text
- Live member counter channel that updates on join/leave (tracks human members only)

**Moderation** *(role-gated via `MOD_ROLES`)*
- `/kick`, `/ban` — with owner/self-protection checks and permission-hierarchy error handling
- `/safai` — bulk message purge
- `/assign`, `/remove` — role management
- `/rules`, `/howto` — posts formatted server rules and a full navigation guide for new members

**Community / Fun**
- `/ask` — Gemini-powered Q&A command with a custom persona ("Khawsa-Bot") that responds in a mix of English, Gujarati, and Surti slang
- `/afk` — AFK status tracking with automatic nickname tagging and welcome-back messages
- Keyword-triggered responses (greetings, local slang) with per-user cooldowns to avoid spam
- Rotating custom status messages and randomized "ghost ping" events on a scheduled loop
- Empty-mention detection with sassy auto-replies

## Tech Stack
Python · discord.py (slash commands + intents) · Google Gemini API (`google-genai`) · `discord.ext.tasks` for scheduled jobs · `python-dotenv` for config · deployed with **pm2**

## Setup

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```
5. Configure `channel_id.py` and `variables.py` with your server's channel IDs, role names, and flavor text
6. Run: `python main.py`

## Running in production
This bot runs continuously via [pm2](https://pmz.keymetrics.io/):
```
pm2 start main.py --name khawsa-bot --interpreter python3
```

## Server
Serving the **r/surat** Discord community (~450 members).
