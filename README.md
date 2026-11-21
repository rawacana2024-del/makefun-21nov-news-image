# makefun-21nov-news-image

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/rawacana2024-del/makefun-21nov-news-image/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/rawacana2024-del/makefun-21nov-news-image/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Entry for the make.fun bounty **"Sum up 21 November's world news in one image"** ($100).

`main.py` renders a newspaper front page — **"THE WORLD — Saturday,
21 November 2026"** — summarising 6 world news stories from 21 November
2026 in a single square image: a Russian missile hitting Poland as the lead
story, a "Where it happened" world map with 6 numbered dots, 5 further story
panels (Ukraine peace talks, Gulf strikes, COP31, GTA 6 launch records, the
ICJ ruling fallout), and an "In brief" box, with sources in the footer.

## Run it

```bash
python3 main.py              # writes /output/entry.png
python3 main.py out.png      # or any path you choose
```

Pure Python standard library, no network access, no third-party packages,
no system fonts — the text is drawn with a 5x7 bitmap font defined in the
file and the PNG is written by hand with zlib. Output is a 1024x1024 RGB
PNG under the 1 MiB limit, deterministic: two runs produce byte-identical
output.

## Notes

- All 6 stories were verified against public reporting on 21 November 2026.
- Built with an AI agent (Muse) for Irpan. This repo is the entry itself;
  nothing here was submitted anywhere by the script.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
