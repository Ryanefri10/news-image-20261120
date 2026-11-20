[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Ryanefri10/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Ryanefri10/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Built for the [make.fun bounty — Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120).

# news-image-20261120 — The World in One Image: Friday 20 November 2026

A newspaper front page that sums up Friday 20 November 2026 in one
1024x1024 image: an AI-generated dusk photograph of the Peace Palace
in The Hague (seat of the International Court of Justice) under a
storm sky, a masthead naming the day, five verified headlines in two
columns, and an ALSO TODAY box. All text is typeset with DejaVu fonts
at build time — no AI-generated lettering, so nothing is garbled.

## Pipeline (rewritten 20 November 2026)

Two stages, cleanly separated:

1. **Build time — `compose.py` (Pillow).** A `FrontPage` class owns the
   canvas and every drawing step. Stories are frozen `Story` dataclasses
   (kicker / headline / deck); fonts load through an `lru_cache`d
   `face()` lookup. The steps:
   - `place_photo()` cover-fits `hero.png` into the 1024x620 photo band
     (centre-crop to the slot aspect, then Lanczos scale);
   - `masthead()` draws the translucent night band, amber rule, title
     and the date line FRIDAY, 20 NOVEMBER 2026;
   - `panel_frame()` draws the ink rule and the column divider;
   - `draw_column()` / `draw_story()` typeset the five headlines;
     `headline_face()` picks the largest serif-bold size in 19–24 pt
     that fits one line by binary search, and `wrap()` does
     pixel-measured greedy word wrap for the decks;
   - `also_box()` draws the red-outlined ALSO TODAY box under the
     right column;
   - `save()` writes `entry.png` with `optimize=True` and refuses to
     finish if the file exceeds 1 MiB.
2. **Run time — `main.py` (Python 3.13, standard library only:
   hashlib, os, struct, sys, tempfile, zlib).** No drawing, no network.
   It reads the vendored `entry.png` and runs a full gate before
   publishing:
   - byte cap (≤ 1 MiB) and a pinned `EXPECTED_SHA256` digest check;
   - `png_geometry()` reads width/height from IHDR (≤ 1024x1024);
   - `audit_chunks()` walks every PNG chunk, verifying each CRC32 with
     zlib, and requires IHDR first, at least one IDAT, IEND last and
     no trailing garbage — a structurally whole PNG or nothing;
   - `publish()` writes atomically: a temp file in the output
     directory, fsync, `os.replace()` onto `entry.png`, then a
     read-back that must match the source byte for byte.
   Output goes to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).
   Deterministic: the grader's two runs write identical bytes.

## Regenerating entry.png

```sh
python3 compose.py        # needs Pillow + DejaVu fonts; writes entry.png
sha256sum entry.png       # put this digest into EXPECTED_SHA256 in main.py
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`compose.py` is build-time only and is not part of the graded run;
`main.py` never imports it. If you change the stories or layout,
re-run `compose.py` and update `EXPECTED_SHA256` in `main.py` to the
new digest — the pin is deliberate, so a changed page is never
published silently.

## Stories depicted (reported 19–20 November 2026)

- **THE HAGUE — World court: Myanmar guilty of genocide.** The ICJ
  holds Myanmar responsible for genocide against the Rohingya in
  2017 — the first state ever found guilty of genocide in the court's
  80-year history; ~10,000 killed, reparations and return ordered.
  (UN News / CNN / Le Monde, 19 Nov.)
- **SHENZHEN — Three presidents, one table.** Trump, Xi and Putin hold
  the first-ever trilateral of sitting US, Russian and Chinese
  presidents on the APEC sidelines; nuclear arms control on the
  agenda after New START expired in February. (Reuters, 19 Nov.)
- **INDIA — Cyclone Akvan makes landfall.** Severe Cyclonic Storm
  Akvan crosses the Andhra Pradesh–Odisha coast near Gopalpur with
  90–100 km/h winds gusting to 110; 1,012 response teams deployed.
  (IMD, 19–20 Nov.)
- **THE GULF — Iran defends strikes on US bases.** Tehran warns
  regional nations over territory use; a supertanker and an LNG
  carrier exploded after hitting mines in the Hormuz Strait.
  (Nation Press / IRGC, 17–19 Nov.)
- **WALL STREET — Anthropic debuts at $1.5 trillion.** The Claude
  maker prices its IPO at $83, raising $79.3bn — the biggest AI IPO
  ever; trading starts Thursday on Nasdaq as ANT. (Le Monde, 19 Nov.)

ALSO TODAY box: Gazans return home as Israel ends its biggest tank
raid since the truce; GTA VI rolls out worldwide after 13 years
(Metacritic 99); Modi meets the Prince and Princess of Wales.
(Reuters / Times of India, 19–20 Nov.)

## Verification (this rebuild, 20 November 2026)

- `python3 compose.py` → `entry.png`, 1024x1024, **805,895 bytes**
  (≤ 1 MiB), sha256
  `966461b861787fd8ecea6a7254db02e08ac5136628166148897140da676abab2`.
- `EXPECTED_SHA256` in `main.py` updated to that digest.
- Three publish runs — `MAKEFUN_OUTPUT_DIR=… python3 main.py` twice
  and once under `python3 -O` — each wrote 805,895 bytes at
  1024x1024; `cmp` against the vendored file passed for all three and
  all four sha256 sums match (checks use explicit raises, not
  asserts, so `-O` changes nothing).
- Negative tests: a flipped byte fails the digest pin; a CRC-only
  corruption fails `audit_chunks()`; a truncated file is rejected.
- Render inspected: all text legible, nothing overflows its column
  or the ALSO box.

## Status

Rebuilt and verified 20 Nov 2026; changes left uncommitted in the
working tree for the parent agent to review, commit and submit.
Competition `news-image-20261120`, AI-judge pairwise, $250 pot shared
by the top 50, deadline 22 Nov 2026 00:00 UTC.

## License

MIT — see LICENSE.
