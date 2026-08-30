#!/usr/bin/env python3
import http.server
import socketserver
import threading
import time

def start_server(port):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    def run():
        try:
            with socketserver.TCPServer(("0.0.0.0", port), QuietHandler) as httpd:
                httpd.serve_forever()
        except Exception:
            pass

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t

start_server(5000)
start_server(8081)

while True:
    time.sleep(3600)
