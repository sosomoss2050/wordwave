# WordWave — Lyric Motion Video Maker

> A fork of [852wa/JIZURA](https://github.com/852wa/JIZURA) (MIT License, Copyright (c) 2026 hakoniwa). The engine core, 860+ expression parts and 27 styles all come from the original project — many thanks to 852wa for open-sourcing it.

**Use online: <https://sosomoss2050.github.io/wordwave/>** · [简体中文](https://sosomoss2050.github.io/wordwave/zh-hans/index.html) · [繁體中文](https://sosomoss2050.github.io/wordwave/zh-hant/index.html) · [한국어](https://sosomoss2050.github.io/wordwave/ko/index.html) · [Bahasa Indonesia](https://sosomoss2050.github.io/wordwave/id/index.html) · [Tiếng Việt](https://sosomoss2050.github.io/wordwave/vi/index.html)

Turn lyrics into animated lyric videos: paste lyrics (LRC / SRT / plain text), load a song, and the engine plans cuts on the beat — then exports MP4 (H.264 + AAC) right in your browser. 860 small parts (layouts, entrances, holds, exits, decorations, transitions, finishing) and 27 styles combine freely; change the seed for a whole new plan. No install, no server rendering — everything runs locally.

## Features

- **In-browser export**: Chrome / Edge (WebCodecs), 720p–4K, 16:9 / 9:16 / 1:1 / 21:9, 24 / 30 / 60 fps
- **Beat alignment**: auto BPM/beat detection from the loaded song snaps cuts to the music; LRC timestamps and tap-sync supported
- **Lyric formats**: LRC as-is, SRT auto-converted, plain text auto-chunked per line
- **Omakase one-shot plans**: press `R` to randomize style/palette/structure, lock the lines you like
- **Project files**: export plan JSON, re-open anytime, or feed it to the automation script for batch renders
- **After Effects panels**: ScriptUI and CEP editions, exporting AE-editable composition data
- **Privacy**: lyrics and songs never leave your machine

## What WordWave adds over upstream JIZURA

Independent version line since v0.11.0:

| Capability | Notes |
|---|---|
| Headless rendering | Playwright-driven headless Chrome; lyrics → MP4 in one command, for batch runs and AI agents |
| Working-folder mode | One folder per song; drop lyrics + audio in, renders/previews/project JSON land back there |
| SRT auto-convert | SRT subtitles in the working folder are converted to LRC automatically |
| Project JSON auto-save | Every render writes `{song}_mv.json` for later fine-tuning or reproduction |
| Audio muxed into MP4 | AAC track included, beat-aligned, no external tools |
| `--quality` flag | medium / **high (default)** / max bitrate presets |
| Render integrity check | Byte-count validation — no corrupt files delivered |
| CJK string handling fixes | Improvements aimed at Chinese lyric workflows |

## Quick start (browser, manual)

1. Open the [web app](https://sosomoss2050.github.io/wordwave/) (or `index.html` from this repo; Chrome/Edge recommended)
2. Paste lyrics, optionally load a song
3. Press `R` for a random plan, or pick style/palette/layouts manually
4. Export MP4 (or PNG sequence / transparent PNG / green-screen)

## Quick start (headless automation)

For batch production / AI agents. Requires Python 3, `pip3 install playwright`, and Google Chrome.

```bash
# Working-folder mode (recommended): drop lyrics + audio in, one command renders
python3 dev/poc_export.py --workdir /path/song-folder --seed 42 --quality high
```

Everything lands back in the folder: `{song}_mv.mp4`, `{song}_mv.json` (project file), `{song}_mv_frame1~3.png` (previews).

Flags: `--style` / `--seed` / `--aspect` / `--res` / `--fps` / `--omakase` / `--project-json` / `--audio`.

### Fine-tune workflow (recommended)

1. Quick draft (`--quality medium`) with auto-saved project JSON
2. Import the JSON in the browser app and tweak by hand (⚠️ lyrics are not stored in the JSON — paste them back and re-load the song)
3. Export the tuned JSON, render the final with `--project-json ... --quality high`

## Repository layout

```
├── index.html etc.  # browser editions per language (build output, GitHub Pages ready)
├── src/             # engine source (numeric order = bundle order)
├── app/             # UI layer & i18n build
├── dev/             # headless render script + test tools (poc_export.py)
├── build*.py        # build scripts (browser / AE panel / CEP)
├── ae/ cep/         # After Effects panel sources
└── WordWave_AE.jsx / WordWave_CEP.zip  # built AE panel artifacts
```

Rebuild: `python3 build.py` (browser, 7 languages) · `python3 build_ae.py` (AE panel) · `python3 build_cep.py` (CEP package).

## Versioning

Independent version line since v0.11.0 (no longer tracking upstream). See [CHANGELOG.md](CHANGELOG.md).

| Version | Notes |
|---|---|
| v0.11.0 (2026-10-09) | First independent release: headless pipeline / audio muxing / SRT conversion / project JSON / rebranding |
| v0.10.1-base | Fork baseline (= upstream JIZURA v0.10.1) |

## Output rights

Videos and images you make belong to you, commercial or not. Lyrics and songs remain the property of their rights holders. The tool itself is MIT licensed (see credits below and LICENSE).

<a id="credits"></a>
## Credits / Acknowledgements

**WordWave is a fork of [JIZURA](https://github.com/852wa/JIZURA) by [852wa](https://github.com/852wa). All credit for the original engine goes to the original author.**

- Original project: https://github.com/852wa/JIZURA
- Original author: https://github.com/852wa
- Original web app: https://852wa.github.io/JIZURA/
- License: MIT (Copyright (c) 2026 hakoniwa)

WordWave is a rebranded, Chinese-focused continuation. The entire engine design, 860+ expression parts and 27 styles come from the original project.

<details>
<summary><h2>Upstream community contributors (JIZURA era)</h2></summary>

Traditional Chinese UI and technique names, Simplified Chinese technique names, font and language detection fixes: [Zaious](https://github.com/Zaious) (#5, #6, #7, #11, #21). Korean UI and technique names: [andongmin94](https://github.com/andongmin94) (#8). Indonesian UI: [auliaramadhann](https://github.com/auliaramadhann) and [enka25](https://github.com/enka25) (#12). Looping technique previews, the pinned tap-sync box, line / cut loops, per-cut picks and Advanced-mode locks: [nocore-dtm](https://github.com/nocore-dtm) (#18, #19, #22, #23, #24). Vietnamese UI: [phamhuulocforwork](https://github.com/phamhuulocforwork) (#20).

</details>

## License

[MIT License](LICENSE). Free to use, modify and redistribute, commercially or not (attribution + license text included). Output videos/images belong to their creator; the license does not extend to output.

Third-party components: see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
