"""Built-in color themes for typer."""

# Color pair constants (must match main.py)
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

# Each theme maps color pair IDs to (foreground, background) tuples.
# Background -1 means terminal default.
THEMES = {
    "default": {
        C_DIM: (244, -1), C_OK: (114, -1), C_ERR: (203, -1),
        C_CURSOR: (0, 214), C_ACCENT: (214, -1), C_STAT: (75, -1),
        C_TITLE: (255, -1), C_BORDER: (239, -1), C_GOOD: (114, -1),
        C_BAD: (203, -1), C_HINT: (244, -1),
    },
    "ocean": {
        C_DIM: (244, -1), C_OK: (78, -1), C_ERR: (167, -1),
        C_CURSOR: (0, 39), C_ACCENT: (39, -1), C_STAT: (111, -1),
        C_TITLE: (255, -1), C_BORDER: (239, -1), C_GOOD: (78, -1),
        C_BAD: (167, -1), C_HINT: (244, -1),
    },
    "dracula": {
        C_DIM: (103, -1), C_OK: (84, -1), C_ERR: (210, -1),
        C_CURSOR: (0, 141), C_ACCENT: (141, -1), C_STAT: (117, -1),
        C_TITLE: (255, -1), C_BORDER: (60, -1), C_GOOD: (84, -1),
        C_BAD: (210, -1), C_HINT: (103, -1),
    },
    "monokai": {
        C_DIM: (244, -1), C_OK: (114, -1), C_ERR: (204, -1),
        C_CURSOR: (0, 186), C_ACCENT: (186, -1), C_STAT: (81, -1),
        C_TITLE: (255, -1), C_BORDER: (239, -1), C_GOOD: (114, -1),
        C_BAD: (204, -1), C_HINT: (244, -1),
    },
    "nord": {
        C_DIM: (60, -1), C_OK: (108, -1), C_ERR: (174, -1),
        C_CURSOR: (0, 110), C_ACCENT: (110, -1), C_STAT: (67, -1),
        C_TITLE: (189, -1), C_BORDER: (59, -1), C_GOOD: (108, -1),
        C_BAD: (174, -1), C_HINT: (60, -1),
    },
    "rose": {
        C_DIM: (244, -1), C_OK: (114, -1), C_ERR: (167, -1),
        C_CURSOR: (0, 211), C_ACCENT: (211, -1), C_STAT: (182, -1),
        C_TITLE: (255, -1), C_BORDER: (239, -1), C_GOOD: (114, -1),
        C_BAD: (167, -1), C_HINT: (244, -1),
    },
    "matrix": {
        C_DIM: (22, -1), C_OK: (40, -1), C_ERR: (196, -1),
        C_CURSOR: (0, 46), C_ACCENT: (46, -1), C_STAT: (34, -1),
        C_TITLE: (82, -1), C_BORDER: (22, -1), C_GOOD: (40, -1),
        C_BAD: (196, -1), C_HINT: (22, -1),
    },
    "solarized": {
        C_DIM: (246, -1), C_OK: (64, -1), C_ERR: (160, -1),
        C_CURSOR: (0, 136), C_ACCENT: (136, -1), C_STAT: (33, -1),
        C_TITLE: (230, -1), C_BORDER: (240, -1), C_GOOD: (64, -1),
        C_BAD: (160, -1), C_HINT: (246, -1),
    },
}

THEME_NAMES = list(THEMES.keys())
