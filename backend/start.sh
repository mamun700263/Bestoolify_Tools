#!/bin/bash

# Start health-check server FIRST and wait for it to be ready
python -c "
import http.server, threading, os, time
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a): pass
port = int(os.environ.get('PORT', 8000))
s = http.server.HTTPServer(('0.0.0.0', port), H)
t = threading.Thread(target=s.serve_forever, daemon=True)
t.start()
print(f'Health check server running on port {port}', flush=True)
" &

# Give it a moment to bind the port
sleep 2

# Then start Celery
celery -A app.core.celery.celery_app worker --loglevel=info