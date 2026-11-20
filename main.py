#!/usr/bin/env python3
"""news-image-20261120 — Sum up 20 November 2026 world news in one image.

Entry for make.fun bounty news-image-20261120.

Writes a 1024x1024 PNG front page to <output>/entry.png (default /output,
overridable with MAKEFUN_OUTPUT_DIR / OUTPUT_DIR).

The image is rendered programmatically with Pillow from the fixed story data
below — no network, no downloaded assets, no randomness: two runs write
byte-identical files. Fonts are embedded in assets/fonts/ so rendering does
not depend on system fonts. If Pillow is unavailable, main() falls back to
copying the pre-rendered assets/entry.png (same bytes).

Stories (all reported on Friday 20 November 2026):
  1. Donald Trump says there is no rush on the Iran decision — he will
     "see what happens" after 1 January, pushing any call on military
     action into 2027.
  2. The International Court of Justice rules that Myanmar committed
     genocide against the Rohingya.
  3. Cyclone Akvan: 300,000 people evacuated as the storm nears
     India's Odisha coast.
  4. NASA's Voyager 1 reaches a "light-day" from Earth — about
     26 billion km, the farthest any human-made object has travelled.
  5. Grand Theft Auto VI sales pass the $1.80bn global run of
     The Odyssey.
Also noted: Europe says it is ready for talks with Russia on Ukraine.
Markets (Thursday 19 November US close): Dow -2.19% to 49,097 (below
50,000), S&P 500 -2.02% to 7,176, Nasdaq -2.25% to 23,879; gold
$3,686; Brent $92; Bitcoin about $61,500.

Sources: Reuters, BBC, The Hindu, NASA, Mezha, Longbridge / The Edge —
see SOURCES.md.
"""

import hashlib
import os
import shutil
import sys

W, H = 1024, 1024
MX = 36                      # side margin
CW = W - 2 * MX              # content width = 952

PAPER = (250, 246, 238)      # warm newsprint
INK = (26, 26, 26)
NAVY = (20, 33, 61)
RED = (185, 28, 28)
GREY = (90, 90, 90)
MUTED = (60, 60, 60)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(ASSETS, "fonts")
PRE_RENDERED = os.path.join(ASSETS, "entry.png")


