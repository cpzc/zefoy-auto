from __future__ import annotations
import asyncio
import base64
import hashlib
import io
import json
import os
import random
import re
import sys
import time

def ensure_deps():
    required = {"playwright": "playwright", "easyocr": "easyocr", "numpy": "numpy",
                "PIL": "Pillow", "Crypto": "pycryptodome", "colorama": "colorama"}
    missing = []
    for mod, pkg in required.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Installing: {', '.join(missing)}...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        if "playwright" in missing:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

ensure_deps()

import colorama
colorama.init()

from playwright.async_api import async_playwright
import easyocr
import numpy as np
from PIL import Image, ImageEnhance
from Crypto.Cipher import AES

import shutil as _shutil

class Colors:
    RESET = "\033[0m"
    BLACK   = "\033[30m"; RED     = "\033[31m"; GREEN   = "\033[32m"
    YELLOW  = "\033[33m"; BLUE    = "\033[34m"; MAGENTA = "\033[35m"
    CYAN    = "\033[36m"; WHITE   = "\033[37m"
    BRIGHT_BLACK   = "\033[90m"; BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"; BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"; BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"; BRIGHT_WHITE   = "\033[97m"
    BOLD = "\033[1m"; DIM = "\033[2m"

    @classmethod
    def supports_color(cls) -> bool:
        if hasattr(sys.stdout, 'isatty') and not sys.stdout.isatty():
            return False
        return True

    @classmethod
    def supports_unicode(cls) -> bool:
        if sys.platform != "win32":
            return True
        try:
            import locale
            encoding = locale.getpreferredencoding() or 'utf-8'
            "●○✔✘─│┌┐└┘╭╮╰╯".encode(encoding)
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False

    @classmethod
    def strip(cls, text: str) -> str:
        return re.sub(r'\033\[[0-9;]*m', '', text)

def success(t): return f"{Colors.BRIGHT_GREEN}{t}{Colors.RESET}" if Colors.supports_color() else t
def error(t):   return f"{Colors.BRIGHT_RED}{t}{Colors.RESET}" if Colors.supports_color() else t
def warning(t): return f"{Colors.BRIGHT_YELLOW}{t}{Colors.RESET}" if Colors.supports_color() else t
def info(t):    return f"{Colors.BRIGHT_CYAN}{t}{Colors.RESET}" if Colors.supports_color() else t
def dim(t):     return f"{Colors.DIM}{t}{Colors.RESET}" if Colors.supports_color() else t
def bold(t):    return f"{Colors.BOLD}{t}{Colors.RESET}" if Colors.supports_color() else t

def ok(t):
    sym = "✔" if Colors.supports_unicode() else "[OK]"
    return f"{success(sym)} {t}"

def fail(t):
    sym = "✘" if Colors.supports_unicode() else "[X]"
    return f"{error(sym)} {t}"

def _term_width():
    return _shutil.get_terminal_size((80, 24)).columns

def _box_chars():
    if Colors.supports_unicode():
        return {"tl":"┌","tr":"┐","bl":"└","br":"┘","h":"─","v":"│"}
    return {"tl":"+","tr":"+","bl":"+","br":"+","h":"-","v":"|"}

def psuccess(t): print(ok(t))
def perror(t):   print(error(t))
def pwarning(t): print(warning(t))
def pinfo(t):    print(info(t))
def pdim(t):     print(dim(t))
def pbold(t):    print(bold(t))

def _gradient(text, c1, c2):
    if not Colors.supports_color():
        return text
    chars = list(text)
    n = max(1, len(chars) - 1)
    result = ""
    for i, ch in enumerate(chars):
        ratio = i / n
        r = int(48 + (96 - 48) * ratio)
        g = int(176 + (220 - 176) * ratio)
        b = int(195 + (130 - 195) * ratio)
        result += f"\033[38;2;{r};{g};{b}m{ch}"
    return result + Colors.RESET

def banner():
    bc = _box_chars()
    tw = _term_width()
    box_w = tw - 4
    c = Colors.BRIGHT_CYAN

    print()
    print(f"  {c}{bc['tl']}{bc['h'] * box_w}{bc['tr']}{Colors.RESET}")
    print(f"  {c}{bc['v']}{Colors.RESET}{' ' * (box_w)}{c}{bc['v']}{Colors.RESET}")
    print(f"  {c}{bc['v']}{Colors.RESET}  {_gradient('Z E F O Y', Colors.BRIGHT_CYAN, Colors.BRIGHT_MAGENTA)}{' ' * max(0, box_w - 12)}  {c}{bc['v']}{Colors.RESET}")
    print(f"  {c}{bc['v']}{Colors.RESET}  {dim('A U T O M A T I O N')}{' ' * max(0, box_w - 18)}  {c}{bc['v']}{Colors.RESET}")
    print(f"  {c}{bc['v']}{Colors.RESET}{' ' * (box_w)}{c}{bc['v']}{Colors.RESET}")
    h = bc['h']
    print(f"  {dim(f'  {h * (box_w - 4)}')}")
    print(f"  {c}{bc['v']}{Colors.RESET}  {dim('by')} {_gradient('@cpzc', Colors.BRIGHT_GREEN, Colors.BRIGHT_CYAN)}  {dim('|')}  {dim('TikTok Engagement Engine')}{' ' * max(0, box_w - 45 - 6)}  {c}{bc['v']}{Colors.RESET}")
    print(f"  {c}{bc['v']}{Colors.RESET}{' ' * (box_w)}{c}{bc['v']}{Colors.RESET}")
    print(f"  {c}{bc['bl']}{bc['h'] * box_w}{bc['br']}{Colors.RESET}")
    print()

def section(title, color=Colors.BRIGHT_CYAN):
    bc = _box_chars()
    tw = _term_width()
    inner = tw - 6
    left = 3
    right = inner - left - len(title) - 2
    if right < 0:
        right = 0
    print()
    print(f"  {color}{bc['tl']}{bc['h'] * left} {bold(title)} {bc['h'] * right}{bc['tr']}{Colors.RESET}")

def footer(color=Colors.BRIGHT_CYAN):
    bc = _box_chars()
    tw = _term_width()
    print(f"  {color}{bc['bl']}{bc['h'] * (tw - 4)}{bc['br']}{Colors.RESET}")
    print()

def progress_bar(current, total, width=30, color=Colors.BRIGHT_CYAN):
    if total == 0:
        return ""
    filled = int(width * current / total)
    bar = f"{'█' * filled}{'░' * (width - filled)}"
    pct = int(100 * current / total)
    return f"{color}{bar}{Colors.RESET} {bold(f'{pct}%')} {dim(f'({current}/{total})')}"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

_LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(_LOGS_DIR, exist_ok=True)
_LOG_FILE = os.path.join(_LOGS_DIR, f"run_{time.strftime('%Y-%m-%d_%H%M%S')}.log")

def _strip_ansi(text):
    return re.sub(r'\033\[[0-9;]*m', '', str(text))

def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        template = {"telegram_enabled": False, "telegram_bot_token": "", "telegram_chat_id": "", "discord_webhook": "", "notify_on_send": True, "notify_on_complete": True}
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(template, f, indent=4)
        except:
            pass
        return template
    except:
        return {}

_config = load_config()
TELEGRAM_ENABLED = _config.get("telegram_enabled", False)
TELEGRAM_BOT_TOKEN = _config.get("telegram_bot_token", "")
TELEGRAM_CHAT_ID = _config.get("telegram_chat_id", "")
DISCORD_WEBHOOK = _config.get("discord_webhook", "")
NOTIFY_ON_SEND = _config.get("notify_on_send", True)
NOTIFY_ON_COMPLETE = _config.get("notify_on_complete", True)

async def send_telegram(message: str):
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        await asyncio.to_thread(urllib.request.urlopen, req, timeout=10, context=ctx)
    except Exception as e:
        pwarning(f"Telegram error: {e}")

async def send_discord(message: str):
    if not DISCORD_WEBHOOK:
        return
    try:
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        data = json.dumps({"content": message}).encode()
        req = urllib.request.Request(DISCORD_WEBHOOK, data=data, headers={"Content-Type": "application/json"})
        await asyncio.to_thread(urllib.request.urlopen, req, timeout=10, context=ctx)
    except Exception as e:
        pwarning(f"Discord error: {e}")


def set_title(text: str):
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(text)
    except:
        pass

async def countdown_sleep(seconds: int, prefix: str = ""):
    pfx = f"{prefix} | " if prefix else ""
    for remaining in range(seconds, 0, -1):
        bar_w = 20
        filled = int(bar_w * (seconds - remaining) / seconds) if seconds > 1 else bar_w
        bar = f"{'█' * filled}{'░' * (bar_w - filled)}"
        line = f"  {dim(f'⏳')} {Colors.BRIGHT_CYAN}{bar}{Colors.RESET} {dim(format_time(remaining))}"
        print(f"\r{line:<80}", end="", flush=True)
        set_title(f"@cpzc/zefoy - {pfx}{format_time(remaining)}")
        await asyncio.sleep(1)
    line = f"  {ok('Done')}"
    print(f"\r{line:<80}", end="", flush=True)
    print()
    set_title("@cpzc/zefoy")


DISMISS_ALERTS = "window.alert = function() { return true; }; window.confirm = function() { return true; };"

BLOCK_NOTIFICATIONS = "Object.defineProperty(Notification, 'permission', { value: 'denied' }); Notification.requestPermission = function() { return Promise.resolve('denied'); };"

REMOVE_AD_OVERLAYS = """() => {
    document.querySelectorAll('iframe').forEach(el => el.remove());
    document.querySelectorAll('.fc-dialog-overlay').forEach(el => el.remove());
    document.querySelectorAll('.adsbygoogle').forEach(el => el.remove());
    document.querySelectorAll('[class*="fullscreen"]').forEach(el => { if (el.querySelector('iframe')) el.remove(); });
    document.querySelectorAll('.fc-monetization-dialog-container, .fc-message-root').forEach(el => el.remove());
    return true;
}"""

BLOCK_FC_POPUPS = """(() => {
    const cleanPage = () => {
        document.querySelectorAll('iframe').forEach(el => el.remove());
        document.querySelectorAll('.fc-monetization-dialog-container, .fc-message-root, .fc-dialog-overlay, .fc-consent-root').forEach(el => el.remove());
        document.querySelectorAll('.adsbygoogle').forEach(el => el.remove());
        document.querySelectorAll('button').forEach(btn => {
            if (btn.textContent.includes('Consent') && btn.offsetParent !== null) btn.click();
        });
    };
    setTimeout(cleanPage, 800);
    const observer = new MutationObserver(cleanPage);
    if (document.body) observer.observe(document.body, { childList: true, subtree: true });
    else document.addEventListener('DOMContentLoaded', () => observer.observe(document.body, { childList: true, subtree: true }));
})();"""

MOUSE_SIMULATION_K9X = """(() => {
    function generateK9xMouseData() {
        const points = [];
        const numPoints = Math.floor(Math.random() * 16) + 12;
        for (let i = 0; i < numPoints; i++) {
            const x = Math.floor(Math.random() * 1850) + 50;
            const y = Math.floor(Math.random() * 950) + 50;
            const d = (Math.random() * 2.75 + 0.05).toFixed(4);
            const g = Math.random() > 0.65 ? "True" : "False";
            points.push(`x=${x}&y=${y}&d=${d}&g=${g}`);
        }
        const raw = points.join("|");
        let xored = "";
        for (let i = 0; i < raw.length; i++) {
            xored += String.fromCharCode(raw.charCodeAt(i) ^ ((i % 5) + 77));
        }
        const wrapped = "K9x!" + xored + "K9x!";
        const encoded = btoa(wrapped);
        let reversed = encoded.split("").reverse().join("");
        while (reversed.length % 4 !== 0) reversed += "=";
        return reversed;
    }
    function injectMouseData() {
        const mouseData = generateK9xMouseData();
        document.querySelectorAll('input[type="hidden"]').forEach(input => {
            if (!input.value && input.name !== 'captcha_encoded') input.value = mouseData;
        });
        window.__zefoyMouseData = mouseData;
    }
    setTimeout(injectMouseData, 500);
    setTimeout(injectMouseData, 1500);
    setTimeout(injectMouseData, 3000);
    document.addEventListener('submit', function(e) { injectMouseData(); }, true);
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) setTimeout(injectMouseData, 50);
    }, true);
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) { if (m.addedNodes.length > 0) setTimeout(injectMouseData, 100); });
    });
    if (document.body) observer.observe(document.body, { childList: true, subtree: true });
    else document.addEventListener('DOMContentLoaded', function() {
        observer.observe(document.body, { childList: true, subtree: true }); injectMouseData();
    });
    window.generateK9xMouseData = generateK9xMouseData;
    window.injectMouseData = injectMouseData;
})();"""

GENERATE_CF_OB_TE = """(() => {
    function generateCfObTeCookie() {
        const source = "HTMLButtonElement.onclick@https://zefoy.com/:1:1";
        const kod = "DOMContentLoaded";
        const payload = `Kod: ${kod}\\nsource: ${source}`;
        const cookieValue = btoa(payload);
        const expiry = new Date(Date.now() + 5 * 60 * 60 * 1000).toUTCString();
        document.cookie = `cf_ob_te=${cookieValue}; Path=/; Expires=${expiry}`;
        return cookieValue;
    }
    generateCfObTeCookie();
    setInterval(generateCfObTeCookie, 60000);
    window.generateCfObTeCookie = generateCfObTeCookie;
})();"""


ZEFOY_AES_KEY = "43fdda1192dde7f8ffff7161e13580d7"

GPU_OPTIONS = [
    {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2060 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"},
    {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11)"},
]
SCREEN_RESOLUTIONS = [
    {"width": 1920, "height": 1080}, {"width": 2560, "height": 1440},
    {"width": 1366, "height": 768}, {"width": 1536, "height": 864},
]

def evp_bytes_to_key(password, salt):
    dtot = b""
    d = b""
    while len(dtot) < 48:
        d = hashlib.md5(d + password + salt).digest()
        dtot += d
    return dtot[:32], dtot[32:48]

def cryptojs_aes_encrypt(plaintext):
    password = ZEFOY_AES_KEY
    salt = os.urandom(8)
    key, iv = evp_bytes_to_key(password.encode(), salt)
    block_size = 16
    padding_len = block_size - (len(plaintext.encode()) % block_size)
    padded = plaintext.encode() + bytes([padding_len] * padding_len)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(padded)
    return {"ct": base64.b64encode(ct).decode(), "iv": iv.hex(), "s": salt.hex()}

def generate_fingerprint():
    gpu = random.choice(GPU_OPTIONS)
    screen = random.choice(SCREEN_RESOLUTIONS)
    return {
        "deviceInfo": {
            "cpuCores": random.choice([4, 6, 8, 12]),
            "cpuLoad": random.randint(1, 20),
            "deviceMemoryGB": random.choice([4, 8, 16]),
            "platform": "Win32", "maxTouchPoints": 0,
            "msMaxTouchPoints": "Not Supported",
            "gpu": gpu,
            "battery": {"charging": random.choice([True, False]), "level": round(random.uniform(0.2, 1.0), 2), "chargingTime": 0, "dischargingTime": None},
            "stylusDetection": random.choice(["Yes", "No"]), "touchSupport": "No"
        },
        "browserInfo": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "timezone": "America/New_York", "timezoneOffset": -240,
            "localeDateTime": time.strftime("%m/%d/%Y, %I:%M:%S %p"),
            "localUnixTime": int(time.time()),
            "calendar": "gregory", "day": "numeric", "locale": "en-US",
            "month": "numeric", "numberingSystem": "latn", "year": "numeric",
            "appName": "Netscape",
            "appVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "vendor": "Google Inc.", "language": "en-US", "languages": ["en-US", "en"],
            "cookieEnabled": True, "onlineStatus": "Online", "javaEnabled": False,
            "doNotTrack": None, "referrerHeader": "None", "httpsConnection": "Yes",
            "historyLength": random.randint(1, 50), "mimeTypes": random.choice([2, 3, 4]),
            "plugins": random.choice([4, 5, 6]), "webdriver": False,
            "pageVisibility": "visible", "isBot": "No",
            "featuresSupported": {
                "geolocation": "Yes", "serviceWorker": "Yes", "localStorage": "Yes",
                "sessionStorage": "Yes", "indexedDB": "Yes", "notifications": "Yes",
                "notificationsFirebase": "default", "clipboard": "Yes", "pushAPI": "Yes",
                "webRTC": "Yes", "gamepadAPI": "Yes", "speechSynthesis": "Yes",
                "webGL": "Yes", "vibrationAPI": "Yes", "deviceMotion": "Yes",
                "deviceOrientation": "Yes", "wakeLock": "Yes", "serial": "Yes",
                "usb": "Yes", "networkInformation": "Yes", "screenCapture": "Yes",
                "fullscreenAPI": "Yes", "pictureInPicture": "Yes"
            }
        },
        "screenInfo": {
            "width": screen["width"], "height": screen["height"],
            "colorDepth": 24, "pixelDepth": 24,
            "devicePixelRatio": random.choice([1, 1.25, 1.5, 2]),
            "orientation": "landscape-primary", "screenOrientationAngle": 0,
            "availableWidth": screen["width"], "availableHeight": screen["height"] - 40,
            "screenLeft": 0, "screenTop": 0,
            "outerWidth": screen["width"], "outerHeight": screen["height"] - 40,
            "innerWidth": screen["width"], "innerHeight": screen["height"] - 127
        },
        "otherData": {
            "mouseAvailable": "Yes", "keyboardAvailable": "Yes",
            "bluetoothSupport": random.choice(["Yes", "No"]), "usbSupport": "Yes",
            "gamepadSupport": "Yes", "incognitoMode": "No"
        },
        "storageInfo": {
            "localStorage": random.randint(0, 15), "sessionStorage": random.randint(0, 5),
            "indexedDB": "Available", "cacheStorage": "Available",
            "storageEstimate": {
                "quota": random.randint(150000000000, 200000000000),
                "usage": random.randint(5000, 100000),
                "usageDetails": {"indexedDB": random.randint(5000, 50000)}
            }
        }
    }

def get_spoofed_captcha_encoded():
    fingerprint = generate_fingerprint()
    fingerprint_json = json.dumps(fingerprint, separators=(",", ":"))
    encrypted = cryptojs_aes_encrypt(fingerprint_json)
    return json.dumps(encrypted, separators=(",", ":"))


SPOOF_FINGERPRINT = """(() => {
    function setSpoofedFingerprint(value) { window.__zefoy_spoofed_fingerprint = value; }
    function spoofCaptchaEncoded() {
        const spoofed = window.__zefoy_spoofed_fingerprint;
        if (!spoofed) return false;
        document.querySelectorAll('input[name="captcha_encoded"], #captcha_encoded').forEach(field => {
            if (field) field.value = spoofed;
        });
        return true;
    }
    document.addEventListener('submit', function(e) { spoofCaptchaEncoded(); }, true);
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) setTimeout(spoofCaptchaEncoded, 10);
    }, true);
    const observer = new MutationObserver(function() { spoofCaptchaEncoded(); });
    if (document.body) observer.observe(document.body, { childList: true, subtree: true });
    else document.addEventListener('DOMContentLoaded', function() {
        observer.observe(document.body, { childList: true, subtree: true });
    });
    window.setSpoofedFingerprint = setSpoofedFingerprint;
    window.spoofCaptchaEncoded = spoofCaptchaEncoded;
})();"""


def parse_wait_time(text):
    if "READY" in text.upper():
        return 0
    hours = minutes = seconds = 0
    m = re.search(r"(\d+)\s*hour", text)
    if m: hours = int(m.group(1))
    m = re.search(r"(\d+)\s*minute", text)
    if m: minutes = int(m.group(1))
    m = re.search(r"(\d+)\s*second", text)
    if m: seconds = int(m.group(1))
    if hours or minutes or seconds:
        return hours * 3600 + minutes * 60 + seconds
    if text and ("too many requests" in text.lower() or "slow down" in text.lower()):
        return 60
    return 0

def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0: return f"{h}h {m}m {s}s"
    if m > 0: return f"{m}m {s}s"
    return f"{s}s"


_ocr_reader = None

def get_reader():
    global _ocr_reader
    if _ocr_reader is None:
        pdim("Loading OCR engine...")
        _ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _ocr_reader

def preprocess_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = img.resize((img.width * 2, img.height * 2))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except:
        return image_bytes

def run_ocr(image_bytes):
    try:
        reader = get_reader()
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)
        results = reader.readtext(img_array, detail=0, paragraph=True)
        if results:
            text = ''.join(results)
            text = text.strip()
            text = text.replace('5', 's')
            text = text.replace('0', 'o')
            text = text.replace('+', 't')
            text = text.replace('1', 'l')
            text = text.replace('4', 'a')
            text = text.replace('3', 'e')
            text = text.replace('7', 't')
            text = text.replace('$', 's')
            text = text.replace('@', 'a')
            text = text.replace('f', 't')
            text = re.sub(r'[^a-zA-Z]', '', text).lower()
            return text if len(text) >= 3 else ""
        return ""
    except Exception as e:
        perror(f"OCR error: {e}")
        return ""


