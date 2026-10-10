# WordWave Live — OSC 同步控制模块设计（v0 草案）

> 状态：设计已评审定案（2026-10-10 老莫拍板），P1 可开工
> 决策记录：①Bridge 先独立 Node 脚本，Electron 阶段再重构内置 ②Cue List 用静态映射表（cue 号人工录入）③MTC 降级为可选后备，默认不做（cue 粒度=整首歌，无中途跟随需求）④触发粒度：一条 QLab cue 对应 WordWave 一首歌，不逐句逐段
> 作者：大壮2号 · 2026-10-10
>
> ⚠️ **2026-10-10 更新**：经 DAW/演出生态调研，OSC 路线已被推翻（Pro Tools/Logic 不支持 OSC）。新方案定案为 SMPTE follower + LTC/MTC 双前端，详见 memory-topics/wordwave-live-sync-research.md。本文档保留作为决策历史，OSC 相关内容仅供 QLab 兼容场景参考。
> 目标：QLab 演出主控（PGM 音频）驱动 WordWave 歌词动画，与灯光/视频同帧同步

---

## 1. 背景与目标

演出场景中，QLab 是 show control 中枢：点击 GO 播放 PGM 音频，同时通过 LTC/MTC 同步灯光台（如 ETC/Onyx）和视频服务器。WordWave 作为歌词视觉引擎，必须纳入同一触发链，做到：

1. **触发同步**：QLab GO → WordWave 立即开始对应段落的歌词动画
2. **时间同步**：动画时间轴 t 跟随 QLab 播放位置（暂停/回退/跳段能跟随）
3. **紧急控制**：一键 Panic/黑场，对齐 QLab 的 panic 习惯
4. **可运营**：操作员有配置面板和 Cue List 界面，非程序员可用

## 2. 架构总览

```
┌──────────┐  OSC/UDP 或 MTC   ┌─────────────────────┐
│  QLab 5  │ ───────────────→ │  OSC Bridge (小工具) │
│ (PGM主控) │                  │  node + osc 库       │
└──────────┘                   │  UDP :8000 ↔ WS      │
                               └────────┬────────────┘
                                        │ WebSocket :9102
                               ┌────────▼────────────┐
                               │ WordWave Live 页面   │
                               │  · OSCClient 模块    │
                               │  · CueMapper         │
                               │  · 配置面板 / CueList │
                               │  · 引擎 frame(ctx,…)  │
                               └─────────────────────┘
```

**部署模式（二选一，运行时无关）**

- **同机部署（推荐首场）**：QLab、Bridge、WordWave 同一台 Mac。Network Cue 目标 IP 填 `127.0.0.1`，回环不出网卡：延迟≈0、无网络丢包、不需要独立 VLAN，无需第二台机器。注意：①演出前跑全负载压测（QLab 放 PGM + WordWave 同屏渲染），老 Intel Mac 必做；②端口冲突处理见 §2.1。
- **分机部署（大型演出）**：QLab 机器与 Bridge/WordWave 机器分开，有线连接、独立 VLAN、同网段静态 IP。

### 2.1 端口配置（不写死，全部可改）

默认端口：Bridge OSC 监听 `8000/udp`、Bridge→WordWave WS `9102/tcp`。三者均可配置，改任一端需同步三处：

| 端口 | 配置位置 | 说明 |
|---|---|---|
| OSC 8000 | ① Bridge 启动参数 `--osc-port` ② QLab Network Cue 目标端口 ③ WordWave 面板显示（只读回显，提示与 Bridge 一致性） | 被占用时 Bridge 启动自检报错退出并列出占用进程，操作员换端口后 QLab 侧同步改 |
| WS 9102 | ① Bridge 启动参数 `--ws-port` ② WordWave 面板连接区 Bridge URL | 面板 URL 改端口重连即可 |

原则：默认值仅为约定俗成的初始值，任何环境下都以"配置面板/启动参数实际填写的值"为准；Bridge 与 WordWave 面板两端显示当前生效端口，排练前核对一次。

**为什么需要 Bridge**：WordWave 引擎是浏览器 Canvas（后续打包 Electron）。浏览器拿不到原始 UDP；Electron 主进程可以，但为保持"网页也能跑"，统一用 Bridge：Node 端收 UDP/OSC + MTC，转 WebSocket 推给页面。Electron 版可将 Bridge 内置进主进程（同一份代码，去掉独立进程）。

## 3. 模块划分

新增 `src/live/` 目录（不触碰现有 src/00–11 核心文件，遵守 pack-only 惯例精神）：

