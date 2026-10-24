# Discord Bot 一鍵安裝（Windows PowerShell）
# 用法：powershell -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Stop"
$Repo = "https://github.com/himango194/discordbot.git"
$Branch = "claude/great-euler-h63e4f"

foreach ($cmd in "git", "python") {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "找不到 $cmd，請先安裝後再執行：" -ForegroundColor Red
        Write-Host "  Git:    https://git-scm.com/download/win"
        Write-Host "  Python: https://www.python.org/downloads/ （安裝時勾選 Add python.exe to PATH）"
        exit 1
    }
}

# 不在專案資料夾內就先下載專案
if (-not (Test-Path "main.py")) {
    if (-not (Test-Path "discordbot")) {
        Write-Host "==> 從 GitHub 下載專案..." -ForegroundColor Cyan
        git clone -b $Branch $Repo discordbot
    }
    Set-Location discordbot
}

if (-not (Test-Path ".venv")) {
    Write-Host "==> 建立虛擬環境..." -ForegroundColor Cyan
    python -m venv .venv
}

Write-Host "==> 安裝套件..." -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -m pip install --upgrade pip -q
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt -q

if (-not (Test-Path ".env")) {
    Write-Host "==> 建立 .env 設定檔" -ForegroundColor Cyan
    $token = Read-Host "請貼上 Discord Bot Token"
    $guild = Read-Host "請輸入測試伺服器 ID（可留空，直接按 Enter）"
    "DISCORD_TOKEN=$token`nGUILD_ID=$guild`n" | Set-Content -Path ".env" -Encoding ascii -NoNewline
}

Write-Host ""
Write-Host "安裝完成！專案位置：$(Get-Location)" -ForegroundColor Green
Write-Host "之後雙擊 start.bat 即可啟動 Bot。"
