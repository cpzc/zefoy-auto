<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-Powered-2EAD33?style=flat-square&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/Zefoy-Auto-C9386C?style=flat-square&logo=ticktock&logoColor=white" />
  <img src="https://img.shields.io/badge/Single-File-FF6B6B?style=flat-square&logo=file&logoColor=white" />
</p>

<h1 align="center">
  <code>&gt;_ zefoy.py</code>
</h1>

<p align="center">
  <b>one file. zero config. full send.</b><br>
  <sub>TikTok engagement on autopilot — powered by Playwright, wrapped in vibes</sub>
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

```
zefoy.py does one thing: send tiktok engagement through zefoy.com.

no browser extensions. no manual clicking. no captcha solving by hand.
just run it, paste a url, pick a service, and let it cook.
```

it handles everything — opening the browser, solving the captcha,
navigating the confusing ui, dodging rate limits, and spamming the
send button until you get what you came for.

---

## install

**the easy way** (auto-installs everything):

```bash
git clone https://github.com/cpzc/zefoy-auto.git
cd zefoy-auto
python zefoy.py
```

it'll pull in `playwright`, `colorama`, `pytesseract`, `Pillow` and
the chromium browser if they're missing.

**the manual way** (if you like doing things yourself):

```bash
pip install playwright colorama pytesseract Pillow
playwright install chromium
```

---

## how it works

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  1. you run it                                              │
│  2. chromium opens zefoy.com                                │
│  3. captcha gets solved automatically (ocr + preprocessing)  │
│  4. you paste a tiktok url                                   │
│  5. it shows you what services are online                    │
│  6. you pick one, set a count, and it starts sending         │
│  7. countdown + view count in the title bar the whole time   │
│  8. when it's done (or rate limited), it loops back          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## config

auto-created on first run. edit `config.json` to enable notifications.

<details>
<summary><b>t.me / bot setup</b></summary>

```json
{
  "telegram_enabled": true,
  "telegram_bot_token": "123456:ABC-DEF...",
  "telegram_chat_id": "987654321"
}
```

get a token from [@BotFather](https://t.me/BotFather).
get your chat id from [@userinfobot](https://t.me/userinfobot).

</details>

<details>
<summary><b>discord webhook</b></summary>

```json
{
  "discord_webhook": "https://discord.com/api/webhooks/..."
}
```

right-click a channel → integrations → webhooks → new webhook → copy url.

</details>

<details>
<summary><b>notification toggles</b></summary>

| key | default | what it does |
|-----|---------|--------------|
| `notify_on_send` | `true` | ping you every time something gets sent |
| `notify_on_complete` | `true` | ping you when the session ends |

set either to `false` to shut it up for that event.

</details>

**full config:**

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

| service | what it does | notes |
|---------|-------------|-------|
| likes | send likes to a video | |
| views | send views to a video | |
| hearts | send hearts to a video | |
| comment hearts | heart a specific comment | auto-paginate, username once |
| favorites | add video to favorites | |
| follow | follow a user | |
| shares | send shares to a video | |

offline services get a ✘ and are skipped automatically.

---

## comment hearts

this one's special. it needs a username, not a url.

```
you type:  @elicacivil
it searches:  all comment entries across all pages
it finds:  that user's comment
it hearts:  that comment
```

if the user isn't on the current page, it clicks "next page"
and keeps looking. if there are no more pages, it tells you
and moves on.

---

## logs

every run gets its own log file:

```
logs/
├── run_2026-06-28_144702.log
├── run_2026-06-28_153011.log
└── run_2026-06-29_091245.log
```

logs include timestamps for: browser launch, page load, captcha
attempts, captcha solve/fail, service detection, send attempts,
rate limits, pagination, and errors.

---

## project structure

```
zefoy-auto/
├── zefoy.py        # the whole thing
├── config.json     # notifications config
├── .gitignore      # keeps config + logs out of git
├── logs/           # debug output
└── README.md       # this file
```

---

## disclaimer

this is for educational purposes. not affiliated with zefoy or tikTok.
automated interactions may violate tos. use at your own risk.
by using this, you accept all responsibility for what happens.

---

<p align="center">
  <code>made by @cpzc</code><br>
  <sub>if this helped you out, a star goes a long way</sub>
</p>
