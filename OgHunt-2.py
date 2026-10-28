#!/usr/bin/env python3
"""
OGHunt XLI/UYP v5.0 — High-Velocity Terminal Username Sniper
lang  : Python 3.10+
file  : OGHunt.py
target: Windows 11 / Linux / macOS
deps  : pip install colorama requests urllib3 tls_client
run   : python OGHunt.py
"""

import os
import sys
import ssl
import time
import json
import queue
import base64
import random
import string
import socket
import select
import urllib3
import itertools
import threading
import re
from datetime import datetime, timezone
from typing import Generator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── optional engines ──────────────────────────────────────────────────────────
try:
    import tls_client as _tls
    _HAS_TLS = True
except ImportError:
    _tls = None
    _HAS_TLS = False

try:
    import requests as _req
    from requests.adapters import HTTPAdapter
except ImportError:
    print("Missing dependency: pip install requests colorama urllib3")
    sys.exit(1)

try:
    from colorama import init as _cinit, Fore, Back, Style
    _cinit(autoreset=True)
except ImportError:
    print("Missing dependency: pip install colorama")
    sys.exit(1)

# Enable VT100 escape sequences on Windows 10/11
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# ── ANSI 256 / TrueColor Palette (XLI & UYP v5.0 Aesthetic) ───────────────────
RE     = Style.RESET_ALL
B      = Style.BRIGHT
DIM    = Style.DIM

C_PURP = "\033[38;5;135m"          # Neon Purple
C_VIO  = "\033[38;5;99m"           # Deep Violet
C_MAG  = "\033[38;5;201m"          # Hot Magenta
C_BLUE = "\033[38;5;39m"           # Electric Blue
C_CYAN = "\033[38;5;51m"           # Cyber Cyan
C_GRN  = "\033[38;5;46m"           # Matrix Green
C_RED  = "\033[38;5;196m"          # Crimson Red (TAKEN)
C_YLW  = "\033[38;5;226m"          # Gold Yellow
C_WHT  = "\033[38;5;255m"          # Crisp White
C_GRY  = "\033[38;5;242m"          # Muted Gray
C_DGRY = "\033[38;5;237m"          # Dark Frame Gray

_RAINBOW = [
    "\033[38;5;196m", "\033[38;5;202m", "\033[38;5;226m", "\033[38;5;46m",
    "\033[38;5;51m",  "\033[38;5;39m",  "\033[38;5;135m", "\033[38;5;201m",
]

def _rainbow(text: str) -> str:
    return "".join(_RAINBOW[i % len(_RAINBOW)] + ch for i, ch in enumerate(text)) + RE

# ── Banner & Branding ─────────────────────────────────────────────────────────
VERSION      = "v5.0"
AUTHOR       = "hz x uyp"
DISCORD_TAG  = "beijariamos"
MAX_WORKERS  = 5000

_BANNER_LINES = [
    "   ██████╗  ██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗",
    "  ██╔═══██╗██╔════╝ ██║  ██║██║   ██║████╗  ██║╚══██╔══╝",
    "  ██║   ██║██║  ███╗███████║██║   ██║██╔██╗ ██║   ██║   ",
    "  ██║   ██║██║   ██║██╔══██║██║   ██║██║╚██╗██║   ██║   ",
    "  ╚██████╔╝╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║   ██║   ",
    "   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ",
]

_BANNER_GRAD = [
    "\033[38;5;201m",
    "\033[38;5;165m",
    "\033[38;5;129m",
    "\033[38;5;93m",
    "\033[38;5;57m",
    "\033[38;5;39m",
]

# ── Files ─────────────────────────────────────────────────────────────────────
CFG_FILE   = "oghunt_config.json"
PROXY_FILE = "oghunt_proxies.json"
HITS_FILE  = "hits.txt"
DATA_DIR   = "data"

os.makedirs(DATA_DIR, exist_ok=True)

# ── Dynamic Fingerprint & Anti-Rate-Limit Profiles ────────────────────────────
API = "https://discord.com/api/v9"

_TLS_PROFILES = [
    "chrome_124", "chrome_120", "chrome_117", "chrome_112",
    "firefox_120", "firefox_117", "opera_90", "safari_16_0",
]

_USER_AGENTS = [
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", "126.0.0.0", '"Chromium";v="126","Google Chrome";v="126","Not-A.Brand";v="99"', 346892),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", "125.0.0.0", '"Chromium";v="125","Google Chrome";v="125","Not-A.Brand";v="24"', 344218),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.208 Safari/537.36", "124.0.6367.208", '"Chromium";v="124","Google Chrome";v="124","Not-A.Brand";v="99"', 341809),
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", "125.0.0.0", '"Chromium";v="125","Google Chrome";v="125","Not-A.Brand";v="24"', 344218),
]

def _build_discord_headers(auth_token: str | None = None) -> dict:
    ua, bver, ch_ua, build_num = random.choice(_USER_AGENTS)
    super_props = {
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": ua,
        "browser_version": bver,
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": build_num,
        "client_event_source": None,
    }
    sp_b64 = base64.b64encode(json.dumps(super_props, separators=(",", ":")).encode()).decode()
    hdrs = {
        "authority":          "discord.com",
        "accept":             "*/*",
        "accept-language":    "en-US,en;q=0.9",
        "content-type":       "application/json",
        "origin":             "https://discord.com",
        "referer":            "https://discord.com/register",
        "sec-ch-ua":          ch_ua,
        "sec-ch-ua-mobile":   "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest":     "empty",
        "sec-fetch-mode":     "cors",
        "sec-fetch-site":     "same-origin",
        "user-agent":         ua,
        "x-discord-locale":   "en-US",
        "x-discord-timezone": "America/New_York",
        "x-debug-options":    "bugReporterEnabled",
        "x-super-properties": sp_b64,
    }
    if auth_token:
        hdrs["Authorization"] = auth_token
    return hdrs

# ── Pre-generated Header Pool (zero json.dumps/base64 on hot path) ───────────
_HEADER_POOL: list[dict] = []
_HEADER_POOL_IDX: int    = 0

def _init_header_pool(n: int = 512) -> None:
    """Build N ready-made header dicts at session start. Thread-safe after init."""
    global _HEADER_POOL, _HEADER_POOL_IDX
    _HEADER_POOL     = [_build_discord_headers() for _ in range(n)]
    _HEADER_POOL_IDX = 0

def _pop_headers(auth_token: str | None = None) -> dict:
    """Return a shallow copy from the pool — no JSON/base64 per request."""
    global _HEADER_POOL_IDX
    if not _HEADER_POOL:
        return _build_discord_headers(auth_token)
    # Not truly atomic, but racing threads just share a slot — harmless.
    idx = _HEADER_POOL_IDX
    _HEADER_POOL_IDX = (idx + 1) % len(_HEADER_POOL)
    h = dict(_HEADER_POOL[idx])
    if auth_token:
        h["Authorization"] = auth_token
    elif "Authorization" in h:
        del h["Authorization"]
    return h

# ── Custom SSL Cipher Adapter for Standard `requests` Fallback ────────────────
_CIPHERS = (
    "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:"
    "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"
    "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:"
    "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305"
)

class _TLSAdapter(HTTPAdapter):
    """Spoofs modern browser cipher suites & pools high-concurrency connections when tls_client is disabled/unavailable."""
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers(_CIPHERS)
        except Exception:
            pass
        pool_kwargs["ssl_context"] = ctx
        return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers(_CIPHERS)
        except Exception:
            pass
        proxy_kwargs["ssl_context"] = ctx
        return super().proxy_manager_for(proxy, **proxy_kwargs)

# ── Runtime State & Config ────────────────────────────────────────────────────
g_hits       = 0
g_epic       = 0
g_checked    = 0
g_errors     = 0
g_rl_count   = 0
g_running    = False
g_paused     = False
g_lock       = threading.Lock()
_print_lock  = threading.Lock()          # kept for UI / menu code outside the hot path
_start_time  = time.perf_counter()

# ── Async display queue — workers enqueue, one daemon owns stdout ─────────────
_display_q: queue.SimpleQueue = queue.SimpleQueue()

def _dwrite(msg: str) -> None:
    """Non-blocking enqueue. Caller never waits on stdout."""
    _display_q.put_nowait(msg)

def _display_daemon() -> None:
    """Drains _display_q every 20 ms — single writer to stdout during snipe."""
    buf: list[str] = []
    deadline = time.perf_counter() + 0.02
    while True:
        # drain all pending messages
        while True:
            try:
                buf.append(_display_q.get_nowait())
            except Exception:
                break
        now = time.perf_counter()
        if buf and now >= deadline:
            try:
                sys.stdout.write("".join(buf))
                sys.stdout.flush()
            except Exception:
                pass
            buf.clear()
            deadline = now + 0.02
        time.sleep(0.005)

PLATFORMS = {
    "D": ("discord",   "Discord"),
    "R": ("roblox",    "Roblox"),
    "T": ("tiktok",    "TikTok"),
    "I": ("instagram", "Instagram"),
    "Y": ("youtube",   "YouTube"),
    "M": ("minecraft", "Minecraft"),
}

g_current_platform = "discord"
g_loaded_names: list[str] = []

cfg: dict = {
    "webhook":           "",
    "webhook_username":  "OGHunt v5.0",
    "webhook_avatar":    "",
    "webhook_color":     "9699539",
    "webhook_ping":      "",

    "bot_token":         "",
    "channel_id":        "",
    "bot_embed_color":   "9699539",
    "bot_embed_title":   "🎯 HIT — Username Available!",
    "bot_embed_footer":  "OGHunt XLI/UYP v5.0",
    "bot_ping_role":     "",
    "bot_ping_user":     "",

    "user_token":        "",
    "user_tokens":       [],
    "discord_check_mode": "auto",  # "auto" (tokens + unauthed fallback), "unauthed", "authed"

    "roblox_cookie":     "",
    "minecraft_token":   "",

    "engine":            "auto",   # "auto", "requests", "tls_client"
    "proxy_mode":        "all",    # "all", "single", "none"
    "selected_proxy":    "",       # specific proxy URL when proxy_mode == "single"
    "require_proxy_verify": True,  # verify proxies before sniping
    "req_delay":         0.0,
    "proxy_max_fails":   6,
    "proxy_test_url":    "https://discord.com/api/v9/experiments",
    "workers_default":   500,
    "debug":             False,
}

