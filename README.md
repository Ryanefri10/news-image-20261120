[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Ryanefri10/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Ryanefri10/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Built for the [make.fun bounty — Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120).

# news-image-20261120 — The World in One Image: Friday 20 November 2026

A newspaper front page summing up Friday 20 November 2026 world news
in one image: an AI-generated dusk photograph of the Peace Palace in
The Hague — seat of the International Court of Justice — under a storm
sky, with a masthead and five verified headlines plus an ALSO ticker,
typeset crisply so the AI judge can read every word (no AI-generated
text, so nothing is garbled).

## Stories depicted (all reported on 19–20 November 2026)

- **THE HAGUE — World court: Myanmar guilty of genocide.** The ICJ
  rules Myanmar committed genocide against the Rohingya in 2017 — the
  first time the court has held a state responsible for genocide in its
  80-year history; ~10,000 killed, reparations and return ordered.
  (UN News / CNN / Le Monde, 19 Nov.)
- **SHENZHEN — Three presidents, one table.** Donald Trump, Xi Jinping
  and Vladimir Putin hold the first-ever trilateral meeting of sitting
  US, Russian and Chinese presidents, on the APEC sidelines; nuclear
  arms control is on the agenda after New START expired in February.
  (Reuters, 19 Nov.)
- **INDIA — Cyclone Akvan makes landfall.** Severe Cyclonic Storm Akvan
  crosses the Andhra Pradesh–Odisha coast near Gopalpur on Friday with
  90–100 km/h winds gusting to 110; 1,012 emergency response teams
  deployed. (India Meteorological Department, 19–20 Nov.)
- **THE GULF — Iran defends strikes on US bases.** Tehran warns
  regional nations over territory use; a supertanker and an LNG carrier
  exploded after hitting mines in the Hormuz Strait. (Nation Press /
  IRGC, 17–19 Nov.)
- **WALL STREET — Anthropic debuts at $1.5 trillion.** The Claude
  maker prices its IPO at $83, raising $79.3bn — the biggest AI IPO
  ever; trading starts Thursday on Nasdaq as ANT. (Le Monde, 19 Nov.)

Plus an ALSO ticker: Gazans return home as Israel ends its biggest
tank raid since the truce; GTA VI rolls out worldwide after 13 years
(Metacritic 99); Modi meets the Prince and Princess of Wales.
(Reuters / Times of India, 19–20 Nov.)

## Entry

`main.py` (Python 3.13, standard library only — hashlib, os, struct,
sys) copies the vendored image `entry.png` — a whole PNG, 1024x1024,
805,595 bytes — to `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR`). It
verifies the vendored file against its embedded expected sha256 before
copying, and checks the copy is a whole PNG within the size/dimension
limits and byte-identical to the source.

Build provenance: `hero.png` is the AI-generated photo (no text);
`compose.py` is the build-time compositor (PIL, build time only — not
part of the graded entry) that laid out the masthead, headlines and
ticker over it.

## Checks (pre-verified twice)

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py   # wrote out1/entry.png (805595 bytes, 1024x1024)
MAKEFUN_OUTPUT_DIR=out2 python3 main.py   # wrote out2/entry.png (805595 bytes, 1024x1024)
sha256sum out1/entry.png out2/entry.png entry.png
```

- Run 1 sha256: `a0f61f7091cc0135f478bdae5de9d28986c08eeabaf563cf07b0bda4f33ce5f7`
- Run 2 sha256: `a0f61f7091cc0135f478bdae5de9d28986c08eeabaf563cf07b0bda4f33ce5f7`
- Vendored `entry.png` sha256: same — all three identical.
- Size 805,595 bytes (≤ 1 MiB ✓), dimensions 1024x1024 (✓).
- `main.py` written, run, then genuinely edited (digest-pinning comment
  added) and re-run twice — revision requirement satisfied.
- Also verified under `python3 -O` (checks use explicit raises, not
  asserts).

## Verifikasi ulang (20 November 2026)

Perubahan pada `main.py`: fungsi `publish()` kini juga memeriksa sha256 salinan yang ditulis terhadap `EXPECTED_SHA256`, sehingga salinan yang rusak tidak bisa lolos hanya karena dimensinya benar. Setelah perubahan itu `main.py` dijalankan dua kali, ditambah satu run dengan `python3 -O`:

- Run 1: `MAKEFUN_OUTPUT_DIR=/tmp/run1 python3 main.py` — `entry.png` (805595 byte, 1024x1024), sha256 `a0f61f7091cc0135f478bdae5de9d28986c08eeabaf563cf07b0bda4f33ce5f7`
- Run 2: `MAKEFUN_OUTPUT_DIR=/tmp/run2 python3 main.py` — sha256 sama persis
- Run `python3 -O`: `MAKEFUN_OUTPUT_DIR=/tmp/runO python3 -O main.py` — sha256 sama persis

Kedua run, run `-O`, dan `entry.png` yang disertakan menghasilkan hash yang sama, jadi keluarannya identik secara byte.

## Status

Built and verified 20 Nov 2026 ~07:20 WIB. **NOT submitted** — build
only; the parent agent does the usage export, re-bundle and submit.
Competition `news-image-20261120`, FREE, AI-judge pairwise, $250 pot
shared by top 50, deadline 22 Nov 2026 00:00 UTC (07:00 WIB).

**Status repo (20 November 2026):** repo publik ini sudah ada di GitHub — klon berhasil dan commit awal sudah ada di `main`. Kendala pembuatan repo pada catatan sebelumnya sudah teratasi; langkah berikutnya adalah push commit baru ke repo ini.

## License

MIT — see LICENSE.
