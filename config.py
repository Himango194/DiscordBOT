"""機器人設定：Token 從環境變數讀取，其餘 ID 直接在這裡修改。"""

import os

from dotenv import load_dotenv

load_dotenv()

# ======================
# 機密 / 環境設定（寫在 .env）
# ======================
TOKEN = os.getenv("DISCORD_TOKEN", "")
GUILD_ID = int(os.getenv("GUILD_ID") or 0) or None

# ======================
# 狀態輪換
# ======================
STATUSES = [
    "☭ 革命進行中",
    "☭ 為人民服務",
    "☭ 已被國家徵用",
    "☭ 全世界無產者，聯合起來",
]
STATUS_INTERVAL_SECONDS = 30

# ======================
# 歡迎訊息
# ======================
WELCOME_CHANNEL_ID = 1352133950998450388
ROLE_CHANNEL_ID = 1451266846593515610  # 歡迎訊息中提示去領身分組的頻道

# ======================
# 點名
# ======================
ROLL_CALL_LOG_CHANNEL_ID = 0  # 點名結果紀錄要發送到的文字頻道（0 = 不發送）
ROLL_CALL_PING_CHANNEL_ID = 0  # 自動 TAG 未到成員的頻道（0 = 使用指令的頻道）

# ======================
# 身分組選單（名稱, 身分組 ID, emoji）
# ======================
ROLE_OPTIONS = [
    ("Minecraft", 1121616771925938236, "<:Minecraft:1121616616099156018>"),
    ("APEX", 1075339041517604935, "<:apex:1075339374251741205>"),
    ("Overwatch", 1057244921330941972, "<:Overwatch:1027860652880044052>"),
    ("Valorant", 1075340988366737419, "<:Valorant:1075341351211765770>"),
    ("League of Legends", 1125382270254067833, "<:LeagueofLegends:1125382589402861680>"),
    ("CSGO", 1451245428573081702, "♥️"),
]

ROLE_MENU_IMAGES = [
    "https://i.meee.com.tw/BYigMCq.png",
    "https://i.meee.com.tw/0IsCCnA.png",
    "https://i.meee.com.tw/Fm1SQIk.png",
]
ROLE_MENU_AUTHOR_ICON = "https://i.meee.com.tw/vPGC0xr.png"

# 可以使用管理指令（例如 /menu-role）的身分組
ADMIN_ROLE_IDS = [
    1072779660347318322,
]