SERVICES = {
    "hearts": {"name": "Hearts", "selector": ".t-hearts-button"},
    "favorites": {"name": "Favorites", "selector": ".t-favorites-button"},
    "chearts": {"name": "Comment Hearts", "selector": ".t-chearts-button"},
    "followers": {"name": "Followers", "selector": ".t-followers-button"},
    "views": {"name": "Views", "selector": ".t-views-button"},
    "shares": {"name": "Shares", "selector": ".t-shares-button"},
    "livestream": {"name": "Live Stream", "selector": ".t-livestream-button"},
    "repost": {"name": "Repost", "selector": ".t-repost-button"},
}

IMPLEMENTED = ["hearts", "favorites", "chearts", "followers", "views", "shares"]

MAIN_PAGE_SELECTORS = [".t-hearts-button", ".t-followers-button", ".t-views-button", ".t-favorites-button", ".t-chearts-button", ".t-shares-button"]


def ask(question, options=None, default=None):
    if options:
        print(f"\n  {bold(question)}")
        for i, opt in enumerate(options, 1):
            marker = f" {dim('(default)')}" if opt == default else ""
            print(f"    {info(str(i) + '.') } {opt}{marker}")
        while True:
            choice = input(f"\n  {bold('Your choice')}: ").strip()
            if not choice and default:
                return default
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
            except ValueError:
                pass
            perror("  Invalid choice, try again.")
    else:
        suffix = f" {dim(f'[{default}]')}" if default else ""
        answer = input(f"\n  {bold(question)}{suffix}: ").strip()
        return answer if answer else default


