# Native Windows PowerShell HTTP Server (Port 8080 User Mode)
$ErrorActionPreference = "SilentlyContinue"

# Find local IPv4 address
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*" } | Select-Object -First 1).IPAddress
if (-not $ip) { $ip = "127.0.0.1" }

$port = 8080
$mobileUrl = "http://" + $ip + ":" + $port + "/index.html"
$qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=350x350&data=" + [System.Uri]::EscapeDataString($mobileUrl)

$webAppPath = Join-Path $PSScriptRoot "web_app"
if (-not (Test-Path $webAppPath)) { $webAppPath = Join-Path (Get-Location) "web_app" }

# Write UTF-8 qr.html
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$qrHtml = @"
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>스마트폰 ADAS 연결 QR</title>
    <style>
        body { background: #0f172a; color: #fff; font-family: system-ui, -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
        .card { background: #1e293b; padding: 30px; border-radius: 20px; border: 1px solid #334155; max-width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
        img { border-radius: 12px; background: white; padding: 10px; margin: 20px 0; }
        .url { background: #0f172a; padding: 12px 24px; border-radius: 10px; color: #38bdf8; font-weight: bold; font-size: 1.4rem; word-break: break-all; margin: 15px 0; }
        .notice { background: rgba(34, 197, 94, 0.2); color: #4ade80; padding: 10px; border-radius: 8px; font-size: 1rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📱 스마트폰 ADAS 즉시 연결</h1>
        <div class="notice">✔ 스마트폰 카메라로 QR 코드를 스캔하세요</div>
        <img src="$qrUrl" width="300" height="300" alt="QR Code">
        <p>스마트폰 크롬 주소창에 입력하실 주소:</p>
        <div class="url">$mobileUrl</div>
    </div>
</body>
</html>
"@

$qrFile = Join-Path $webAppPath "qr.html"
[System.IO.File]::WriteAllText($qrFile, $qrHtml, $utf8NoBom)

# Start HttpListener on Port 8080
$listener = New-Object System.Net.HttpListener
try {
    $listener.Prefixes.Add("http://*:${port}/")
    $listener.Start()
} catch {
    $listener = New-Object System.Net.HttpListener
    $listener.Prefixes.Add("http://localhost:${port}/")
    $listener.Start()
}

# Open qr.html directly as a local file (Guaranteed 100% open without connection refused)
Start-Process $qrFile

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "📱 ADAS Mobile Web Server Running on Port 8080" -ForegroundColor Green
Write-Host "👉 Mobile Access URL: $mobileUrl" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    
    $localPath = $request.Url.LocalPath.TrimStart('/')
    if ([string]::IsNullOrEmpty($localPath)) { $localPath = "index.html" }
    $filePath = Join-Path $webAppPath $localPath
    
    if (Test-Path $filePath -PathType Leaf) {
        $bytes = [System.IO.File]::ReadAllBytes($filePath)
        $response.ContentLength64 = $bytes.Length
        if ($filePath.EndsWith(".html")) { $response.ContentType = "text/html; charset=utf-8" }
        elseif ($filePath.EndsWith(".js")) { $response.ContentType = "text/javascript" }
        elseif ($filePath.EndsWith(".css")) { $response.ContentType = "text/css" }
        $response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
        $response.StatusCode = 404
    }
    $response.Close()
}
