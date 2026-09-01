"""
QR Code & Mobile Local Server Launcher
"""

import os
import socket
import webbrowser
import http.server
import socketserver

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_app")

def main():
    local_ip = get_local_ip()
    mobile_url = f"http://{local_ip}:{PORT}/index.html"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={mobile_url}"
    
    # Create HTML helper page with big QR Code
    qr_html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>핸드폰 연결 QR 코드</title>
    <style>
        body {{
            background: #0f172a;
            color: #fff;
            font-family: sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }}
        .card {{
            background: #1e293b;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid #334155;
        }}
        img {{
            border-radius: 12px;
            background: white;
            padding: 10px;
            margin: 20px 0;
        }}
        .url {{
            background: #0f172a;
            padding: 10px 20px;
            border-radius: 10px;
            color: #38bdf8;
            font-weight: bold;
            font-size: 1.2rem;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>📱 핸드폰에서 열기 (QR 코드)</h1>
        <p style="color: #94a3b8;">핸드폰 카메라로 아래 QR 코드를 스캔하세요!</p>
        <img src="{qr_url}" alt="QR Code" width="280" height="280">
        <p>또는 핸드폰 크롬 주소창에 아래 주소를 치세요:</p>
        <div class="url">{mobile_url}</div>
    </div>
</body>
</html>
"""
    
    qr_page_path = os.path.join(DIRECTORY, "qr.html")
    with open(qr_page_path, "w", encoding="utf-8") as f:
        f.write(qr_html_content)
        
    print(f"\n========================================================")
    print(f"📱 스마트폰 QR 코드 연결 서버 구동 중...")
    print(f"👉 핸드폰 접속 주소: {mobile_url}")
    print(f"========================================================\n")
    
    webbrowser.open(f"http://localhost:{PORT}/qr.html")
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)
            
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()

if __name__ == "__main__":
    main()
