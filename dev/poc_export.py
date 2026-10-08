"""WordWave headless PoC: 中文歌词 → MP4 出片。
usage: python3 dev/poc_export.py [out.mp4]
自起自停 8765 端口的 dev/www 静态服务。"""
import asyncio, base64, sys, os
from playwright.async_api import async_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/wordwave_poc.mp4'
LYRICS = "\n".join([
    "夜色漫过城市的天桥",
    "灯火在玻璃上轻轻燃烧",
    "我们说过的话像风一样",
    "穿过街道，穿过人潮",
    "明天还在很远的地方",
    "可我已经开始奔跑",
])

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=True,
            args=['--autoplay-policy=no-user-gesture-required'])
        page = await browser.new_page()
        page.on('console', lambda m: print('  [console]', m.type, m.text[:150]) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: print('  [pageerror]', str(e)[:200]))
        await page.goto('http://localhost:8765/poc.html')
        await page.wait_for_function('typeof window.WW !== "undefined" && typeof J !== "undefined"')

        info = await page.evaluate('WW.setup(' + repr(LYRICS).replace("'", '"') + ')')
        print('plan:', info)

        for i, t in enumerate([info['dur']*0.25, info['dur']*0.5, info['dur']*0.75]):
            dataurl = await page.evaluate(f'WW.shot({t}, 0.5)')
            png = base64.b64decode(dataurl.split(',', 1)[1])
            fn = OUT.replace('.mp4', f'_frame{i+1}.png')
            open(fn, 'wb').write(png)
            print('preview:', fn, len(png), 'bytes')

        print('encoding MP4 ...')
        result = await page.evaluate('WW.export()')
        print('encode done:', result)

        b64 = await page.evaluate('WW.b64()')
        mp4 = base64.b64decode(b64)
        open(OUT, 'wb').write(mp4)
        print('MP4 saved:', OUT, len(mp4), 'bytes')
        await browser.close()

import http.server, socketserver, threading, functools
_handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                             directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www'))
httpd = socketserver.TCPServer(('127.0.0.1', 8765), _handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
try:
    asyncio.run(main())
finally:
    httpd.shutdown()
