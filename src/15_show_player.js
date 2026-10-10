/* ============================================================
   WordWave Show — Show Player UI shell
   双播放模式：NORMAL（GO 手动）/ SYNC（SMPTE follower 驱动）
   快捷键继承编辑器：Space 播放、←→ 逐帧（Shift±1s，仅 NORMAL）、F 全屏
   ============================================================ */
(() => {
'use strict';
if (!document.getElementById('showapp')) return;    // engine-only pages (tests)
const $ = id => document.getElementById(id);
const LS_KEY = 'wordwave.project.v1';               // 与编辑器共用工程存储

const S = {
  project: null, plan: null, audio: null,
  renderer: new J.Renderer(),
  playing: false, t: 0, need: true,
  mode: 'normal',        // normal | sync
  tcOffset: 0,           // SMPTE 偏移（秒）：plan时间 = 绝对MTC - tcOffset
  follower: null, mtc: null, midiIn: null,
};

/* ---------- 渲染循环 ---------- */
function tick() {
  if (S.mode === 'sync' && S.follower) {
    const abs = S.follower.now();              // 宿主原始 MTC 秒
    const t = Math.max(0, abs + S.tcOffset);   // 工程时间 = 宿主 + 偏移（偏移带符号）
    if (Math.abs(t - S.t) > 0.001) { S.t = t; S.need = true; }
    S._absTc = abs;
  }
  if (S.need && S.plan) {
    const cv = $('view'), ctx = cv.getContext('2d');
    S.renderer.frame(ctx, S.plan, S.t, { fast: false });
    S.need = false;
  }
  updateTc();
  requestAnimationFrame(tick);
}
function updateTc() {
  const fps = (S.mode === 'sync' && S.follower) ? (S.follower.fpsEff || 25) : 25;
  const fmtSmp = t => {
    const fr = Math.floor((t % 1) * fps + 1e-6);
    const h = Math.floor(t / 3600), m = Math.floor(t / 60) % 60, s = Math.floor(t) % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}:${String(fr).padStart(2, '0')}`;
  };
  // 顶栏：工程时间码（宿主 MTC 经偏移映射后的工程时间，供 WordWave 工作人员查看）
  $('spTc').textContent = fmtSmp(S.t);
  const ht = $('spHostTc');
  if (ht) ht.textContent = (S.mode === 'sync' && S._absTc != null) ? fmtSmp(S._absTc) : '--:--:--:--';   // 宿主原始 MTC
}

/* ---------- 工程加载：文件打开 + 同浏览器 localStorage 回退 ---------- */
async function useProject(proj, label) {
  S.project = proj;
  await replan();
  $('spProj').textContent = label + '（只读）';
}
function loadProject() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) { useProject(JSON.parse(raw), '本地工程'); return; }
  } catch (e) { $('spProj').textContent = '本地工程损坏: ' + e.message; }
}
$('spOpen').addEventListener('click', () => $('spFile').click());
$('spFile').addEventListener('change', async e => {
  const f = e.target.files && e.target.files[0];
  if (!f) return;
  try {
    const proj = JSON.parse(await f.text());
    await useProject(proj, f.name);
    // 工程自带歌曲名时，尝试从同浏览器 IndexedDB 恢复音频（编辑器存过即可）
    if (S.project.audioName && !S.audio && J.loadSong) {
      const song = await J.loadSong();
      if (song && song.name === S.project.audioName) {
        S.audio = await J.analyzeAudio(song);
        await replan();
        $('spMsg').textContent = '已加载音频：' + song.name;
      } else {
        $('spMsg').textContent = '提示：音频 "' + S.project.audioName + '" 不在本浏览器，需在编辑器中重新装载一次';
      }
    }
  } catch (err) { $('spProj').textContent = '工程打开失败: ' + err.message; }
  e.target.value = '';
});
async function replan() {
  if (!S.project) return;
  await J.ensureFonts(S.project.lyrics + (S.project.title || '') + '0123456789XYLINEREC:/.・【】No', null);
  S.plan = J.plan(S.project, S.audio);
  S.need = true;
}

/* ---------- NORMAL 模式走带 ---------- */
function go() {
  if (S.mode !== 'normal' || !S.plan) return;
  if (S.t >= S.plan.duration - 0.01) seek(0);
  play();
}
let _raf0 = 0;
function play() {
  if (S.playing || !S.plan) return;
  S.playing = true;
  S._t0 = performance.now() - S.t * 1000;
  requestAnimationFrame(normalTick);
}
function normalTick() {
  if (!S.playing || S.mode !== 'normal') { S.playing = false; return; }
  S.t = (performance.now() - S._t0) / 1000;
  if (S.t >= S.plan.duration) { S.t = S.plan.duration; pause(); }
  S.need = true;
  requestAnimationFrame(normalTick);
}
function pause() { S.playing = false; }
function seek(t) { S.t = Math.max(0, Math.min(t, S.plan ? S.plan.duration : t)); S.need = true; }

/* ---------- SYNC 模式 ---------- */
function setMode(m) {
  if (S.mode === m) return;
  if (S.mode === 'sync') teardownSync();
  S.mode = m;
  document.body.classList.toggle('sp-sync', m === 'sync');
  $('tabNormal').classList.toggle('on', m === 'normal');
  $('tabSync').classList.toggle('on', m === 'sync');
  if (m === 'sync') setupSync();
  $('spMsg').textContent = m === 'sync'
    ? 'SYNC：等待时间码…选择 MTC 输入端口'
    : 'NORMAL：空格/GO 播放；←→ 逐帧（Shift ±1s）；F 全屏';
  $('spGo').disabled = (m === 'sync');
  pause();
}
function setupSync() {
  S.follower = new J.SMPTEFollower({
    fps: 25,
    onSeek: abs => { seek(Math.max(0, abs + S.tcOffset)); },
    onState: st => {
      const dot = $('spDot');
      dot.className = 'sp-dot ' + (st === 'following' ? 'following' : st === 'paused' ? 'paused' : '');
      $('spState').textContent = st;
      $('spGo').disabled = (S.mode === 'sync' && st === 'following');   // paused 时 GO 可接管
    },
  });
  restoreOrPickPort();   // 恢复上次端口，或回退第一个可用设备
}
function teardownSync() {
  if (S.midiIn) { try { S.midiIn.onmidimessage = null; } catch (e) {} S.midiIn = null; }
  S.follower = null; S.mtc = null;
  $('spDot').className = 'sp-dot'; $('spState').textContent = 'idle';
}
/* ---------- 同步源记忆：localStorage 保存端口 id，不可用则回退第一个 ---------- */
const SRC_KEY = 'wordwave.show.midiPort';
async function restoreOrPickPort() {
  if (!navigator.requestMIDIAccess) { $('spMsg').textContent = '此环境无 Web MIDI'; return; }
  try {
    const acc = await navigator.requestMIDIAccess();
    const sel = $('spSrc');
    sel.innerHTML = '<option value="">选择 MTC 端口…</option>';
    for (const port of acc.inputs.values()) {
      const o = document.createElement('option');
      o.value = port.id; o.textContent = port.name;
      sel.appendChild(o);
    }
    let pick = null;
    const saved = (() => { try { return localStorage.getItem(SRC_KEY); } catch (e) { return null; } })();
    if (saved && acc.inputs.has(saved)) pick = saved;
    else if (acc.inputs.size) pick = acc.inputs.values().next().value;   // 回退：第一个可用设备
    if (pick) { sel.value = pick; connectPort(acc, pick); }
    sel.onchange = () => {
      try { localStorage.setItem(SRC_KEY, sel.value); } catch (e) {}
      connectPort(acc, sel.value);
    };
  } catch (e) { $('spMsg').textContent = 'MIDI 访问被拒绝: ' + e.message; }
}
function connectPort(acc, id) {
  if (S.midiIn) { try { S.midiIn.onmidimessage = null; } catch (e) {} }
  const port = acc.inputs.get(id);
  if (!port) { S.midiIn = null; return; }
  S.midiIn = port;
  S.mtc = new J.MTCDecoder({
    onTimecode: (tc, fps) => S.follower && S.follower.feedTimecode(tc, fps),
    onStop: () => S.follower && S.follower.transportStop(),
  });
  port.onmidimessage = ev => S.mtc && S.mtc.feed(ev);
  $('spMsg').textContent = 'SYNC：已连接 ' + port.name + '，等待时间码…';
}

/* ---------- SMPTE 偏移：把绝对时间码映射到工程时间轴 ---------- */
function parseTc(str) {
  const m = /^([+-]?\d+):(\d{1,2}):(\d{1,2}):(\d{1,2})$/.exec((str || '').trim());
  if (!m) return null;
  const sign = m[1].startsWith('-') ? -1 : 1;
  return sign * ((Math.abs(parseInt(m[1], 10)) * 3600) + (+m[2]) * 60 + (+m[3]) + (+m[4]) / 25);
}
function applyOffset() {
  const v = parseTc($('spOffset').value);
  if (v == null) { $('spOffset').style.borderColor = '#e5484d'; return; }
  $('spOffset').style.borderColor = '';
  S.tcOffset = v;
  S.need = true;
}

/* ---------- 全屏（继承编辑器 toggleFullscreen） ---------- */
function toggleFullscreen() {
  const st = $('spStage');
  if (document.fullscreenElement) document.exitFullscreen();
  else if (st.requestFullscreen) st.requestFullscreen().catch(e => console.warn(e.message));
}

/* ---------- 快捷键（继承编辑器；show 模式差异点已标注） ---------- */
document.addEventListener('keydown', e => {
  const typing = /INPUT|TEXTAREA|SELECT/.test((e.target && e.target.tagName) || '');
  if (typing) return;
  if (e.code === 'Space') { e.preventDefault(); S.mode === 'normal' ? (S.playing ? pause() : go()) : null; }
  else if (e.code === 'ArrowRight' && S.mode === 'normal') { e.preventDefault(); seek(S.t + (e.shiftKey ? 1 : 1 / 25)); }
  else if (e.code === 'ArrowLeft' && S.mode === 'normal') { e.preventDefault(); seek(S.t - (e.shiftKey ? 1 : 1 / 25)); }
  else if (e.code === 'KeyF') { e.preventDefault(); toggleFullscreen(); }
  // Esc：浏览器原生退出全屏；show 模式未来改长按 Esc（防误触）
});

/* ---------- 绑定与启动 ---------- */
$('tabNormal').addEventListener('click', () => setMode('normal'));
$('tabSync').addEventListener('click', () => setMode('sync'));
$('spGo').addEventListener('click', go);
$('spPause').addEventListener('click', () => { if (S.mode === 'normal') pause(); });
$('spStop').addEventListener('click', () => { if (S.mode === 'normal') { pause(); seek(0); } });
$('spFull').addEventListener('click', toggleFullscreen);
$('spOffset').addEventListener('change', applyOffset);
// 偏移输入掩码：数字自动入位 HH:MM:SS:FF，逐段范围钳制（时0-23/分秒0-59/帧0-24），前缀 ± 可选
(function () {
  const el = $('spOffset');
  const LIM = [23, 59, 59, 24];
  function mask(raw) {
    const sign = /^\s*[-]/.test(raw) ? '-' : (/^\s*\+/.test(raw) ? '+' : '');
    const digits = raw.replace(/[^0-9]/g, '').slice(0, 8);
    if (!digits) return sign;
    const seg = [];
    for (let i = 0; i < 4; i++) {
      let v = parseInt(digits.slice(i * 2, i * 2 + 2) || '0', 10);
      if (v > LIM[i]) v = LIM[i];
      seg.push(String(v).padStart(2, '0'));
    }
    return sign + seg.join(':');
  }
  el.addEventListener('input', () => {
    const clean = mask(el.value);
    if (clean !== el.value) el.value = clean;
  });
  el.addEventListener('blur', () => { if (!el.value.trim()) el.value = '00:00:00:00'; });
})();

loadProject();
requestAnimationFrame(tick);
})();
