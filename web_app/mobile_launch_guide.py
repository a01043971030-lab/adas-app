"""
Mobile Smartphone Launcher Helper
Prints your computer's local IP address so you can open the app on your smartphone!
"""

import os
import socket
import webbrowser
import http.server
import socketserver

def get_local_ip():
    """Finds the local WiFi IP address of this computer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address to get local interface IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_app")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    local_ip = get_local_ip()
    mobile_url = f"http://{local_ip}:{PORT}/index.html"
    
    print("\n" + "="*65)
    print("📱 [스마트폰에서 접속하는 방법]")
    print("="*65)
    print(f"1. 스마트폰과 컴퓨터를 '같은 와이파이(Wi-Fi)'에 연결하세요.")
    print(f"2. 스마트폰 크롬/사파리 브라우저 주소창에 아래 주소를 입력하세요:")
    print(f"\n   👉  {mobile_url}\n")
    print("="*65 + "\n")
    
    webbrowser.open(f"http://localhost:{PORT}/index.html")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버가 종료되었습니다.")
            httpd.server_close()

if __name__ == "__main__":
    main()
