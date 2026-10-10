"""Build the Show Player single-file page from src/ (engine) + app/show_body.html.
usage: python3 build_show.py -> show/index.html"""
import glob, os
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
read = lambda p: open(p, encoding='utf-8').read()

ENGINE_FILES = [f for f in sorted(glob.glob('src/*.js'))
                if not os.path.basename(f).startswith(('12_', '15_'))]      # engine only, no editor UI, no show UI inline
SHOW_UI = read('src/15_show_player.js')
css = read('app/style.css')

html = f'''<!doctype html>
<html lang="zh-hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WordWave Show Player</title>
<style>
{css}
/* ---- show player overrides ---- */
html,body{{margin:0;padding:0;width:100%;height:100%;background:#141417;color:#ededf0;font-family:system-ui,'PingFang SC',sans-serif;overflow:hidden}}
#showapp{{display:flex;flex-direction:column;width:100vw;height:100vh;background:#141417}}
.sp-bar{{display:flex;align-items:center;justify-content:space-between;padding:8px 14px;background:#1d1d22;border-bottom:1px solid #2e2e36;font-size:13px;gap:8px 12px;flex-wrap:wrap;row-gap:6px}}
.sp-brand{{display:flex;align-items:baseline;gap:8px;margin-right:10px;white-space:nowrap}}
.sp-mark{{font-weight:800;font-size:16px;color:#fff}}
.sp-word{{font-weight:600;font-size:13px;color:#ededf0}}
.sp-tag{{font-size:10px;color:#8b8b94;letter-spacing:.5px}}
.sp-ver{{font-family:ui-monospace,monospace;font-size:10px;color:#8b8b94}}
.sp-mode{{display:flex;gap:6px;align-items:center}}
.sp-badge{{padding:3px 10px;border-radius:6px;font-weight:600}}
.sp-badge.show{{background:#e5484d;color:#fff}}
.sp-tab{{padding:4px 14px;border:1px solid #2e2e36;border-radius:6px;background:transparent;color:#8b8b94;cursor:pointer}}
.sp-tab.on{{background:#2e2e36;color:#fff}}
.sp-tc{{font-family:ui-monospace,monospace;font-size:15px;letter-spacing:1px;color:#f5a623;margin-left:auto;margin-right:auto}}
.sp-stage{{flex:1;position:relative;width:100%;background:#000;display:flex;align-items:center;justify-content:center;min-height:0;overflow:hidden}}
.sp-stage canvas{{max-width:100%;max-height:100%;width:auto;height:auto;display:block}}
.sp-row input[type=range]{{accent-color:#46a758}}
.sp-ops{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:#2e2e36;border-top:1px solid #2e2e36}}
.sp-cell{{background:#1d1d22;padding:10px 14px}}
.sp-cell h4{{margin:0 0 8px;font-size:10px;color:#8b8b94;text-transform:uppercase;letter-spacing:1px}}
.sp-row{{display:flex;gap:6px;flex-wrap:wrap;align-items:center}}
.sp-btn{{background:#2a2a31;color:#ededf0;border:1px solid #2e2e36;border-radius:6px;padding:5px 12px;font-size:13px;cursor:pointer}}
.sp-btn.go{{background:#46a758;color:#fff;border-color:#46a58f;font-weight:700;min-width:64px}}
.sp-btn:disabled{{opacity:.35;cursor:not-allowed}}
.sp-st{{display:flex;align-items:center;gap:8px;font-size:12px}}
.sp-dot{{width:8px;height:8px;border-radius:50%;background:#555}}
.sp-dot.following{{background:#46a758;box-shadow:0 0 8px #46a758}}
.sp-dot.paused{{background:#f5a623;box-shadow:0 0 8px #f5a623}}
.sp-dot.chasing{{background:#f5a623;box-shadow:0 0 8px #f5a623}}
.sp-src{{font-family:ui-monospace,monospace;color:#f5a623}}
.sp-note{{font-size:11px;color:#8b8b94}}
.sp-srcsel{{display:none}}
.sp-sync .sp-srcsel{{display:flex;flex-direction:column;align-items:flex-start;gap:6px}}
</style>
</head>
<body>
<div id="showapp">
  <div class="sp-bar">
    <div class="sp-mode">
      <div class="sp-brand">
        <span class="sp-mark">字浪</span>
        <span class="sp-word">WordWave</span>
        <span class="sp-tag">lyric motion engine</span>
        <span class="sp-ver">v@VERSION@</span>
      </div>
      <span class="sp-badge show">SHOW</span>
      <button class="sp-tab on" id="tabNormal">NORMAL</button>
      <button class="sp-tab" id="tabSync">SYNC</button>
    </div>
    <div class="sp-tc" id="spTc">--:--:--:--</div>
    <div class="sp-mode">
      <span class="sp-note" id="spProj">未加载工程</span>
      <button class="sp-tab" id="spOpen">打开工程…</button>
      <input type="file" id="spFile" accept=".json,.wordwave.json,application/json" hidden>
      <button class="sp-tab" id="spReset" title="清除已加载的工程与音频，回到初始状态">初始化</button>
      <button class="sp-tab" id="spHelp">使用说明</button>
    </div>
  </div>
  <div class="sp-stage" id="spStage"><canvas id="view" width="1280" height="720"></canvas></div>
  <div class="sp-ops" id="spOps">
    <div class="sp-cell">
      <h4>走带</h4>
      <div class="sp-row">
        <button class="sp-btn go" id="spGo">GO</button>
        <button class="sp-btn" id="spPause">⏸</button>
        <button class="sp-btn" id="spStop">⏹</button>
        <button class="sp-btn" id="spFull">全屏</button>
        <button class="sp-btn" id="spSong">加载音乐…</button>
        <input type="file" id="spSongFile" accept="audio/*" hidden>
        <span class="sp-note" id="spSongName">未加载音频</span>
      </div>
      <div class="sp-row" style="margin-top:6px">
        <span class="sp-tc" id="spNow" style="font-size:12px">00:00</span>
        <input id="spScrub" type="range" min="0" max="10000" value="0" style="flex:1" aria-label="歌曲进度">
        <span class="sp-note" id="spDur">00:00</span>
      </div>
    </div>
    <div class="sp-cell sp-srcsel">
      <h4>同步</h4>
      <div class="sp-row">
        <select class="sp-btn" id="spSrc"><option value="">选择 MTC 端口…</option></select>
        <span class="sp-st"><span class="sp-dot" id="spDot"></span><span id="spState">idle</span></span>
      </div>
      <div class="sp-row" style="margin-top:6px">
        <span class="sp-note">宿主时间 <span class="sp-src" id="spHostTc">--:--:--:--</span></span>
      </div>
      <div class="sp-row" style="margin-top:6px">
        <span class="sp-note">时间码偏移 <input id="spOffset" class="sp-btn" style="width:100px" placeholder="HH:MM:SS:FF" value="00:00:00:00" inputmode="numeric" autocomplete="off" spellcheck="false"></span>
      </div>
    </div>
    <div class="sp-cell">
      <h4>状态</h4>
      <div class="sp-row sp-note" id="spMsg">NORMAL：空格/GO 播放；←→ 逐帧（Shift ±1s）；F 全屏</div>
    </div>
  </div>
</div>
<dialog id="spHelpDlg" class="terms" aria-labelledby="spHelpTitle">
  <form method="dialog">
    <h2 id="spHelpTitle">WordWave Show Player 使用说明</h2>
    <div class="terms-main">
      <p class="terms-big">① 打开工程：点击右上角「打开工程…」选择编辑器导出的 .json 工程文件；若歌曲已在本浏览器（编辑器保存过），将自动恢复音频</p>
    </div>
    <p>② NORMAL 模式：空格/GO 播放，←→ 逐帧（Shift ±1 秒），F 全屏；进度条可拖拽</p>
    <p>③ SYNC 模式：选择 MTC 端口（自动记忆），宿主播放时自动跟随；时间码偏移支持正负值</p>
    <p>④ 快捷键：空格 播放/暂停 · ←→ 逐帧 · F 全屏 · Esc 退出全屏</p>
    <div class="terms-foot"><span></span><span class="row"><button value="close" class="primary" autofocus>关闭</button></span></div>
  </form>
</dialog>
<dialog id="spResetDlg" class="terms" aria-labelledby="spResetTitle">
  <form method="dialog" id="spResetForm">
    <h2 id="spResetTitle">初始化</h2>
    <p>将复位播放器状态，清除以下内容：</p>
    <ul class="reset-list">
      <li>已加载的工程（含歌词与渲染画面）</li>
      <li>本次会话中加载的音频</li>
      <li>MTC 同步连接（端口记忆与时间码偏移保留）</li>
    </ul>
    <p class="terms-sub">播放器只读加载，不影响编辑器数据；已保存的工程文件（.json）也不会被删除。</p>
    <div class="terms-foot"><span></span><span class="row"><button value="cancel" class="ghost">取消</button><button value="reset" class="danger">初始化</button></span></div>
  </form>
</dialog>
<script>
{chr(10).join(read(f) for f in ENGINE_FILES)}
</script>
<script>
{SHOW_UI}
</script>
</body>
</html>'''
os.makedirs('show', exist_ok=True)
VERSION = read('VERSION').strip()
html = html.replace('@VERSION@', VERSION)
open('show/index.html', 'w', encoding='utf-8').write(html)
print('show/index.html built (v%s), %d bytes' % (VERSION, len(html)))
