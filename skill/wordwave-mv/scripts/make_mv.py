"""WordWave MV 出片脚本：歌词 → MP4（headless Chrome）。
用法示例：
  python3 make_mv.py --lyrics-file song.txt --out /tmp/mv.mp4
  python3 make_mv.py --lyrics "第一行
第二行" --style noir --seed 42
  python3 make_mv.py --lyrics-file song.txt --omakase        # 全自动摇方案
  python3 make_mv.py --lyrics-file song.txt --project-json p.json  # 套用浏览器精调方案

默认规格：1920x1080 / 16:9 / 24fps（引擎原生时间基，老莫定案）。
依赖：playwright (pip3 install playwright) + Google Chrome。
"""
import argparse, base64, json, os, random, subprocess, sys, time

REPO = os.environ.get('WORDWAVE_REPO', '/Volumes/Work/TeamShare/project-workspace/wordwave')
PORT = 8765
DEFAULTS = dict(aspect='16:9', res=1080, fps=24)


def srt_to_lrc(text):
    """SRT → LRC：取每条字幕的起始时间，合并同刻文本行。"""
    import re
    out, stamp = [], None
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*\d+:\d+:\d+[,.]\d+', line)
        if m:
            h, mi, s, ms = (int(x) for x in m.groups())
            stamp = f'[{h*60+mi:02d}:{s:02d}.{ms//100:02d}]'
            continue
        if not line or line.isdigit():
            continue
        if stamp:
            out.append(stamp + line)
            stamp = None
        else:
            out.append(line)
    return '\n'.join(out)


def check_deps(auto_install=True):
    """依赖自检 + 自动安装（小白零操作）。

    1. playwright Python 包：缺失时自动 pip 安装（--user 兜底无权限场景）
    2. 浏览器：优先系统 Chrome；没有则自动 `playwright install chromium`
    3. 全部失败才退出，报错信息含可直接复制的安装命令
    """
    import shutil, subprocess

    # --- playwright 包 ---
    try:
        import playwright  # noqa
    except ImportError:
        if not auto_install:
            sys.exit('[deps] 缺少 playwright：pip3 install playwright')
        print('[deps] 正在自动安装 playwright（约 30 秒）...')
        for cmd in ([sys.executable, '-m', 'pip', 'install', '--user', 'playwright'],
                    [sys.executable, '-m', 'pip', 'install', 'playwright']):
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                break
        else:
            sys.exit('[deps] playwright 自动安装失败。请手动执行：\n  pip3 install playwright\n然后重新运行本命令。')
        print('[deps] playwright 安装完成')

    # --- 浏览器 ---
    chrome_candidates = [
        '/Applications/Google Chrome.app', '/Applications/Chromium.app',                      # macOS
        shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chrome'),       # Linux
    ]
    if any(c and os.path.isdir(c) for c in chrome_candidates if isinstance(c, str) and c.startswith('/')):
        return
    if any(c for c in chrome_candidates if c and not c.startswith('/')):
        return
    # 系统 Chrome 没有 → 用 playwright 自带 chromium（自动下载）
    print('[deps] 未检测到系统 Chrome，自动下载 chromium 内核（一次性，约 2 分钟）...')
    r = subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'])
    if r.returncode != 0:
        sys.exit('[deps] chromium 自动下载失败。请安装 Google Chrome 后重试，或手动执行：\n  python3 -m playwright install chromium')


def ensure_www():
    """dev/www 构建产物不存在时自动构建。"""
    www = os.path.join(REPO, 'dev', 'www')
    if not os.path.isfile(os.path.join(www, 'jizura.js')):
        print('[build] dev/www 不存在，执行 build.py --dev ...')
        subprocess.run([sys.executable, 'build.py', '--dev'], cwd=REPO, check=True)
    if not os.path.isfile(os.path.join(www, 'mp4-muxer.min.js')):
        import shutil
        shutil.copy(os.path.join(REPO, 'vendor', 'mp4-muxer.min.js'), www)
    # skill 宿主页（源文件在 dev/poc.html）
    import shutil
    shutil.copy(os.path.join(REPO, 'dev', 'poc.html'), www)
    return www


