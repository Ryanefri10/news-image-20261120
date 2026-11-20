#!/usr/bin/env python3
"""Build-time compositor for the news-image-20261120 entry.

Draws the newspaper front page for Friday 20 November 2026 on top of
the AI-generated hero photograph (hero.png, which carries no text):
a masthead band over the photo, then a two-column headline panel and
an ALSO box on cream paper. The result is entry.png, 1024x1024 and
under 1 MiB.

This script needs Pillow and runs only at build time. The graded
entry point, main.py, is stdlib-only and merely validates and copies
the finished entry.png.

Regenerate with:  python3 compose.py
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

# --- canvas and layout geometry -------------------------------------------
CANVAS_W, CANVAS_H = 1024, 1024
PHOTO_H = 620                 # height of the photo band at the top
MASTHEAD_H = 96               # dark band drawn over the photo's sky
RULE_H = 4                    # amber rule under the masthead
PANEL_PAD = 18                # breathing room above the first story
COLUMN_W = 462
LEFT_X, RIGHT_X = 24, 538
GUTTER_X = CANVAS_W // 2      # hairline divider between the columns
BOTTOM_MARGIN = 12
MAX_BYTES = 1024 * 1024

# --- palette ---------------------------------------------------------------
INK = (17, 24, 39)
PAPER = (245, 239, 224)
CRIMSON = (178, 34, 34)
BODY_GREY = (74, 74, 74)
AMBER = (245, 185, 66)
DIVIDER = (190, 180, 160)
NIGHT = (10, 14, 24)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FACES = {
    "serif-bold": "DejaVuSerif-Bold.ttf",
    "sans-bold": "DejaVuSans-Bold.ttf",
    "sans": "DejaVuSans.ttf",
}


@lru_cache(maxsize=None)
def face(kind: str, pt: int) -> ImageFont.FreeTypeFont:
    """Cached truetype lookup so repeated sizes cost one load each."""
    return ImageFont.truetype(os.path.join(FONT_DIR, FACES[kind]), pt)


@dataclass(frozen=True)
class Story:
    """One headline slot: red kicker, serif headline, grey deck."""

    kicker: str
    headline: str
    deck: str


# The day's five verified stories, in reading order per column.
LEFT_COLUMN: tuple[Story, ...] = (
    Story(
        kicker="THE HAGUE",
        headline="World court: Myanmar guilty of genocide",
        deck="First state ever found guilty of genocide; 10,000 killed "
             "in 2017, reparations ordered.",
    ),
    Story(
        kicker="SHENZHEN",
        headline="Three presidents, one table",
        deck="Trump, Xi and Putin hold the first US\u2013Russia\u2013China "
             "trilateral; nuclear arms on the agenda.",
    ),
    Story(
        kicker="INDIA",
        headline="Cyclone Akvan makes landfall",
        deck="90\u2013100 km/h winds hit the Andhra\u2013Odisha coast; "
             "1,012 response teams deployed.",
    ),
)
RIGHT_COLUMN: tuple[Story, ...] = (
    Story(
        kicker="THE GULF",
        headline="Iran defends strikes on US bases",
        deck="Tehran warns neighbours over territory use; tankers hit "
             "mines in the Hormuz Strait.",
    ),
    Story(
        kicker="WALL STREET",
        headline="Anthropic debuts at $1.5 trillion",
        deck="Priced at $83, raised $79.3bn; trading starts Thursday.",
    ),
)
ALSO_ITEMS: tuple[str, ...] = (
    "Gazans return as Israel ends its biggest tank raid since the truce.",
    "GTA VI rolls out worldwide after 13 years; Metacritic 99.",
    "Modi meets the Prince and Princess of Wales.",
)


class FrontPage:
    """Owns the canvas and every drawing step of the front page."""

    def __init__(self) -> None:
        self.page = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
        self.pen = ImageDraw.Draw(self.page, "RGBA")

    # -- photo band ----------------------------------------------------------
    def place_photo(self, hero_path: str) -> None:
        """Cover-fit hero.png into the top band: centre-crop, then scale."""
        photo = Image.open(hero_path).convert("RGB")
        slot_ratio = CANVAS_W / PHOTO_H
        src_w, src_h = photo.size
        if src_w / src_h > slot_ratio:
            # Too wide: keep full height, trim the sides evenly.
            keep_w = round(src_h * slot_ratio)
            left = (src_w - keep_w) // 2
            window = (left, 0, left + keep_w, src_h)
        else:
            # Too tall: keep full width, trim top and bottom evenly.
            keep_h = round(src_w / slot_ratio)
            top = (src_h - keep_h) // 2
            window = (0, top, src_w, top + keep_h)
        band = photo.crop(window).resize((CANVAS_W, PHOTO_H), Image.Resampling.LANCZOS)
        self.page.paste(band, (0, 0))

    # -- masthead ------------------------------------------------------------
    def masthead(self) -> None:
        self.pen.rectangle([0, 0, CANVAS_W, MASTHEAD_H], fill=NIGHT + (215,))
        self.pen.rectangle(
            [0, MASTHEAD_H, CANVAS_W, MASTHEAD_H + RULE_H], fill=AMBER
        )
        centre = CANVAS_W // 2
        self.pen.text(
            (centre, 16), "THE WORLD IN ONE IMAGE",
            font=face("serif-bold", 46), fill=(255, 255, 255), anchor="ma",
        )
        self.pen.text(
            (centre, 66), "FRIDAY, 20 NOVEMBER 2026",
            font=face("sans-bold", 21), fill=AMBER, anchor="ma",
        )

    # -- text helpers --------------------------------------------------------
    def wrap(self, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
        """Greedy word wrap measured in pixels, not characters."""
        lines: list[str] = []
        buffer: list[str] = []
        for word in text.split():
            trial = " ".join(buffer + [word])
            if self.pen.textlength(trial, font=fnt) <= width:
                buffer.append(word)
                continue
            if buffer:
                lines.append(" ".join(buffer))
            buffer = [word]
        if buffer:
            lines.append(" ".join(buffer))
        return lines

    def headline_face(self, text: str, width: int) -> ImageFont.FreeTypeFont:
        """Biggest serif-bold size in [19, 24] that fits one line.

        Binary search over the size range instead of stepping down one
        point at a time; a headline too long even at 19 keeps size 19.
        """
        lo, hi = 19, 24
        while lo < hi:
            mid = (lo + hi + 1) // 2
            fits = self.pen.textlength(text, font=face("serif-bold", mid)) <= width
            if fits:
                lo = mid
            else:
                hi = mid - 1
        return face("serif-bold", lo)

    # -- headline panel ------------------------------------------------------
    def panel_frame(self) -> None:
        top = PHOTO_H
        self.pen.rectangle([0, top, CANVAS_W, top + 4], fill=INK)
        self.pen.rectangle(
            [GUTTER_X - 1, top + 14, GUTTER_X + 1, CANVAS_H - BOTTOM_MARGIN],
            fill=DIVIDER,
        )

    def draw_story(self, story: Story, x: int, y: int, width: int) -> int:
        """Render one story block; return the y below its last line."""
        self.pen.text((x, y), story.kicker, font=face("sans-bold", 19), fill=CRIMSON)
        y += 26
        self.pen.text(
            (x, y), story.headline,
            font=self.headline_face(story.headline, width), fill=INK,
        )
        y += 33
        deck_font = face("sans", 18)
        for line in self.wrap(story.deck, deck_font, width):
            self.pen.text((x, y), line, font=deck_font, fill=BODY_GREY)
            y += 23
        return y

    def draw_column(self, stories: tuple[Story, ...], x: int) -> int:
        y = PHOTO_H + PANEL_PAD
        for story in stories:
            y = self.draw_story(story, x, y, COLUMN_W) + 12
        return y

    # -- ALSO box ------------------------------------------------------------
    def also_box(self, x: int, top: int, width: int) -> None:
        bottom = CANVAS_H - BOTTOM_MARGIN
        self.pen.rectangle([x, top, x + width, bottom], outline=CRIMSON, width=2)
        self.pen.text((x + 14, top + 8), "ALSO TODAY", font=face("sans-bold", 18), fill=CRIMSON)
        cursor = top + 34
        item_font = face("sans", 16)
        for item in ALSO_ITEMS:
            for line in self.wrap("\u2022  " + item, item_font, width - 28):
                self.pen.text((x + 14, cursor), line, font=item_font, fill=INK)
                cursor += 18
            cursor += 3

    # -- orchestration -------------------------------------------------------
    def render(self, hero_path: str) -> None:
        self.place_photo(hero_path)
        self.masthead()
        self.panel_frame()
        self.draw_column(LEFT_COLUMN, LEFT_X)
        right_end = self.draw_column(RIGHT_COLUMN, RIGHT_X)
        self.also_box(RIGHT_X, right_end + 2, 1000 - RIGHT_X)

    def save(self, out_path: str) -> int:
        self.page.save(out_path, optimize=True)
        size = os.path.getsize(out_path)
        if size > MAX_BYTES:
            raise SystemExit(f"compose.py: {out_path} is {size} bytes, over the 1 MiB cap")
        return size


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    page = FrontPage()
    page.render(os.path.join(here, "hero.png"))
    size = page.save(os.path.join(here, "entry.png"))
    print(f"compose.py: wrote entry.png {CANVAS_W}x{CANVAS_H}, {size} bytes")


if __name__ == "__main__":
    main()