| 模块 | 文件 | 职责 |
|---|---|---|
| OSCClient | `live/osc-client.js` | WS 连接、重连退避、消息解析（OSC address + args / MTC quarter-frame 拼装） |
| TimecodeSource | `live/tc-source.js` | MTC→平滑时间轴 t（本地 performance.now 插值，MTC 约 2Hz 更新），暴露 `now()`、`isRunning()`、漂移校正 |
| CueMapper | `live/cue-mapper.js` | OSC 地址→动作路由；按映射表把 QLab cue 号匹配到 WordWave 段落（支持 `*`/`?` 通配，语义对齐 QLab） |
| Transport | `live/transport.js` | 播放状态机：idle → armed → playing（一首歌）→ idle → panic；歌级切换 |
| LivePanel | `live/panel.js` + `live/panel.css` | 配置面板 UI（见 §5） |
| CueListView | `live/cue-list.js` | Cue List 界面（见 §6） |

## 4. OSC 协议规范（WordWave 侧监听字典）

命名规范：全小写 ASCII，无空格无 unicode（QLab 文档硬性约束）。

### 4.1 控制命令（QLab → WordWave）

| 地址 | 参数 | 行为 |
|---|---|---|
| `/wordwave/show/load` | s: showId | 加载演出配置（映射表+plan 参数） |
| `/wordwave/cue/{n}/go` | s: lyricLine(可选) | 触发 cue n 对应段落（n=QLab cue number，ASCII 化） |
| `/wordwave/cue/{n}/stop` | — | 停止该段落（exit 动画收尾） |
| `/wordwave/panic` | — | 立即黑场，状态回 idle（对齐 QLab Panic） |
| `/wordwave/transport/pause` | i: 0\|1 | 暂停/继续（t 冻结/恢复） |
| `/wordwave/transport/seek` | f: seconds | 跳转当前段落内时间 |
| `/wordwave/scene/{id}/start` | — | 直接切场景（调试/手动模式用） |

### 4.2 时间码（MTC 为可选后备，默认不实施）

- **纯 OSC 模式（默认）**：QLab 每首歌一条 Network Cue 发 `/wordwave/cue/{n}/go`。WordWave 收到后以本地时钟自走整首歌。精度：局域网触发延迟 <5ms；本地时钟漂移一首歌毫秒级，可忽略。每首歌结束误差归零，不累积。
- **MTC 模式（可选后备，P3）**：仅当演出需要在歌曲中途暂停/回退/跳转且 WordWave 画面需跟随时启用。Bridge 解析 quarter-frame 拼 SMPTE 推 `ww/tc`，页面端插值平滑。帧率两端必须一致（24/25/30）。

### 4.3 状态回报（WordWave → Bridge → 可选回 OSC）

`/wordwave/status {state, cueN, t}` 每 500ms 一帧，供 QLab Script Cue 查询或监控屏显示。

## 5. 配置面板（LivePanel）

挂在现有 UI 侧边，新增 "Live" 标签页：

1. **连接区**
   - Bridge URL（默认 `ws://localhost:9102`，IP/端口可改，与 Bridge 启动参数一致），连接状态灯（绿/黄/红 + 延迟 ms）
   - 模式选择：`OSC 触发模式`（默认）/ `MTC 跟随模式`（后备）
   - [Reconnect] [Test GO]（本地自触发，不依赖 QLab 验证链路）
2. **Show 配置区**
   - Show 选择（对应一份 JSON：音频文件 + 歌词 + cue 映射表）
   - 帧率锁定：24/25/30（MTC 模式必填，两端必须一致）
3. **安全区**
   - Panic 大红按钮（面板上常驻，同 /wordwave/panic）
   - "MTC 丢失"策略：`冻结画面` / `播完当前段落` / `黑场`（默认冻结）
4. **诊断区（可折叠）**
   - 最近 20 条 OSC 消息 log（时间戳、地址、参数）
   - 时间码漂移读数（MTC 模式）

所有配置持久化到 localStorage（键 `ww.live.*`），Show 配置文件本身随 show JSON 走。

## 6. Cue List 界面

两栏布局，演出操作员视角：

- **左栏：QLab Cue（由 WordWave 导出的绑定清单导入生成，禁止反向手改）**
  - 列：Cue 号 / 名称（如歌名）/ 时长 / 绑定状态（●已绑定 ○未绑定）
  - 导入按钮：读入 WordWave 导出的 `{cue号 → 工程}` JSON，批量生成对照表
- **右栏：WordWave 播放列表（可编辑，数据源头）**
  - 列：序号 / 歌名 / 首句歌词 / 时长 / **Live Cue 号（每首歌人工填写）**
  - 支持添加/排序/删除工程；cue 号变更从这里改起
