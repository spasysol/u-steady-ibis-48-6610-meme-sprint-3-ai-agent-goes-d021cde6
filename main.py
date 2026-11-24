#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a single-panel meme (1024x1024 PNG): a cheerful robot agent that
was told to "clean up the codebase", deleted production (burning server
rack behind it), and proudly reports "TASK COMPLETE!".

PURE PYTHON STDLIB ONLY. No PIL, no third-party imports, no font files,
no network, nothing read from disk. The image is drawn by a small
rasterizer in this file (rect/ellipse/polygon/line/arc spans over a
bytearray) and the text comes from a tiny 5x7 bitmap font embedded below,
rendered scaled up as filled rectangles. The PNG is written with
zlib + struct (IHDR/IDAT/IEND, CRC32). Deterministic: same bytes on
every run. Writes <MAKEFUN_OUTPUT_DIR>/entry.png (default /output).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

CREAM = (255, 243, 214)
INK = (30, 30, 30)
WHITE = (255, 255, 255)
TEAL = (38, 166, 154)
TEAL_DARK = (0, 121, 107)
GREEN = (46, 160, 67)
SERVER = (55, 65, 75)
SERVER_DARK = (38, 46, 54)
FLAME_OUT = (255, 110, 0)
FLAME_MID = (255, 180, 0)
FLAME_IN = (255, 235, 120)
SMOKE = (150, 150, 150)
BIN = (120, 130, 140)
BIN_DARK = (90, 100, 110)
BROWN = (139, 94, 52)
GOLD = (255, 200, 60)
GOLD_DARK = (220, 160, 30)
RED = (230, 60, 60)
PINK = (255, 150, 150)
TERM = (20, 24, 30)
TERM_GREEN = (80, 255, 120)
SLOT_LINE = (140, 150, 160)
GREY_LINE = (180, 180, 180)

# ---------------------------------------------------------------- font ----
# Tiny 5x7 bitmap font. Each glyph is 7 rows of 5 bits ('1' = ink).
# Covers A-Z, a-z, 0-9, space, $ - ! . ' /
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    'q': ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}

# ------------------------------------------------------------- rasterizer --
# The image is one bytearray of W*H*3 RGB bytes, row-major.
buf = bytearray()


def rect(x0, y0, x1, y1, color):
    """Fill half-open rect [x0,x1) x [y0,y1) with a solid colour."""
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    if x0 >= x1 or y0 >= y1:
        return
    row = bytes(color) * (x1 - x0)
    for y in range(y0, y1):
        off = (y * W + x0) * 3
        buf[off:off + len(row)] = row


def ellipse(cx, cy, rx, ry, color, clip=None):
    """Fill an ellipse centred (cx, cy) with radii (rx, ry).

    clip, if given, is (x0, y0, x1, y1): spans are intersected with it,
    which is how rounded-rectangle corners are drawn.
    """
    if rx <= 0 or ry <= 0:
        return
    y_lo = max(0, cy - ry)
    y_hi = min(H, cy + ry + 1)
    for y in range(y_lo, y_hi):
        dy = (y + 0.5 - cy) / ry
        if dy <= -1.0 or dy >= 1.0:
            continue
        half = rx * math.sqrt(1.0 - dy * dy)
        xa = int(math.ceil(cx - half))
        xb = int(math.floor(cx + half)) + 1
        if clip is not None:
            xa = max(xa, clip[0])
            xb = min(xb, clip[2])
            if y < clip[1] or y >= clip[3]:
                continue
        rect(xa, y, xb, y + 1, color)