async def main_playwright(url: str, auto_captcha: bool, count: int, headless: bool):
    clear_screen()
    print()
    banner()

    pdim("Starting browser...")
    log(f"Starting browser headless={headless}")
    pw = None
    browser = None
    try:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled', '--disable-infobars', '--no-first-run']
        )
        log("Browser launched successfully")
    except Exception as e:
        log(f"Browser launch failed: {e}", "ERROR")
        perror(f"Failed to start browser: {e}")
        return
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    )
    await context.clear_cookies()
    page = await context.new_page()
    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(60000)

    async def handle_dialog(dialog):
        await dialog.accept()
    page.on("dialog", handle_dialog)

    spoofed_fp = get_spoofed_captcha_encoded()
    for script in [DISMISS_ALERTS, BLOCK_NOTIFICATIONS, BLOCK_FC_POPUPS, GENERATE_CF_OB_TE, MOUSE_SIMULATION_K9X, SPOOF_FINGERPRINT]:
        await page.add_init_script(script)
    await page.add_init_script(f"window.__zefoy_spoofed_fingerprint = {spoofed_fp!r};")

    try:
        pdim("Opening zefoy.com...")
        log("Navigating to zefoy.com")
        await page.goto("https://zefoy.com", wait_until="domcontentloaded", timeout=60000)
        log("Page loaded")
        await asyncio.sleep(0.05)

        await page.evaluate(REMOVE_AD_OVERLAYS)
        for sel in ['button:has-text("Consent")', '.fc-cta-consent']:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=500):
                    await btn.click(force=True)
                    await asyncio.sleep(0.05)
            except: pass

        clear_screen()
        banner()
        section("CAPTCHA REQUIRED", Colors.BRIGHT_YELLOW)
        print()

        solved = False
        for attempt in range(1, 26):
            log(f"CAPTCHA attempt {attempt}/25 (auto={auto_captcha})")
            print(f"     {dim(f'Attempt')} {bold(str(attempt) + '/25')}")
            print()

            if auto_captcha:
                for _ in range(20):
                    loaded = await page.evaluate("""() => {
                        const img = document.getElementById('captcha-img');
                        if (img && img.src && img.src.length > 10 && img.complete && img.naturalWidth > 50) return true;
                        return false;
                    }""")
                    if loaded: break
                    await asyncio.sleep(0.05)

                captcha_el = page.locator('#captcha-img')
                try:
                    image = await captcha_el.screenshot()
                except:
                    image = None

                if not image:
                    perror("Could not get CAPTCHA image")
                    if attempt < 25:
                        await page.goto("https://zefoy.com", timeout=10000)
                        await asyncio.sleep(0.05)
                        await page.evaluate(REMOVE_AD_OVERLAYS)
                    continue

                processed = preprocess_image(image)
                text = run_ocr(processed)
                if not text:
                    pwarning("OCR could not read it")
                    if attempt < 25:
                        await page.goto("https://zefoy.com", timeout=10000)
                        await asyncio.sleep(0.05)
                        await page.evaluate(REMOVE_AD_OVERLAYS)
                    continue
                pinfo(f"OCR sees: {text}")
                log(f"OCR result: {text}")
                print()
            else:
                print()
                pdim("Look at the browser window and read the CAPTCHA.")
                text = input("  Type what you see: ").strip()
                if not text: continue

            try:
                inp = page.locator('#captchatoken')
                await inp.fill(text)
                await asyncio.sleep(0.05)
                btn = page.locator('.submit-captcha')
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                else:
                    await page.locator('button[type="submit"]').first.click()
                await asyncio.sleep(1)

                solved_check = await page.evaluate("""() => {
                    for (const sel of [".t-hearts-button", ".t-followers-button", ".t-views-button", ".t-favorites-button", ".t-chearts-button", ".t-shares-button"]) {
                        const el = document.querySelector(sel);
                        if (el && el.offsetParent !== null) return true;
                    }
                    return false;
                }""")
                if solved_check:
                    solved = True
                    log("CAPTCHA solved")
                    print()
                    psuccess("CAPTCHA solved!")
                    break

                has_error = await page.evaluate("""() => {
                    const m = document.getElementById('zbcd');
                    return m && m.offsetParent !== null;
                }""")
                if has_error:
                    log("CAPTCHA wrong answer (error modal)", "WARN")
                    pwarning("Wrong answer, dismissing error...")
                    for sel in ['.modal .close', 'button[data-dismiss="modal"]']:
                        try:
                            b = page.locator(sel).first
                            if await b.is_visible(timeout=500): await b.click(); await asyncio.sleep(0.05)
                        except: pass
                else:
                    pwarning("Wrong answer, reloading...")
            except Exception as e:
                perror(f"Error: {e}")

            if attempt < 25:
                await page.goto("https://zefoy.com", timeout=10000)
                await asyncio.sleep(0.05)
                await page.evaluate(REMOVE_AD_OVERLAYS)

        if not solved:
            log("CAPTCHA failed after 25 attempts", "ERROR")
            print()
            perror("Failed to solve CAPTCHA. Exiting.")
            await browser.close(); await pw.stop(); return

        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        await asyncio.sleep(1)
        await page.evaluate(REMOVE_AD_OVERLAYS)

        clear_screen()
        banner()
        pdim("Checking available services...")
        log("Detecting available services")

        available = {}
        selectable = []
        for key, config in SERVICES.items():
            try:
                btn = page.locator(config["selector"])
                is_visible = await btn.is_visible(timeout=2000)
                if is_visible:
                    is_disabled = await page.evaluate("""(selector) => {
                        const el = document.querySelector(selector);
                        if (!el) return true;
                        if (el.disabled) return true;
                        const cls = (el.getAttribute('class') || '').toLowerCase();
                        if (cls.includes('disabled')) return true;
                        let parent = el.parentElement;
                        while (parent && parent !== document.body) {
                            if (parent.disabled) return true;
                            const pcls = (parent.getAttribute('class') || '').toLowerCase();
                            if (pcls.includes('disabled')) return true;
                            parent = parent.parentElement;
                        }
                        return false;
                    }""", config["selector"])
                    is_available = not is_disabled
                    available[key] = is_available
                    if is_available:
                        selectable.append(key)
                else:
                    available[key] = False
            except Exception:
                available[key] = False

        print()
        section("SERVICE STATUS")
        print()
        sel_num = 1
        for key, config in SERVICES.items():
            name = config["name"]
            if available.get(key, False):
                num_text = str(sel_num) + "."
                print(f"     {ok(f'{bold(num_text)}  {name}')}")
                log(f"Service available: {name}")
                sel_num += 1
            else:
                dash = dim("-")
                print(f"     {fail(f'{dash}  {dim(name)}')}")
        print()

        if not selectable:
            perror("No services available! Try again later.")
            await browser.close(); await pw.stop(); return

        sel_map = {str(i+1): k for i, k in enumerate(selectable)}
        print()
        section("SELECT SERVICE")
        print()
        for i, k in enumerate(selectable, 1):
            print(f"     {info(bold(str(i) + '.'))}  {SERVICES[k]['name']}")
        print()
        choice = input(f"  {bold('Enter number')} (1-{len(selectable)}) {dim('[1]')}: ").strip() or "1"
        while choice not in sel_map:
            choice = input(f"  {error('Invalid.')} Enter number (1-{len(selectable)}) {dim('[1]')}: ").strip() or "1"
        service_key = sel_map[choice]

        service_name = SERVICES[service_key]["name"]
        btn_selector = SERVICES[service_key]["selector"]

        comment_username = ""
        if service_key == "chearts":
            comment_username = ask("Enter the TikTok username to send comment hearts to").strip()
            if not comment_username:
                perror("Comment Hearts requires a username."); return
            psuccess(f"Sending comment hearts to @{comment_username}")

        sent = 0

        pdim(f"Opening {service_name} panel...")
        await page.evaluate(REMOVE_AD_OVERLAYS)
        try:
            await page.locator(btn_selector).click(force=True)
        except:
            pass
        await asyncio.sleep(2)
        await page.evaluate(REMOVE_AD_OVERLAYS)

        panel_open = await page.evaluate("""() => {
            const inputs = document.querySelectorAll('input[placeholder="Enter Video URL"]');
            for (const inp of inputs) {
                const rect = inp.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) return true;
            }
            return false;
        }""")
        if not panel_open:
            pwarning("Panel may not be open, retrying...")
            await page.locator(btn_selector).click(force=True)
            await asyncio.sleep(2)

        pdim("Entering video URL...")
        url_filled = False
        for sel in ['input[placeholder="Enter Video URL"]:visible', 'input[type="search"]:visible']:
            try:
                inp = page.locator(sel).first
                if await inp.is_visible(timeout=2000):
                    await inp.fill(url)
                    url_filled = True
                    break
            except: continue
        if not url_filled:
            await page.evaluate("""([url]) => {
                const inputs = document.querySelectorAll('input[placeholder="Enter Video URL"]');
                for (const input of inputs) {
                    const rect = input.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        input.value = url;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        return true;
                    }
                }
                return false;
            }""", [url])
        await asyncio.sleep(1)
        await page.evaluate(REMOVE_AD_OVERLAYS)

        for i in range(count):
            clear_screen()
            banner()
            section(f"{service_name}")
            print()
            print(f"     {progress_bar(i, count)}")
            print()
            attempt_success = False
            rate_limit_count = 0
            title_prefix = f"{service_name} ({i+1}/{count})"

            while not attempt_success:
                try:
                    log(f"Send {i+1}/{count}: Searching...")
                    pdim("Searching...")
                    try:
                        btn = page.locator('button:has-text("Search"):visible')
                        if await btn.count() > 0:
                            await btn.first.click(timeout=3000)
                    except:
                        pass
                    await asyncio.sleep(2.5)

                    rate_limit_text = ""
                    for _ in range(8):
                        try:
                            body_text = await page.evaluate("() => document.body.innerText")
                            for line in body_text.split('\n'):
                                line = line.strip()
                                if not line: continue
                                if re.search(r"Please wait \d+ minute.*\d+ second", line, re.I):
                                    rate_limit_text = line; break
                                if re.search(r"Please wait \d+ second", line, re.I):
                                    rate_limit_text = line; break
                                if re.search(r"\d+ minute.*\d+ second.*before", line, re.I):
                                    rate_limit_text = line; break
                                if re.search(r"\d+ second.*before trying", line, re.I):
                                    rate_limit_text = line; break
                                if re.search(r"too many requests", line, re.I):
                                    rate_limit_text = line; break
                                if re.search(r"slow down", line, re.I):
                                    rate_limit_text = line; break
                        except: pass
                        if rate_limit_text: break
                        await asyncio.sleep(0.5)

                    if rate_limit_text:
                        wt = parse_wait_time(rate_limit_text)
                        if wt >= 86400:
                            hours = wt // 3600
                            log(f"BANNED: {hours} hour rate limit", "ERROR")
                            print()
                            perror(f"BANNED! {hours} hour rate limit!")
                            await browser.close(); await pw.stop(); return
                        log(f"Rate limited: {format_time(wt)}")
                        pwarning(f"Rate limited. Waiting {format_time(wt)}...")
                        await countdown_sleep(wt + 3, title_prefix)
                        continue

                    if service_key == "chearts":
                        log(f"Searching for @{comment_username}")
                        pinfo(f"Looking for @{comment_username}...")
                        await asyncio.sleep(2)

                        panel_html = await page.evaluate("""() => {
                            const panel = document.getElementById('c2VuZC9mb2xsb3dlcnNfdGlrdG9r');
                            return panel ? panel.innerHTML : '';
                        }""")
                        if not panel_html or len(panel_html.strip()) < 10:
                            log("Panel empty, retrying", "WARN")
                            pwarning("Panel empty, waiting more...")
                            await asyncio.sleep(2)
                            panel_html = await page.evaluate("""() => {
                                const panel = document.getElementById('c2VuZC9mb2xsb3dlcnNfdGlrdG9r');
                                return panel ? panel.innerHTML : '';
                            }""")

                        if not panel_html or len(panel_html.strip()) < 10:
                            perror("No panel content loaded after Search")
                            continue

                        try:
                            await page.locator('#c2VuZC9mb2xsb3dlcnNfdGlrdG9r button[type="submit"]').click(force=True)
                            psuccess("Clicked comment count button")
                            await asyncio.sleep(2.5)
                        except Exception as e:
                            pwarning(f"Count button click failed: {e}")
                            continue

                        page_attempt = 0
                        max_pages = 100
                        entry_found = False

                        while page_attempt < max_pages:
                            entry_found = await page.evaluate("""(username) => {
                                const panel = document.getElementById('c2VuZC9mb2xsb3dlcnNfdGlrdG9r');
                                if (!panel) return false;
                                const forms = panel.querySelectorAll('form');
                                for (const f of forms) {
                                    const text = (f.textContent || '').trim().toLowerCase();
                                    if (text.includes('@' + username) || text.includes(username)) {
                                        f.setAttribute('data-zefoy-form', '');
                                        return true;
                                    }
                                }
                                return false;
                            }""", comment_username.lower())

                            if entry_found:
                                log(f"Found @{comment_username} on page {page_attempt + 1}")
                                break

                            log(f"@{comment_username} not found on page {page_attempt + 1}", "WARN")
                            pwarning(f"@{comment_username} not found on page {page_attempt + 1}")

                            next_btn = page.locator('#c2VuZC9mb2xsb3dlcnNfdGlrdG9r li[title="Next"] button').first
                            has_next = await next_btn.count() > 0

                            if has_next and await next_btn.is_disabled():
                                has_next = False

                            if not has_next:
                                log(f"@{comment_username} not found on any page", "ERROR")
                                perror(f"@{comment_username} not found on any page")
                                entries_text = await page.evaluate("""() => {
                                    const panel = document.getElementById('c2VuZC9mb2xsb3dlcnNfdGlrdG9r');
                                    if (!panel) return [];
                                    const all = panel.querySelectorAll('*');
                                    const seen = new Set();
                                    const res = [];
                                    for (const el of all) {
                                        const t = (el.textContent || '').trim();
                                        if (t.length > 1 && t.length < 200 && !seen.has(t)) {
                                            seen.add(t); res.push(t);
                                        }
                                    }
                                    return res.slice(0, 20);
                                }""")
                                if entries_text:
                                    pinfo("Entries found in panel:")
                                    for t in entries_text:
                                        print(f"    {t[:80]}")
                                break

                            psuccess("Going to next page...")
                            try:
                                await next_btn.click(force=True, timeout=5000)
                            except Exception as e:
                                pwarning(f"Next click failed ({e}), trying JS...")
                                await page.evaluate("""() => {
                                    const btn = document.querySelector('#c2VuZC9mb2xsb3dlcnNfdGlrdG9r li[title="Next"] button');
                                    if (btn) btn.click();
                                }""")
                            await asyncio.sleep(2.5)
                            page_attempt += 1

                        if not entry_found:
                            continue

                        psuccess(f"Found entry for @{comment_username}")
                        await asyncio.sleep(0.05)

                        try:
                            select_el = page.locator('[data-zefoy-form] select')
                            if await select_el.count() > 0:
                                option_100 = page.locator('[data-zefoy-form] select option[value="100"]')
                                if await option_100.count() > 0:
                                    await select_el.first.select_option(value="100")
                                    psuccess("Selected 100 from dropdown")
                                    await asyncio.sleep(0.05)
                                else:
                                    opt = page.locator('[data-zefoy-form] select option:has-text("100")')
                                    if await opt.count() > 0:
                                        val = await opt.first.get_attribute('value')
                                        await select_el.first.select_option(value=val)
                                        psuccess("Selected 100 from dropdown")
                                        await asyncio.sleep(0.05)
                                    else:
                                        pwarning("No 100 option in dropdown")
                            else:
                                pwarning("No select found in form")
                        except Exception as e:
                            pwarning(f"100 selection failed: {e}")

                        pdim("Sending...")
                        await asyncio.sleep(0.05)
                        clicked = False

                        try:
                            send_btn = page.locator('[data-zefoy-form] button[type="submit"]').first
                            if await send_btn.count() > 0:
                                await send_btn.click(force=True)
                                clicked = True
                                psuccess("Clicked heart send button")
                        except Exception as e:
                            pwarning(f"Send button click failed: {e}")

                        if not clicked:
                            btn_info = await page.evaluate("""() => {
                                const form = document.querySelector('[data-zefoy-form]');
                                if (!form) return [];
                                const btns = form.querySelectorAll('button');
                                return Array.from(btns).map((b, i) => ({
                                    idx: i, text: (b.textContent || '').trim().substring(0, 30),
                                    vis: b.getBoundingClientRect().width > 0,
                                    disabled: b.disabled, type: b.type || '',
                                    html: b.innerHTML.substring(0, 100)
                                }));
                            }""")
                            visible = [b for b in btn_info if b['vis'] and not b['disabled']]
                            if visible:
                                try:
                                    await page.locator('[data-zefoy-form] button').nth(visible[0]['idx']).click(force=True)
                                    clicked = True
                                    psuccess(f"Clicked button: {visible[0]['text'][:20]}")
                                except:
                                    pass
                            if not clicked:
                                perror("No send button found in the matched form")
                                for b in visible[:3]:
                                    print(f"    {b['text'][:20]} type={b.get('type','')} html={b.get('html','')[:40]}")

                        await page.evaluate("() => document.querySelectorAll('[data-zefoy-form]').forEach(el => el.removeAttribute('data-zefoy-form'))")
                    else:
                        try:
                            btn_text = await page.evaluate("""() => {
                                const btns = document.querySelectorAll('button');
                                for (const b of btns) {
                                    const cls = b.className || '';
                                    const rect = b.getBoundingClientRect();
                                    if ((cls.includes('btn-dark') || cls.includes('wbutton')) && rect.width > 0 && rect.height > 0) {
                                        return b.innerText.trim();
                                    }
                                }
                                return '';
                            }""")
                            if btn_text:
                                title_prefix = f"{btn_text} ({sent+1}/{count})"
                                set_title(f"@cpzc/zefoy - {title_prefix}")
                        except: pass

                        clicked = False
                        for sel in ['button.btn-dark:visible', 'button.wbutton:visible', 'button.btn-success:visible']:
                            try:
                                b = page.locator(sel).first
                                if await b.is_visible(timeout=2000):
                                    await b.click(); clicked = True; break
                            except: continue
                        if not clicked:
                            try:
                                b = page.locator('.btn-dark:visible').first
                                if await b.is_visible(timeout=1000):
                                    await b.click(); clicked = True
                            except: pass
                        if not clicked:
                            clicked = await page.evaluate("""() => {
                                const btns = document.querySelectorAll('button');
                                for (const b of btns) {
                                    const cls = b.className || '';
                                    const rect = b.getBoundingClientRect();
                                    if (cls.includes('btn-dark') && rect.width > 0 && rect.height > 0) {
                                        b.click(); return true;
                                    }
                                }
                                for (const b of btns) {
                                    const cls = b.className || '';
                                    const rect = b.getBoundingClientRect();
                                    if (cls.includes('wbutton') && rect.width > 0 && rect.height > 0) {
                                        b.click(); return true;
                                    }
                                }
                                return false;
                            }""")
                    if not clicked:
                        try:
                            btns_info = await page.evaluate("""() => {
                                const btns = document.querySelectorAll('button');
                                return Array.from(btns).map(b => ({
                                    text: (b.textContent || '').trim().substring(0,30),
                                    cls: (b.className || '').substring(0,60),
                                    vis: b.offsetParent !== null,
                                    disabled: b.disabled
                                }));
                            }""")
                            visible = [b for b in btns_info if b['vis']]
                            perror(f"Send button not found. Visible: {visible}")
                        except:
                            perror("Send button not found")
                        await asyncio.sleep(0.05)
                        continue

                    await asyncio.sleep(3)

                    result = ""
                    try:
                        body_text2 = await page.evaluate("() => document.body.innerText")
                        cooldown = ""
                        for line in body_text2.split('\n'):
                            line = line.strip()
                            if not line: continue
                            if not result and re.search(r"successfully|sent \d+", line, re.I):
                                result = line
                            if not cooldown and re.search(r"Please wait \d+ (minute|second)|\d+ (minute|second).*before|too many requests|slow down", line, re.I):
                                cooldown = line
                        if not result:
                            result = cooldown
                    except: pass

                    wait2 = parse_wait_time(result)
                    cd_wait = parse_wait_time(cooldown)
                    if "success" in result.lower() or "sent" in result.lower():
                        sent += 1
                        attempt_success = True
                        log(f"SUCCESS: {result}")
                        psuccess(f"SUCCESS! {result}")
                        if NOTIFY_ON_SEND:
                            await send_telegram(f"@cpzc/zefoy | {service_name} sent ({sent}/{count})\n{result}\nURL: {url}")
                            await send_discord(f"@cpzc/zefoy | {service_name} sent ({sent}/{count})\n{result}\nURL: {url}")
                        if cd_wait > 0:
                            pwarning(f"Cooldown {format_time(cd_wait)} before next send...")
                            await countdown_sleep(cd_wait + 2, title_prefix)
                    elif wait2 > 0:
                        if wait2 >= 86400:
                            hours = wait2 // 3600
                            print()
                            perror(f"BANNED! {hours} hour rate limit!")
                            await browser.close(); await pw.stop(); return
                        rate_limit_count += 1
                        multiplier = 1.5 ** (rate_limit_count - 1)
                        total_wait = int(wait2 * multiplier) + 3
                        pwarning(f"Rate limited (x{multiplier:.1f}). Waiting {format_time(total_wait)}...")
                        await countdown_sleep(total_wait, title_prefix)
                        continue
                    else:
                        msg = result or "empty"
                        log(f"Unknown result: {msg}", "WARN")
                        pwarning(f"Unknown result: {msg}, retrying...")
                        await asyncio.sleep(0.05)

                except Exception as e:
                    log(f"Error: {e}", "ERROR")
                    perror(f"Error: {e}, retrying...")
                    await asyncio.sleep(0.05)

        print()
        clear_screen()
        banner()
        log(f"COMPLETE: Sent {sent}/{count} {service_name}")
        section("COMPLETE", Colors.BRIGHT_GREEN)
        print()
        print(f"     {progress_bar(count, count, color=Colors.BRIGHT_GREEN)}")
        print()
        ratio_text = str(sent) + "/" + str(count)
        print(f"     {ok(f'{bold(ratio_text)} {service_name} sent successfully')}")
        if NOTIFY_ON_COMPLETE:
            await send_telegram(f"@cpzc/zefoy | Finished\nSent {sent}/{count} {service_name}\nURL: {url}")
            await send_discord(f"@cpzc/zefoy | Finished\nSent {sent}/{count} {service_name}\nURL: {url}")
        footer(Colors.BRIGHT_GREEN)
        print()
        input(f"  {dim('Press Enter to continue...')}")

    except Exception as e:
        print()
        perror(f"Error: {e}")
    finally:
        try:
            if browser:
                await asyncio.wait_for(browser.close(), timeout=3)
        except:
            pass
        try:
            if pw:
                await asyncio.wait_for(pw.stop(), timeout=3)
        except:
            pass


def main():
    while True:
        clear_screen()
        print()
        banner()

        section("NEW SESSION")
        print()
        url = ask("Paste your TikTok video URL")
        if not url:
            break

        captcha_mode = ask("How to solve CAPTCHAs?",
                           ["manual (you type it)", "auto (OCR reads it)"],
                           default="auto (OCR reads it)")
        auto_captcha = "auto" in captcha_mode

        count = ask("How many times to send?", default="1")
        try: count = int(count)
        except: count = 1

        headless = ask("Run in background (no browser window)?", ["yes", "no"], default="no") == "yes"

        print()
        print(f"     {dim('URL:')} {url}")
        print(f"     {dim('CAPTCHA:')} {'Auto (OCR)' if auto_captcha else 'Manual'}")
        print(f"     {dim('Count:')} {count}")
        print(f"     {dim('Headless:')} {'Yes' if headless else 'No'}")
        print()

        try:
            asyncio.run(main_playwright(url, auto_captcha, count, headless))
        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        os._exit(0)
