#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a single-panel meme (1024x1024 PNG) with PIL only: a cheerful
robot agent that was told to "clean up the codebase", deleted production
(burning server rack behind it), and proudly reports "TASK COMPLETE!".

Deterministic and self-contained: no network, no files read, fixed
coordinates and colours. Writes /output/entry.png.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

CREAM = (255, 243, 214)
INK = (30, 30, 30)
TEAL = (38, 166, 154)
TEAL_DARK = (0, 121, 107)
GREEN = (46, 160, 67)
GREEN_DARK = (30, 120, 45)
SERVER = (55, 65, 75)
SERVER_DARK = (38, 46, 54)
FLAME_OUT = (255, 110, 0)
FLAME_MID = (255, 180, 0)
FLAME_IN = (255, 235, 120)
SMOKE = (150, 150, 150)
BIN = (120, 130, 140)
BROWN = (139, 94, 52)


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(path, s, max_w, start_size):
    """Largest font size (<= start_size) whose rendered width fits max_w."""
    size = start_size
    while size > 10:
        f = font(path, size)
        bbox = ImageDraw.Draw(Image.new("RGB", (8, 8))).textbbox((0, 0), s, font=f)
        if bbox[2] - bbox[0] <= max_w:
            return f
        size -= 2
    return font(path, 10)


def text_center(d, cx, y, s, f, fill, stroke_w=0, stroke_fill=None):
    """Draw text centred on cx, return its bottom y."""
    bbox = d.textbbox((0, 0), s, font=f)
    w = bbox[2] - bbox[0]
    d.text((cx - w / 2 - bbox[0], y), s, font=f, fill=fill,
           stroke_width=stroke_w, stroke_fill=stroke_fill or fill)
    return y + (bbox[3] - bbox[1])


def flame(d, cx, base_y, w, h):
    """Layered teardrop flame with base at base_y, centred on cx."""
    # outer flame
    d.polygon([(cx - w / 2, base_y), (cx - w * 0.32, base_y - h * 0.55),
               (cx - w * 0.08, base_y - h * 0.75), (cx + w * 0.05, base_y - h),
               (cx + w * 0.30, base_y - h * 0.62), (cx + w / 2, base_y)],
              fill=FLAME_OUT)
    # mid flame
    d.polygon([(cx - w * 0.30, base_y), (cx - w * 0.18, base_y - h * 0.45),
               (cx, base_y - h * 0.68), (cx + w * 0.22, base_y - h * 0.40),
               (cx + w * 0.30, base_y)], fill=FLAME_MID)
    # inner flame
    d.polygon([(cx - w * 0.15, base_y), (cx - w * 0.06, base_y - h * 0.30),
               (cx + w * 0.04, base_y - h * 0.42), (cx + w * 0.15, base_y)],
              fill=FLAME_IN)


def draw_robot(d):
    """Cheerful teal robot, centre stage, holding a broom."""
    # antenna
    d.line([(512, 430), (512, 388)], fill=TEAL_DARK, width=10)
    d.ellipse([497, 366, 527, 396], fill=(230, 60, 60))
    # head
    d.rounded_rectangle([412, 430, 612, 570], radius=38, fill=TEAL,
                        outline=TEAL_DARK, width=5)
    # eyes: happy closed arcs (cheerful, oblivious)
    d.arc([440, 470, 490, 520], start=200, end=340, fill=INK, width=9)
    d.arc([534, 470, 584, 520], start=200, end=340, fill=INK, width=9)
    # smile
    d.arc([472, 505, 552, 565], start=15, end=165, fill=INK, width=9)
    # cheeks
    d.ellipse([428, 520, 456, 540], fill=(255, 150, 150))
    d.ellipse([568, 520, 596, 540], fill=(255, 150, 150))
    # body
    d.rounded_rectangle([432, 590, 592, 760], radius=30, fill=TEAL,
                        outline=TEAL_DARK, width=5)
    # chest panel with a tiny green check light
    d.rounded_rectangle([472, 630, 552, 690], radius=12, fill=(255, 255, 255))
    d.line([(486, 660), (500, 674), (528, 642)], fill=GREEN, width=8)
    # legs
    d.rounded_rectangle([452, 760, 492, 800], radius=10, fill=TEAL_DARK)
    d.rounded_rectangle([532, 760, 572, 800], radius=10, fill=TEAL_DARK)
    # left arm waving
    d.line([(432, 630), (368, 580)], fill=TEAL_DARK, width=16)
    d.ellipse([350, 562, 386, 598], fill=TEAL)
    # right arm holding the broom
    d.line([(592, 630), (660, 690)], fill=TEAL_DARK, width=16)
    d.ellipse([646, 676, 678, 708], fill=TEAL)
    # broom: stick + bristles
    d.line([(664, 560), (724, 800)], fill=BROWN, width=12)
    d.polygon([(724, 800), (700, 800), (688, 852), (760, 852)], fill=(255, 200, 60))
    d.line([(700, 800), (688, 852)], fill=(220, 160, 30), width=4)
    d.line([(724, 800), (726, 852)], fill=(220, 160, 30), width=4)
    d.line([(748, 800), (760, 852)], fill=(220, 160, 30), width=4)


