# -*- coding: utf-8 -*-
# config.py

# Animation settings
FPS = 30

# Breathing Presets (in seconds)
# Each preset is a list of tuples: (phase_name, duration)
PRESETS = {
    "4-7-8呼吸 (放松)": [("inhale", 4), ("hold", 7), ("exhale", 8)],
    "盒子呼吸 (专注)": [
        ("inhale", 4),
        ("hold", 4),
        ("exhale", 4),
        ("hold_post", 4),  # Post-exhale hold
    ],
    "自定义": [("inhale", 4), ("hold", 4), ("exhale", 6)],
}

# --- Morandi Color Palette ---
MORANDI_BLUE_DARK = 59
MORANDI_BLUE_LIGHT = 67
MORANDI_PINK_LIGHT = 175
MORANDI_GREY = 244
MORANDI_WHITE = 252

# --- Breathing Color Scheme ---
# Maps phase names to start/end colors
COLOR_MAP = {
    "inhale": (MORANDI_BLUE_DARK, MORANDI_BLUE_LIGHT),
    "hold": (MORANDI_BLUE_LIGHT, MORANDI_PINK_LIGHT),
    "exhale": (MORANDI_BLUE_LIGHT, MORANDI_BLUE_DARK),
    "hold_post": (
        MORANDI_BLUE_DARK,
        MORANDI_BLUE_DARK,
    ),  # A static, calm color for the second hold
}

# --- Shape Settings ---
MIN_RADIUS = 2.0
MAX_RADIUS = 10.0
# Reverted to character-based anti-aliasing
ANTI_ALIAS_CHARS = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]
