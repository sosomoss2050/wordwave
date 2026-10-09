# WordWave 字浪 — 歌词动态视频（MV）生成工具

> 基于 [852wa/JIZURA](https://github.com/852wa/JIZURA)（MIT License, Copyright (c) 2026 hakoniwa）二次开发。引擎核心、860+ 表现部品与 27 种风格均源自原项目，感谢原作者的慷慨开源。

**在线使用：<https://sosomoss2050.github.io/wordwave/zh-hans/index.html>**（其他语言：[English](https://sosomoss2050.github.io/wordwave/) · [繁體中文](https://sosomoss2050.github.io/wordwave/zh-hant/index.html) · [한국어](https://sosomoss2050.github.io/wordwave/ko/index.html) · [Bahasa Indonesia](https://sosomoss2050.github.io/wordwave/id/index.html) · [Tiếng Việt](https://sosomoss2050.github.io/wordwave/vi/index.html)）

把歌词变成文字动画 MV：输入歌词（支持 LRC / SRT / 纯文本），载入歌曲，引擎自动按拍点规划镜头，浏览器内直接导出 MP4（H.264 + AAC）。布局、入场、退场、装饰、转场、收尾共 860 个小部品与 27 种风格自由组合，换个种子就是一套全新方案。无需安装、无需联网渲染，所有处理都在浏览器本地完成。

## 功能特性

- **零安装浏览器出片**：Chrome / Edge 打开即用（依赖 WebCodecs），720p〜4K、16:9 / 9:16 / 1:1 / 21:9 等画幅、24 / 30 / 60fps
- **音频拍点对齐**：载入歌曲自动检测 BPM 与拍点，镜头切换贴合音乐节奏；支持 LRC 时间戳精确定位、手动点拍同步
- **字幕格式通吃**：LRC 直接用，SRT 自动转换，纯文本按行自动切镜头
- **おまかせ一键方案**：按 `R` 随机整套风格/配色/构成，不满意继续摇，喜欢的行可以锁定
- **方案可保存**：导出工程 JSON，随时回来继续调；也可以把精调方案交给自动化脚本批量复现
- **AE 面板**：After Effects ScriptUI / CEP 两种面板，导出 AE 可编辑的构成数据
- **隐私安全**：歌词与歌曲不上传任何服务器，全流程本地处理

## WordWave 相对上游 JIZURA 的增量

WordWave 自 v0.11.0 起独立版本线演进，在原引擎之上新增：

| 能力 | 说明 |
|---|---|
| headless 全自动出片 | Playwright 驱动无头 Chrome，一条命令歌词→MP4，适合批量生产与 agent 自动化 |
| 工作文件夹模式 | 每首歌一个文件夹，歌词/音频放进去，成片/预览帧/工程 JSON 自动归位 |
| SRT 自动转 LRC | 工作文件夹内检测到 SRT 字幕自动转换 |
| 工程文件自动落盘 | 每次出片同步导出方案 JSON，可回浏览器精调或复现 |
| 音频混流出片 | 歌曲直接混进 MP4（AAC），拍点对齐，无需外部工具 |
| 画质参数 | `--quality medium/high/max` 三档码率（默认 high 质量优先） |
| 出片完整性校验 | 字节数校验，杜绝坏文件交付 |
| 中文字符串国际化修复 | 面向中文歌词场景的字串处理改进 |

## 快速开始（浏览器人工模式）

1. 打开 [在线版](https://sosomoss2050.github.io/wordwave/zh-hans/index.html)（或下载仓库后本地打开 `zh-hans/index.html`，推荐 Chrome/Edge）
2. 粘贴歌词，载入歌曲文件（可选）
3. 按 `R` 摇一套方案，或手动选风格/配色/布局
4. 导出 MP4（或 PNG 序列 / 透視 PNG / 绿幕素材）

## 快速开始（headless 自动出片）

适合批量生产或 AI agent 调用，依赖：Python3 + `pip3 install playwright` + Google Chrome。

```bash
# 工作文件夹模式（推荐）：歌词+音频放进文件夹，一条命令出片
python3 dev/poc_export.py --workdir /path/歌曲文件夹 --seed 42 --quality high
```

产物全部归位工作文件夹：`{歌名}_mv.mp4`（成片）、`{歌名}_mv.json`（工程文件）、`{歌名}_mv_frame1~3.png`（预览帧）。

常用参数：`--style`（风格）/ `--seed`（复现）/ `--aspect` / `--res` / `--fps` / `--omakase`（全自动摇方案）/ `--project-json`（套用精调方案）/ `--audio`（歌曲文件）。

### 精调工作流（推荐）

1. 快速出片（`--quality medium`）+ 自动落盘工程 JSON
2. 浏览器版导入工程 JSON 人工微调（⚠️ 导入后需把歌词粘回歌词框并重新载入音乐）
3. 导出新 JSON，`--project-json` 出高清正式版

## Skill 部署指南（OpenClaw / AI Agent 自动化）

`skill/wordwave-mv/` 是一个即插即用的 Agent Skill，让 AI agent 用一句自然语言出片（「用字浪把这段歌词做成 MV」）。

### 安装（三步，全程自动）

```bash
# 1. 克隆仓库（已装可跳过）
git clone https://github.com/sosomoss2050/wordwave.git

# 2. 把 skill 拷进 OpenClaw 全局技能目录
cp -r wordwave/skill/wordwave-mv ~/.openclaw/skills/

# 3. 完成。首次运行时依赖自动安装（见下）
```

安装后**新开一个 agent 会话**即可生效。触发词：歌词MV / 歌词动画 / 文字MV / 动态歌词 / lyric video / 字浪 / WordWave。

### 依赖自动安装（小白零操作）

skill 脚本首次运行时自检并**自动安装**缺失依赖，无需手动操作：

| 依赖 | 检测 | 自动处理 |
|---|---|---|
| playwright（Python 包） | import 失败 | 自动 `pip install --user playwright`（约 30 秒） |
| 浏览器内核 | 找系统 Chrome/Chromium | 没有 → 自动 `playwright install chromium`（一次性约 2 分钟） |
| 仓库引擎构建产物 `dev/www/` | 文件缺失 | 自动执行 `build.py --dev` 构建 |
| mp4-muxer 库 | 文件缺失 | 自动从 vendor/ 复制 |

全部失败才会退出，报错信息含可直接复制的安装命令。

### 环境变量（可选）

```bash
export WORDWAVE_REPO=/path/to/wordwave   # 引擎仓库位置（默认 /Volumes/Work/TeamShare/project-workspace/wordwave）
```

> 其他机器部署时务必设置此项，指向你 clone 的仓库路径。

### Agent 使用示例

```
用户：「使用字浪，帮我把这首歌生成歌词MV」（附歌词文件路径/工作文件夹）
Agent：自动选风格 → headless 出片 → 回传 MP4 路径 + seed（可复现）+ 预览帧
```

详细的风格推荐表见 [skill/wordwave-mv/STYLES.md](skill/wordwave-mv/STYLES.md)，歌词语法见 [skill/wordwave-mv/LYRICS.md](skill/wordwave-mv/LYRICS.md)。

## 仓库结构

```
├── index.html 等    # 各语言浏览器版（构建产物，可直接部署 GitHub Pages）
├── src/             # 引擎源码（编号即拼装顺序）
├── app/             # UI 层与 i18n 构建
├── dev/             # headless 出片脚本 + 测试工具（poc_export.py）
├── build*.py        # 构建脚本（浏览器版 / AE 面板 / CEP 包）
├── ae/ cep/         # After Effects 面板源码
└── WordWave_AE.jsx / WordWave_CEP.zip  # AE 面板构建产物
```

重新构建：`python3 build.py`（浏览器版七语言）· `python3 build_ae.py`（AE 面板）· `python3 build_cep.py`（CEP 包）。

## 版本

独立版本线，自 v0.11.0 起不再跟随上游。版本记录见 [CHANGELOG.md](CHANGELOG.md)。

| 版本 | 说明 |
|---|---|
| v0.11.0（2026-10-09） | 首个独立版本：headless 链路 / 音频混流 / SRT 转换 / 工程 JSON / 品牌重塑 |
| v0.10.1-base | fork 基线（= 上游 JIZURA v0.10.1） |

## 输出物权利

用本工具制作的视频/图片版权归制作者所有，可商用。歌词与歌曲的权利归各自权利人。工具本体遵循 MIT 许可（见下方鸣谢与 LICENSE）。

<a id="credits"></a>
## 鸣谢 / Credits

**本项目基于原作者 [852wa](https://github.com/852wa) 的杰出作品 [JIZURA](https://github.com/852wa/JIZURA) 二次开发而来，衷心感谢原作者的慷慨开源。**

- 原项目：https://github.com/852wa/JIZURA
- 原作者：https://github.com/852wa
- 在线使用（原版）：https://852wa.github.io/JIZURA/
- 许可：MIT License（Copyright (c) 2026 hakoniwa）

WordWave 在原引擎基础上进行中文场景的二次开发与品牌重塑，引擎核心的全部设计、860+ 表现部品与 27 种风格均源自原项目，功劳属于原作者与本项目贡献者。

<details>
<summary><h2>上游社区贡献者（JIZURA 时代）</h2></summary>

- 繁體中文版の画面・部品名の翻訳、简体中文版の部品名、フォントや言語判定の修正、今の案の書体名の表示：[Zaious](https://github.com/Zaious)（#5・#6・#7・#11・#21）
- 한국어版の画面・部品名の翻訳：[andongmin94](https://github.com/andongmin94)（#8）
- Bahasa Indonesia 版の画面の翻訳：[auliaramadhann](https://github.com/auliaramadhann)・[enka25](https://github.com/enka25)（#12）
- 手法タブのループプレビュー、タップ同期の固定表示、行・カットのループ、カットごとの差し替え、詳細モードのロック：[nocore-dtm](https://github.com/nocore-dtm)（#18・#19・#22・#23・#24）
- Tiếng Việt 版の画面の翻訳：[phamhuulocforwork](https://github.com/phamhuulocforwork)（#20）

</details>

## 许可

[MIT License](LICENSE)。商用・非商用均可自由使用、修改、再分发（须同梱著作权表示与许可文本）。本工具制作的视频/图片权利归制作者所有，许可不及于输出物。

第三方组件见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