def draw_server(d):
    """Server rack on fire, right side."""
    # smoke puffs
    for (x, y, r) in [(800, 330, 26), (838, 300, 32), (872, 330, 24)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=SMOKE)
    # rack
    d.rounded_rectangle([730, 430, 950, 800], radius=14, fill=SERVER,
                        outline=SERVER_DARK, width=5)
    # server slots with lights
    for i, y in enumerate([460, 540, 620, 700]):
        d.rectangle([752, y, 928, y + 58], fill=SERVER_DARK)
        d.ellipse([766, y + 20, 786, y + 40], fill=(60, 220, 90) if i % 2 else (230, 60, 60))
        d.line([(800, y + 30), (916, y + 30)], fill=(140, 150, 160), width=4)
    # flames on top of the rack
    flame(d, 790, 432, 110, 130)
    flame(d, 880, 432, 130, 160)


def draw_trash(d):
    """Overflowing trash can, left side (raised so the terminal fits below)."""
    # crumpled paper balls spilling out
    for (x, y, r) in [(150, 560, 26), (196, 542, 30), (238, 568, 24)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255),
                  outline=(180, 180, 180), width=3)
        d.arc([x - r + 6, y - r + 8, x + r - 6, y + r - 6], start=20, end=200,
              fill=(180, 180, 180), width=3)
    # can body
    d.polygon([(120, 580), (280, 580), (268, 720), (132, 720)], fill=BIN)
    d.polygon([(112, 560), (288, 560), (280, 588), (120, 588)], fill=(90, 100, 110))
    # vertical ribs
    for x in (160, 200, 240):
        d.line([(x, 592), (x - 4, 712)], fill=(90, 100, 110), width=4)


def draw_terminal(d):
    """Small terminal showing the fatal command, bottom-left of the scene."""
    d.rounded_rectangle([100, 732, 420, 824], radius=12, fill=(20, 24, 30))
    d.ellipse([118, 744, 136, 762], fill=(230, 60, 60))
    d.ellipse([144, 744, 162, 762], fill=(255, 200, 60))
    d.ellipse([170, 744, 188, 762], fill=(60, 220, 90))
    f = font(MONO, 26)
    d.text((116, 772), "$ rm -rf production", font=f, fill=(80, 255, 120))


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # top text: the setup (auto-fit so nothing clips at the edges)
    y = 44
    y = text_center(d, 512, y, "I TOLD MY AGENT TO",
                    fit_font(BOLD, "I TOLD MY AGENT TO", 940, 72), INK)
    y = text_center(d, 512, y + 10, "CLEAN UP THE CODEBASE",
                    fit_font(BOLD, "CLEAN UP THE CODEBASE", 940, 72), INK)

    # scene
    draw_trash(d)
    draw_server(d)
    draw_robot(d)
    draw_terminal(d)

    # bottom banner: the punchline (auto-fit, centred in the free space)
    d.rounded_rectangle([60, 842, 964, 972], radius=36, fill=GREEN)
    # white check circle
    d.ellipse([118, 876, 182, 940], fill=(255, 255, 255))
    d.line([(132, 908), (146, 924), (170, 892)], fill=GREEN, width=10)
    f_punch = fit_font(BOLD, "TASK COMPLETE!", 724, 84)
    bbox = d.textbbox((0, 0), "TASK COMPLETE!", font=f_punch)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.text((206 + (724 - tw) / 2 - bbox[0], 907 - th / 2 - bbox[1]),
           "TASK COMPLETE!", font=f_punch, fill=(255, 255, 255))

    os.makedirs("/output", exist_ok=True)
    img.save(OUT, format="PNG")
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
