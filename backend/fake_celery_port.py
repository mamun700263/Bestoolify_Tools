import http.server
import os
import subprocess
import sys
import threading

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a):
        pass

port = int(os.environ.get('PORT', 10000))
server = http.server.HTTPServer(('0.0.0.0', port), Handler)
print(f'Listening on 0.0.0.0:{port}', flush=True)

# Start Celery as a subprocess
celery_proc = subprocess.Popen([
    'celery', '-A', 'app.core.celery.celery_app', 'worker', '--loglevel=info'
])

# Serve forever (main thread)
server.serve_forever()