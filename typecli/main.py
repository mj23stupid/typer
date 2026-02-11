import curses
import time
import argparse
import sys

from typecli.words import generate

# ── colors ───────────────────────────────────────────────────────────────────

C_DIM = 1
C_OK = 2
C_ERR = 3
C_CURSOR = 4
C_ACCENT = 5
C_STAT = 6
C_TITLE = 7
C_BORDER = 8
C_GOOD = 9
C_BAD = 10
C_HINT = 11


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_DIM, 244, -1)
    curses.init_pair(C_OK, 114, -1)
    curses.init_pair(C_ERR, 203, -1)
    curses.init_pair(C_CURSOR, 0, 214)
    curses.init_pair(C_ACCENT, 214, -1)
    curses.init_pair(C_STAT, 75, -1)
    curses.init_pair(C_TITLE, 255, -1)
    curses.init_pair(C_BORDER, 239, -1)
    curses.init_pair(C_GOOD, 114, -1)
    curses.init_pair(C_BAD, 203, -1)
    curses.init_pair(C_HINT, 244, -1)


# ── draw helpers ─────────────────────────────────────────────────────────────

def cx(w, n):
    return max(0, (w - n) // 2)


def put(win, y, x, text, cp=0, attr=0):
    try:
        win.addstr(y, x, text, curses.color_pair(cp) | attr)
    except curses.error:
        pass


def putc(win, y, w, text, cp=0, attr=0):
    put(win, y, cx(w, len(text)), text, cp, attr)


def box(win, y, x, h, w):
    put(win, y, x, "╭", C_BORDER)
    put(win, y, x + w - 1, "╮", C_BORDER)
    put(win, y + h - 1, x, "╰", C_BORDER)
    put(win, y + h - 1, x + w - 1, "╯", C_BORDER)
    for i in range(1, w - 1):
        put(win, y, x + i, "─", C_BORDER)
        put(win, y + h - 1, x + i, "─", C_BORDER)
    for j in range(1, h - 1):
        put(win, y + j, x, "│", C_BORDER)
        put(win, y + j, x + w - 1, "│", C_BORDER)


def wrap(text, width):
    lines, cur = [], ""
    for word in text.split(" "):
        test = f"{cur} {word}" if cur else word
        if len(test) <= width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ── settings ─────────────────────────────────────────────────────────────────

TIMES = [15, 30, 60, 120]
DIFFS = ["easy", "medium", "hard"]


def draw_settings(scr, y, w, ti, di, locked):
    """Draw the inline settings bar: 15  30  60  120  |  easy  medium  hard"""
    parts = []
    total = 0
    for i, t in enumerate(TIMES):
        label = str(t)
        parts.append(("time", i, label))
        total += len(label) + 2
    total += 3  # separator
    for i, d in enumerate(DIFFS):
        parts.append(("diff", i, d))
        total += len(d) + 2

    x = cx(w, total)
    for kind, idx, label in parts:
        if kind == "time" and idx == 0:
            pass  # first item, no prefix spacing needed
        if kind == "diff" and idx == 0:
            put(scr, y, x, " | ", C_BORDER)
            x += 3

        if kind == "time":
            active = idx == ti
        else:
            active = idx == di

        if active:
            if locked:
                put(scr, y, x, label, C_DIM, curses.A_BOLD)
            else:
                put(scr, y, x, label, C_ACCENT, curses.A_BOLD)
        else:
            put(scr, y, x, label, C_DIM)
        x += len(label) + 2


# ── stats helpers ────────────────────────────────────────────────────────────

def calc_wpm(target, typed, elapsed):
    if elapsed < 0.5:
        return "-"
    ok = sum(1 for i in range(min(len(typed), len(target))) if typed[i] == target[i])
    return f"{(ok / 5) / (elapsed / 60):.0f}"


def calc_acc(target, typed):
    if not typed:
        return "-"
    ok = sum(1 for i in range(min(len(typed), len(target))) if typed[i] == target[i])
    return f"{ok / len(typed) * 100:.1f}%"


def calc_results(target, typed, elapsed):
    n = min(len(typed), len(target))
    ok = sum(1 for i in range(n) if typed[i] == target[i])
    bad = n - ok
    w = (ok / 5) / (elapsed / 60) if elapsed > 0 else 0
    rw = (len(typed) / 5) / (elapsed / 60) if elapsed > 0 else 0
    a = (ok / len(typed) * 100) if typed else 0
    errs = {}
    for i in range(n):
        if typed[i] != target[i]:
            errs[target[i]] = errs.get(target[i], 0) + 1
    return dict(wpm=w, raw=rw, acc=a, ok=ok, bad=bad,
                missed=max(0, len(target) - len(typed)),
                chars=len(typed), time=elapsed, errs=errs)


# ── text drawing ─────────────────────────────────────────────────────────────

def draw_text(scr, lines, typed, target, sy, sx, aw, sh):
    pos = len(typed)
    maxl = sh - sy - 4
    cline, ci = 0, 0
    for i, line in enumerate(lines):
        if ci + len(line) >= pos:
            cline = i
            break
        ci += len(line) + 1

    vis = min(maxl, 3)
    ss = max(0, min(cline - 1, len(lines) - vis))
    off = sum(len(lines[i]) + 1 for i in range(ss))

    for li in range(ss, min(ss + vis, len(lines))):
        line = lines[li]
        y = sy + (li - ss)
        if y >= sh - 3:
            break
        for ci2, ch in enumerate(line):
            ri = off + ci2
            x = sx + ci2
            if x >= sx + aw:
                break
            if ri < pos:
                cp = C_OK if ri < len(typed) and typed[ri] == target[ri] else C_ERR
                at = curses.A_UNDERLINE if cp == C_ERR else 0
                put(scr, y, x, ch, cp, at)
            elif ri == pos:
                put(scr, y, x, ch, C_CURSOR, curses.A_BOLD)
            else:
                put(scr, y, x, ch, C_DIM)
        off += len(line) + 1


# ── main test loop ───────────────────────────────────────────────────────────

def test(scr, ti, di):
    curses.curs_set(0)
    scr.nodelay(True)
    scr.timeout(50)

    tlimit = TIMES[ti]
    diff = DIFFS[di]
    wc = max(80, tlimit * 3)
    target = generate(wc, diff)
    typed = []
    started = False
    t0 = 0.0

    while True:
        now = time.time()
        elapsed = (now - t0) if started else 0.0
        remain = tlimit - elapsed
        done = started and elapsed >= tlimit
        if done:
            break

        scr.erase()
        h, w = scr.getmaxyx()
        if h < 10 or w < 40:
            scr.addstr(0, 0, "terminal too small!")
            scr.refresh()
            if scr.getch() == 27:
                return None, ti, di
            continue

        # settings bar
        draw_settings(scr, 1, w, ti, di, started)

        # stats (only show once started)
        by = 3
        if started:
            _wpm = calc_wpm(target, typed, elapsed)
            _acc = calc_acc(target, typed)
            ts = f"{max(0, remain):.0f}s"

            bar = f"  {_wpm} wpm   {_acc} acc   {ts}  "
            bx = cx(w, len(bar) + 4)
            box(scr, by, bx, 3, len(bar) + 4)

            px = bx + 3
            put(scr, by + 1, px, _wpm, C_ACCENT, curses.A_BOLD)
            put(scr, by + 1, px + len(_wpm), " wpm   ", C_DIM)
            px += len(_wpm) + 7
            ac = C_GOOD if _acc not in ("-",) and float(_acc.rstrip("%")) >= 90 else C_BAD if _acc != "-" else C_DIM
            put(scr, by + 1, px, _acc, ac, curses.A_BOLD)
            put(scr, by + 1, px + len(_acc), " acc   ", C_DIM)
            px += len(_acc) + 7
            tc = C_BAD if remain < 5 else C_ACCENT
            put(scr, by + 1, px, ts, tc, curses.A_BOLD)
        else:
            # countdown placeholder
            ts = f"{tlimit}s"
            putc(scr, by + 1, w, ts, C_ACCENT, curses.A_BOLD)

        # text
        aw = min(w - 8, 72)
        tx = cx(w, aw)
        ty = by + 5
        lines = wrap(target, aw)
        draw_text(scr, lines, typed, target, ty, tx, aw, h)

        # hints
        if not started:
            putc(scr, ty - 1, w, "start typing...", C_DIM)
            putc(scr, h - 2, w, "←/→ time   ↑/↓ difficulty   tab new words   esc quit", C_HINT)
        else:
            putc(scr, h - 2, w, "tab restart   esc quit", C_HINT)

        scr.refresh()

        # input
        k = scr.getch()
        if k == -1:
            continue
        if k == 27:
            return None, ti, di
        if k == 9:  # tab
            return "restart", ti, di

        if not started:
            # settings keys (before test starts)
            if k == curses.KEY_LEFT:
                ti = (ti - 1) % len(TIMES)
                tlimit = TIMES[ti]
                target = generate(max(80, tlimit * 3), DIFFS[di])
                typed = []
                continue
            elif k == curses.KEY_RIGHT:
                ti = (ti + 1) % len(TIMES)
                tlimit = TIMES[ti]
                target = generate(max(80, tlimit * 3), DIFFS[di])
                typed = []
                continue
            elif k == curses.KEY_UP:
                di = (di - 1) % len(DIFFS)
                target = generate(max(80, tlimit * 3), DIFFS[di])
                typed = []
                continue
            elif k == curses.KEY_DOWN:
                di = (di + 1) % len(DIFFS)
                target = generate(max(80, tlimit * 3), DIFFS[di])
                typed = []
                continue

        # typing
        if not started and 32 <= k <= 126:
            started = True
            t0 = time.time()

        if k in (curses.KEY_BACKSPACE, 127, 8):
            if typed:
                typed.pop()
        elif 32 <= k <= 126 and len(typed) < len(target):
            typed.append(chr(k))

    elapsed = time.time() - t0 if started else 0.001
    return calc_results(target, typed, elapsed), ti, di


# ── results screen ───────────────────────────────────────────────────────────

def show_results(scr, r, ti, di):
    curses.curs_set(0)
    scr.nodelay(False)
    scr.timeout(-1)

    while True:
        scr.erase()
        h, w = scr.getmaxyx()
        y = max(1, h // 2 - 10)

        putc(scr, y, w, "── results ──", C_TITLE, curses.A_BOLD)
        y += 2
        putc(scr, y, w, f"{r['wpm']:.0f} wpm", C_ACCENT, curses.A_BOLD)
        y += 2

        bw = 48
        bx = cx(w, bw)
        box(scr, y, bx, 8, bw)
        c1 = bx + 3
        c2 = bx + bw // 2 + 2
        ry = y + 1

        def sr(label, val, cp, col, row):
            put(scr, row, col, f"{label}: ", C_DIM)
            put(scr, row, col + len(label) + 2, str(val), cp, curses.A_BOLD)

        sr("wpm", f"{r['wpm']:.1f}", C_ACCENT, c1, ry)
        sr("raw", f"{r['raw']:.1f}", C_STAT, c2, ry)
        ry += 1
        sr("accuracy", f"{r['acc']:.1f}%", C_GOOD if r['acc'] >= 90 else C_BAD, c1, ry)
        sr("time", f"{r['time']:.1f}s", C_ACCENT, c2, ry)
        ry += 1
        sr("correct", str(r['ok']), C_GOOD, c1, ry)
        sr("incorrect", str(r['bad']), C_BAD, c2, ry)
        ry += 2

        blen = min(int(r['wpm']), bw - 6)
        put(scr, ry, c1, "█" * max(blen, 1), C_ACCENT)
        ry += 2

        if r['acc'] >= 97 and r['wpm'] >= 80:
            putc(scr, ry, w, "blazing", C_ACCENT, curses.A_BOLD)
        elif r['acc'] >= 95 and r['wpm'] >= 60:
            putc(scr, ry, w, "great", C_GOOD, curses.A_BOLD)
        elif r['acc'] >= 90:
            putc(scr, ry, w, "solid", C_STAT, curses.A_BOLD)
        elif r['acc'] >= 80:
            putc(scr, ry, w, "keep practicing", C_DIM, curses.A_BOLD)
        else:
            putc(scr, ry, w, "slow down, focus on accuracy", C_BAD, curses.A_BOLD)

        if r['errs']:
            ry += 2
            top = sorted(r['errs'].items(), key=lambda x: -x[1])[:6]
            putc(scr, ry, w, "missed: " + "  ".join(f"'{c}'x{n}" for c, n in top), C_DIM)

        # mode reminder
        putc(scr, h - 4, w, f"{TIMES[ti]}s  {DIFFS[di]}", C_DIM)
        putc(scr, h - 2, w, "tab restart   esc new test   q quit", C_HINT)
        scr.refresh()

        k = scr.getch()
        if k == 9:
            return "restart"
        elif k == 27:
            return "new"
        elif k in (ord('q'), ord('Q')):
            return "quit"


# ── main ─────────────────────────────────────────────────────────────────────

def run(scr, args):
    init_colors()
    curses.curs_set(0)

    # default: 30s, medium
    ti = TIMES.index(args.time) if args.time and args.time in TIMES else 1
    di = DIFFS.index(args.diff) if args.diff and args.diff in DIFFS else 1

    while True:
        result, ti, di = test(scr, ti, di)

        if result is None:
            return
        if result == "restart":
            continue

        action = show_results(scr, result, ti, di)
        if action == "restart":
            continue
        elif action == "quit":
            return
        else:  # "new" — loop back to test with settings bar
            continue


def entry():
    parser = argparse.ArgumentParser(
        prog="typer",
        description="typer — typing practice in your terminal",
    )
    parser.add_argument("-t", "--time", type=int, metavar="SEC",
                        help="time in seconds (15, 30, 60, 120)")
    parser.add_argument("-d", "--diff", type=str, metavar="LEVEL",
                        choices=["easy", "medium", "hard"],
                        help="difficulty (easy, medium, hard)")
    args = parser.parse_args()

    try:
        curses.wrapper(lambda scr: run(scr, args))
    except KeyboardInterrupt:
        pass
