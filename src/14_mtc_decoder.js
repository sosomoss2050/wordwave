/* ============================================================
   WordWave Show — MTC (MIDI Timecode) decoder front-end
   输入：Web MIDI 消息（quarter-frame F1 / full-frame SysEx）
   输出：组装完成的时间码锚点 → 喂给 J.SMPTEFollower
   ============================================================ */
'use strict';
(() => {
  const root = typeof window !== 'undefined' ? window : globalThis;
  root.J = root.J || {};
  const nowMs = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());
  const FPS_BY_TYPE = [24, 25, 30, 30];  // 0:24 1:25 2:30drop(按30计) 3:30

  class MTCDecoder {
    constructor(opts = {}) {
      this.onTimecode = opts.onTimecode || null;   // (tcSec, fps) => void
      this.onStop = opts.onStop || null;           // () => void
      this._qf = new Array(8).fill(null);          // quarter-frame 缓存
      this._got = 0;
      this._fps = null;
    }

    /** message: Web MIDI 事件 { data: Uint8Array } */
    feed(event, at = nowMs()) {
      const d = event.data;
      if (!d || !d.length) return;
      const st = d[0];
      if (st === 0xf1 && d.length >= 2) {
        this._quarter(d[1], at);
      } else if (st === 0xf0 && d.length >= 10 && d[1] === 0x7f && d[4] === 0x01) {
        this._fullFrame(d, at);                  // full-frame SysEx
      } else if (st === 0xfc) {                  // MIDI Stop
        if (this.onStop) this.onStop();
      }
    }

    _quarter(b, at) {
      // 规范：数据字节 0nnn nnnn —— 高 4 位=piece 序号(0-7)，低 4 位=值
      const piece = b >> 4, nib = b & 0x0f;
      if (piece === 0 && this._got === 8) { this._got = 0; this._qf = new Array(8).fill(null); }   // 新一帧开始
      this._qf[piece] = nib;
      this._got = Math.max(this._got, piece + 1);
      if (piece === 7) {
        // 规范组装：p0-2=时/分/秒低4位，p3=帧低4位，p4.bit0=帧高位，p5.bit0=秒高位，
        // p6.bit0=分高位，p7.bit0=时高位，p7.bit1-2=帧率类型
        const [p0, p1, p2, p3, p4, p5, p6, p7] = this._qf;
        if ([p0,p1,p2,p3,p4,p5,p6,p7].some(v => v == null)) return;
        const h = p0 | ((p7 & 0x01) << 4);
        const m = p1 | ((p6 & 0x01) << 4);
        const s = p2 | ((p5 & 0x01) << 4);
        const f = p3 | ((p4 & 0x01) << 4);
        this._fps = FPS_BY_TYPE[(p7 >> 1) & 0x03] || 25;
        if (this.onTimecode) this.onTimecode(J.tcToSec(h, m, s, f, this._fps), this._fps, at);
        this._got = 0;
      }
    }

    _fullFrame(d, at) {
      const hh = d[5] & 0x1f, mm = d[6], ss = d[7], ff = d[8];
      const type = (d[5] >> 5) & 0x03;
      const fps = FPS_BY_TYPE[type] || 25;
      if (this.onTimecode) this.onTimecode(J.tcToSec(hh, mm, ss, ff, fps), fps, at);
    }
  }

  root.J.MTCDecoder = MTCDecoder;
  if (typeof module === 'object' && module.exports) module.exports = { MTCDecoder, FPS_BY_TYPE };
})();