# ── Token Pool (with Cooldown Support) ────────────────────────────────────────
class TokenPool:
    def __init__(self):
        self._tokens:   list[str]        = []
        self._dead:     set[str]         = set()
        self._cooldown: dict[str, float] = {}
        self._lock      = threading.Lock()
        self._idx       = 0

    def load_from_cfg(self) -> int:
        raw: list[str] = []
        for t in cfg.get("user_tokens", []):
            for part in re.split(r"[,\n\r]+", str(t)):
                part = part.strip()
                if part:
                    raw.append(part)
        single = str(cfg.get("user_token", "")).strip()
        if single and single not in raw:
            raw.append(single)
        with self._lock:
            self._tokens   = list(dict.fromkeys(raw))
            self._dead     = set()
            self._cooldown = {}
            self._idx      = 0
        return len(self._tokens)

    def next(self) -> str | None:
        with self._lock:
            n = len(self._tokens)
            if n == 0:
                return None
            now = time.monotonic()
            for _ in range(n):
                t = self._tokens[self._idx % n]
                self._idx += 1
                if t in self._dead:
                    continue
                if self._cooldown.get(t, 0.0) > now:
                    continue
                return t
            return None

    def set_cooldown(self, token: str, seconds: float):
        with self._lock:
            self._cooldown[token] = time.monotonic() + min(seconds, 60.0)

    def mark_dead(self, token: str):
        with self._lock:
            self._dead.add(token)

    def count(self)       -> int: return len(self._tokens)
    def dead_count(self)  -> int: return len(self._dead)
    def alive_count(self) -> int: return max(0, len(self._tokens) - len(self._dead))
    def alive_list(self)  -> list[str]:
        with self._lock:
            return [t for t in self._tokens if t not in self._dead]

token_pool = TokenPool()

# ── Proxy Pool (with Verification, Cooldowns & Specific Selection) ────────────
class ProxyPool:
    def __init__(self):
        self._all:      list[str]         = []
        self._verified: list[str]         = []
        self._dead:     set[str]          = set()
        self._fail:     dict[str, int]    = {}
        self._cooldown: dict[str, float]  = {}
        self._latency:  dict[str, float]  = {}
        self._lock      = threading.Lock()
        self._idx       = 0
        self.is_verified = False
        # ── Lock-free read snapshot (rebuilt under _lock, read without it) ──
        self._snapshot:  list[str] = []
        self._snap_idx:  int       = 0

    def _rebuild_snapshot(self) -> None:
        """Rebuild the lock-free read list. Must be called while holding _lock."""
        now = time.monotonic()
        pool = self._verified if (self.is_verified and self._verified) else self._all
        self._snapshot = [
            p for p in pool
            if p not in self._dead and self._cooldown.get(p, 0.0) <= now
        ]

    def _parse(self, raw: str) -> str | None:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            return None
        if "://" in raw:
            return raw
        parts = raw.split(":")
        if len(parts) == 4:
            h, p, u, pw = parts
            return f"http://{u}:{pw}@{h}:{p}"
        if len(parts) == 2:
            return f"http://{raw}"
        return None

    def load(self, path: str = PROXY_FILE) -> int:
        proxies = []
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                if content.startswith("{") or content.startswith("["):
                    data = json.loads(content)
                    raw_list = data if isinstance(data, list) else data.get("proxies", [])
                    for entry in raw_list:
                        p = self._parse(str(entry))
                        if p:
                            proxies.append(p)
                else:
                    for line in content.splitlines():
                        p = self._parse(line)
                        if p:
                            proxies.append(p)
            except Exception:
                pass
        with self._lock:
            deduped = list(dict.fromkeys(proxies))
            if deduped != self._all:
                self.is_verified = False
                self._verified = []
            self._all      = deduped
            self._dead     = set()
            self._fail     = {}
            self._cooldown = {}
            self._idx      = 0
            self._rebuild_snapshot()
        return len(self._all)

    def get_for_request(self) -> str | None:
        """Returns proxy per cfg proxy_mode. Hot path: lock-free snapshot read."""
        mode = cfg.get("proxy_mode", "all")
        if mode == "none":
            return None
        if mode == "single":
            sel = cfg.get("selected_proxy", "").strip()
            return sel if sel else None

        # Fast path — snapshot was built under _lock; single-read is GIL-safe.
        snap = self._snapshot
        if not snap:
            with self._lock:
                self._rebuild_snapshot()
                snap = self._snapshot
                if not snap:
                    return None

        # Increment is not truly atomic, but racing threads just share a slot —
        # harmless for rotation; correctness matters, not strict uniqueness.
        idx = self._snap_idx
        self._snap_idx = idx + 1
        return snap[idx % len(snap)]

    def mark_ratelimit(self, proxy: str | None, retry_after: float):
        """Puts proxy on cooldown — NEVER marks it dead. Rebuilds snapshot."""
        if not proxy:
            return
        with self._lock:
            self._cooldown[proxy] = time.monotonic() + min(max(retry_after, 0.5), 45.0)
            self._rebuild_snapshot()

    def mark_fail(self, proxy: str | None):
        """Network/connection errors increment fail counter. Rebuilds snapshot."""
        if not proxy:
            return
        max_f = int(cfg.get("proxy_max_fails", 6))
        with self._lock:
            self._fail[proxy] = self._fail.get(proxy, 0) + 1
            if self._fail[proxy] >= max_f:
                self._dead.add(proxy)
            self._rebuild_snapshot()

    def mark_ok(self, proxy: str | None):
        if not proxy:
            return
        with self._lock:
            self._fail.pop(proxy, None)
            self._cooldown.pop(proxy, None)
            self._rebuild_snapshot()

    def count(self)          -> int: return len(self._all)
    def dead_count(self)     -> int: return len(self._dead)
    def verified_count(self) -> int: return len(self._verified)
    def alive_count(self)    -> int:
        with self._lock:
            return sum(1 for p in self._all if p not in self._dead)

    def cooldown_count(self) -> int:
        now = time.monotonic()
        with self._lock:
            return sum(1 for p, cd in self._cooldown.items() if cd > now and p not in self._dead)

    def list_all(self) -> list[tuple[str, str, float]]:
        now = time.monotonic()
        with self._lock:
            out = []
            for p in self._all:
                ms = self._latency.get(p, 0.0)
                if p in self._dead:
                    st = "DEAD"
                elif self._cooldown.get(p, 0.0) > now:
                    rem = self._cooldown[p] - now
                    st = f"COOL({rem:.1f}s)"
                elif p in self._verified:
                    st = "VERIFIED"
                elif self._fail.get(p, 0) > 0:
                    st = f"WARN({self._fail[p]})"
                else:
                    st = "UNVERIFIED"
                out.append((p, st, ms))
            return out

    def verify_all(self, platform: str = "discord", max_n: int = 0, timeout_s: float = 6.0) -> list[tuple[str, bool, float]]:
        targets = self._all[:max_n] if max_n else list(self._all)
        if not targets:
            return []

        test_urls = {
            "discord":   "https://discord.com/api/v9/experiments",
            "roblox":    "https://auth.roblox.com/v1/usernames/validate?birthday=2006-09-21T07:00:00.000Z&context=Signup&username=roblox",
            "tiktok":    "https://www.tiktok.com/robots.txt",
            "instagram": "https://www.instagram.com/robots.txt",
            "youtube":   "https://www.youtube.com/robots.txt",
            "minecraft": "https://api.mojang.com/users/profiles/minecraft/Notch",
        }
        url = test_urls.get(platform, cfg.get("proxy_test_url", "https://discord.com/api/v9/experiments"))

        results: list[tuple[str, bool, float]] = []
        res_lock = threading.Lock()
        q = queue.Queue()
        for p in targets:
            q.put(p)

        total = len(targets)
        done_cnt = 0

        def _v_worker():
            nonlocal done_cnt
            s = _req.Session()
            adapter = _TLSAdapter(pool_connections=10, pool_maxsize=10)
            s.mount("https://", adapter)
            s.mount("http://", adapter)
            while True:
                try:
                    p = q.get_nowait()
                except queue.Empty:
                    break
                t0 = time.perf_counter()
                ok = False
                try:
                    r = s.get(
                        url,
                        proxies={"http": p, "https": p},
                        headers={"User-Agent": _USER_AGENTS[0][0]},
                        timeout=timeout_s,
                        verify=False,
                    )
                    ok = r.status_code < 500
                except Exception:
                    ok = False
                ms = (time.perf_counter() - t0) * 1000.0
                with res_lock:
                    results.append((p, ok, ms))
                    done_cnt += 1
                    pct = (done_cnt / total) * 100
                    bar_len = 28
                    filled = int(bar_len * done_cnt // total)
                    bar = f"{C_PURP}{'█' * filled}{C_DGRY}{'░' * (bar_len - filled)}{RE}"
                    sys.stdout.write(f"\r  {C_VIO}⚡ Verifying proxies [{platform.upper()}]{RE} {bar} {C_WHT}{pct:5.1f}%{RE} ({done_cnt}/{total})")
                    sys.stdout.flush()
                q.task_done()

        n_threads = min(len(targets), 120)
        threads = [threading.Thread(target=_v_worker, daemon=True) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=timeout_s + 6.0)
        print()

        results.sort(key=lambda x: (not x[1], x[2]))
        with self._lock:
            self._verified = [p for p, ok, _ in results if ok]
            for p, ok, ms in results:
                self._latency[p] = ms
                if not ok:
                    self._dead.add(p)
                else:
                    self._dead.discard(p)
            self.is_verified = True
            self._rebuild_snapshot()
        return results

    def remove_dead(self):
        with self._lock:
            self._all      = [p for p in self._all if p not in self._dead]
            self._verified = [p for p in self._verified if p not in self._dead]
            self._dead.clear()
            self._fail     = {k: v for k, v in self._fail.items() if k in self._all}
            self._cooldown = {k: v for k, v in self._cooldown.items() if k in self._all}
            self._idx      = 0
            self._rebuild_snapshot()

    def save(self, path: str = PROXY_FILE):
        with self._lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"proxies": list(self._all)}, f, indent=2, ensure_ascii=False)