def serve(www):
    import functools, http.server, socketserver, threading
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=www)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(('127.0.0.1', PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


async def render(args):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=True)
        page = await browser.new_page(accept_downloads=True)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)[:200]))
        await page.goto(f'http://localhost:{PORT}/poc.html')
        await page.wait_for_function('typeof window.WW !== "undefined" && typeof J !== "undefined"')

        seed = args.seed if args.seed is not None else random.randint(1, 9999999)
        planinfo = None
        if args.omakase:
            planinfo = await page.evaluate(
                f'WW.setupOmakase({json.dumps(args.lyrics)}, {seed}, {json.dumps(bool(args.audio))})')
        elif args.project_json:
            with open(args.project_json, encoding='utf-8') as f:
                pj = f.read()
            planinfo = await page.evaluate(
                f'WW.setupFromJson({json.dumps(args.lyrics)}, {pj}, {json.dumps(bool(args.audio))})')
        else:
            planinfo = await page.evaluate(
                'WW.setup(' + json.dumps(args.lyrics) + ', ' + json.dumps(
                    dict(style=args.style, seed=seed, aspect=args.aspect, res=args.res, fps=args.fps)) + 
                ', ' + json.dumps(bool(args.audio)) + ')')
        print(f'[plan] {planinfo}')

        if args.audio:
            with open(args.audio, 'rb') as f:
                ab64 = base64.b64encode(f.read()).decode()
            ainfo = await page.evaluate(
                f'WW.loadAudio({json.dumps(ab64)}, {json.dumps(os.path.basename(args.audio))})')
            planinfo = {**planinfo, 'dur': ainfo['dur'], 'cuts': ainfo['cuts']}
            print(f'[audio] BPM={ainfo["bpm"]} 拍点{ainfo["beats"]}个 音频时长{ainfo["audioDur"]:.1f}s')
            print(f'[plan] 重规划（含拍点对齐）: {planinfo}')
        for i, frac in enumerate([0.25, 0.5, 0.75]):
            durl = await page.evaluate(f'WW.shot({planinfo["dur"] * frac}, 0.5)')
            fn = args.out.replace('.mp4', f'_frame{i+1}.png')
            open(fn, 'wb').write(base64.b64decode(durl.split(',', 1)[1]))
            print('[preview]', fn)

        print('[encode] 开始渲染 MP4 ...')
        t0 = time.time()
        result = await page.evaluate(f'WW.export({json.dumps(args.quality)})')
        # 走 Playwright 原生下载通道流式取片（大文件不走 b64 字符串，避免内存炸裂/传输出错）
        async with page.expect_download() as dl_info:
            await page.evaluate("document.getElementById('ww-dl').click()")
        download = await dl_info.value
        tmp_out = os.path.join('/tmp', '_ww_render_' + os.path.basename(args.out))
        await download.save_as(tmp_out)
        # 完整性校验：字节数对不上视为失败，绝不交付坏文件
        actual = os.path.getsize(tmp_out)
        expected = result.get('size', 0)
        if actual != expected or actual == 0:
            await page.evaluate('WW.dispose()')
            sys.exit(f'[fail] 成片字节数异常：磁盘 {actual} / 编码器 {expected}。请重试。')
        import shutil
        shutil.move(tmp_out, args.out)
        await page.evaluate('WW.dispose()')
        # 工程文件与成片同目录同名，供浏览器二次精调/复现
        try:
            pj = await page.evaluate('WW.dumpProject()')
            pj_path = args.out[:-4] + '.json'
            open(pj_path, 'w', encoding='utf-8').write(pj)
            print('[project]', pj_path)
        except Exception as e:
            print('[warn] 工程文件导出失败：', e)
        print(f'[done] {args.out}  {result.get("size", 0)} bytes  {result.get("codec", "")}  {time.time()-t0:.0f}s  seed={seed}')
        await browser.close()
        if errors:
            print('[warn] 页面报错（可能影响成片）：', *errors, sep='\n  ')