# ---------------------------------------------------------------- fonts
def load_font(name, size):
    from PIL import ImageFont
    path = os.path.join(FONTS, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------- helpers
def wrap_text(draw, text, fnt, max_w):
    """Greedy word wrap; returns the lines that fit inside max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def shrink_to_fit(draw, text, name, sizes, max_w):
    """Largest font (sizes descending) in which text fits max_w."""
    for size in sizes:
        fnt = load_font(name, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
    return load_font(name, sizes[-1])


def centered_pair(draw, y, left, left_font, left_fill,
                  right, right_font, right_fill, gap=20):
    """Two text runs centred as one line; returns nothing."""
    lw = draw.textlength(left, font=left_font)
    rw = draw.textlength(right, font=right_font)
    x = (W - lw - gap - rw) // 2
    draw.text((x, y), left, font=left_font, fill=left_fill)
    draw.text((x + lw + gap, y), right, font=right_font, fill=right_fill)


# ---------------------------------------------------------------- icons
def tile(draw, x, y, s, color):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=14, fill=color)


def icon_scales(draw, x, y, s):
    # scales of justice: post, beam, two hanging pans
    cx = x + s // 2
    draw.line([(cx, y + 14), (cx, y + 64)], fill=WHITE, width=5)
    draw.line([(cx - 28, y + 22), (cx + 28, y + 22)], fill=WHITE, width=5)
    draw.ellipse([cx - 5, y + 10, cx + 5, y + 20], fill=WHITE)
    for side in (-1, 1):
        px = cx + side * 28
        draw.line([(px, y + 22), (px - 12, y + 44)], fill=WHITE, width=3)
        draw.line([(px, y + 22), (px + 12, y + 44)], fill=WHITE, width=3)
        draw.pieslice([px - 13, y + 38, px + 13, y + 58], start=0, end=180,
                      fill=WHITE)
    draw.line([(cx - 22, y + 68), (cx + 22, y + 68)], fill=WHITE, width=5)


def icon_storm(draw, x, y, s):
    # cloud, rain and a lightning bolt
    draw.ellipse([x + 14, y + 16, x + 44, y + 44], fill=WHITE)
    draw.ellipse([x + 34, y + 10, x + 64, y + 40], fill=WHITE)
    draw.ellipse([x + 52, y + 20, x + 76, y + 46], fill=WHITE)
    draw.rectangle([x + 16, y + 34, x + 74, y + 48], fill=WHITE)
    for rx in (24, 38, 52, 66):
        draw.line([(x + rx, y + 56), (x + rx - 4, y + 70)],
                  fill=(150, 200, 255), width=4)
    draw.polygon([(x + 58, y + 40), (x + 46, y + 62), (x + 54, y + 62),
                  (x + 48, y + 76), (x + 64, y + 54), (x + 56, y + 54),
                  (x + 66, y + 40)], fill=GOLD)


def icon_satellite(draw, x, y, s):
    # satellite body, two solar panels, antenna
    cx, cy = x + s // 2, y + s // 2
    draw.polygon([(cx - 14, cy - 8), (cx + 8, cy - 16), (cx + 16, cy + 6),
                  (cx - 6, cy + 14)], fill=WHITE)
    draw.polygon([(cx - 40, cy + 2), (cx - 20, cy - 6), (cx - 16, cy + 8),
                  (cx - 36, cy + 16)], fill=(150, 200, 255))
    draw.polygon([(cx + 18, cy - 4), (cx + 38, cy - 12), (cx + 42, cy + 2),
                  (cx + 22, cy + 10)], fill=(150, 200, 255))
    draw.line([(cx + 4, cy - 16), (cx + 14, cy - 30)], fill=WHITE, width=3)
    draw.ellipse([cx + 10, cy - 36, cx + 18, cy - 28], fill=GOLD)


def icon_controller(draw, x, y, s):
    # gamepad: body, d-pad, buttons, sticks
    draw.rounded_rectangle([x + 10, y + 28, x + 78, y + 62], radius=14,
                           fill=WHITE)
    draw.rectangle([x + 22, y + 36, x + 28, y + 52], fill=INK)
    draw.rectangle([x + 17, y + 41, x + 33, y + 47], fill=INK)
    for bx, by in [(58, 36), (66, 44), (58, 52), (50, 44)]:
        draw.ellipse([x + bx, y + by, x + bx + 7, y + by + 7], fill=RED)
    draw.ellipse([x + 38, y + 50, x + 46, y + 58], fill=INK)
    draw.ellipse([x + 56, y + 30, x + 64, y + 38], fill=INK)


# ---------------------------------------------------------------- lead art
def draw_calendar(draw, x, y, w, h):
    """A calendar page for 1 January 2027."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=WHITE,
                           outline=INK, width=2)
    draw.rounded_rectangle([x, y, x + w, y + 32], radius=8, fill=RED)
    draw.rectangle([x, y + 24, x + w, y + 32], fill=RED)
    f_year = load_font("DejaVuSans-Bold.ttf", 20)
    draw.text((x + w // 2, y + 16), "2027", font=f_year, fill=WHITE,
              anchor="mm")
    f_day = load_font("DejaVuSans-Bold.ttf", 34)
    draw.text((x + w // 2, y + 72), "JAN 1", font=f_day, fill=NAVY,
              anchor="mm")
    for rx in (x + 52, x + w - 52):
        draw.ellipse([rx - 5, y - 4, rx + 5, y + 8], fill=INK)


def draw_quote(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10,
                           outline=NAVY, width=2)
    f_q = load_font("DejaVuSerif-Bold.ttf", 27)
    f_a = load_font("DejaVuSans.ttf", 18)
    draw.text((x + 24, y + 20), "\u201cWe\u2019ll see what happens.\u201d",
              font=f_q, fill=INK)
    draw.text((x + 24, y + 66), "\u2014 Donald Trump, on the Iran decision",
              font=f_a, fill=GREY)


# ---------------------------------------------------------------- render
def render():
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_mast = load_font("DejaVuSerif-Bold.ttf", 58)
    f_date = load_font("DejaVuSans-Bold.ttf", 21)
    f_kick = load_font("DejaVuSans-Bold.ttf", 20)
    f_lead = load_font("DejaVuSans-Bold.ttf", 46)
    f_sub = load_font("DejaVuSans.ttf", 23)
    f_head = load_font("DejaVuSans-Bold.ttf", 28)
    f_sum = load_font("DejaVuSans.ttf", 21)
    f_also = load_font("DejaVuSans.ttf", 19)
    f_mkt = load_font("DejaVuSans-Bold.ttf", 18)
    f_foot = load_font("DejaVuSans.ttf", 14)

    # ---- masthead
    d.text((W // 2, 26), "THE WORLD TODAY", font=f_mast, fill=NAVY,
           anchor="ma")
    d.text((W // 2, 94), "FRIDAY, 20 NOVEMBER 2026", font=f_date,
           fill=RED, anchor="ma")
    d.line([MX, 126, MX + CW, 126], fill=NAVY, width=3)
    d.line([MX, 132, MX + CW, 132], fill=NAVY, width=1)

    # ---- lead story
    y = 148
    d.text((MX, y), "IRAN DECISION DELAYED  \u2022  LEAD STORY",
           font=f_kick, fill=RED)
    y = 176
    for line in ["TRUMP PUSHES IRAN WAR", "DECISION TO 2027"]:
        d.text((MX, y), line, font=f_lead, fill=INK)
        y += 56
    y = 292
    sub = ("Trump says there is no rush on the Iran decision, pushing "
           "any call on military action into the new year.")
    for line in wrap_text(d, sub, f_sub, CW)[:2]:
        d.text((MX, y), line, font=f_sub, fill=INK)
        y += 30

    # ---- lead art: calendar + quote
    ay = 366
    draw_calendar(d, MX, ay, 220, 110)
    draw_quote(d, MX + 244, ay, CW - 244, 110)

    # ---- divider
    d.line([MX, 514, MX + CW, 514], fill=NAVY, width=3)

    # ---- four story rows
    stories = [
        ("ICJ RULES MYANMAR COMMITTED GENOCIDE",
         "The World Court finds Myanmar committed genocide against "
         "the Rohingya people.",
         (76, 29, 149), icon_scales),
        ("CYCLONE AKVAN: 300,000 EVACUATED",
         "The storm nears India's Odisha coast as authorities move "
         "residents to safety.",
         (13, 110, 71), icon_storm),
        ("VOYAGER 1 REACHES \u201cLIGHT-DAY\u201d MILESTONE",
         "NASA's farthest spacecraft passes one light-day from Earth "
         "\u2014 about 26 billion km.",
         (37, 99, 235), icon_satellite),
        ("GTA 6 SALES PASS THE ODYSSEY'S $1.80BN RUN",
         "Rockstar's blockbuster overtakes the $1.80bn global run of "
         "Christopher Nolan's epic.",
         (185, 28, 28), icon_controller),
    ]
    ry = 532
    tile_s = 88
    for headline, summary, color, icon in stories:
        tile(d, MX, ry, tile_s, color)
        icon(d, MX, ry, tile_s)
        tx = MX + tile_s + 16
        tw = CW - tile_s - 16
        hf = shrink_to_fit(d, headline, "DejaVuSans-Bold.ttf",
                           [28, 27, 26, 25, 24], tw)
        d.text((tx, ry + 2), headline, font=hf, fill=INK)
        sy = ry + 38
        for line in wrap_text(d, summary, f_sum, tw)[:2]:
            d.text((tx, sy), line, font=f_sum, fill=MUTED)
            sy += 26
        ry += 94

    # ---- also in the news
    also = ("ALSO:  Europe ready for Russia talks on Ukraine")
    ay = 912
    for line in wrap_text(d, also, f_also, CW)[:2]:
        d.text((MX, ay), line, font=f_also, fill=GREY)
        ay += 24

    # ---- markets band (two lines, Thursday 19 Nov US close)
    # The MARKETS label gets its own treatment: a wider gap plus a gold
    # vertical divider, so the label reads as the band's header rather
    # than blending into the first index value.
    d.rectangle([0, 946, W, 1000], fill=NAVY)
    mkt_label = "MARKETS"
    mkt_line1 = ("Dow \u22122.19% 49,097    S&P 500 \u22122.02% 7,176    "
                 "Nasdaq \u22122.25% 23,879")
    mkt_gap = 34
    lw = d.textlength(mkt_label, font=f_mkt)
    rw = d.textlength(mkt_line1, font=f_mkt)
    mx = (W - lw - mkt_gap - rw) // 2
    d.text((mx, 950), mkt_label, font=f_mkt, fill=GOLD)
    d.text((mx + lw + mkt_gap, 950), mkt_line1, font=f_mkt, fill=WHITE)
    sep_x = mx + lw + mkt_gap // 2
    d.line([(sep_x, 953), (sep_x, 969)], fill=GOLD, width=2)
    line2 = "Gold $3,686    Brent $92    Bitcoin ~$61,500"
    d.text(((W - d.textlength(line2, font=f_mkt)) // 2, 974), line2,
           font=f_mkt, fill=WHITE)

    # ---- footer
    d.text((W // 2, 1005), "A summary of world news \u2014 Friday 20 November 2026",
           font=f_foot, fill=GREY, anchor="ma")

    return img


def main():
    out_dir = (os.environ.get("MAKEFUN_OUTPUT_DIR")
               or os.environ.get("OUTPUT_DIR") or "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    try:
        img = render()
        img.save(out_path, format="PNG")
    except Exception as exc:  # Pillow missing/broken: use pre-rendered
        print(f"render failed ({exc}); copying pre-rendered image",
              file=sys.stderr)
        if not os.path.exists(PRE_RENDERED):
            raise
        shutil.copyfile(PRE_RENDERED, out_path)

    with open(out_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    size = os.path.getsize(out_path)
    print(f"wrote {out_path} ({size} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
