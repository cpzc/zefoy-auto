<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-Powered-2EAD33?style=flat-square&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/Zefoy-Auto-C9386C?style=flat-square" />
  <img src="https://img.shields.io/badge/Single-File-FF6B6B?style=flat-square" />
</p>

<h1 align="center">
  <code>&gt;_ zefoy.py</code>
</h1>

<p align="center">
  <b>Automated TikTok engagement through zefoy.com</b><br>
  <sub>Playwright-based, single-file, zero config</sub>
</p>

<p align="center">
  <a href="#how-it-works">how it works</a> •
  <a href="#install">install</a> •
  <a href="#config">config</a> •
  <a href="#services">services</a> •
  <a href="#comment-hearts">comment hearts</a> •
  <a href="#logs">logs</a>
</p>

---

## what is this

A Python script that automates TikTok engagement using [zefoy.com](https://zefoy.com). It opens a Chromium browser, solves the CAPTCHA via OCR, navigates the site, and sends engagement (likes, views, hearts, etc.) to whichever service you pick.

No browser extensions, no manual interaction required.

---

## install

Clone and run — dependencies install automatically if missing:

```bash
git clone https://github.com/cpzc/zefoy-auto.git
cd zefoy-auto
python zefoy.py
```

Or install manually:

```bash
pip install playwright colorama pytesseract Pillow
playwright install chromium
```

---

## how it works

```
1. you run zefoy.py
2. chromium opens zefoy.com
3. captcha is solved automatically (ocr + image preprocessing)
4. you paste a tiktok video url
5. available services are detected and displayed
6. you pick a service and set the send count
7. engagement is sent with a live countdown in the title bar
8. on completion or rate limit, it loops back for another url
```

---

## config

A `config.json` is created on first run. Edit it to enable notifications.

<details>
<summary><b>Telegram</b></summary>

```json
{
  "telegram_enabled": true,
  "telegram_bot_token": "your-bot-token",
  "telegram_chat_id": "your-chat-id"
}
```

Get a token from [@BotFather](https://t.me/BotFather). Get your chat ID from [@userinfobot](https://t.me/userinfobot).

</details>

<details>
<summary><b>Discord</b></summary>

```json
{
  "discord_webhook": "https://discord.com/api/webhooks/..."
}
```

Right-click a channel → Integrations → Webhooks → New Webhook → Copy URL.

</details>

<details>
<summary><b>Notification toggles</b></summary>

| Key | Default | Description |
|-----|---------|-------------|
| `notify_on_send` | `true` | Send a message on each successful send |
| `notify_on_complete` | `true` | Send a message when the session finishes |

Set either to `false` to disable that notification.

</details>

**Full config example:**

```json
{
  "telegram_enabled": false,
  "telegram_bot_token": "",
  "telegram_chat_id": "",
  "discord_webhook": "",
  "notify_on_send": true,
  "notify_on_complete": true
}
```

---

## services

| Service | Description | Notes |
|---------|-------------|-------|
| Likes | Send likes to a video | |
| Views | Send views to a video | |
| Hearts | Send hearts to a video | |
| Comment Hearts | Heart a specific user's comment | Auto-paginate across pages |
| Favorites | Add video to favorites | |
| Follow | Follow a user | |
| Shares | Send shares to a video | |

Offline services are marked with ✘ and skipped automatically.

---

## comment hearts

This service requires a TikTok username instead of a URL. The script searches all comment entries for that username, navigates across pages if needed, and heart-boosts the comment when found. If the user isn't on any page, it reports that and moves on.

---

## logs

Each run produces a timestamped log file in `logs/`:

```
logs/
├── run_2026-06-28_144702.log
├── run_2026-06-28_153011.log
└── run_2026-06-29_091245.log
```

Logs include timestamps for browser launch, page load, CAPTCHA attempts, service detection, sends, rate limits, pagination, and errors.

---

## project structure

```
zefoy-auto/
├── zefoy.py        # main script
├── config.json     # notification settings
├── .gitignore      # excludes config, logs, cache
├── logs/           # debug output
└── README.md
```

---

## disclaimer

This tool is for educational and research purposes only. Not affiliated with or endorsed by zefoy.com or TikTok. Automated interactions may violate Terms of Service. Use at your own risk.

---

<p align="center">
  <sub>Made by <a href="https://github.com/cpzc">@cpzc</a></sub>
</p>
