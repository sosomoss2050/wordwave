"""Show 播放器开发服务器：带 no-cache 头，普通刷新永远拿到最新版。
usage: python3 dev/show_server.py [port]   （默认 8631，仅绑定 127.0.0.1）"""
import http.server, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8631

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(ROOT)
    print(f'show dev server: http://127.0.0.1:{PORT}/show/index.html (no-cache)')
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