def poly(points, color):
    """Fill a polygon (list of (x, y)) with a scanline fill."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_lo = max(0, int(math.floor(min(ys))))
    y_hi = min(H, int(math.ceil(max(ys))))
    n = len(points)
    for y in range(y_lo, y_hi):
        yc = y + 0.5
        xs = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= yc < y1) or (y1 <= yc < y0):
                t = (yc - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            rect(int(math.ceil(xs[i])), y, int(math.floor(xs[i + 1])) + 1,
                 y + 1, color)


def disc(cx, cy, r, color):
    ellipse(cx, cy, r, r, color)


def line(x0, y0, x1, y1, width, color):
    """Thick line via Bresenham steps with a disc at each step."""
    r = max(1, width // 2)
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        disc(x, y, r, color)
        if x == x1 and y == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def arc(cx, cy, rx, ry, a0, a1, width, color):
    """Arc from angle a0 to a1 (degrees, clockwise from 3 o'clock,
    y pointing down -- same convention as PIL's ImageDraw.arc)."""
    r = max(1, width // 2)
    a = a0
    while a <= a1:
        t = math.radians(a)
        disc(int(round(cx + rx * math.cos(t))),
             int(round(cy + ry * math.sin(t))), r, color)
        a += 2


def rrect(x0, y0, x1, y1, r, color):
    """Fill a rounded rectangle (half-open coords, corner radius r)."""
    r = max(1, min(r, (x1 - x0) // 2, (y1 - y0) // 2))
    rect(x0 + r, y0, x1 - r, y1, color)
    rect(x0, y0 + r, x1, y1 - r, color)
    ellipse(x0 + r, y0 + r, r, r, color, clip=(x0, y0, x0 + r, y0 + r))
    ellipse(x1 - r, y0 + r, r, r, color, clip=(x1 - r, y0, x1, y0 + r))
    ellipse(x0 + r, y1 - r, r, r, color, clip=(x0, y1 - r, x0 + r, y1))
    ellipse(x1 - r, y1 - r, r, r, color, clip=(x1 - r, y1 - r, x1, y1))


def rrect_outline(x0, y0, x1, y1, r, outline, fill, w):
    """Rounded rect with an outline: outer shape in outline colour,
    inner shape inset by w in the fill colour."""
    rrect(x0, y0, x1, y1, r, outline)
    rrect(x0 + w, y0 + w, x1 - w, y1 - w, max(1, r - w), fill)


# ------------------------------------------------------------------- text --
def text_w(s, scale):
    """Pixel width of string s rendered at the given scale."""
    return (len(s) * 6 - 1) * scale


def fit_scale(s, max_w, start):
    """Largest scale (<= start) whose rendered width fits max_w."""
    scale = start
    while scale > 1 and text_w(s, scale) > max_w:
        scale -= 1
    return scale


def text(s, x, y, scale, color):
    """Draw string s with its top-left at (x, y). One glyph cell is
    6*scale wide (5 px glyph + 1 px gap), 7*scale tall."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is not None:
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == '1':
                        rect(cx + col_i * scale, y + row_i * scale,
                             cx + (col_i + 1) * scale,
                             y + (row_i + 1) * scale, color)
        cx += 6 * scale


# ------------------------------------------------------------------ scene --
def flame(cx, base_y, w, h):
    """Layered teardrop flame with its base at base_y, centred on cx."""
    poly([(cx - w / 2, base_y), (cx - w * 0.32, base_y - h * 0.55),
          (cx - w * 0.08, base_y - h * 0.75), (cx + w * 0.05, base_y - h),
          (cx + w * 0.30, base_y - h * 0.62), (cx + w / 2, base_y)],
         FLAME_OUT)
    poly([(cx - w * 0.30, base_y), (cx - w * 0.18, base_y - h * 0.45),
          (cx, base_y - h * 0.68), (cx + w * 0.22, base_y - h * 0.40),
          (cx + w * 0.30, base_y)], FLAME_MID)
    poly([(cx - w * 0.15, base_y), (cx - w * 0.06, base_y - h * 0.30),
          (cx + w * 0.04, base_y - h * 0.42), (cx + w * 0.15, base_y)],
         FLAME_IN)


def draw_robot():
    """Cheerful teal robot, centre stage, holding a broom."""
    # antenna
    line(512, 430, 512, 388, 10, TEAL_DARK)
    disc(512, 381, 15, RED)
    # head
    rrect_outline(412, 430, 612, 570, 38, TEAL_DARK, TEAL, 5)
    # eyes: happy closed arcs (top half)
    arc(465, 495, 25, 25, 200, 340, 9, INK)
    arc(559, 495, 25, 25, 200, 340, 9, INK)
    # smile (bottom half)
    arc(512, 535, 40, 30, 15, 165, 9, INK)
    # cheeks
    ellipse(442, 530, 14, 10, PINK)
    ellipse(582, 530, 14, 10, PINK)
    # body
    rrect_outline(432, 590, 592, 760, 30, TEAL_DARK, TEAL, 5)
    # chest panel with a tiny green check light
    rrect(472, 630, 552, 690, 12, WHITE)
    line(486, 660, 500, 674, 8, GREEN)
    line(500, 674, 528, 642, 8, GREEN)
    # legs
    rrect(452, 760, 492, 800, 10, TEAL_DARK)
    rrect(532, 760, 572, 800, 10, TEAL_DARK)
    # left arm waving
    line(432, 630, 368, 580, 16, TEAL_DARK)
    ellipse(368, 580, 18, 18, TEAL)
    # right arm holding the broom
    line(592, 630, 660, 690, 16, TEAL_DARK)
    ellipse(662, 692, 16, 16, TEAL)
    # broom: stick + bristles (kept fully above the bottom banner)
    line(664, 560, 722, 786, 12, BROWN)
    poly([(722, 786), (700, 786), (690, 836), (756, 836)], GOLD)
    line(700, 786, 690, 836, 4, GOLD_DARK)
    line(722, 786, 724, 836, 4, GOLD_DARK)
    line(744, 786, 756, 836, 4, GOLD_DARK)


def draw_server():
    """Server rack on fire, right side."""
    # smoke puffs
    ellipse(800, 330, 26, 26, SMOKE)
    ellipse(838, 300, 32, 32, SMOKE)
    ellipse(872, 330, 24, 24, SMOKE)
    # rack
    rrect_outline(730, 430, 950, 800, 14, SERVER_DARK, SERVER, 5)
    # server slots with lights
    for i, y in enumerate([460, 540, 620, 700]):
        rect(752, y, 928, y + 58, SERVER_DARK)
        disc(776, y + 30, 10, (60, 220, 90) if i % 2 else RED)
        line(800, y + 30, 916, y + 30, 4, SLOT_LINE)
    # flames on top of the rack
    flame(790, 432, 110, 130)
    flame(880, 432, 130, 160)


def draw_trash():
    """Overflowing trash can, left side (raised so the terminal fits)."""
    # crumpled paper balls spilling out
    for (x, y, r) in [(150, 560, 26), (196, 542, 30), (238, 568, 24)]:
        disc(x, y, r + 3, GREY_LINE)
        disc(x, y, r, WHITE)
        arc(x, y + 1, r - 6, r - 7, 20, 200, 3, GREY_LINE)
    # can body
    poly([(120, 580), (280, 580), (268, 720), (132, 720)], BIN)
    poly([(112, 560), (288, 560), (280, 588), (120, 588)], BIN_DARK)
    # vertical ribs
    for x in (160, 200, 240):
        line(x, 592, x - 4, 712, 4, BIN_DARK)


def draw_terminal():
    """Small terminal showing the fatal command, bottom-left."""
    rrect(92, 732, 448, 824, 12, TERM)
    disc(127, 753, 9, RED)
    disc(153, 753, 9, (255, 200, 60))
    disc(179, 753, 9, (60, 220, 90))
    text("$ rm -rf production", 104, 776, 3, TERM_GREEN)


# -------------------------------------------------------------------- png --
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)


def write_png(path):
    """Write the canvas as a deterministic 1024x1024 RGB PNG."""
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", comp) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------------------- main --
def main():
    global buf
    buf = bytearray(CREAM * (W * H))

    # top text: the setup (auto-fit so nothing clips at the edges)
    y = 44
    s1 = fit_scale("I TOLD MY AGENT TO", 940, 8)
    text("I TOLD MY AGENT TO", (W - text_w("I TOLD MY AGENT TO", s1)) // 2,
         y, s1, INK)
    y += 7 * s1 + 10
    s2 = fit_scale("CLEAN UP THE CODEBASE", 940, 8)
    text("CLEAN UP THE CODEBASE",
         (W - text_w("CLEAN UP THE CODEBASE", s2)) // 2, y, s2, INK)

    # scene
    draw_trash()
    draw_server()
    draw_robot()
    draw_terminal()

    # bottom banner: the punchline
    rrect(60, 842, 964, 972, 36, GREEN)
    # white check circle
    disc(150, 908, 32, WHITE)
    line(132, 908, 146, 924, 10, GREEN)
    line(146, 924, 170, 892, 10, GREEN)
    s3 = fit_scale("TASK COMPLETE!", 724, 8)
    text("TASK COMPLETE!", 206 + (724 - text_w("TASK COMPLETE!", s3)) // 2,
         907 - (7 * s3) // 2, s3, WHITE)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    write_png(out)
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
