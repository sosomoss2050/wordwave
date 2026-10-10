/* Node 单元测试：SMPTE follower + MTC decoder
   用法：node dev/show_test.js */
'use strict';
const { SMPTEFollower, tcToSec } = require('../src/13_smpte_follower.js');
const { MTCDecoder } = require('../src/14_mtc_decoder.js');

let pass = 0, fail = 0;
function eq(name, got, want, tol = 0) {
  const ok = tol ? Math.abs(got - want) <= tol : got === want;
  if (ok) { pass++; } else { fail++; console.log(`FAIL ${name}: got=${got} want=${want}`); }
}

// ---- 1. tcToSec ----
eq('tcToSec 01:02:03:12@25', tcToSec(1, 2, 3, 12, 25), 3723.48);

// ---- 2. 正常跟随：quarter-frame 流驱动，插值平滑 ----
{
  const f = new SMPTEFollower({ fps: 25 });
  const seeks = [];
  f.onSeek = tc => seeks.push(tc);
  let t = 0; const T0 = 1000;
  // 每帧喂锚点（40ms@25fps），模拟 MTC quarter-frame 每 1/4 帧一条，简化为整帧锚点
  for (let i = 0; i <= 50; i++) f.feedTimecode(i / 25, 25, T0 + i * 40);
  eq('following 状态', f.state, 'following');
  eq('seeks 次数（首锚+无跳变）', seeks.length, 1);
  eq('now() 插值 @ 帧中间', f.now(T0 + 50 * 40 + 20), 2.02, 0.002);  // 锤点在50帧=2s，再过20ms → 2.02
}

// ---- 3. 跳变检测：拖拽播放头 ----
{
  const f = new SMPTEFollower({ fps: 25, jumpSec: 0.35 });
  const seeks = [];
  f.onSeek = tc => seeks.push(tc);
  const T0 = 2000;
  f.feedTimecode(10, 25, T0);
  f.feedTimecode(10.04, 25, T0 + 40);
  f.feedTimecode(30, 25, T0 + 80);      // 突跳 20s
  f.feedTimecode(30.04, 25, T0 + 120);
  eq('跳变 seek 触发', seeks.length, 2);
  eq('跳变后时间', f.now(T0 + 160), 30.08, 0.002);
}

// ---- 4. 信号丢失 ----
{
  const f = new SMPTEFollower({ fps: 25, lostMs: 500 });
  let states = [];
  f.onState = s => states.push(s);
  const T0 = 3000;
  f.feedTimecode(5, 25, T0);
  eq('丢失前 following', f.now(T0 + 100), 5.1, 0.002);
  f.now(T0 + 700);                    // 超过 lostMs，触发状态迁移
  eq('丢失后状态', f.state, 'lost');
  eq('lost 保持最后时间', f.now(T0 + 800), 5.1, 0.002);
}

// ---- 5. transportStop 回 idle ----
{
  const f = new SMPTEFollower({ fps: 25 });
  f.feedTimecode(5, 25, 1000);
  f.transportStop();
  eq('stop 后 idle', f.state, 'idle');
  eq('stop 后时间冻结', f.now(9000), 5, 0.0001);
}

// ---- 6. MTC quarter-frame 组装 ----
{
  const dec = new MTCDecoder();
  const got = [];
  dec.onTimecode = (tc, fps) => got.push([tc, fps]);
  // 01:02:03:12 @25fps：数据字节 = piece<<4 | value；frame=12→低位0xC，piece7 value = fps1(25)<<1 | 时高位0 = 0x02
  const nibs = [0x01, 0x12, 0x23, 0x3C, 0x40, 0x50, 0x60, 0x72];

  for (const b of nibs) dec.feed({ data: new Uint8Array([0xf1, b]) });
  eq('MTC 帧数', got.length, 1);
  eq('MTC 时间', got[0][0], tcToSec(1, 2, 3, 12, 25), 0.0001);
  eq('MTC 帧率', got[0][1], 25);
}

// ---- 7. MTC full-frame SysEx ----
{
  const dec = new MTCDecoder();
  const got = [];
  dec.onTimecode = (tc, fps) => got.push([tc, fps]);
  // full-frame：02:03:12:00 @25fps → hh字节=0x22（帧率1在bit5-6，时=2），mm=0x03, ss=0x0C, ff=0x00
  dec.feed({ data: new Uint8Array([0xf0, 0x7f, 0x7f, 0x06, 0x01, 0x22, 0x03, 0x0C, 0x00, 0xf7]) });
  eq('full-frame 帧数', got.length, 1);
  eq('full-frame 时间', got[0][0], tcToSec(2, 3, 12, 0, 25), 0.0001);
}

// ---- 8. MTC Stop ----
{
  const dec = new MTCDecoder();
  let stopped = false;
  dec.onStop = () => { stopped = true; };
  dec.feed({ data: new Uint8Array([0xfc]) });
  eq('MTC stop', stopped, true);
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
