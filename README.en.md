<div align="center">

# 🌊 WordWave

**Lyrics in, lyric-video out — rendered in your browser, or fully automated by AI agents**

[![Version](https://img.shields.io/badge/version-v0.11.6-blue)](https://github.com/sosomoss2050/wordwave/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Web%20%7C%20macOS%20%7C%20Linux-lightgrey)](#quick-start)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill%20Ready-purple)](#skill-deployment-openclaw--ai-agent-automation)
[![Built on JIZURA](https://img.shields.io/badge/built%20on-JIZURA%20by%20852wa-orange)](#credits)

[简体中文](README.md) · [English](README.en.md)

**🌐 Use online: <https://sosomoss2050.github.io/wordwave/en/index.html>**

</div>

---

## Why WordWave?

A 3-minute lyric MV used to mean days in After Effects: keyframes, beat-syncing, animation.

**WordWave** compresses that into one step: paste lyrics, load the song, and the engine plans 80+ beat-aligned cuts across 860 expression parts and 27 styles — exporting 1080p MP4 right in the browser. Change the random seed for a brand-new plan. Not perfect? Fine-tune the project file in the browser, or let an AI agent render it end-to-end.

> 🙌 WordWave is a fork of [852wa/JIZURA](https://github.com/852wa/JIZURA) — see [Credits](#credits).

## ✨ Features

**🎬 Rendering**
- In-browser MP4 export (H.264 + AAC), 720p–4K, 7 aspect ratios, 24/30/60 fps
- 860+ parts (layouts/entrances/exits/decor/transitions) × 27 styles, seed-driven and reproducible
- Green-screen / black-screen export, PNG sequences, transparent PNG, layered output

**🎵 Music sync**
- Auto BPM/beat detection snaps cuts to the music
- LRC timestamps, tap-sync, interlude markers

**🤖 AI agent automation (OpenClaw Skill)**
- Official Skill: say "make a lyric MV with WordWave" → agent renders end-to-end
- Headless pipeline: Playwright-driven, batch production with zero manual work
- Working-folder mode: drop lyrics + audio in, renders/previews/project files land back there
- Auto dependency install: playwright/browser kernel set up on first run — zero-config

**🛠 Manual fine-tuning**
- Project JSON export/import: browser fine-tuning ↔ agent batch rendering, both ways
- SRT subtitles auto-converted to LRC
- One-shot auto plans + per-line locks

**🔒 Privacy**
- Lyrics and songs never leave your machine

## 🚀 Quick start

**Browser (manual)**: open the [web app](https://sosomoss2050.github.io/wordwave/en/index.html) → paste lyrics → press `R` → export MP4. Done.

**Agent (automated)**:

```bash
git clone https://github.com/sosomoss2050/wordwave.git
cp -r wordwave/skill/wordwave-mv ~/.openclaw/skills/
# New agent session, then: "Make a lyric MV with WordWave"
```

Dependencies install themselves on first run. See the [deployment guide](#skill-deployment-openclaw--ai-agent-automation).

**CLI direct render**:

```bash
python3 dev/poc_export.py --workdir song-folder --quality high
```

## 🎨 Styles at a glance

| | |
|---|---|
| 🌑 **noir** | 🔴 **crimson** |
| 🟡 **caution** | 🩷 **magenta** |
| 📜 **paper** | 🖥 **hud** |
| 🌿 **mint** | 📖 **specimen** |
| 🚏 **transit** | 📘 **blueprint** |
| 🌹 **rouge** | 🩶 **mono** |

*27 styles × 860 parts × unlimited seeds — full catalog in [STYLES.md](skill/wordwave-mv/STYLES.md).*

## 📦 Repository layout

```
├── index.html etc.          # 7-language browser editions (GitHub Pages ready)
├── skill/wordwave-mv/       # OpenClaw Agent Skill
├── src/                     # engine source
├── dev/                     # headless render script + test tools
├── build*.py                # build scripts (browser / AE panel / CEP)
└── ae/ cep/                 # After Effects panel sources
```

Rebuild: `python3 build.py` · `build_ae.py` · `build_cep.py`.

## 📌 Versioning

Independent version line (forked from JIZURA v0.10.1). See [CHANGELOG.md](CHANGELOG.md).

| Version | Highlights |
|---|---|
| v0.11.6 | Privacy hardening / skill auto-dependency-install |
| v0.11.0 | First independent release: headless pipeline / audio muxing / SRT conversion / project JSON / rebranding |
| v0.10.1-base | Fork baseline |

## Output rights

Videos and images you make belong to you, commercial or not. Lyrics and songs remain the property of their rights holders.

<a id="credits"></a>
## 🙏 Credits

**WordWave is a fork of [JIZURA](https://github.com/852wa/JIZURA) by [852wa](https://github.com/852wa). All credit for the original engine goes to the original author — thank you for open-sourcing it.**

- Original project: https://github.com/852wa/JIZURA
- Original author: https://github.com/852wa
- Original web app: https://852wa.github.io/JIZURA/
- License: MIT (Copyright (c) 2026 hakoniwa)

WordWave is a rebranded, Chinese-focused continuation. The entire engine design, 860+ expression parts and 27 styles come from the original project.

<details>
<summary><h4>Upstream community contributors (JIZURA era)</h4></summary>

- Traditional/Traditional Chinese UI & technique names, font and language detection fixes: [Zaious](https://github.com/Zaious) (#5, #6, #7, #11, #21)
- Korean UI: [andongmin94](https://github.com/andongmin94) (#8)
- Indonesian UI: [auliaramadhann](https://github.com/auliaramadhann), [enka25](https://github.com/enka25) (#12)
- Loop previews, tap-sync box, line/cut loops, per-cut picks, Advanced-mode locks: [nocore-dtm](https://github.com/nocore-dtm) (#18, #19, #22, #23, #24)
- Vietnamese UI: [phamhuulocforwork](https://github.com/phamhuulocforwork) (#20)

</details>

## 📄 License

[MIT License](LICENSE). Free to use, modify and redistribute, commercially or not.

Third-party components: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
