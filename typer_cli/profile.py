"""Local user profile and stats persistence."""

import json
import os
from datetime import date, datetime, timedelta

PROFILE_DIR = os.path.expanduser("~/.config/typer")
PROFILE_FILE = os.path.join(PROFILE_DIR, "profile.json")

_DEFAULT = {"name": "", "created": "", "tests": []}


def profile_exists():
    return os.path.isfile(PROFILE_FILE)


def read_profile():
    try:
        with open(PROFILE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(_DEFAULT)


def write_profile(data):
    os.makedirs(PROFILE_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create_profile(name):
    data = {
        "name": name,
        "created": datetime.now().isoformat(),
        "tests": [],
    }
    write_profile(data)
    return data


def set_name(name):
    p = read_profile()
    p["name"] = name
    write_profile(p)
    return p


def append_test(result, time_limit, difficulty):
    p = read_profile()
    p["tests"].append({
        "ts": datetime.now().isoformat(),
        "wpm": result["wpm"],
        "raw": result["raw"],
        "acc": result["acc"],
        "ok": result["ok"],
        "bad": result["bad"],
        "time_limit": time_limit,
        "difficulty": difficulty,
        "elapsed": result["time"],
    })
    write_profile(p)


# ── stats computation ────────────────────────────────────────────────────────

def _sparkline(wpms):
    if len(wpms) < 2:
        return ""
    lo, hi = min(wpms), max(wpms)
    chars = ["_", "-", "~", "^"]
    if hi == lo:
        return " ".join(["-"] * len(wpms))
    result = []
    for v in wpms:
        norm = (v - lo) / (hi - lo)
        idx = min(3, int(norm * 4))
        result.append(chars[idx])
    return " ".join(result)


def _streak(tests):
    if not tests:
        return 0
    dates = set()
    for t in tests:
        try:
            d = date.fromisoformat(t["ts"][:10])
            dates.add(d)
        except (ValueError, KeyError):
            continue
    if not dates:
        return 0
    today = date.today()
    day = today if today in dates else max(dates)
    streak = 0
    while day in dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def _fmt_time(secs):
    mins = int(secs) // 60
    if mins < 1:
        return "< 1m"
    hours = mins // 60
    mins = mins % 60
    if hours == 0:
        return f"{mins}m"
    return f"{hours}h {mins}m"


def _fmt_date(iso_str):
    try:
        d = datetime.fromisoformat(iso_str)
        return d.strftime("%b %-d, %Y")
    except (ValueError, TypeError):
        return ""


def _fmt_date_short(iso_str):
    try:
        d = datetime.fromisoformat(iso_str)
        return d.strftime("%b %-d")
    except (ValueError, TypeError):
        return ""


def compute_stats(profile):
    tests = profile.get("tests", [])
    name = profile.get("name", "")
    created = profile.get("created", "")

    s = {
        "name": name,
        "member_since": _fmt_date(created),
        "tests_completed": len(tests),
        "total_time_fmt": "0m",
        "best_wpm": None,
        "best_wpm_diff": None,
        "best_wpm_date": None,
        "avg_wpm_recent": None,
        "avg_acc": None,
        "sparkline": "",
        "per_diff": {},
        "streak": 0,
    }

    if not tests:
        return s

    # total time
    total_secs = sum(t.get("elapsed", 0) for t in tests)
    s["total_time_fmt"] = _fmt_time(total_secs)

    # best wpm
    best = max(tests, key=lambda t: t.get("wpm", 0))
    s["best_wpm"] = best.get("wpm", 0)
    s["best_wpm_diff"] = best.get("difficulty", "")
    s["best_wpm_date"] = _fmt_date_short(best.get("ts", ""))

    # avg wpm (last 10)
    recent = tests[-10:]
    s["avg_wpm_recent"] = sum(t.get("wpm", 0) for t in recent) / len(recent)

    # avg accuracy (all tests)
    s["avg_acc"] = sum(t.get("acc", 0) for t in tests) / len(tests)

    # sparkline (last 10)
    s["sparkline"] = _sparkline([t.get("wpm", 0) for t in recent])

    # per-difficulty averages
    for diff in ("easy", "medium", "hard"):
        dt = [t for t in tests if t.get("difficulty") == diff]
        if dt:
            s["per_diff"][diff] = sum(t.get("wpm", 0) for t in dt) / len(dt)

    # streak
    s["streak"] = _streak(tests)

    return s


def post_race_stats(current_wpm):
    """Compute leaderboard + avg delta after a race (called after append_test)."""
    p = read_profile()
    tests = p.get("tests", [])

    # top 3 fastest WPMs ever
    wpms = sorted([t.get("wpm", 0) for t in tests], reverse=True)
    top3 = wpms[:3]

    # avg delta: compare avg with this test vs avg without it
    if len(tests) >= 2:
        all_wpms = [t.get("wpm", 0) for t in tests]
        avg_with = sum(all_wpms) / len(all_wpms)
        prev_wpms = all_wpms[:-1]
        avg_without = sum(prev_wpms) / len(prev_wpms)
        avg_delta = avg_with - avg_without
    else:
        avg_delta = 0.0

    # what rank did this race land? (None if not in top 3)
    rank = None
    for i, w in enumerate(top3):
        if abs(w - current_wpm) < 0.01:
            rank = i + 1
            break

    return {
        "top3": top3,
        "avg_delta": avg_delta,
        "rank": rank,
    }
