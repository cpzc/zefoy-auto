[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Playwright](https://img.shields.io/badge/Playwright-Powered-orange.svg)](https://playwright.dev/)

# Zefoy Automation

**Fully automated TikTok engagement tool for zefoy.com**

[Features](#features) | [Quick Start](#quick-start) | [Config](#configuration) | [Services](#services) | [Disclaimer](#disclaimer)

---

## Features

- **Single File** - One `zefoy.py`, zero setup complexity
- **All Services** - Likes, Views, Hearts, Comment Hearts, Favorites, Follows, Shares
- **Auto-CAPTCHA** - OCR with image preprocessing, auto-retry on failure
- **Comment Hearts** - Enter username once, auto-paginate to find entries
- **Live Countdown** - Timer + video view count in console title bar
- **Telegram Notifications** - Get alerts on success, bans, completion
- **Discord Webhooks** - Same alerts via Discord webhook
- **Ban Detection** - Auto-stops on 24h+ rate limits
- **Debug Logging** - Timestamped per-run log files in `logs/`
- **Auto-Install** - Dependencies install themselves on first run
- **Clean UI** - Box-drawing characters, color-coded status
- **Loop Mode** - Returns to URL prompt after completion

---

## Quick Start

### Install

```bash
git clone https://github.com/cpzc/zefoy-auto.git
cd zefoy-auto
pip install playwright colorama pytesseract Pillow
playwright install chromium
```

Dependencies auto-install on first run if missing.

### Usage

```bash
python zefoy.py
```

The tool will:
1. Open a Chromium browser to zefoy.com
2. Solve the CAPTCHA automatically
3. Ask for your TikTok video URL
4. Show available services
5. Send engagement continuously until rate-limited or complete

---

## Configuration

Config is stored in `config.json` (auto-created on first run if missing).

### Telegram

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get your chat ID via [@userinfobot](https://t.me/userinfobot)
3. Edit `config.json`:

```json
{
    "telegram_enabled": true,
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "discord_webhook": ""
}
```

### Discord

1. Right-click a channel > Integrations > Webhooks > New Webhook
2. Copy the webhook URL
3. Edit `config.json`:

```json
{
    "telegram_enabled": false,
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "discord_webhook": "https://discord.com/api/webhooks/..."
}
```

### Notifications

| Event | Telegram | Discord |
|---|---|---|
| Send success | Sent count + result | Sent count + result |
| Session complete | Final summary | Final summary |
| Ban detected | Ban alert | Ban alert |

---

## Services

| Service | What it does | Notes |
|---|---|---|
| Likes | Send likes to video | |
| Views | Send views to video | |
| Hearts | Send hearts to video | |
| Comment Hearts | Heart specific comments | Auto-paginate, enter username once |
| Favorites | Send favorites to video | |
| Follows | Send follows to user | |
| Shares | Send shares to video | |

Services marked with X are offline on zefoy and automatically skipped.

---

## Comment Hearts

Comment Hearts have a unique workflow:

1. Tool asks for a TikTok username
2. It searches all comment entries for that username
3. If not found on the current page, it clicks "Next Page" and retries
4. When found, it heart-boosts that user's comment
5. Stops with "not found on any page" when no more pages exist

---

## Debug Logs

Logs are written to the `logs/` folder with timestamped filenames:

```
logs/run_2026-06-28_144702.log
```

Each log includes timestamps for every event: browser start, page load, CAPTCHA attempts, service detection, sends, rate limits, pagination, and errors.

---

## Project Structure

```
zefoy-auto/
├── zefoy.py          # Everything in one file
├── config.json       # Telegram + Discord config
├── .gitignore        # Ignores config, logs, cache
└── logs/             # Debug log output
```

---

## Disclaimer

**This tool is for educational and research purposes only.**

- Not affiliated with or endorsed by zefoy.com or TikTok
- Automated interactions may violate Terms of Service
- Use entirely at your own risk
- You are responsible for any consequences

**By using this software, you agree to:**
1. Understand the risks (account bans, etc.)
2. Verify compliance with platform ToS
3. Use responsibly
4. Accept full liability

---

Made by [@cpzc](https://github.com/cpzc)
