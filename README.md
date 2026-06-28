<div align="center">

# Zefoy Automation

**Fully automated TikTok engagement tool powered by Playwright**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-Powered-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Discord](https://img.shields.io/badge/Discord-Webhooks-5865F2?style=for-the-badge&logo=discord&logoColor=white)](#discord)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](#telegram)

[Features](#features) &nbsp;|&nbsp; [Quick Start](#quick-start) &nbsp;|&nbsp; [Configuration](#configuration) &nbsp;|&nbsp; [Services](#supported-services) &nbsp;|&nbsp; [Disclaimer](#disclaimer)

---

A single-file Python tool that automates TikTok engagement through [zefoy.com](https://zefoy.com) — no browser extension, no manual interaction required.

</div>

---

## Features

<table>
<tr>
<td width="50%">

**Core**
- **Single File** — one `zefoy.py`, nothing else needed
- **All Services** — likes, views, hearts, comment hearts, favorites, follows, shares
- **Auto-CAPTCHA** — OCR with image preprocessing and auto-retry
- **Loop Mode** — returns to URL prompt after each session

</td>
<td width="50%">

**Notifications**
- **Telegram Bot** — real-time alerts on sends and bans
- **Discord Webhooks** — same alerts via webhook
- **Per-Event Toggles** — choose exactly what you get notified about
- **Ban Detection** — auto-stops on 24h+ rate limits

</td>
</tr>
<tr>
<td>

**Automation**
- **Comment Hearts** — enter username once, auto-paginate to find entries
- **Live Countdown** — timer + view count in console title bar
- **Auto-Install** — dependencies install themselves on first run

</td>
<td>

**Developer**
- **Debug Logging** — timestamped per-run log files in `logs/`
- **Clean UI** — box-drawing characters, color-coded status
- **Zero Config** — works out of the box with no setup

</td>
</tr>
</table>

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/cpzc/zefoy-auto.git
cd zefoy-auto
pip install playwright colorama pytesseract Pillow
playwright install chromium
```

> Dependencies auto-install on first run if missing.

### 2. Run

```bash
python zefoy.py
```

### 3. That's it

The tool will:
1. Open a Chromium browser to zefoy.com
2. Solve the CAPTCHA automatically
3. Ask for your TikTok video URL
4. Detect available services and let you pick one
5. Send engagement continuously until rate-limited or done

---

## Configuration

Config is stored in `config.json` and is **auto-created on first run** if missing.

<details>
<summary><b>Telegram Setup</b></summary>

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get your chat ID via [@userinfobot](https://t.me/userinfobot)
3. Edit `config.json`:

```json
{
    "telegram_enabled": true,
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
}
```

</details>

<details>
<summary><b>Discord Setup</b></summary>

1. Right-click a channel → **Integrations** → **Webhooks** → **New Webhook**
2. Copy the webhook URL
3. Edit `config.json`:

```json
{
    "discord_webhook": "https://discord.com/api/webhooks/..."
}
```

</details>

<details>
<summary><b>Notification Toggles</b></summary>

Control which events trigger a message:

| Setting | Default | Description |
|:--------|:-------:|:------------|
| `notify_on_send` | `true` | Message on each successful send |
| `notify_on_complete` | `true` | Message when session finishes |

Set either to `false` to silence that event.

**Example — Discord only, sends only:**

```json
{
    "telegram_enabled": false,
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "discord_webhook": "https://discord.com/api/webhooks/...",
    "notify_on_send": true,
    "notify_on_complete": false
}
```

</details>

---

## Supported Services

| Service | Description | Notes |
|:--------|:------------|:------|
| Likes | Send likes to a video | |
| Views | Send views to a video | |
| Hearts | Send hearts to a video | |
| Comment Hearts | Heart a specific user's comment | Auto-paginate across all pages |
| Favorites | Add video to favorites | |
| Follows | Follow a user | |
| Shares | Send shares to a video | |

> Services marked with ✘ on zefoy are offline and automatically skipped.

---

## Comment Hearts

Comment Hearts have a unique workflow compared to other services:

```
┌─────────────────────────────────────────────────┐
│  1. Tool asks for a TikTok username             │
│  2. Searches all comment entries for it         │
│  3. If not found → clicks "Next Page" & retries │
│  4. When found → heart-boosts that comment      │
│  5. Stops when no more pages exist              │
└─────────────────────────────────────────────────┘
```

---

## Debug Logs

Every run produces a timestamped log file:

```
logs/
├── run_2026-06-28_144702.log
├── run_2026-06-28_153011.log
└── run_2026-06-29_091245.log
```

Each log includes: browser start, page load, CAPTCHA attempts, service detection, sends, rate limits, pagination, and errors.

---

## Project Structure

```
zefoy-auto/
├── zefoy.py          # Everything lives here
├── config.json       # Telegram + Discord settings
├── .gitignore        # Ignores config, logs, cache
├── logs/             # Debug log output
└── README.md         # You're reading this
```

---

## Disclaimer

<div align="center">

**This tool is for educational and research purposes only.**

</div>

- Not affiliated with or endorsed by zefoy.com or TikTok
- Automated interactions may violate Terms of Service
- Use entirely at your own risk
- You are responsible for any consequences

**By using this software, you agree to:**

1. Understand the risks involved (account bans, etc.)
2. Verify compliance with all applicable platform Terms of Service
3. Use the tool responsibly and ethically
4. Accept full liability for any outcomes

---

<div align="center">

Made by [@cpzc](https://github.com/cpzc)

</div>
