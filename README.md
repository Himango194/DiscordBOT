# DiscordBOT

使用 [discord.py](https://discordpy.readthedocs.io/) 2.x 打造的 Discord 機器人，採用斜線指令與 Cog 模組化架構。

## 功能

| 模組 | 說明 |
| --- | --- |
| `cogs/status.py` | 每 30 秒輪換「正在玩」狀態 |
| `cogs/welcome.py` | 新成員加入時發送歡迎 Embed（本人可按 🗑️ 刪除） |
| `cogs/role_menu.py` | `/menu-role` 發送遊戲身分組下拉選單（重啟後仍可使用） |
| `cogs/roll_call.py` | `/點名 語音頻道 身分組`：檢查身分組成員是否都在語音頻道，列出並提及未到成員，結果自動存入資料庫 |
| `cogs/roll_call.py` | `/點名紀錄 [編號] [身分組]`：查看最近 10 筆點名紀錄，輸入編號可看該次已到 / 未到名單 |
| `cogs/general.py` | `/ping`、`/help` |

## 專案結構

```
DiscordBOT/
├── main.py           # 進入點：建立 Bot、自動載入 cogs、同步斜線指令
├── config.py         # 所有頻道 / 身分組 ID 等設定
├── database.py       # SQLite 資料庫（點名紀錄），檔案預設存在 data/bot.db
├── cogs/             # 功能模組，新增 .py 檔會自動載入
├── requirements.txt
└── .env.example      # 環境變數範本
```

## 一鍵安裝

已安裝 [Git](https://git-scm.com/downloads) 與 [Python](https://www.python.org/downloads/) 後：

- **Windows**：下載 [`setup.ps1`](setup.ps1)，在檔案所在資料夾開啟 PowerShell 執行
  `powershell -ExecutionPolicy Bypass -File setup.ps1`，完成後雙擊 `start.bat` 啟動。
- **macOS / Linux**：`bash setup.sh`

腳本會下載專案、建立虛擬環境、安裝套件，並詢問 Token 建立 `.env`。

## 快速開始（手動安裝）

1. **建立機器人**：到 [Discord Developer Portal](https://discord.com/developers/applications) → New Application → Bot → Reset Token，複製 Token。
2. **開啟 Intent**：在 Bot 頁面開啟 **Server Members Intent**。
3. **邀請進伺服器**：OAuth2 → URL Generator，勾選 `bot`、`applications.commands`，權限勾選 `Manage Roles`、`Send Messages`、`Embed Links`、`Manage Messages`。
   > 機器人的身分組必須排在要發放的遊戲身分組**之上**，否則無法發放。
4. **安裝與執行**：

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env           # 填入 DISCORD_TOKEN（與 GUILD_ID）
   python main.py
   ```

5. 到 `config.py` 修改歡迎頻道、身分組 ID 與管理員身分組。

## 新增功能

在 `cogs/` 新增一個檔案即可，啟動時會自動載入：

```python
import discord
from discord import app_commands
from discord.ext import commands


class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="打招呼")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"你好，{interaction.user.mention}！")


async def setup(bot):
    await bot.add_cog(Hello(bot))
```

> ⚠️ 絕對不要把 Token 寫進程式碼或上傳到 GitHub，請只放在 `.env`。
