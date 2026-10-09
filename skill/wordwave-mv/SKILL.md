---
name: wordwave-mv
description: 字浪/WordWave — 歌词一键生成文字动画 MV（MP4）。当用户提到"歌词MV、歌词动画、文字MV、动态歌词、lyric video、字浪、WordWave"时触发。注意："歌曲MV"、"做个视频"等泛化说法不触发本 skill（除非同句中出现歌词/字浪等明确指称）。基于 fork 自 852wa/JIZURA 的引擎。
---

# WordWave MV 生成

把歌词变成文字动画 MV（MP4）。默认规格：**1920×1080 / 16:9 / 24fps**（引擎原生时间基）。

## 使用方法

**⭐ 推荐方式：工作文件夹模式**——每首歌建一个文件夹（批量时按歌名建子文件夹），歌词和音频放进去，产物全部归位其中：

```bash
python3 ~/.openclaw/skills/wordwave-mv/scripts/make_mv.py --workdir "/path/歌曲文件夹" --seed 42
```

工作文件夹约定：
- 放入 `歌词.txt`（或 `.lrc`/`.srt`）+ `歌曲.mp3/wav`（可选）
- 自动发现歌词与音频，无需指定文件路径；找不到音频则出无声版并提示
- SRT 自动转 LRC（生成 `*_converted.lrc`）
- 成片命名 `{歌名}_mv.mp4`，与预览帧一起写回同一文件夹
- 用户只看到一个文件夹：输入、输出、预览，一目了然

其他方式（指定路径的精细控制）：

```bash
python3 ~/.openclaw/skills/wordwave-mv/scripts/make_mv.py --lyrics-file 歌词.txt --out /tmp/mv.mp4
```

## 歌词格式（必读）

**处理任何歌词前，先读本 skill 目录下的 [LYRICS.md](LYRICS.md)**——引擎按行消费歌词，支持 LRC 时间戳、`[间奏]`、`*强调*`、`！`冲击帧等语法；也列了 agent 整理规则（纯文本直接用、Markdown/Verse 标签必须清洗掉）。

## 三级模式

**1. 全自动（omakase）** — 引擎随机整套风格方案，适合快速出片：

```bash
python3 .../make_mv.py --lyrics "第一行
第二行" --omakase --seed 7
```

**2. 半自动（指定风格）** — 指定 style，其余引擎规划：

```bash
python3 .../make_mv.py --lyrics-file song.txt --style noir
```

**3. 精调级（project JSON）** — 人在浏览器里调好后导出方案 JSON，agent 套用：

```bash
# 先在浏览器打开 http://localhost:8080/zh-hans/index.html 调好并导出 JSON，然后：
python3 .../make_mv.py --lyrics-file song.txt --project-json my_style.json
```

### 4. 精调工作流（人机协作，正式出片推荐）⭐

人工调审美 + agent 出片，适合对风格有要求的正式项目：

```
① agent 快速出片（medium 草稿 + 工程JSON自动落盘）
② 用户在浏览器精调：导入 JSON → 换风格/调配色 → 导出新 JSON
③ agent 套用新 JSON 出高清正式版
```

**② 用户操作指引**（agent 发给用户）：
1. 起浏览器版：`cd <仓库根目录> && python3 -m http.server 8080`，Chrome 打开 `http://localhost:8080/zh-hans/index.html`
2. 导入工程 JSON（详细模式 → 导入构成数据）
3. ⚠️ **导入后歌词是空的**（dumpProject 不含歌词正文）——把工作文件夹里的 `.lrc` 内容粘回歌词框，并重新「载入音乐」选音频文件
4. 自由调整（风格/配色/行级锁定，按 R 重摇不丢锁定项）
5. 满意后导出方案 JSON 存回工作文件夹（如 `我的精调.json`）

**③ agent 出正式版**：

```bash
python3 .../make_mv.py --workdir "工作文件夹" \
  --project-json "工作文件夹/我的精调.json" --quality high
```

注意：`--project-json` 建议同时给 `--audio`（浏览器导出的 JSON 自带歌词，但拍点对齐仍需音频）；出片后成片+新工程 JSON 自动归档到工作文件夹。

已实战验收：《七子之歌》noir→crimson 精调，86 cuts 高清版 50s 出片。

### 全部参数