proxy_pool = ProxyPool()

# ── High-Speed Connection-Pooled HTTP Layer ───────────────────────────────────
_tlocal = threading.local()

def _use_tls_engine(concurrency: int = 1) -> bool:
    eng = cfg.get("engine", "auto")
    if eng == "requests" or not _HAS_TLS:
        return False
    if eng == "tls_client":
        return True
    return concurrency <= 60

def _get_pooled_session(proxy_url: str | None = None, use_tls: bool = False):
    cache: dict = getattr(_tlocal, "session_cache", None)
    if cache is None:
        cache = {}
        _tlocal.session_cache = cache

    key = (use_tls, proxy_url or "DIRECT")
    sess = cache.get(key)
    if sess is not None:
        if len(cache) > 32:
            oldest = next(iter(cache))
            cache.pop(oldest, None)
        return sess

    if use_tls and _HAS_TLS:
        prof = random.choice(_TLS_PROFILES)
        sess = _tls.Session(client_identifier=prof, random_tls_extension_order=True)
        if proxy_url:
            sess.proxies = {"http": proxy_url, "https": proxy_url}
    else:
        sess = _req.Session()
        adapter = _TLSAdapter(pool_connections=32, pool_maxsize=64, max_retries=0)
        sess.mount("https://", adapter)
        sess.mount("http://", adapter)
        if proxy_url:
            sess.proxies = {"http": proxy_url, "https": proxy_url}

    cache[key] = sess
    return sess

def _reset_thread_session(proxy_url: str | None = None):
    cache: dict = getattr(_tlocal, "session_cache", None)
    if cache:
        cache.pop((True, proxy_url or "DIRECT"), None)
        cache.pop((False, proxy_url or "DIRECT"), None)

def _http_call(method: str, url: str, proxy_url: str | None = None,
               use_tls: bool = False, timeout_s: int = 3, **kwargs):
    sess = _get_pooled_session(proxy_url, use_tls=use_tls)
    fn = getattr(sess, method)
    if use_tls and _HAS_TLS:
        return fn(url, timeout_seconds=timeout_s, **kwargs)
    return fn(url, timeout=timeout_s, verify=False, **kwargs)

def _extract_retry_after(r, default: float = 2.5) -> float:
    try:
        j = r.json()
        if isinstance(j, dict) and "retry_after" in j:
            return float(j["retry_after"])
    except Exception:
        pass
    ra = r.headers.get("Retry-After") or r.headers.get("retry-after") or r.headers.get("x-ratelimit-reset-after")
    if ra:
        try:
            return float(ra)
        except Exception:
            pass
    return default

# ── 15 Username Generators (Matching UYP v5.0 & XLI v4.0) ────────────────────
_VOWELS     = "aeiou"
_CONSONANTS = "bcdfghjklmnpqrstvwxyz"
_LEET       = "aeiostl013457"
_ALPHANUM   = string.ascii_lowercase + string.digits

PATTERN_CATALOG = [
    ("1",  "Letters Only",        "abc"),
    ("2",  "Letters + Numbers",   "a1b2"),
    ("3",  "Double Letters",      "aabb"),
    ("4",  "Period Ending",       "ab.c"),
    ("5",  "Triple + Different",  "aaab"),
    ("6",  "Underscore Mix",      "a_bc"),
    ("7",  "Vowel-Heavy",         "bako"),
    ("8",  "Mirror / Palindrome", "abba"),
    ("9",  "Digit Dot",           "a.1b"),
    ("10", "All Consonants",      "xvzk"),
    ("11", "LEET / 1337",         "l337"),
    ("12", "Digit Suffix",        "ab12"),
    ("13", "Repeat Half",         "abab"),
    ("14", "WORD-LIKE",           "zeno"),
    ("15", "CHAOS (MIX ALL)",     "x_9.z"),
]

