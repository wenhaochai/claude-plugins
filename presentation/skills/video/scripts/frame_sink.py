"""Frame sink for rendering a video from a web page.

POST /save?name=NAME with a PNG data URL body writes NAME.png into OUT_DIR, and GET /files/NAME serves NAME from
SERVE_DIR, so the page can fetch its director script. CORS is open, so a page on any localhost port can use it.

    python3 frame_sink.py OUT_DIR [SERVE_DIR] [PORT]
"""
import base64, http.server, os, sys, urllib.parse

OUT = sys.argv[1]
SERVE = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 8793
os.makedirs(OUT, exist_ok=True)


class Handler(http.server.BaseHTTPRequestHandler):
    def cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store')

    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        f = os.path.join(SERVE, os.path.basename(path)) if path.startswith('/files/') else None
        if f and os.path.isfile(f):
            data = open(f, 'rb').read()
            self.send_response(200); self.cors()
            self.send_header('Content-Type', 'text/javascript' if f.endswith('.js') else 'application/octet-stream')
            self.end_headers(); self.wfile.write(data); return
        self.send_response(404 if f else 200); self.cors(); self.end_headers()

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = os.path.basename(q.get('name', ['frame'])[0])
        body = self.rfile.read(int(self.headers.get('Content-Length', 0))).decode()
        data = body.split(',', 1)[1] if body.startswith('data:') else body
        with open(os.path.join(OUT, name + '.png'), 'wb') as fh:
            fh.write(base64.b64decode(data))
        self.send_response(200); self.cors(); self.end_headers(); self.wfile.write(b'ok')

    def log_message(self, *args):
        pass


http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
