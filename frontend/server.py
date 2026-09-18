"""Dependency-free static server for the StartupReady frontend.

Run with: python server.py
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

PORT = int(os.environ.get("PORT", "5173"))
WEB_ROOT = Path(__file__).parent


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)


if __name__ == "__main__":
    print(f"StartupReady frontend running at http://localhost:{PORT}")
    ThreadingHTTPServer(("", PORT), FrontendHandler).serve_forever()
