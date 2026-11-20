[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Andy74453533/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Andy74453533/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Built for the [make.fun bounty: Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120).

# The World Today — 20 November 2026

Entry for `news-image-20261120`: a program that writes one 1024×1024 PNG
summarising the world's news of Friday 20 November 2026 to
`/output/entry.png`. Standard library plus Pillow for rendering (with a
pre-rendered fallback), offline, deterministic — two runs write
byte-identical files.

## The image

A newspaper front page, "THE WORLD TODAY", dated Friday, 20 November
2026. Everything is drawn programmatically — no downloaded photos, no
network at run time:

- **Lead story — Trump pushes Iran war decision to 2027:** Trump says
  there is no rush on the Iran decision — he'll "see what happens"
  after 1 January, pushing any call on military action into the new
  year. Illustrated with a calendar page for 1 January 2027 and his
  quoted line.
- **ICJ rules Myanmar committed genocide** — the World Court finds
  Myanmar committed genocide against the Rohingya people.
- **Cyclone Akvan: 300,000 evacuated** — the storm nears India's
  Odisha coast as authorities move residents to safety.
- **Voyager 1 reaches a "light-day" milestone** — NASA's farthest
  spacecraft passes one light-day from Earth, about 26 billion km.
- **GTA 6 sales pass The Odyssey's $1.80bn run** — Rockstar's
  blockbuster overtakes the $1.80bn global run of Christopher Nolan's
  epic.
- **Also:** Europe ready for Russia talks on Ukraine. Plus a markets
  strip (Thu 19 Nov US close: Dow −2.19% to 49,097, S&P 500 −2.02% to
  7,176, Nasdaq −2.25% to 23,879; gold $3,686, Brent $92, Bitcoin
  ~$61,500).

Story selection: the five most widely reported developments of the day
across the major briefings (see SOURCES.md), chosen to be recognisable
to a picture editor judging the image on its own — each story is
self-contained, with a headline and a one-line summary, so the image
needs no news feed to be understood.

## Run it

```sh
python3 main.py
# writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)
```

Deterministic and offline: no network, no randomness, no clock.
Two runs produce byte-identical output.
