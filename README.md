<div align="center">

# 🌊 WordWave 字浪

**歌词一键生成文字动画 MV — 浏览器内渲染，无需安装**

*Paste lyrics → beat-aligned cuts → MP4. In your browser, or fully automated via AI agents.*

[![Version](https://img.shields.io/badge/version-v0.11.10-blue)](https://github.com/sosomoss2050/wordwave/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Web%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/sosomoss2050/wordwave#quick-start)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill%20Ready-purple)](#skill-部署指南openclaw--ai-agent-自动化)
[![Built on JIZURA](https://img.shields.io/badge/built%20on-JIZURA%20by%20852wa-orange)](#credits)

[简体中文](README.md) · [English](README.en.md)

**🌐 在线使用：<https://sosomoss2050.github.io/wordwave/zh-hans/index.html>**

</div>

---

## 为什么是 WordWave？

做歌词 MV，传统流程是 AE 里堆关键帧、卡节拍、调动画——一支 3 分钟的 MV 要磨好几天。

**WordWave** 把这件事压缩成一步：歌词贴进去，歌曲载进来，引擎自动按拍点规划 80+ 个镜头切分，860 种表现部品与 27 种风格自由组合，浏览器里直接导出 1080p MP4。换个随机种子，就是一套全新方案。不满意？导出工程文件在浏览器里精调，或让 AI agent 帮你全自动出片。

## ✨ 功能特性

**🎬 核心出片**
- 浏览器内直接导出 MP4（H.264 + AAC），720p〜4K，七种画幅，24/30/60fps
- 860+ 表现部品（布局/入场/退场/装饰/转场）× 27 种风格，种子驱动可复现
- 绿幕/黑幕导出、PNG 序列、透明 PNG、前后景分层

**🎵 音乐节奏**
- 载入歌曲自动检测 BPM 与拍点，镜头切换贴合音乐
- LRC 时间戳精确对齐、点拍手动同步、间奏标记

**🤖 AI Agent 自动化（OpenClaw Skill）**
- 官方 Skill：一句「用字浪生成歌词MV」→ agent 全自动出片
- headless 渲染管线：Playwright 驱动，批量生产零人工
- 工作文件夹模式：歌词+音频放进去，成片/预览帧/工程文件自动归位
- 依赖自动安装：首次运行自动配好 playwright/浏览器内核，小白零操作

**🛠 人工精调**
- 工程 JSON 导出/导入，浏览器精调 ↔ agent 批量出片双向打通
- SRT 字幕自动转 LRC
- 一键智能方案（Omakase）+ 行级锁定微调

**🔒 隐私安全**
- 歌词与歌曲全程本地处理，绝不上传服务器

## 🚀 快速开始

**浏览器人工模式**：打开[在线版](https://sosomoss2050.github.io/wordwave/zh-hans/index.html) → 贴歌词 → 按 `R` 摇方案 → 导出 MP4。完事。

**Agent 自动模式**：

```bash
git clone https://github.com/sosomoss2050/wordwave.git
cp -r wordwave/skill/wordwave-mv ~/.openclaw/skills/
# 新开 agent 会话，说：「使用字浪，帮我把这首歌生成歌词MV」
```

首次运行自动安装依赖（playwright / 浏览器内核），无需手动配置。详见[部署指南](#skill-部署指南openclaw--ai-agent-自动化)。

**命令行直接出片**：

```bash
python3 dev/poc_export.py --workdir 歌曲文件夹 --quality high
```

## 🎨 一览 WordWave 能做什么

| | |
|---|---|
| 🌑 **noir** 黑白映画 | 🔴 **crimson** 绯红信号 |
| 🟡 **caution** 警示牌 | 🩷 **magenta** 波普洋红 |
| 📜 **paper** 纸上墨印 | 🖥 **hud** 暗色界面 |
| 🌿 **mint** 薄荷终端 | 📖 **specimen** 字样标本 |
| 🚏 **transit** 转乘交通 | 📘 **blueprint** 蓝图 |
| 🌹 **rouge** 朱红渐变 | 🩶 **mono** 单色RGB |

*27 种风格 × 860 部品 × 无限种子 —— 完整目录见 [STYLES.md](skill/wordwave-mv/STYLES.md)。*

## 📦 仓库结构

```
├── index.html 等          # 七语言浏览器版（GitHub Pages 就绪）
├── skill/wordwave-mv/     # OpenClaw Agent Skill（本仓库特色）
├── src/                   # 引擎源码
├── dev/                   # headless 出片脚本 + 测试工具
├── build*.py              # 构建脚本（浏览器 / AE 面板 / CEP）
└── ae/ cep/               # After Effects 面板源码
```

## 📌 版本

独立版本线（fork 自 JIZURA v0.10.1），记录见 [CHANGELOG.md](CHANGELOG.md)。

| 版本 | 亮点 |
|---|---|
| v0.11.10 | 保存反馈 toast（七语言） |
| v0.11.9 | 全屏预览（F 键 / 七语言适配） |
| v0.11.8 | 语言自动检测跳转 / 导出文件名换牌 / 弹窗换牌 / 隐私加固 / skill 依赖自动安装 |
| v0.11.7 | 日文版迁至 ja/，根路径语言分流 |
| v0.11.0 | 首个独立版本：headless 管线 / 音频混流 / SRT 转换 / 工程 JSON / 品牌重塑 |
| v0.10.1-base | fork 基线 |

## 输出物权利

用本工具制作的视频/图片版权归制作者所有，可商用。歌词与歌曲的权利归各自权利人。

<a id="credits"></a>
## 🙏 鸣谢 / Credits

**本项目基于原作者 [852wa](https://github.com/852wa) 的杰出作品 [JIZURA](https://github.com/852wa/JIZURA) 二次开发而来，衷心感谢原作者的慷慨开源。**

- 原项目：https://github.com/852wa/JIZURA
- 原作者：https://github.com/852wa
- 在线使用（原版）：https://852wa.github.io/JIZURA/
- 许可：MIT License（Copyright (c) 2026 hakoniwa）

WordWave 在原引擎基础上进行中文场景的二次开发与品牌重塑，引擎核心的全部设计、860+ 表现部品与 27 种风格均源自原项目，功劳属于原作者与本项目贡献者。

<details>
<summary><h4>上游社区贡献者（JIZURA 时代）</h4></summary>

- 繁體中文版の画面・部品名の翻訳、简体中文版の部品名、フォントや言語判定の修正、今の案の書体名の表示：[Zaious](https://github.com/Zaious)（#5・#6・#7・#11・#21）
- 한국어版の画面・部品名の翻訳：[andongmin94](https://github.com/andongmin94)（#8）
- Bahasa Indonesia 版の画面の翻訳：[auliaramadhann](https://github.com/auliaramadhann)・[enka25](https://github.com/enka25)（#12）
- 手法タブのループプレビュー、タップ同期の固定表示、行・カットのループ、カットごとの差し替え、詳細モードのロック：[nocore-dtm](https://github.com/nocore-dtm)（#18・#19・#22・#23・#24）
- Tiếng Việt 版の画面の翻訳：[phamhuulocforwork](https://github.com/phamhuulocforwork)（#20）

</details>

## 📄 许可

[MIT License](LICENSE)。商用・非商用均可自由使用、修改、再分发（须同梱著作权表示与许可文本）。

第三方组件见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