def _gen_one(mode: str, length: int, extra: str = "") -> str:
    length = max(2, length)
    if mode == "1":
        return "".join(random.choices(string.ascii_lowercase, k=length))
    if mode == "2":
        return "".join(random.choices(_ALPHANUM, k=length))
    if mode == "3":
        pairs = [random.choice(string.ascii_lowercase) * 2 for _ in range((length + 1) // 2)]
        return "".join(pairs)[:length]
    if mode == "4":
        if length <= 2:
            return random.choice(string.ascii_lowercase) + "."
        chars = random.choices(string.ascii_lowercase, k=length - 1)
        pos = random.randint(1, len(chars) - 1)
        chars.insert(pos, ".")
        return "".join(chars)[:length]
    if mode == "5":
        c1 = random.choice(string.ascii_lowercase)
        c2 = random.choice([c for c in _ALPHANUM if c != c1])
        base = [c1] * (length - 1) + [c2]
        random.shuffle(base)
        return "".join(base)
    if mode == "6":
        chars = random.choices(_ALPHANUM, k=length - 1)
        pos = random.randint(0, len(chars))
        chars.insert(pos, "_")
        return "".join(chars)[:length]
    if mode == "7":
        return "".join(random.choice(_VOWELS if i % 2 == 1 else _CONSONANTS) for i in range(length))
    if mode == "8":
        half = (length + 1) // 2
        left = [random.choice(_ALPHANUM) for _ in range(half)]
        right = left[:length - half][::-1]
        return "".join(left + right)
    if mode == "9":
        chars = [random.choice(string.ascii_lowercase), random.choice(string.digits)]
        while len(chars) < length - 1:
            chars.append(random.choice(_ALPHANUM))
        random.shuffle(chars)
        pos = random.randint(1, max(1, len(chars) - 1))
        chars.insert(pos, ".")
        return "".join(chars)[:length]
    if mode == "10":
        return "".join(random.choices(_CONSONANTS, k=length))
    if mode == "11":
        return "".join(random.choices(_LEET, k=length))
    if mode == "12":
        n_dig = max(1, length // 2)
        n_let = length - n_dig
        return "".join(random.choices(string.ascii_lowercase, k=n_let) + random.choices(string.digits, k=n_dig))
    if mode == "13":
        half = max(1, length // 2)
        chunk = "".join(random.choices(_ALPHANUM, k=half))
        return (chunk * ((length // half) + 2))[:length]
    if mode == "14":
        out = []
        start_c = random.choice([True, False])
        for i in range(length):
            pool = _CONSONANTS if (i % 2 == 0) == start_c else _VOWELS
            out.append(random.choice(pool))
        return "".join(out)
    if mode == "15":
        pool = string.ascii_lowercase + string.digits + "_."
        w = "".join(random.choices(pool, k=length))
        while ".." in w or w.startswith(".") or w.endswith("."):
            w = "".join(random.choices(pool, k=length))
        return w
    return "".join(random.choices(_ALPHANUM, k=length))

def stream_generator(mode: str, length: int, count: int = 0) -> Generator[str, None, None]:
    seen: set[str] = set()
    yielded = 0
    max_attempts = (count * 6) if count > 0 else 0
    attempts = 0
    while True:
        if count > 0 and yielded >= count:
            break
        if max_attempts and attempts >= max_attempts and yielded >= count:
            break
        w = _gen_one(mode, length)
        attempts += 1
        if w not in seen:
            seen.add(w)
            yielded += 1
            yield w
            if len(seen) > 2_500_000:
                seen.clear()

def is_epic_username(u: str) -> bool:
    if len(u) <= 3 and u.isalpha():
        return True
    if len(set(u)) <= 2 and len(u) >= 3:
        return True
    if u == u[::-1] and len(u) >= 3:
        return True
    return False

# ── Platform Checkers ─────────────────────────────────────────────────────────
def check_discord(username: str, proxy_url: str | None = None, use_tls: bool = False):
    mode = cfg.get("discord_check_mode", "auto")
    token = None if mode == "unauthed" else token_pool.next()

    if token:
        endpoint = f"{API}/unique-username/username-attempt"
        headers = _pop_headers(auth_token=token)
    else:
        if mode == "authed" and token_pool.alive_count() == 0:
            return ("dead", 401)
        endpoint = f"{API}/unique-username/username-attempt-unauthed"
        headers = _pop_headers()

    try:
        r = _http_call(
            "post", endpoint,
            proxy_url=proxy_url,
            use_tls=use_tls,
            timeout_s=6,
            json={"username": username},
            headers=headers,
        )
        if cfg.get("debug"):
            _dbg(f"[discord/{'authed' if token else 'unauthed'}] {username} -> {r.status_code} {r.text[:120]}")

        if r.status_code == 200:
            data = r.json()
            if "taken" in data:
                return not bool(data["taken"])
            return None

        if r.status_code == 429:
            ra = _extract_retry_after(r, default=3.0)
            if token:
                token_pool.set_cooldown(token, ra)
            _reset_thread_session(proxy_url)
            return ("rl", ra)

        if r.status_code == 401 and token:
            token_pool.mark_dead(token)
            return None

        if r.status_code in (403, 503):
            _reset_thread_session(proxy_url)
            return ("rl", 4.0)

        return None
    except Exception:
        return None


ROBLOX_BIRTHDAY = "2006-09-21T07:00:00.000Z"

def check_roblox(username: str, proxy_url: str | None = None, use_tls: bool = False):
    url = (
        f"https://auth.roblox.com/v1/usernames/validate"
        f"?birthday={ROBLOX_BIRTHDAY}&context=Signup&username={username}"
    )
    headers = {
        "User-Agent": random.choice(_USER_AGENTS)[0],
        "Accept":     "application/json, text/plain, */*",
        "Origin":     "https://www.roblox.com",
        "Referer":    "https://www.roblox.com/",
    }
    try:
        r = _http_call("get", url, proxy_url=proxy_url, use_tls=use_tls, timeout_s=6, headers=headers)
        if cfg.get("debug"):
            _dbg(f"[roblox] {username} -> {r.status_code} {r.text[:100]}")
        if r.status_code == 200:
            code = r.json().get("code", -1)
            return code == 0
        if r.status_code == 429:
            return ("rl", _extract_retry_after(r, 4.0))
        return None
    except Exception:
        return None


def check_tiktok(username: str, proxy_url: str | None = None, use_tls: bool = False):
    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent":      random.choice(_USER_AGENTS)[0],
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer":         "https://www.tiktok.com/",
    }
    try:
        r = _http_call("get", url, proxy_url=proxy_url, use_tls=use_tls, timeout_s=7, headers=headers)
        if cfg.get("debug"):
            _dbg(f"[tiktok] {username} -> {r.status_code}")
        if r.status_code == 404:
            return True
        if r.status_code == 200:
            if '"statusCode":10202' in r.text or '"userInfo":{}' in r.text:
                return True
            return False
        if r.status_code in (429, 403, 503):
            return ("rl", _extract_retry_after(r, 8.0))
        return None
    except Exception:
        return None


def check_instagram(username: str, proxy_url: str | None = None, use_tls: bool = False):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": random.choice(_USER_AGENTS)[0],
        "Accept":     "*/*",
        "X-IG-App-ID": "936619743392459",
        "Referer":    f"https://www.instagram.com/{username}/",
    }
    try:
        r = _http_call("get", url, proxy_url=proxy_url, use_tls=use_tls, timeout_s=7, headers=headers)
        if r.status_code == 404:
            return True
        if r.status_code == 200:
            return False
        if r.status_code in (429, 401, 403):
            return ("rl", _extract_retry_after(r, 10.0))
        return None
    except Exception:
        return None


def check_youtube(username: str, proxy_url: str | None = None, use_tls: bool = False):
    url = f"https://www.youtube.com/@{username}"
    headers = {
        "User-Agent":      random.choice(_USER_AGENTS)[0],
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = _http_call("get", url, proxy_url=proxy_url, use_tls=use_tls, timeout_s=7, headers=headers)
        if r.status_code == 404:
            return True
        if r.status_code == 200:
            return False
        if r.status_code == 429:
            return ("rl", _extract_retry_after(r, 6.0))
        return None
    except Exception:
        return None


def check_minecraft(username: str, proxy_url: str | None = None, use_tls: bool = False):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    headers = {
        "User-Agent": random.choice(_USER_AGENTS)[0],
        "Accept":     "application/json",
    }
    try:
        r = _http_call("get", url, proxy_url=proxy_url, use_tls=use_tls, timeout_s=7, headers=headers)
        if r.status_code == 200:
            return False
        if r.status_code in (404, 204):
            return True
        if r.status_code == 429:
            return ("rl", _extract_retry_after(r, 10.0))
        return None
    except Exception:
        return None


PLATFORM_CHECKERS = {
    "discord":   check_discord,
    "roblox":    check_roblox,
    "tiktok":    check_tiktok,
    "instagram": check_instagram,
    "youtube":   check_youtube,
    "minecraft": check_minecraft,
}

# ── Auto-Claim Functions ──────────────────────────────────────────────────────
def claim_discord(username: str, proxy_url: str | None = None) -> tuple[bool, str]:
    tokens = token_pool.alive_list()
    if not tokens:
        return False, "no tokens configured for auto-claim"
    last_msg = "claim failed"
    for tk in tokens:
        try:
            r = _http_call(
                "patch", f"{API}/users/@me",
                proxy_url=proxy_url,
                use_tls=_HAS_TLS,
                timeout_s=8,
                json={"username": username},
                headers=_build_discord_headers(auth_token=tk),
            )
            if r.status_code == 200:
                return True, f"locked on token {tk[:10]}..."
            if r.status_code == 401:
                token_pool.mark_dead(tk)
                continue
            last_msg = r.text[:140]
        except Exception as e:
            last_msg = str(e)[:80]
    return False, last_msg


def claim_roblox(username: str, proxy_url: str | None = None) -> tuple[bool, str]:
    cookie = cfg.get("roblox_cookie", "").strip()
    if not cookie:
        return False, "no roblox_cookie configured"
    try:
        cookies = {".ROBLOSECURITY": cookie}
        hdrs = {"User-Agent": _USER_AGENTS[0][0], "Origin": "https://www.roblox.com", "Referer": "https://www.roblox.com/"}
        r0 = _http_call("post", "https://auth.roblox.com/v2/logout", proxy_url=proxy_url, headers=hdrs, cookies=cookies, timeout_s=7)
        csrf = r0.headers.get("x-csrf-token", "")
        if not csrf:
            return False, "csrf token missing (cookie expired)"
        r = _http_call(
            "post", "https://auth.roblox.com/v1/username",
            proxy_url=proxy_url,
            json={"username": username, "password": ""},
            headers={**hdrs, "x-csrf-token": csrf},
            cookies=cookies,
            timeout_s=8,
        )
        if r.status_code == 200:
            return True, "ok"
        return False, r.text[:120]
    except Exception as e:
        return False, str(e)[:80]


def claim_minecraft(username: str, proxy_url: str | None = None) -> tuple[bool, str]:
    token = cfg.get("minecraft_token", "").strip()
    if not token:
        return False, "no minecraft_token configured"
    try:
        r = _http_call(
            "put", f"https://api.minecraftservices.com/minecraft/profile/name/{username}",
            proxy_url=proxy_url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout_s=8,
        )
        if r.status_code == 200:
            return True, "ok"
        return False, r.text[:120]
    except Exception as e:
        return False, str(e)[:80]

# ── Notifications (Webhook & Bot) ─────────────────────────────────────────────
def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _elapsed() -> str:
    e = int(max(0, time.perf_counter() - _start_time))
    h, m, s = e // 3600, (e % 3600) // 60, e % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def _current_rps() -> int:
    el = max(0.001, time.perf_counter() - _start_time)
    return int(g_checked / el)

def _build_embed(username: str, platform: str = "discord") -> dict:
    color = int(cfg.get("webhook_color", "9699539") or 9699539)
    return {
        "title": cfg.get("bot_embed_title", "🎯 HIT — Username Available!"),
        "description": (
            f"**`@{username}`** is available on **{platform.upper()}**!\n\n"
            f"> Checked: **{g_checked:,}** | Hits: **{g_hits}** | Speed: **{_current_rps()} r/s**"
        ),
        "color": color,
        "timestamp": _utcnow(),
        "footer": {"text": cfg.get("bot_embed_footer", "OGHunt XLI/UYP v5.0")},
    }

def send_webhook(username: str, platform: str = "discord"):
    url = cfg.get("webhook", "").strip()
    if not url:
        return
    try:
        ping = cfg.get("webhook_ping", "").strip()
        payload = {
            "username": cfg.get("webhook_username", "OGHunt v5.0"),
            "content":  f"<@{ping}>" if ping else "",
            "embeds":   [_build_embed(username, platform)],
        }
        if av := cfg.get("webhook_avatar", "").strip():
            payload["avatar_url"] = av
        _req.post(url, json=payload, timeout=6, verify=False)
    except Exception:
        pass

def send_bot(username: str, platform: str = "discord"):
    token = cfg.get("bot_token", "").strip()
    chan  = cfg.get("channel_id", "").strip()
    if not token or not chan:
        return
    try:
        parts = []
        if pr := cfg.get("bot_ping_role", "").strip():
            parts.append(f"<@&{pr}>")
        if pu := cfg.get("bot_ping_user", "").strip():
            parts.append(f"<@{pu}>")
        payload = {
            "content": " ".join(parts),
            "embeds":  [_build_embed(username, platform)],
        }
        hdrs = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
        _req.post(f"{API}/channels/{chan}/messages", json=payload, headers=hdrs, timeout=6, verify=False)
    except Exception:
        pass

# ── Terminal UI Helpers ───────────────────────────────────────────────────────
def set_title(t: str):
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(t)
        except Exception:
            pass
    else:
        sys.stdout.write(f"\033]0;{t}\007")
        sys.stdout.flush()

def clr():
    os.system("cls" if sys.platform == "win32" else "clear")

def _dbg(msg: str):
    if cfg.get("debug"):
        with _print_lock:
            sys.stdout.write(f"{C_GRY}[DBG] {msg}{RE}\n")
            sys.stdout.flush()

def boot_animation():
    clr()
    set_title(f"OGHunt {VERSION} — Initializing")
    print("\n")
    for i, line in enumerate(_BANNER_LINES):
        print(_BANNER_GRAD[i % len(_BANNER_GRAD)] + B + line + RE)
    print(f"\n  {C_PURP}OGHunt Username Sniper {VERSION}{RE}   {C_GRY}by {AUTHOR}   |   discord: {DISCORD_TAG}{RE}\n")
    steps = 36
    for s in range(steps + 1):
        pct = int((s / steps) * 100)
        bar = f"{C_MAG}{'█' * s}{C_DGRY}{'░' * (steps - s)}{RE}"
        sys.stdout.write(f"\r  {bar}  {C_WHT}{B}{pct:>3}%{RE}")
        sys.stdout.flush()
        time.sleep(0.012)
    print("\n")
    time.sleep(0.15)

def render_banner(subtitle: str = ""):
    clr()
    for i, line in enumerate(_BANNER_LINES):
        print(_BANNER_GRAD[i % len(_BANNER_GRAD)] + B + line + RE)
    print(
        f"  {C_PURP}{B}OGHunt Sniper {VERSION}{RE}  "
        f"{C_GRY}by {C_WHT}{AUTHOR}{C_GRY}  |  discord: {C_PURP}{DISCORD_TAG}{RE}"
    )

    p_mode = cfg.get("proxy_mode", "all").upper()
    if p_mode == "SINGLE" and cfg.get("selected_proxy"):
        p_label = f"1 pinned ({cfg['selected_proxy'][:22]}...)"
    elif p_mode == "NONE":
        p_label = "DIRECT (0)"
    else:
        v_tag = "✓" if proxy_pool.is_verified else "?"
        p_label = f"{proxy_pool.alive_count():,}/{proxy_pool.count():,} [{v_tag}]"

    hits_total = 0
    if os.path.exists(HITS_FILE):
        try:
            with open(HITS_FILE, encoding="utf-8", errors="ignore") as f:
                hits_total = sum(1 for l in f if l.strip())
        except Exception:
            pass

    print(f"  {C_DGRY}{'─' * 68}{RE}")
    print(
        f"  {C_GRY}platform{RE} {C_WHT}{B}{g_current_platform.capitalize():<10}{RE} "
        f"{C_GRY}proxies{RE} {C_PURP}{B}{p_label:<18}{RE} "
        f"{C_GRY}names{RE} {C_WHT}{B}{len(g_loaded_names):,}{RE}   "
        f"{C_GRY}tokens{RE} {C_CYAN}{B}{token_pool.alive_count()}{RE}   "
        f"{C_GRY}hits{RE} {C_GRN}{B}{hits_total}{RE}"
    )
    print(f"  {C_DGRY}{'─' * 68}{RE}")
    if subtitle:
        print(f"  {C_VIO}» {C_WHT}{B}{subtitle}{RE}")
        print(f"  {C_DGRY}{'─' * 68}{RE}")

def save_hit(u: str, platform: str):
    try:
        with open(HITS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  [{platform.upper()}]  {u}\n")
    except Exception:
        pass

def print_hit_banner(u: str, platform: str, is_epic: bool = False):
    tag = "★ EPIC HIT ★" if is_epic else "★ HIT FOUND ★"
    bar = _rainbow("✦ " * 32)
    mid = _rainbow(f"   {tag}   @{u}   [{platform.upper()}]   ")
    _dwrite(f"\r{' ' * 76}\r\n  {B}{bar}{RE}\n  {B}{mid}{RE}\n  {B}{bar}{RE}\n\n")

# ── Proxy Selection & Mandatory Verification Modal ────────────────────────────
def select_and_verify_proxies(platform: str) -> bool:
    proxy_pool.load()
    render_banner(f"PROXY SELECTOR & VERIFICATION — {platform.upper()}")

    total = proxy_pool.count()
    alive = proxy_pool.alive_count()
    ver   = proxy_pool.verified_count()
    cur_m = cfg.get("proxy_mode", "all")

    print(f"""
  {C_PURP}{B}PROXY OPTIONS FOR {platform.upper()} SNIPER{RE}
  {C_GRY}Loaded:{RE} {C_WHT}{total:,}{RE}   {C_GRY}Alive:{RE} {C_GRN}{alive:,}{RE}   {C_GRY}Verified:{RE} {C_CYAN}{ver:,}{RE}   {C_GRY}Current Mode:{RE} {C_YLW}{cur_m.upper()}{RE}

  {C_PURP}[1]{RE} {C_WHT}Verify & Use ALL Alive Proxies{RE}     {C_GRY}(tests proxies against {platform} & rotates all working){RE}
  {C_PURP}[2]{RE} {C_WHT}Use ALL Proxies Immediately{RE}        {C_GRY}(rotate all {alive:,} proxies without pre-test){RE}
  {C_PURP}[3]{RE} {C_WHT}Select a SPECIFIC Proxy{RE}            {C_GRY}(verify & pick 1 exact proxy from your list){RE}
  {C_PURP}[4]{RE} {C_WHT}Direct Connection (No Proxy){RE}       {C_GRY}(use local machine IP){RE}
  {C_PURP}[5]{RE} {C_WHT}Import Proxies from File{RE}           {C_GRY}(load .txt or .json proxy list){RE}
  {C_PURP}[0]{RE} {C_WHT}Cancel / Back{RE}
""")
    choice = input(f"  {C_PURP}${RE} {C_WHT}Select proxy option [Enter=1]: {RE}").strip() or "1"

    if choice == "0":
        return False

    if choice == "5":
        path = input(f"  {C_YLW}File path (e.g. proxies.txt): {RE}").strip()
        if os.path.exists(path):
            n = proxy_pool.load(path)
            proxy_pool.save()
            print(f"  {C_GRN}✓ Imported {n:,} proxies.{RE}")
            time.sleep(0.8)
            return select_and_verify_proxies(platform)
        else:
            print(f"  {C_RED}✗ File not found.{RE}")
            time.sleep(1.0)
            return select_and_verify_proxies(platform)

    if choice == "4":
        cfg["proxy_mode"] = "none"
        cfg["selected_proxy"] = ""
        save_config()
        return True

    if proxy_pool.count() == 0:
        print(f"\n  {C_YLW}⚠ No proxies found in {PROXY_FILE}. Running in Direct Mode (No Proxy).{RE}")
        cfg["proxy_mode"] = "none"
        time.sleep(1.0)
        return True

    if choice == "1":
        print()
        results = proxy_pool.verify_all(platform=platform)
        ok_cnt = sum(1 for _, ok, _ in results if ok)
        if ok_cnt == 0:
            print(f"\n  {C_RED}✗ 0/{len(results)} proxies passed verification!{RE}")
            fallback = input(f"  {C_YLW}Continue with unverified proxies anyway? [y/N]: {RE}").strip().lower()
            if fallback not in ("y", "yes", "s", "sim"):
                return False
            proxy_pool.is_verified = False
            proxy_pool._dead.clear()
        else:
            print(f"  {C_GRN}✓ {ok_cnt:,}/{len(results):,} proxies verified & ready for rotation!{RE}")
        cfg["proxy_mode"] = "all"
        cfg["selected_proxy"] = ""
        save_config()
        time.sleep(0.7)
        return True

    if choice == "2":
        if cfg.get("require_proxy_verify") and not proxy_pool.is_verified:
            ask_v = input(f"  {C_YLW}Proxies are unverified. Quick-verify first? [Y/n]: {RE}").strip().lower()
            if ask_v not in ("n", "no", "nao"):
                proxy_pool.verify_all(platform=platform)
        cfg["proxy_mode"] = "all"
        cfg["selected_proxy"] = ""
        save_config()
        return True

    if choice == "3":
        if not proxy_pool.is_verified:
            print(f"\n  {C_VIO}Verifying proxies first so you only pick a live one...{RE}")
            proxy_pool.verify_all(platform=platform)
        items = proxy_pool.list_all()
        alive_items = [(p, st, ms) for p, st, ms in items if st != "DEAD"]
        if not alive_items:
            alive_items = items
        print(f"\n  {C_PURP}{B}AVAILABLE PROXIES:{RE}")
        for idx, (p, st, ms) in enumerate(alive_items[:50], 1):
            col = C_GRN if "VERIFIED" in st else C_YLW
            ms_str = f"{ms:>5.0f}ms" if ms > 0 else "  n/a "
            print(f"  {C_PURP}[{idx:>2}]{RE} {C_WHT}{p:<46}{RE} {col}{st:<10}{RE} {C_GRY}{ms_str}{RE}")
        sel = input(f"\n  {C_PURP}${RE} {C_WHT}Pick proxy number (1-{min(50, len(alive_items))}): {RE}").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(alive_items):
            chosen = alive_items[int(sel) - 1][0]
            cfg["proxy_mode"] = "single"
            cfg["selected_proxy"] = chosen
            save_config()
            print(f"  {C_GRN}✓ Locked onto proxy: {chosen}{RE}")
            time.sleep(0.7)
            return True
        print(f"  {C_RED}Invalid selection.{RE}")
        time.sleep(0.8)
        return False

    return True

# ── Keyboard Listener (Pause/Resume with N) ───────────────────────────────────
def _kb_listener():
    global g_paused, g_running
    if sys.platform == "win32":
        import msvcrt
        while g_running:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch.lower() == "n":
                    g_paused = not g_paused
                    st = f"{C_YLW}[PAUSED]{RE}" if g_paused else f"{C_GRN}[RESUMED]{RE}"
                    with _print_lock:
                        sys.stdout.write(f"\r{' ' * 76}\r  {st} (Press N to toggle)\n")
                        sys.stdout.flush()
            time.sleep(0.05)
    else:
        try:
            import termios, tty
        except ImportError:
            return
        if not sys.stdin.isatty():
            return
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while g_running:
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    ch = sys.stdin.read(1)
                    if ch.lower() == "n":
                        g_paused = not g_paused
                        st = f"{C_YLW}[PAUSED]{RE}" if g_paused else f"{C_GRN}[RESUMED]{RE}"
                        with _print_lock:
                            sys.stdout.write(f"\r\n  {st} (Press N to toggle)\r\n")
                            sys.stdout.flush()
                    elif ch == "\x03":
                        os.kill(os.getpid(), 2)
        except Exception:
            pass
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            except Exception:
                pass

# ── High-Velocity Worker & Sniper Engine (Up to 5000 Workers) ─────────────────
def _worker(
    work_q: queue.Queue,
    done_ev: threading.Event,
    platform: str,
    check_fn,
    use_tls: bool,
    total_target: int,
):
    global g_hits, g_epic, g_checked, g_errors, g_rl_count, g_running

    delay = float(cfg.get("req_delay", 0.0))
    _MAX_PROXY_RETRIES = 8   # max proxy rotations per username before re-queue

    while g_running:
        while g_paused and g_running:
            time.sleep(0.08)

        try:
            username = work_q.get(timeout=0.3)
        except queue.Empty:
            if done_ev.is_set():
                break
            continue

        try:
            if delay > 0:
                time.sleep(delay)

            result = None
            tried_proxies: list[str | None] = []

            for _attempt in range(_MAX_PROXY_RETRIES):
                if not g_running:
                    break

                proxy = proxy_pool.get_for_request()

                # avoid re-using a proxy we already got a 429 from this iteration
                # (snapshot rotates atomically so usually gives a fresh one)
                _tried_set = set(id(p) for p in tried_proxies)  # noqa: use str comparison
                if tried_proxies and proxy in tried_proxies and len(tried_proxies) < proxy_pool.alive_count():
                    continue  # snapshot gave same proxy — skip, get next on next loop
                tried_proxies.append(proxy)

                result = check_fn(username, proxy_url=proxy, use_tls=use_tls)

                if isinstance(result, tuple) and result[0] == "rl":
                    wait = float(result[1])
                    proxy_pool.mark_ratelimit(proxy, wait)
                    with g_lock:
                        g_rl_count += 1
                    # no sleep — immediately rotate to next proxy and retry inline
                    if proxy is None or cfg.get("proxy_mode") == "single":
                        # no proxy pool: must wait a little
                        time.sleep(min(wait, 0.5))
                        break  # re-queue below
                    # multi-proxy: just loop — next iteration picks a fresh proxy
                    continue

                if isinstance(result, tuple) and result[0] == "dead":
                    proxy_pool.mark_fail(proxy)
                    with g_lock:
                        g_errors += 1
                    continue  # try next proxy immediately

                # got a real result (True / False / None/error)
                break

            else:
                # exhausted all retries — re-queue so another worker handles it
                try:
                    work_q.put_nowait(username)
                except queue.Full:
                    pass
                continue

            # if last result was still rl or dead after retries — re-queue
            if result is None or (isinstance(result, tuple) and result[0] in ("rl", "dead")):
                try:
                    work_q.put_nowait(username)
                except queue.Full:
                    pass
                continue

            if result is True:
                proxy_pool.mark_ok(proxy)
                epic = is_epic_username(username)
                with g_lock:
                    g_hits += 1
                    if epic:
                        g_epic += 1
                    g_checked += 1
                lh, lepic, lc = g_hits, g_epic, g_checked   # read after lock; benign-stale for display

                print_hit_banner(username, platform, is_epic=epic)
                save_hit(username, platform)

                threading.Thread(target=send_webhook, args=(username, platform), daemon=True).start()
                threading.Thread(target=send_bot,     args=(username, platform), daemon=True).start()

                if platform == "discord" and token_pool.alive_count() > 0:
                    ok, msg = claim_discord(username, proxy)
                    _dwrite(
                        f"  {C_GRN}{B}[CLAIMED]{RE} {C_WHT}@{username} -> {msg}{RE}\n"
                        if ok else
                        f"  {C_YLW}[CLAIM FAIL]{RE} {C_GRY}@{username} -> {msg}{RE}\n"
                    )
                elif platform == "roblox" and cfg.get("roblox_cookie"):
                    ok, msg = claim_roblox(username, proxy)
                    _dwrite(f"  {C_GRN if ok else C_YLW}[ROBLOX CLAIM]{RE} @{username} -> {msg}\n")
                elif platform == "minecraft" and cfg.get("minecraft_token"):
                    ok, msg = claim_minecraft(username, proxy)
                    _dwrite(f"  {C_GRN if ok else C_YLW}[MC CLAIM]{RE} @{username} -> {msg}\n")

            elif result is False:
                proxy_pool.mark_ok(proxy)
                with g_lock:
                    g_checked += 1
                lc, lh = g_checked, g_hits   # benign-stale for display

                rps = _current_rps()
                if total_target > 0:
                    pct = min(100.0, (lc / total_target) * 100.0)
                    status_bar = (
                        f"  {C_PURP}{'━' * 16}{RE} {C_WHT}{pct:5.1f}%{RE} "
                        f"{C_GRY}{lc:,}/{total_target:,}{RE}  "
                        f"{C_WHT}hits {C_GRN}{lh}{RE}  "
                        f"{C_WHT}rps {C_CYAN}{rps:,}{RE}"
                    )
                else:
                    status_bar = (
                        f"  {C_PURP}{'━' * 16}{RE} "
                        f"{C_GRY}checked {lc:,}{RE}  "
                        f"{C_WHT}hits {C_GRN}{lh}{RE}  "
                        f"{C_WHT}rps {C_CYAN}{rps:,}{RE}"
                    )
                # _dwrite: enqueue without blocking; display daemon batches to stdout
                _dwrite(
                    f"\r{' ' * 78}\r  {C_RED}{B}[TAKEN]{RE}  {C_WHT}{username:<20}{RE}\n{status_bar}"
                )

            else:
                # unexpected result — proxy already marked inside retry loop
                with g_lock:
                    g_errors += 1

        finally:
            work_q.task_done()


def _title_updater(platform: str):
    while g_running:
        rps = _current_rps()
        set_title(
            f"OGHunt {VERSION} | {platform.capitalize()} | "
            f"Hits: {g_hits} | Epic: {g_epic} | {rps:,} r/s | "
            f"Checked: {g_checked:,} | Proxies: {proxy_pool.alive_count()}"
        )
        time.sleep(0.2)


def run_sniper_session(
    platform: str,
    names_source: list[str] | Generator[str, None, None],
    total_count: int,
    workers: int,
):
    global g_hits, g_epic, g_checked, g_errors, g_rl_count, g_running, g_paused, _start_time

    workers = max(1, min(int(workers), MAX_WORKERS))
    use_tls = _use_tls_engine(workers)
    check_fn = PLATFORM_CHECKERS.get(platform, check_discord)

    g_hits     = 0
    g_epic     = 0
    g_checked  = 0
    g_errors   = 0
    g_rl_count = 0
    g_paused   = False
    g_running  = True
    _start_time = time.perf_counter()

    clr()
    print(f"\n  {C_PURP}■{RE} {C_WHT}{total_count:,}{RE} {C_PURP}{platform.capitalize()}{RE} names ready" if total_count > 0 else f"\n  {C_PURP}■{RE} Infinite {C_PURP}{platform.capitalize()}{RE} stream ready")
    p_mode = cfg.get("proxy_mode", "all")
    if p_mode == "single":
        print(f"  {C_PURP}■{RE} 1 pinned proxy ({cfg.get('selected_proxy')})")
    elif p_mode == "none":
        print(f"  {C_PURP}■{RE} Direct mode (0 proxies)")
    else:
        print(f"  {C_PURP}■{RE} {proxy_pool.alive_count():,} proxies loaded ({'verified' if proxy_pool.is_verified else 'unverified'})")

    print(f"  {C_PURP}■{RE} Engine: {C_CYAN}{'tls_client (JA3 spoof)' if use_tls else 'Pooled Custom-SSL (High-RPS)'}{RE}")
    print(f"\n  {C_WHT}Launching {C_PURP}{B}{workers:,}{RE}{C_WHT} workers on {C_PURP}{B}{platform.capitalize()}{RE} ... {C_GRY}(Ctrl+C stop · N pause){RE}\n")

    # Pre-build header pool (no json.dumps/base64 on hot path)
    _init_header_pool(512)

    # Rebuild proxy snapshot so lock-free reads are warm from the first request
    with proxy_pool._lock:
        proxy_pool._rebuild_snapshot()

    # Start async display daemon — workers never block on stdout
    threading.Thread(target=_display_daemon, daemon=True).start()

    time.sleep(0.35)

    _saved_term = None
    if sys.platform != "win32":
        try:
            import termios
            if sys.stdin.isatty():
                _saved_term = termios.tcgetattr(sys.stdin.fileno())
        except Exception:
            pass

    qsize = max(workers * 64, 16_384)   # large buffer — producer never stalls
    work_q  = queue.Queue(maxsize=qsize)
    done_ev = threading.Event()

    def _producer():
        for name in names_source:
            if not g_running:
                break
            while g_running:
                try:
                    work_q.put(name, timeout=0.4)
                    break
                except queue.Full:
                    continue
        done_ev.set()

    threading.Thread(target=_producer, daemon=True).start()
    threading.Thread(target=_kb_listener, daemon=True).start()
    threading.Thread(target=_title_updater, args=(platform,), daemon=True).start()

    for _ in range(workers):
        threading.Thread(
            target=_worker,
            args=(work_q, done_ev, platform, check_fn, use_tls, total_count),
            daemon=True,
        ).start()

    try:
        while g_running:
            if done_ev.is_set() and work_q.empty():
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        g_running = False

    g_running = False
    if _saved_term is not None:
        try:
            import termios
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _saved_term)
        except Exception:
            pass

    time.sleep(0.25)
    print(
        f"\n\n  {C_PURP}{B}[SESSION COMPLETE]{RE}  "
        f"Hits: {C_GRN}{B}{g_hits}{RE} (Epic: {C_MAG}{g_epic}{RE})  |  "
        f"Checked: {C_WHT}{g_checked:,}{RE}  |  "
        f"429 Cooldowns: {C_YLW}{g_rl_count:,}{RE}  |  "
        f"Avg Speed: {C_CYAN}{_current_rps():,} r/s{RE}  |  "
        f"Time: {C_WHT}{_elapsed()}{RE}"
    )
    input(f"\n  {C_GRY}Press Enter to return to dashboard...{RE}")

# ── UYP v5.0 Workflows: Generate, Check, Gen + Check, Wordlist ────────────────
def prompt_pattern_and_generate(platform: str) -> list[str] | None:
    render_banner(f"GENERATOR — {platform.upper()}")
    print()
    half = (len(PATTERN_CATALOG) + 1) // 2
    for i in range(half):
        l_id, l_name, l_ex = PATTERN_CATALOG[i]
        left_str = f"  {C_PURP}{l_id:>2}{RE}  {C_WHT}{l_name:<21}{RE} {C_GRY}{l_ex:<6}{RE}"
        if i + half < len(PATTERN_CATALOG):
            r_id, r_name, r_ex = PATTERN_CATALOG[i + half]
            right_str = f"   {C_PURP}{r_id:>2}{RE}  {C_WHT}{r_name:<21}{RE} {C_GRY}{r_ex}{RE}"
        else:
            right_str = ""
        print(left_str + right_str)

    print(f"\n  {C_DGRY}{'─' * 68}{RE}")
    pat = input(f"  {C_PURP}${RE} {C_WHT}Pattern (1-15) [2]: {RE}").strip() or "2"
    if pat not in [p[0] for p in PATTERN_CATALOG]:
        pat = "2"

    raw_len = input(f"  {C_PURP}${RE} {C_WHT}Length (2-32) [4]: {RE}").strip() or "4"
    length = int(raw_len) if raw_len.isdigit() and 2 <= int(raw_len) <= 32 else 4

    raw_cnt = input(f"  {C_PURP}${RE} {C_WHT}Count (1-10,000,000) [19999]: {RE}").strip() or "19999"
    count = int(raw_cnt) if raw_cnt.isdigit() and int(raw_cnt) > 0 else 19999
    count = min(count, 10_000_000)

    print(f"\n  {C_PURP}■{RE} {C_WHT}Generating {count:,} {platform.capitalize()} usernames ...{RE}")
    t0 = time.perf_counter()
    names: list[str] = []
    bar_w = 26
    step = max(1, count // 50)

    for idx, name in enumerate(stream_generator(pat, length, count), 1):
        names.append(name)
        if idx % step == 0 or idx == count:
            pct = (idx / count) * 100.0
            filled = int(bar_w * idx // count)
            bar = f"{C_PURP}{'█' * filled}{C_DGRY}{'░' * (bar_w - filled)}{RE}"
            sys.stdout.write(f"\r  {bar} {C_WHT}{B}{pct:6.1f}%{RE}  {C_GRY}{idx:,}/{count:,}{RE}")
            sys.stdout.flush()

    dt = time.perf_counter() - t0
    out_path = os.path.join(DATA_DIR, f"{platform}_names.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(names) + "\n")

    print(f"\n\n  {C_GRN}■{RE} {C_WHT}Done ({dt:.2f}s){RE}")
    print(f"  {C_PURP}■{RE} {C_GRY}Saved ->{RE} {C_WHT}{out_path}{RE}\n")
    print(f"  {C_GRY}Preview (first 10):{RE}\n")
    for i, sample in enumerate(names[:10], 1):
        print(f"  {C_PURP}[0]{RE} {C_GRY}{i:>2}.{RE} {C_WHT}{sample}{RE}")

    global g_loaded_names
    g_loaded_names = names
    return names


def prompt_workers() -> int:
    default_w = int(cfg.get("workers_default", 200))
    raw = input(f"\n  {C_PURP}${RE} {C_WHT}Workers (1-{MAX_WORKERS}, Enter = {default_w}): {RE}").strip()
    if raw.isdigit() and int(raw) > 0:
        w = min(int(raw), MAX_WORKERS)
        cfg["workers_default"] = w
        save_config()
        return w
    return min(default_w, MAX_WORKERS)


def action_generate_only():
    names = prompt_pattern_and_generate(g_current_platform)
    if names is not None:
        input(f"\n  {C_GRY}Press Enter to return...{RE}")


def action_check_loaded():
    global g_loaded_names
    if not g_loaded_names:
        default_file = os.path.join(DATA_DIR, f"{g_current_platform}_names.txt")
        if os.path.exists(default_file):
            with open(default_file, encoding="utf-8", errors="ignore") as f:
                g_loaded_names = [l.strip() for l in f if l.strip()]
    if not g_loaded_names:
        print(f"\n  {C_YLW}⚠ No names loaded in memory. Generating batch first...{RE}")
        time.sleep(0.8)
        names = prompt_pattern_and_generate(g_current_platform)
        if not names:
            return
    if not select_and_verify_proxies(g_current_platform):
        return
    workers = prompt_workers()
    run_sniper_session(g_current_platform, list(g_loaded_names), len(g_loaded_names), workers)


def action_gen_and_check():
    names = prompt_pattern_and_generate(g_current_platform)
    if not names:
        return
    print(f"\n  {C_GRY}Launching proxy & worker setup...{RE}")
    time.sleep(0.6)
    if not select_and_verify_proxies(g_current_platform):
        return
    workers = prompt_workers()
    run_sniper_session(g_current_platform, names, len(names), workers)


def action_wordlist_check():
    render_banner(f"WORDLIST CHECK — {g_current_platform.upper()}")
    default_path = os.path.join(DATA_DIR, f"{g_current_platform}_names.txt")
    path = input(f"\n  {C_PURP}${RE} {C_WHT}Wordlist path [{default_path}]: {RE}").strip() or default_path
    if not os.path.exists(path):
        print(f"\n  {C_RED}✗ File not found: {path}{RE}")
        time.sleep(1.2)
        return
    with open(path, encoding="utf-8", errors="ignore") as f:
        words = [l.strip() for l in f if l.strip()]
    if not words:
        print(f"\n  {C_RED}✗ Wordlist is empty.{RE}")
        time.sleep(1.2)
        return
    global g_loaded_names
    g_loaded_names = words
    print(f"  {C_GRN}✓ Loaded {len(words):,} usernames from {path}{RE}")
    time.sleep(0.5)
    if not select_and_verify_proxies(g_current_platform):
        return
    workers = prompt_workers()
    run_sniper_session(g_current_platform, words, len(words), workers)

# ── Managers (Proxies, Tokens, Hits, Config, Diagnostics) ─────────────────────
def proxy_manager_menu():
    while True:
        proxy_pool.load()
        render_banner("PROXY MANAGER & VERIFIER")
        p_mode = cfg.get("proxy_mode", "all").upper()
        sel_p  = cfg.get("selected_proxy", "") or "none"
        print(f"""
  {C_GRY}Total:{RE} {C_WHT}{proxy_pool.count():,}{RE}   {C_GRY}Alive:{RE} {C_GRN}{proxy_pool.alive_count():,}{RE}   {C_GRY}Verified:{RE} {C_CYAN}{proxy_pool.verified_count():,}{RE}   {C_GRY}Dead:{RE} {C_RED}{proxy_pool.dead_count():,}{RE}
  {C_GRY}Active Mode:{RE} {C_PURP}{B}{p_mode}{RE}   {C_GRY}Pinned Proxy:{RE} {C_WHT}{sel_p}{RE}

  {C_PURP}[1]{RE} {C_WHT}Verify ALL Proxies Against {g_current_platform.capitalize()}{RE}
  {C_PURP}[2]{RE} {C_WHT}Select Proxy Mode (Use All / Pick Specific / Direct){RE}
  {C_PURP}[3]{RE} {C_WHT}View Proxy List & Status{RE}
  {C_PURP}[4]{RE} {C_WHT}Remove Dead Proxies & Save{RE}
  {C_PURP}[5]{RE} {C_WHT}Import Proxies from File (.txt / .json){RE}
  {C_PURP}[6]{RE} {C_WHT}Paste Proxies Directly{RE}
  {C_PURP}[7]{RE} {C_WHT}Clear All Proxies{RE}
  {C_PURP}[0]{RE} {C_WHT}Back{RE}
""")
        ch = input(f"  {C_PURP}${RE} ").strip()
        if ch == "0":
            break
        elif ch == "1":
            print()
            res = proxy_pool.verify_all(platform=g_current_platform)
            ok = sum(1 for _, o, _ in res if o)
            print(f"\n  {C_GRN}✓ Verified {ok:,}/{len(res):,} working proxies.{RE}")
            input(f"\n  {C_GRY}Press Enter...{RE}")
        elif ch == "2":
            select_and_verify_proxies(g_current_platform)
        elif ch == "3":
            render_banner("PROXY LIST")
            items = proxy_pool.list_all()
            if not items:
                print(f"\n  {C_GRY}No proxies loaded.{RE}")
            else:
                for i, (u, st, ms) in enumerate(items[:100], 1):
                    col = C_GRN if st == "VERIFIED" else (C_RED if st == "DEAD" else C_YLW)
                    ms_s = f"{ms:>5.0f}ms" if ms > 0 else "   -  "
                    print(f"  {C_PURP}[{i:>3}]{RE} {C_WHT}{u:<48}{RE} {col}{st:<12}{RE} {C_GRY}{ms_s}{RE}")
            input(f"\n  {C_GRY}Press Enter...{RE}")
        elif ch == "4":
            proxy_pool.remove_dead()
            proxy_pool.save()
            print(f"  {C_GRN}✓ Dead proxies pruned and saved.{RE}")
            time.sleep(0.8)
        elif ch == "5":
            path = input(f"  {C_YLW}Path to file: {RE}").strip()
            if os.path.exists(path):
                n = proxy_pool.load(path)
                proxy_pool.save()
                print(f"  {C_GRN}✓ Imported {n:,} proxies.{RE}")
            else:
                print(f"  {C_RED}✗ File not found.{RE}")
            time.sleep(1.0)
        elif ch == "6":
            print(f"  {C_YLW}Paste proxies (ip:port or ip:port:user:pass), empty line to finish:{RE}")
            existing = [p for p, _, _ in proxy_pool.list_all()]
            added = 0
            while True:
                line = input().strip()
                if not line:
                    break
                parsed = proxy_pool._parse(line)
                if parsed and parsed not in existing:
                    existing.append(parsed)
                    added += 1
            with open(PROXY_FILE, "w", encoding="utf-8") as f:
                json.dump({"proxies": existing}, f, indent=2)
            proxy_pool.load()
            print(f"  {C_GRN}✓ Added {added} proxies.{RE}")
            time.sleep(0.8)
        elif ch == "7":
            with open(PROXY_FILE, "w", encoding="utf-8") as f:
                json.dump({"proxies": []}, f, indent=2)
            proxy_pool.load()
            print(f"  {C_GRN}✓ Proxy list cleared.{RE}")
            time.sleep(0.8)


def token_manager_menu():
    while True:
        token_pool.load_from_cfg()
        render_banner("DISCORD TOKEN MANAGER")
        tokens = token_pool.alive_list()
        mode = cfg.get("discord_check_mode", "auto")
        print(f"\n  {C_GRY}Alive Tokens:{RE} {C_GRN}{token_pool.alive_count()}{RE}   {C_GRY}Dead:{RE} {C_RED}{token_pool.dead_count()}{RE}   {C_GRY}Discord Check Mode:{RE} {C_CYAN}{mode.upper()}{RE}")
        print(f"  {C_GRY}(Note: Unauthed checks work with 0 tokens! Tokens are used for higher rate limits + instant auto-claim){RE}\n")
        if tokens:
            for i, t in enumerate(tokens[:30], 1):
                masked = t[:10] + "..." + t[-4:] if len(t) > 16 else t
                print(f"  {C_PURP}[{i:>2}]{RE} {C_WHT}{masked}{RE}")
        else:
            print(f"  {C_GRY}  No tokens loaded (using unauthed POMELO endpoint).{RE}")

        print(f"""
  {C_PURP}[1]{RE} {C_WHT}Add Token(s) (paste one or multiple){RE}
  {C_PURP}[2]{RE} {C_WHT}Import Tokens from File (tokens.txt){RE}
  {C_PURP}[3]{RE} {C_WHT}Toggle Discord Check Mode (auto / unauthed / authed){RE}
  {C_PURP}[4]{RE} {C_WHT}Clear All Tokens{RE}
  {C_PURP}[0]{RE} {C_WHT}Back{RE}
""")
        ch = input(f"  {C_PURP}${RE} ").strip()
        if ch == "0":
            break
        elif ch == "1":
            print(f"  {C_YLW}Paste token(s) (empty line to finish):{RE}")
            all_t = list(cfg.get("user_tokens", []))
            added = 0
            while True:
                line = input().strip()
                if not line:
                    break
                for part in re.split(r"[,\s]+", line):
                    if part and part not in all_t:
                        all_t.append(part)
                        added += 1
            cfg["user_tokens"] = all_t
            save_config()
            print(f"  {C_GRN}✓ Added {added} token(s).{RE}")
            time.sleep(0.7)
        elif ch == "2":
            path = input(f"  {C_YLW}File path [tokens.txt]: {RE}").strip() or "tokens.txt"
            if os.path.exists(path):
                all_t = list(cfg.get("user_tokens", []))
                with open(path, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        t = line.strip()
                        if t and not t.startswith("#") and t not in all_t:
                            all_t.append(t)
                cfg["user_tokens"] = all_t
                save_config()
                print(f"  {C_GRN}✓ Loaded {len(all_t)} total tokens.{RE}")
            else:
                print(f"  {C_RED}✗ File not found.{RE}")
            time.sleep(0.8)
        elif ch == "3":
            modes = ["auto", "unauthed", "authed"]
            cur = cfg.get("discord_check_mode", "auto")
            nxt = modes[(modes.index(cur) + 1) % len(modes)] if cur in modes else "auto"
            cfg["discord_check_mode"] = nxt
            save_config()
        elif ch == "4":
            cfg["user_tokens"] = []
            cfg["user_token"] = ""
            save_config()


def view_hits_menu():
    render_banner("SAVED HITS")
    print()
    if not os.path.exists(HITS_FILE):
        print(f"  {C_GRY}No hits recorded yet.{RE}")
    else:
        with open(HITS_FILE, encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
        if not lines:
            print(f"  {C_GRY}No hits recorded yet.{RE}")
        else:
            for i, h in enumerate(lines[-100:], 1):
                print(f"  {C_PURP}[{i:>3}]{RE} {C_GRN}★{RE} {C_WHT}{h}{RE}")
            print(f"\n  {C_PURP}Total Hits:{RE} {C_WHT}{B}{len(lines)}{RE}")
    input(f"\n  {C_GRY}Press Enter...{RE}")


def config_menu():
    while True:
        render_banner("SETTINGS & SNIPER OPTIONS")
        print(f"""
  {C_PURP}[1]{RE} {C_WHT}Webhook URL{RE}              {C_GRY}{('configured' if cfg.get('webhook') else 'empty')}{RE}
  {C_PURP}[2]{RE} {C_WHT}Discord Bot Token/Chan{RE}   {C_GRY}{('configured' if cfg.get('bot_token') else 'empty')}{RE}
  {C_PURP}[3]{RE} {C_WHT}HTTP Engine{RE}              {C_CYAN}{cfg.get('engine', 'auto')} (tls_client={'installed' if _HAS_TLS else 'not installed'}){RE}
  {C_PURP}[4]{RE} {C_WHT}Require Proxy Verify{RE}     {C_GRN if cfg.get('require_proxy_verify') else C_YLW}{cfg.get('require_proxy_verify')}{RE}
  {C_PURP}[5]{RE} {C_WHT}Default Workers (1-5000){RE} {C_WHT}{cfg.get('workers_default', 200)}{RE}
  {C_PURP}[6]{RE} {C_WHT}Request Delay (sec){RE}      {C_WHT}{cfg.get('req_delay', 0.0)}{RE}
  {C_PURP}[7]{RE} {C_WHT}Roblox / Minecraft Claim{RE} {C_GRY}Configure auto-claim tokens{RE}
  {C_PURP}[8]{RE} {C_WHT}Debug Raw Responses{RE}      {C_WHT}{cfg.get('debug', False)}{RE}
  {C_PURP}[9]{RE} {C_WHT}Test Endpoint / Webhook{RE}  {C_GRY}Live API & notification diagnostic{RE}
  {C_PURP}[0]{RE} {C_WHT}Back{RE}
""")
        ch = input(f"  {C_PURP}${RE} ").strip()
        if ch == "0":
            break
        elif ch == "1":
            cfg["webhook"] = input(f"  {C_YLW}Webhook URL: {RE}").strip()
            cfg["webhook_ping"] = input(f"  {C_YLW}User ID to @ping (optional): {RE}").strip()
            save_config()
        elif ch == "2":
            cfg["bot_token"] = input(f"  {C_YLW}Bot Token: {RE}").strip()
            cfg["channel_id"] = input(f"  {C_YLW}Channel ID: {RE}").strip()
            save_config()
        elif ch == "3":
            modes = ["auto", "requests", "tls_client"]
            cur = cfg.get("engine", "auto")
            cfg["engine"] = modes[(modes.index(cur) + 1) % len(modes)] if cur in modes else "auto"
            save_config()
        elif ch == "4":
            cfg["require_proxy_verify"] = not bool(cfg.get("require_proxy_verify", True))
            save_config()
        elif ch == "5":
            w = input(f"  {C_YLW}Default workers (1-{MAX_WORKERS}): {RE}").strip()
            if w.isdigit() and 1 <= int(w) <= MAX_WORKERS:
                cfg["workers_default"] = int(w)
                save_config()
        elif ch == "6":
            d = input(f"  {C_YLW}Delay in seconds (0.0 for max velocity): {RE}").strip()
            try:
                cfg["req_delay"] = max(0.0, float(d))
                save_config()
            except Exception:
                pass
        elif ch == "7":
            cfg["roblox_cookie"] = input(f"  {C_YLW}Roblox .ROBLOSECURITY (Enter to skip): {RE}").strip() or cfg.get("roblox_cookie", "")
            cfg["minecraft_token"] = input(f"  {C_YLW}Minecraft Bearer Token (Enter to skip): {RE}").strip() or cfg.get("minecraft_token", "")
            save_config()
        elif ch == "8":
            cfg["debug"] = not bool(cfg.get("debug", False))
            save_config()
        elif ch == "9":
            uname = input(f"  {C_YLW}Username to test on {g_current_platform} [testxyz991]: {RE}").strip() or "testxyz991"
            proxy = proxy_pool.get_for_request()
            fn = PLATFORM_CHECKERS[g_current_platform]
            t0 = time.perf_counter()
            res = fn(uname, proxy_url=proxy, use_tls=_use_tls_engine(1))
            ms = (time.perf_counter() - t0) * 1000.0
            print(f"\n  {C_WHT}Platform :{RE} {C_PURP}{g_current_platform.upper()}{RE}")
            print(f"  {C_WHT}Proxy    :{RE} {C_CYAN}{proxy or 'DIRECT'}{RE}")
            print(f"  {C_WHT}Result   :{RE} {C_GRN if res is True else (C_RED if res is False else C_YLW)}{res} ({ms:.0f}ms){RE}")
            if cfg.get("webhook"):
                send_webhook(uname, g_current_platform)
                print(f"  {C_GRN}✓ Sent test webhook.{RE}")
            input(f"\n  {C_GRY}Press Enter...{RE}")


def load_config():
    global cfg
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, encoding="utf-8") as f:
                saved = json.load(f)
            cfg.update(saved)
        except Exception:
            pass
    else:
        save_config()

def save_config():
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def _ensure_proxy_file():
    if not os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, "w", encoding="utf-8") as f:
            json.dump({"proxies": []}, f, indent=2)

# ── Main Two-Column Terminal Dashboard ────────────────────────────────────────
def main():
    global g_current_platform
    load_config()
    _ensure_proxy_file()
    proxy_pool.load()
    token_pool.load_from_cfg()
    boot_animation()

    while True:
        set_title(f"OGHunt {VERSION} | Platform: {g_current_platform.capitalize()} | Proxies: {proxy_pool.alive_count():,}")
        render_banner()

        def _plat_tag(key: str, code: str, label: str) -> str:
            active = (g_current_platform == code)
            dot = f"{C_PURP}●{RE}" if active else " "
            lbl_col = f"{C_WHT}{B}" if active else C_GRY
            return f"{C_PURP}[{key}]{RE} {lbl_col}{label:<10}{RE} {dot}"

        print(f"""  {C_GRY}ACTIONS                                  PLATFORM{RE}
  {C_PURP}[1]{RE} {C_WHT}Generate Names{RE}                       {_plat_tag('D', 'discord',   'Discord')}
  {C_PURP}[2]{RE} {C_WHT}Check Names{RE}                          {_plat_tag('R', 'roblox',    'Roblox')}
  {C_PURP}[3]{RE} {C_WHT}Gen + Check{RE}                          {_plat_tag('T', 'tiktok',    'TikTok')}
  {C_PURP}[4]{RE} {C_WHT}Wordlist Check{RE}                       {_plat_tag('I', 'instagram', 'Instagram')}
  {C_PURP}[5]{RE} {C_WHT}View Hits{RE}                            {_plat_tag('Y', 'youtube',   'YouTube')}
  {C_PURP}[6]{RE} {C_WHT}Proxy Manager & Verify{RE}               {_plat_tag('M', 'minecraft', 'Minecraft')}
  {C_PURP}[7]{RE} {C_WHT}Discord Token Manager{RE}
  {C_PURP}[8]{RE} {C_WHT}Sniper Options & Config{RE}
  {C_PURP}[0]{RE} {C_WHT}Exit{RE}
""")
        ch = input(f"  {C_PURP}${RE} ").strip().upper()

        if ch in PLATFORMS:
            g_current_platform = PLATFORMS[ch][0]
            proxy_pool.is_verified = False
        elif ch == "1":
            action_generate_only()
        elif ch == "2":
            action_check_loaded()
        elif ch == "3":
            action_gen_and_check()
        elif ch == "4":
            action_wordlist_check()
        elif ch == "5":
            view_hits_menu()
        elif ch == "6":
            proxy_manager_menu()
        elif ch == "7":
            token_manager_menu()
        elif ch == "8":
            config_menu()
        elif ch == "0":
            clr()
            for i, line in enumerate(_BANNER_LINES):
                print(_BANNER_GRAD[i % len(_BANNER_GRAD)] + B + line + RE)
            print(f"\n  {C_GRY}Session closed.{RE}\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n  {C_PURP}Exiting...{RE}")
