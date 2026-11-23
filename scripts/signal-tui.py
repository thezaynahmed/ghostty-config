#!/usr/bin/env python3
"""Modern Vercel/Google-inspired Neofetch Batcomputer TUI for ghostty-theme --signal."""

from __future__ import annotations

import colorsys
import json
import os
import re
import sys
from pathlib import Path

INNER_W = 74  # Total bordered line width = 2 ("│ ") + 74 + 2 (" │") = 78 cols
ANSI_RE = re.compile(r"\033\[[0-9;]*m")

LORE_META = {
    "Gotham Noir - Year One": {
        "short": "Year One",
        "protocol": "YEAR-ONE / DETECTIVE-27",
        "badge": "DETECTIVE #27",
        "canvas_label": "Kevlar",
        "accent_label": "Signal",
        "roles": ["Kevlar", "Crimsn", "Oracle", "Signal", "Detect", "Violet", "Sonar", "Text"],
        "quote": "Without fear, life has no meaning.  - Gotham, Year One",
    },
    "Gotham Noir - Batcomputer": {
        "short": "Batcomputer",
        "protocol": "BATCAVE / SUB-LEVEL-04",
        "badge": "DETECTIVE #27",
        "canvas_label": "Cave",
        "accent_label": "Beacon",
        "roles": ["Cave", "Crimsn", "Oracle", "Signal", "Detect", "Violet", "Sonar", "Text"],
        "quote": "Applied Sciences: Sub-Level 04 telemetry online.",
    },
    "Gotham Noir - Arkham Slate": {
        "short": "Arkham Slate",
        "protocol": "ARKHAM / DETECTIVE-MODE",
        "badge": "DETECTIVE #27",
        "canvas_label": "Slate",
        "accent_label": "Signal",
        "roles": ["Slate", "Crimsn", "Oracle", "Signal", "Detect", "Violet", "Sonar", "Text"],
        "quote": "Weathered Arkham stonework calibrated for 3 AM clarity.",
    },
    "Gotham Noir - Vengeance": {
        "short": "Vengeance",
        "protocol": "VENGEANCE / ICEBERG-2022",
        "badge": "DETECTIVE #27",
        "canvas_label": "Kevlar",
        "accent_label": "Flare",
        "roles": ["Kevlar", "Flare", "Oracle", "Signal", "Detect", "Violet", "Sonar", "Text"],
        "quote": "Thursday, October 31st. Iceberg Lounge emergency telemetry.",
    },
}


def visible_len(text: str) -> int:
    """Return visible terminal cell width excluding ANSI SGR escape sequences."""
    return len(ANSI_RE.sub("", text))


def hex_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB into (r, g, b) integer tuple."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (216, 214, 207)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix_hex(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate two #RRGGBB colors."""
    r1, g1, b1 = hex_rgb(c1)
    r2, g2, b2 = hex_rgb(c2)
    r = max(0, min(255, round(r1 + (r2 - r1) * t)))
    g = max(0, min(255, round(g1 + (g2 - g1) * t)))
    b = max(0, min(255, round(b1 + (b2 - b1) * t)))
    return f"#{r:02x}{g:02x}{b:02x}"


def fg(hex_color: str, text: str, bold: bool = False) -> str:
    """Apply 24-bit ANSI foreground color."""
    r, g, b = hex_rgb(hex_color)
    prefix = "\033[1;" if bold else "\033["
    return f"{prefix}38;2;{r};{g};{b}m{text}\033[0m"


