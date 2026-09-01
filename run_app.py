"""
ADAS Mobile Web Simulator Local Launcher
Opens the Web Simulator in default web browser.
"""

import os
import sys
import webbrowser
import http.server
import socketserver

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_app")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    url = f"http://localhost:{PORT}/index.html"
    print(f"==========================================================")
    print(f"🚗 ADAS Mobile Web Safety Simulator Running at: {url}")
    print(f"Press Ctrl+C to stop the server.")
    print(f"==========================================================")
    
    webbrowser.open(url)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.server_close()

if __name__ == "__main__":
    main()
