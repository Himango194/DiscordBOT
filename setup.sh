#!/usr/bin/env bash
# Discord Bot 一鍵安裝（macOS / Linux）
# 用法：bash setup.sh
set -euo pipefail
REPO="https://github.com/himango194/discordbot.git"
BRANCH="claude/great-euler-h63e4f"

for cmd in git python3; do
    command -v "$cmd" >/dev/null || { echo "找不到 $cmd，請先安裝後再執行。"; exit 1; }
done

# 不在專案資料夾內就先下載專案
if [ ! -f main.py ]; then
    [ -d discordbot ] || git clone -b "$BRANCH" "$REPO" discordbot
    cd discordbot
fi

[ -d .venv ] || python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install -r requirements.txt -q

if [ ! -f .env ]; then
    read -rp "請貼上 Discord Bot Token: " token
    read -rp "請輸入測試伺服器 ID（可留空）: " guild
    printf 'DISCORD_TOKEN=%s\nGUILD_ID=%s\n' "$token" "$guild" > .env
fi

echo
echo "安裝完成！專案位置：$(pwd)"
echo "啟動指令：.venv/bin/python main.py"
