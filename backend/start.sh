#!/bin/bash
# Start a tiny health-check server on the port Render expects
python -c "
import http.server, threading, os
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a): pass
s = http.server.HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8000))), H)
threading.Thread(target=s.serve_forever, daemon=True).start()
" &

# Start the actual Celery worker
celery -A app.core.celery.celery_app worker --loglevel=info