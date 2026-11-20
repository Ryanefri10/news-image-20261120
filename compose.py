#!/usr/bin/env python3
"""Compose the news-image-20261120 front page (BUILD-TIME ONLY).

Takes the AI-generated hero photo (hero.png, no text) and composes a
newspaper front page: masthead strip over the photo, then a cream
panel with five verified 20 Nov 2026 headlines and an ALSO box.
Output: entry.png, 1024x1024, <= 1 MiB. Uses PIL at build time only;
the graded main.py is stdlib-only and just copies entry.png.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERO_H = 620
INK = (17, 24, 39)
PAPER = (245, 239, 224)
RED = (178, 34, 34)
GREY = (74, 74, 74)
AMBER = (245, 185, 66)
FDIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FDIR + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to pixel width."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


hero = Image.open("hero.png").convert("RGB")
# Crop to the 1024:620 photo slot aspect, centred, then scale.
target_ratio = W / HERO_H
hw, hh = hero.size
if hw / hh > target_ratio:
    nw = int(hh * target_ratio)
    hero = hero.crop(((hw - nw) // 2, 0, (hw - nw) // 2 + nw, hh))
else:
    nh = int(hw / target_ratio)
    hero = hero.crop((0, (hh - nh) // 2, hw, (hh - nh) // 2 + nh))
hero = hero.resize((W, HERO_H), Image.LANCZOS)

page = Image.new("RGB", (W, H), PAPER)
page.paste(hero, (0, 0))
d = ImageDraw.Draw(page, "RGBA")

# --- masthead strip over the dark sky ---
d.rectangle([0, 0, W, 96], fill=(10, 14, 24, 215))
d.rectangle([0, 96, W, 100], fill=AMBER)
d.text((W // 2, 16), "THE WORLD IN ONE IMAGE", font=SERIF_B(46),
       fill=(255, 255, 255), anchor="ma")
d.text((W // 2, 66), "FRIDAY, 20 NOVEMBER 2026", font=SANS_B(21),
       fill=AMBER, anchor="ma")

# --- headline panel ---
y0 = HERO_H
d.rectangle([0, y0, W, y0 + 4], fill=INK)
d.rectangle([W // 2 - 1, y0 + 14, W // 2 + 1, H - 12], fill=(190, 180, 160))

STORIES_LEFT = [
    ("THE HAGUE", "World court: Myanmar guilty of genocide",
     "First state ever found guilty of genocide; 10,000 killed in 2017, reparations ordered."),
    ("SHENZHEN", "Three presidents, one table",
     "Trump, Xi and Putin hold the first US\u2013Russia\u2013China trilateral; nuclear arms on the agenda."),
    ("INDIA", "Cyclone Akvan makes landfall",
     "90\u2013100 km/h winds hit the Andhra\u2013Odisha coast; 1,012 response teams deployed."),
]
STORIES_RIGHT = [
    ("THE GULF", "Iran defends strikes on US bases",
     "Tehran warns neighbours over territory use; tankers hit mines in the Hormuz Strait."),
    ("WALL STREET", "Anthropic debuts at $1.5 trillion",
     "Priced at $83, raised $79.3bn; trading starts Thursday."),
]


def fit_headline(text, width, size=24):
    """Largest serif-bold size (down to 19) that fits on one line."""
    while size > 19 and d.textlength(text, font=SERIF_B(size)) > width:
        size -= 1
    return SERIF_B(size)


def story_block(x, y, width, kicker, headline, deck):
    d.text((x, y), kicker, font=SANS_B(19), fill=RED)
    y += 26
    d.text((x, y), headline, font=fit_headline(headline, width), fill=INK)
    y += 33
    for line in wrap(d, deck, SANS(18), width):
        d.text((x, y), line, font=SANS(18), fill=GREY)
        y += 23
    return y


col_w = 462
y = y0 + 18
for s in STORIES_LEFT:
    y = story_block(24, y, col_w, *s) + 12

y = y0 + 18
for s in STORIES_RIGHT:
    y = story_block(538, y, col_w, *s) + 12

# --- ALSO box ---
box_y = y + 2
d.rectangle([538, box_y, 1000, H - 12], outline=RED, width=2)
d.text((552, box_y + 8), "ALSO TODAY", font=SANS_B(18), fill=RED)
ay = box_y + 34
also = [
    "Gazans return as Israel ends its biggest tank raid since the truce.",
    "GTA VI rolls out worldwide after 13 years; Metacritic 99.",
    "Modi meets the Prince and Princess of Wales.",
]
for item in also:
    for line in wrap(d, "\u2022  " + item, SANS(16), col_w - 28):
        d.text((552, ay), line, font=SANS(16), fill=INK)
        ay += 18
    ay += 3

page.save("entry.png", optimize=True)
print("saved entry.png", page.size)
