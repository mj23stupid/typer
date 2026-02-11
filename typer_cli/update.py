"""Auto-update checker — hits GitHub releases API, caches daily."""

import json
import os
import time
import subprocess
import shutil
from urllib.request import urlopen, Request
from urllib.error import URLError

from typer_cli import __version__

REPO = "William-Ger/typer"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
CACHE_DIR = os.path.expanduser("~/.config/typer")
CACHE_FILE = os.path.join(CACHE_DIR, "update_cache.json")
CHECK_INTERVAL = 86400  # 1 day in seconds


def _read_cache():
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_cache(data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def _fetch_latest():
    """Fetch latest release tag from GitHub. Returns version string or None."""
    try:
        req = Request(API_URL, headers={"Accept": "application/vnd.github+json"})
        with urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            tag = data.get("tag_name", "")
            return tag.lstrip("v")
    except (URLError, OSError, json.JSONDecodeError, KeyError):
        return None


def _parse_version(v):
    """Parse '0.1.0' into tuple (0, 1, 0) for comparison."""
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0,)


def _is_newer(latest, current):
    return _parse_version(latest) > _parse_version(current)


def check_for_update():
    """Check for updates. Returns (latest_version, needs_update) or (None, False)."""
    cache = _read_cache()
    last_check = cache.get("last_check", 0)
    cached_latest = cache.get("latest_version")

    # only hit the API once per day
    if time.time() - last_check < CHECK_INTERVAL and cached_latest:
        if _is_newer(cached_latest, __version__):
            return cached_latest, True
        return None, False

    latest = _fetch_latest()
    if latest:
        _write_cache({"last_check": time.time(), "latest_version": latest})
        if _is_newer(latest, __version__):
            return latest, True

    return None, False


def prompt_update():
    """Check for updates and prompt the user. Call before entering curses."""
    try:
        latest, needs_update = check_for_update()
    except Exception:
        return  # never let update check crash the app

    if not needs_update:
        return

    print(f"\n  typer v{latest} is available (you have v{__version__})")

    has_brew = shutil.which("brew") is not None
    if has_brew:
        try:
            answer = input("  update now? [y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if answer in ("y", "yes"):
            print("  updating...")
            result = subprocess.run(
                ["brew", "upgrade", "typer"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print("  updated! restart typer to use the new version.")
                raise SystemExit(0)
            else:
                print(f"  brew upgrade failed: {result.stderr.strip()}")
                print("  continuing with current version...\n")
        else:
            print()
    else:
        print(f"  run: pip install --upgrade typer-cli-tool\n")
