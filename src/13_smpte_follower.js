/* ============================================================
   WordWave Show — SMPTE follower core (protocol-agnostic)
   协议前端（MTC/LTC/Art-Net）只负责喂锚点；本模块负责：
   ① 状态机 idle → following → lost  ② 本地时钟外推插值
   ③ 跳变(seek)检测  ④ 帧率协商警告
   独立于 DOM/引擎，Node 可直接加载测试。
   ============================================================ */
'use strict';
(() => {
  const root = typeof window !== 'undefined' ? window : globalThis;
  root.J = root.J || {};
  const nowMs = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());

  class SMPTEFollower {
    constructor(opts = {}) {
      this.fps = opts.fps || 25;              // 期望帧率
      this.lostMs = opts.lostMs ?? 500;       // 判定信号丢失阈值
      this.jumpSec = opts.jumpSec ?? 0.35;    // 跳变判定阈值
      this.onSeek = opts.onSeek || null;      // (tcSec) => void  锚点跳变
      this.onState = opts.onState || null;    // (state) => void
      this.onFpsMismatch = opts.onFpsMismatch || null; // (expected, actual) => void
      this.state = 'idle';
      this.fpsEff = this.fps;
      this._anchor = null;   // { tc, at }
      this._t = 0;           // last known time (idle/lost 时返回它)
    }

    /** 协议前端喂锚点：tcSec 为 SMPTE 秒数 */
    feedTimecode(tcSec, fps, at = nowMs()) {
      if (!Number.isFinite(tcSec)) return;
      if (Number.isFinite(fps) && fps > 0 && fps !== this.fpsEff) {
        this.fpsEff = fps;
        if (this.onFpsMismatch) this.onFpsMismatch(this.fps, fps);
      }
      const prev = this._anchor;
      if (prev) {
        const dt = (at - prev.at) / 1000;
        const expected = prev.tc + dt;
        if (Math.abs(tcSec - expected) > this.jumpSec) {
          this._set('following');
          if (this.onSeek) this.onSeek(tcSec);
        }
      } else {
        this._set('following');
        if (this.onSeek) this.onSeek(tcSec);
      }
      this._anchor = { tc: tcSec, at };
      this._t = tcSec;
    }

    /** 传输停止（如 DAW 按了停止）：保持在当前时间，回 idle */
    transportStop() {
      this._set('idle');
      this._anchor = null;
    }

    /** 消费端轮询：返回平滑插值后的秒数 */
    now(at = nowMs()) {
      const a = this._anchor;
      if (!a) return this._t;
      if (this.state === 'following' && at - a.at > this.lostMs) this._set('lost');
      if (this.state !== 'following') return this._t;
      this._t = a.tc + (at - a.at) / 1000;
      return this._t;
    }

    _set(s) {
      if (this.state === s) return;
      this.state = s;
      if (this.onState) this.onState(s);
    }
  }

  /** SMPTE 时间码字符串 "HH:MM:SS:FF" → 秒 */
  function tcToSec(h, m, s, f, fps) {
    return h * 3600 + m * 60 + s + f / fps;
  }

  root.J.SMPTEFollower = SMPTEFollower;
  root.J.tcToSec = tcToSec;
  if (typeof module === 'object' && module.exports) module.exports = { SMPTEFollower, tcToSec };
})();