def wcag_contrast(c1: str, c2: str) -> float:
    """Compute WCAG 2.1 contrast ratio."""
    def lum(h: str) -> float:
        def ch(v: float) -> float:
            return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        r, g, b = (ch(x / 255.0) for x in hex_rgb(h))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    l1, l2 = lum(c1), lum(c2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def apca_lc(fg_hex: str, bg_hex: str) -> float:
    """Compute absolute APCA-W3 Lc contrast value."""
    def y_apca(h: str) -> float:
        r, g, b = (x / 255.0 for x in hex_rgb(h))
        y = 0.2126729 * (r ** 2.4) + 0.7151522 * (g ** 2.4) + 0.0721750 * (b ** 2.4)
        return y if y >= 0.022 else y + (0.022 - y) ** 1.414
    yt, yb = y_apca(fg_hex), y_apca(bg_hex)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        sapc = (yb ** 0.56 - yt ** 0.57) * 1.14
        return abs((sapc - 0.027) * 100.0) if sapc >= 0.1 else 0.0
    sapc = (yb ** 0.65 - yt ** 0.62) * 1.14
    return abs((sapc + 0.027) * 100.0) if sapc <= -0.1 else 0.0


def hue_sep_deg(c1: str, c2: str) -> float:
    """Return circular HSV hue separation in degrees."""
    h1 = colorsys.rgb_to_hsv(*(x / 255.0 for x in hex_rgb(c1)))[0] * 360.0
    h2 = colorsys.rgb_to_hsv(*(x / 255.0 for x in hex_rgb(c2)))[0] * 360.0
    diff = abs(h1 - h2) % 360.0
    return min(diff, 360.0 - diff)


def read_runtime_meta(config_path: str) -> tuple[str, str, str]:
    """Read font family, font size, and cursor style from Ghostty config plus Starship profile."""
    font_family = "Monaspace Neon"
    font_size = "14.5"
    cursor_style = "block"
    cfg = Path(config_path)
    if cfg.exists():
        for line in cfg.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            m = re.match(r"^(\S+)\s*=\s*(.+)$", s)
            if not m:
                continue
            k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
            if k == "font-family":
                font_family = v
            elif k == "font-size":
                font_size = v
            elif k == "cursor-style":
                cursor_style = v

    profile = "off"
    state_dir = os.environ.get("GHOSTTY_SHELL_STATE_DIR") or str(
        Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "ghostty-shell"
    )
    prof_file = Path(state_dir) / "profile"
    if prof_file.exists():
        val = prof_file.read_text(encoding="utf-8").strip()
        if val:
            profile = val
    return f"{font_family} {font_size}", cursor_style, profile


def truncate_plain(text: str, max_len: int) -> str:
    """Truncate plain text cleanly using ASCII ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."


def render_card(config_path: str, theme: str, colors: dict) -> str:
    """Render the full 78-column Batcomputer TUI diagnostic card."""
    bg = colors.get("background", "#15171a")
    fg_col = colors.get("foreground", "#d8d6cf")
    bright_fg = colors.get("ansiBrightWhite", fg_col)
    muted = colors.get("ansiBrightBlack", "#878d96")
    red = colors.get("ansiRed", "#e86a74")
    green = colors.get("ansiGreen", "#63c794")
    yellow = colors.get("ansiYellow", "#f0c946")
    blue = colors.get("ansiBlue", "#74aeeb")
    cursor = colors.get("cursor_color", yellow)
    sel_bg = colors.get("selection_bg", "#323a46")
    accent = cursor if theme.endswith("Vengeance") else yellow

    border_col = mix_hex(bg, muted, 0.35)
    glow_col = mix_hex(bg, accent, 0.32)

    meta = LORE_META.get(
        theme,
        {
            "short": theme,
            "protocol": "STANDARD / GHOSTTY",
            "badge": "LIVE CONFIG",
            "canvas_label": "Canvas",
            "accent_label": "Cursor",
            "roles": ["Black", "Red", "Green", "Yellow", "Blue", "Magen", "Cyan", "White"],
            "quote": "Live Ghostty terminal telemetry and ANSI contrast audit.",
        },
    )

    def box_row(content: str) -> str:
        vis = visible_len(content)
        pad = max(0, INNER_W - vis)
        return fg(border_col, "│ ") + content + (" " * pad) + fg(border_col, " │")

    def top_line() -> str:
        return fg(border_col, "╭" + ("─" * (INNER_W + 2)) + "╮")

    def mid_line() -> str:
        return fg(border_col, "├" + ("─" * (INNER_W + 2)) + "┤")

    def bot_line() -> str:
        return fg(border_col, "╰" + ("─" * (INNER_W + 2)) + "╯")

    def lbl(name: str) -> str:
        return fg(muted, f"{name:<10}")

    # Header bar
    brand = "GOTHAM NOIR" if theme in LORE_META else "GHOSTTY THEME"
    hdr_left = f"{fg(accent, '▲')} {fg(bright_fg, brand, bold=True)}  {fg(muted, '/')}  {fg(fg_col, truncate_plain(meta['short'], 24))}"
    hdr_right = f"{fg(green, '● ONLINE')}  {fg(muted, '·')}  {fg(accent, meta['badge'])}"
    hdr_gap = max(1, INNER_W - visible_len(hdr_left) - visible_len(hdr_right))
    header = hdr_left + (" " * hdr_gap) + hdr_right

    # Left spotlight emblem (strictly 20 visual cols + 2 trailing spaces = 22)
    emblem_rows = [
        ("    ", "░░░░░░░░░░░░", "    "),
        ("  ", "░░ ", "▀▄  ▄▄  ▄▀", " ░░  "),
        (" ", "░░ ", "████████████", " ░░ "),
        (" ", "░░ ", "████████████", " ░░ "),
        (" ", "░░  ", "▀██▀██▀██▀", "  ░░ "),
        ("  ", "░░   ", "▀████▀", "   ░░  "),
        ("    ", "░░░░░", "▀▀", "░░░░░    "),
    ]

    def render_emblem_row(idx: int) -> str:
        parts = emblem_rows[idx]
        if len(parts) == 3:
            s = parts[0] + fg(glow_col, parts[1]) + parts[2]
        else:
            s = parts[0] + fg(glow_col, parts[1]) + fg(accent, parts[2], bold=True) + fg(glow_col, parts[3])
        return s + (" " * 2)  # exact 22 visual cols

    # Live telemetry values
    cr = wcag_contrast(fg_col, bg)
    lc = apca_lc(fg_col, bg)
    rg_deg = hue_sep_deg(red, green)
    grade = "AAA" if cr >= 7.0 else ("AA" if cr >= 4.5 else "LOW")
    grade_col = green if cr >= 7.0 else (yellow if cr >= 4.5 else red)
    font_str, cursor_style, starship_prof = read_runtime_meta(config_path)

    canvas_lbl = f"{meta['canvas_label']:<8}"
    accent_lbl = f"{meta['accent_label']:<8}"
    contrast_str = f"{cr:.2f}:1 {grade}"

    info_rows = [
        lbl("THEME") + fg(bright_fg, truncate_plain(theme, 40), bold=True),
        lbl("PROTOCOL") + fg(accent, truncate_plain(meta["protocol"], 40)),
        lbl("CANVAS") + f"{fg(bg, '██')} {fg(fg_col, bg.lower())} {fg(muted, canvas_lbl)}  {fg(fg_col, '██')} {fg(fg_col, fg_col.lower())}",
        lbl("ACCENT") + f"{fg(cursor, '██')} {fg(fg_col, cursor.lower())} {fg(muted, accent_lbl)}  {fg(sel_bg, '██')} {fg(fg_col, sel_bg.lower())}",
        lbl("CONTRAST") + f"{fg(grade_col, contrast_str, bold=True)} {fg(muted, '·')} {fg(fg_col, f'Lc {lc:.1f}')} {fg(muted, '·')} {fg(fg_col, f'R/G {rg_deg:.0f}deg')}",
        lbl("RUNTIME") + fg(fg_col, truncate_plain(f"Ghostty · {font_str} · zsh", 40)),
        lbl("PROMPT") + fg(fg_col, truncate_plain(f"Starship {starship_prof} · {cursor_style} cursor", 40)),
    ]

    split_rows = []
    sep = fg(border_col, "│ ")
    for i in range(7):
        left = render_emblem_row(i)
        right = info_rows[i]
        split_rows.append(box_row(left + sep + right))

    # 8-Channel Spectrum Grid (8 cols x 9 chars = 72 chars + 2 indent = 74)
    ansi_keys = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
    norm_tiles = "  " + "".join(fg(colors.get(f"ansi{k}", "#000000"), "██████") + "   " for k in ansi_keys)
    bright_tiles = "  " + "".join(fg(colors.get(f"ansiBright{k}", "#000000"), "██████") + "   " for k in ansi_keys)
    role_row = "  " + "".join(fg(muted, f"{r:<9}") for r in meta["roles"])
    hex_row = "  " + "".join(fg(fg_col, f"{colors.get(f'ansi{k}', '#000000').lstrip('#').lower():<9}") for k in ansi_keys)

    # Telemetry & switch footer
    hal_ok = bg.lower() != "#000000" and fg_col.lower() != "#ffffff"
    hal_msg = fg(accent, "▲ 0 halation") if hal_ok else fg(red, "▲ #000/#fff glare")
    telem = (
        lbl("TELEMETRY")
        + fg(green, "✔ 6/6 pods ready")
        + fg(muted, " · ")
        + fg(green, "+42")
        + " "
        + fg(red, "-8")
        + fg(muted, " diff · ")
        + hal_msg
        + fg(muted, " · ")
        + fg(blue, f"● WCAG {grade}")
    )

    sw_left = lbl("SWITCH") + fg(fg_col, "batman") + fg(muted, " · ") + fg(fg_col, "batcomputer") + fg(muted, " · ") + fg(fg_col, "arkham") + fg(muted, " · ") + fg(fg_col, "vengeance")
    sw_right = fg(muted, "Cmd+Shift+, reload")
    sw_gap = max(1, INNER_W - visible_len(sw_left) - visible_len(sw_right))
    switch_line = sw_left + (" " * sw_gap) + sw_right

    lines = [
        top_line(),
        box_row(header),
        mid_line(),
        *split_rows,
        mid_line(),
        box_row(lbl("PALETTE") + fg(muted, "8-CHANNEL SPECTRUM (NORMAL / BRIGHT)")),
        box_row(norm_tiles.rstrip()),
        box_row(bright_tiles.rstrip()),
        box_row(role_row.rstrip()),
        box_row(hex_row.rstrip()),
        mid_line(),
        box_row(telem),
        box_row(switch_line),
        bot_line(),
        "  " + fg(muted, meta["quote"]),
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: signal-tui.py <config-path> <theme-name> <colors-json>", file=sys.stderr)
        return 2
    config_path = sys.argv[1]
    theme = sys.argv[2]
    colors = json.loads(sys.argv[3]) if sys.argv[3] else {}
    print(render_card(config_path, theme, colors))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