def main():
    ap = argparse.ArgumentParser(description='WordWave：歌词 → 文字动画 MV')
    ap.add_argument('--lyrics', help='歌词文本（多行）')
    ap.add_argument('--lyrics-file', help='歌词文件路径')
    ap.add_argument('--out', default=time.strftime('wordwave_%Y%m%d_%H%M%S.mp4'), help='输出 MP4 路径')
    ap.add_argument('--style', default=None, help='风格 id（留空=引擎默认；可用列表见 SKILL.md）')
    ap.add_argument('--seed', type=int, default=None, help='随机种子（复现成片）')
    ap.add_argument('--aspect', default=DEFAULTS['aspect'], help='画幅 16:9/9:16/1:1/21:9 ...')
    ap.add_argument('--res', type=int, default=DEFAULTS['res'], help='分辨率高度档 720/1080/2160')
    ap.add_argument('--fps', type=int, default=DEFAULTS['fps'], help='帧率（默认24，引擎原生）')
    ap.add_argument('--omakase', action='store_true', help='全自动：引擎随机整套方案')
    ap.add_argument('--project-json', help='浏览器导出的方案 JSON（精调级）')
    ap.add_argument('--audio', help='歌曲音频文件（mp3/wav/m4a/ogg）：拍点对齐镜头+混入成片')
    ap.add_argument('--quality', default='high', choices=['medium', 'high', 'max'], help='画质（码率系数 medium=0.16/high=0.28/max=0.42，默认 high 质量优先）')
    ap.add_argument('--workdir', help='工作文件夹（推荐）：歌词/音频从中读取，成片与预览帧写入其中；批量时每首歌一个子文件夹')
    args = ap.parse_args()

    if args.project_json and args.omakase:
        sys.exit('[args] --project-json 与 --omakase 互斥')

    # ---- 工作文件夹模式：输入从中发现，输出归位其中 ----
    AUDIO_EXT = ('.mp3', '.wav', '.m4a', '.ogg', '.flac')
    if args.workdir:
        wd = os.path.abspath(args.workdir)
        if not os.path.isdir(wd):
            sys.exit(f'[workdir] 工作文件夹不存在：{wd}（请先建好并放入歌词/音频）')
        files = os.listdir(wd)
        if not args.lyrics_file and not args.lyrics:
            cand = sorted(f for f in files if f.lower().endswith(('.txt', '.lrc', '.srt')))
            if not cand:
                sys.exit(f'[workdir] {wd} 里没找到歌词文件（.txt/.lrc/.srt）')
            args.lyrics_file = os.path.join(wd, cand[0])
            print(f'[workdir] 歌词文件：{cand[0]}')
            if cand[0].lower().endswith('.srt'):
                raw = open(args.lyrics_file, encoding='utf-8', errors='replace').read()
                lrc_path = os.path.join(wd, os.path.splitext(cand[0])[0] + '_converted.lrc')
                open(lrc_path, 'w', encoding='utf-8').write(srt_to_lrc(raw))
                args.lyrics_file = lrc_path
                print(f'[workdir] SRT 已转换为 LRC：{os.path.basename(lrc_path)}')
        if not args.audio:
            cand = sorted(f for f in files if f.lower().endswith(AUDIO_EXT))
            if cand:
                args.audio = os.path.join(wd, cand[0])
                print(f'[workdir] 音频文件：{cand[0]}')
            else:
                print('[workdir] 未发现音频文件，将输出无声 MV')
        if args.out == time.strftime('wordwave_%Y%m%d_%H%M%S.mp4'):
            song = os.path.splitext(os.path.basename(args.lyrics_file or 'wordwave'))[0]
            args.out = os.path.join(wd, f'{song}_mv.mp4')
        else:
            args.out = os.path.join(wd, os.path.basename(args.out))
    elif args.out and os.path.dirname(args.out):
        os.makedirs(os.path.dirname(args.out), exist_ok=True)

    lyrics = args.lyrics
    if args.lyrics_file:
        with open(args.lyrics_file, encoding='utf-8') as f:
            lyrics = f.read()
    if not lyrics or not lyrics.strip():
        sys.exit('[args] 必须提供 --lyrics 或 --lyrics-file')
    args.lyrics = lyrics.strip()
    if not args.out.endswith('.mp4'):
        args.out += '.mp4'

    check_deps()
    www = ensure_www()
    httpd = serve(www)
    try:
        import asyncio
        asyncio.run(render(args))
    finally:
        httpd.shutdown()


if __name__ == '__main__':
    main()