- **中间联动**：点击左栏 cue → 高亮右栏目标歌曲；导入后自动按 cue 号对齐
- **数据流铁律**：cue 号唯一事实源 = WordWave 播放列表；变更流程 = WordWave 改号 → 导出绑定清单 → QLab 侧导入。禁止在 QLab 侧反向手改映射
- **未知 cue 护栏**：收到未绑定的 cue 号时，面板红条告警“未绑定 cue：{n}”并写入状态回报，排练时即时暴露两边不同步
- **运行态高亮**：播放中当前 cue/歌曲行黄色高亮 + 进度条；已播变灰
- **预演按钮**：每行 [▶] 本地试触发（带 -3s 倒计时），不惊动 QLab

映射表结构（show JSON 内）：

```json
{
  "live": {
    "mode": "osc",
    "songs": [
      { "id": "song01", "title": "七子之歌", "project": "qizizhi_ge.wwproj", "duration": 245, "liveCue": "101" },
      { "id": "song02", "title": "第二首", "project": "song02.wwproj", "duration": 210, "liveCue": "102" }
    ]
  }
}
```

`liveCue` 在 WordWave 播放列表里填写，是 cue 号唯一事实源；此文件即导出的绑定清单，QLab 侧直接导入消费。一条 cue = 一首歌。

## 7. 播放状态机（Transport）

```
idle ──load show──▶ armed ──cue go──▶ playing(整首歌自走) ──播完──▶ armed
 ▲                    │                 │                            
 │                    │                 └─(可选 pause/seek，后备模式)─┐
 └──────panic─────────┴────────────────────────────────────────────┴─▶ idle(黑场)
```

- `playing` 时引擎 `t` 来源：本地时钟累计（默认）；后备 MTC 模式=TimecodeSource.now()
- 一条 cue 触发一首完整歌曲的歌词时间轴，播完自动回 armed 待下一条
- Panic：立即清屏为 scheme.bg，停所有 decor 动画，状态回 idle；再次 go 需重新 armed（防误触）

## 8. 同步精度与风险对策

| 风险 | 对策 |
|---|---|
| OSC 地址含空格/中文（QLab cue number 常见） | CueMapper 强制 ASCII 化映射：非 ASCII cue 号在映射表里用 `pattern` 显式写；加载时校验并报红 |
| MTC 帧率不一致（不报错但漂移） | 面板锁定 fps；TimecodeSource 检测连续抖动超阈值时黄色告警 |
| 网络丢包（WiFi/分机部署） | WS 心跳 1s；分机部署强制有线网、独立 VLAN（QLab 官方建议）；同机部署走 127.0.0.1 回环，自动豁免 |
| 浏览器后台节流 | 演出机用 Electron（已定案）；网页模式提示"保持前台+禁用节能" |
| QLab GO 与音频起点偏差 | OSC 触发模式下提供全局 offset（ms）微调，存 show JSON |

## 9. 分期实施

| 阶段 | 内容 | 验收标准 |
|---|---|---|
| P1 | 独立 Node Bridge 脚本 + OSCClient + panic/cue-go 两条命令 + 状态机（歌级） | QLab 免费版 Network Cue 发 go，WordWave 播放对应整首歌；panic 秒黑 |
| P2 | 配置面板 + Cue List（静态映射表）+ 映射持久化 | 操作员不碰代码完成一场多歌曲演出的排练级配置 |
| P3（可选后备） | MTC 跟随模式 + TimecodeSource 插值 + 漂移告警 | 仅当出现中途暂停/回退需求时启动；QLab 时间码操作画面 1 帧内跟随 |
| P4 | Electron 打包（Bridge 内置主进程重构）+ 状态回报 | 专用演出机脱离浏览器运行 |

## 10. 已定决策（2026-10-10 老莫拍板）

1. ✅ Bridge 形态：P1 用独立 Node 脚本快速验证，Electron 阶段（P4）再重构内置
2. ✅ Cue List 数据源：WordWave 播放列表为唯一事实源（每首歌填 liveCue 号，可导出绑定清单），QLab 侧只导入消费，禁止反向手改；新增未知 cue 告警护栏
3. ✅ MTC：默认不做（cue 粒度=整首歌，无中途跟随需求），保留为可选后备（P3）；仅当演出需要歌曲中途暂停/回退跟随时启用
4. ✅ 触发粒度：一条 QLab cue 对应 WordWave 一首歌，不逐句逐段同步

## 11. 遗留观察点

- 若某场演出 PGM 音频被现场执行推迟/重播单句，WordWave 画面无法跟随——届时再评估 P3 MTC
- 状态回报（/wordwave/status）是否要回喂 QLab Script Cue 做双确认，P2 面板做完后看排练需求