| 参数 | 说明 | 默认 |
|---|---|---|
| `--lyrics` / `--lyrics-file` | 歌词（多行文本/文件） | 必填其一 |
| `--out` | 输出 MP4 路径 | `wordwave_时间戳.mp4` |
| `--seed` | 随机种子，同种子=同成片（复现） | 随机 |
| `--style` | 风格 id | 引擎默认(noir) |
| `--aspect` | 画幅 16:9/9:16/1:1/21:9/4:3/3:4/4:5 | 16:9 |
| `--res` | 分辨率高度档 720/1080/2160 | 1080 |
| `--fps` | 帧率 | 24 |
| `--omakase` | 全自动模式 | 关 |
| `--project-json` | 套用精调方案（与 --omakase 互斥） | 无 |
| `--audio` | 歌曲音频（mp3/wav/m4a）：拍点对齐镜头 + 混入成片 | 无（出无声片） |
| `--quality` | 画质 medium/high/max（码率系数 0.16/0.28/0.42） | **high（质量优先）** |

### 音频处理规则（agent 必读）

接需求时**必问一句**："有没有歌曲的音频文件？有的话放进工作文件夹，或给我路径。"

- **有音频** → workdir 自动发现或 `--audio 路径`：引擎自动检测 BPM/拍点对齐镜头，成片**带歌**（AAC 混流，无需 ffmpeg）
- **没有** → 直接出无声 MP4，并告知用户"这是无音频版本，音画合成需要提供歌曲文件"
- 已实测：120BPM WAV 检测准确（25 拍点/12s），成片 h264+aac 双轨

### 批量处理

批量时在工作文件夹下按歌名建子文件夹，逐个调用：

```
MV项目/
├── 夜航/        （歌词+音频 → 夜航_mv.mp4）
├── 晚风/        （歌词+音频 → 晚风_mv.mp4）
└── 城市之光/    （歌词+音频 → 城市之光_mv.mp4）
```

```bash
for d in /path/MV项目/*/; do python3 .../make_mv.py --workdir "$d"; done
```

## 风格选择（重要：用户不需要知道风格 id）

**先读本 skill 目录下的 [STYLES.md](STYLES.md)**——里面有情绪→风格推荐表和全部 23 种风格的中文速查（核心 12 + 追加 11，追加风格勾选"使用追加特效"后可用）。

Agent 决策流程：
1. 用户没提风格 → 按歌曲情绪查表选首选，直接出片，回话时说“按歌曲情绪选了 X 风格，不满意可以换”
2. 用户提模糊描述（“酷一点”“温柔一点”）→ 对应到风格再出片
3. 用户明确要挑 → 给用户看 STYLES.md 里的“一句话”列，别倒全部细节
4. 拿不准 → `--omakase` 全自动
5. **每次回传成片必须附 seed**，方便复现和微调

常用风格一句话：`noir` 黑白电影感 / `crimson` 深红警报 / `caution` 黄色警示牌 / `magenta` 荧光粉波普 / `paper` 纸质印刷 / `hud` 科幻界面 / `mint` 青绿终端 / `specimen` 词典书卷气 / `transit` 路牌箭头 / `blueprint` 工程蓝图 / `rouge` 红渐变轻柔 / `mono` 极简灰色差。

## 输出物

- `--out` 指定的 MP4（H.264，含 3 张预览帧 PNG 同目录 `*_frame1~3.png`）
- stdout 最后行 `[done]` 含文件路径、体积、编码、耗时、**seed（记下来可复现）**

## 依赖与自检

- Python 3 + `pip3 install playwright`（用系统 Chrome，无需 install chromium）
- Google Chrome 已安装
- `dev/www/` 构建产物缺失时脚本自动执行 `build.py --dev`

## 已验证（2026-10-09）

- 中文歌词渲染排版 OK（Google Fonts headless 加载正常）
- 同 seed 复现一致；不同 seed 方案不同（omakase 已修 UI 层 Object.assign 缺失问题）
- 24fps / 25fps / 30fps 均可出片，25fps 体积省 ~20%

## 人工精调入口

浏览器版：`cd <仓库根目录> && python3 -m http.server 8080`，打开 `http://localhost:8080/zh-hans/index.html`（Chrome）。按 `R` 摇方案，调好后导出方案 JSON 给 skill 用。
