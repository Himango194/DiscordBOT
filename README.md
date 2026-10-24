# DiscordBOT

使用 [discord.py](https://discordpy.readthedocs.io/) 2.x 打造的 Discord 機器人，採用斜線指令與 Cog 模組化架構。

## 功能

| 模組 | 說明 |
| --- | --- |
| `cogs/status.py` | 每 30 秒輪換「正在玩」狀態 |
| `cogs/welcome.py` | 新成員加入時發送歡迎 Embed（本人可按 🗑️ 刪除） |
| `cogs/role_menu.py` | `/menu-role` 發送遊戲身分組下拉選單（重啟後仍可使用） |
| `cogs/general.py` | `/ping`、`/help` |

## 專案結構

```
DiscordBOT/
├── main.py           # 進入點：建立 Bot、自動載入 cogs、同步斜線指令
├── config.py         # 所有頻道 / 身分組 ID 等設定
├── cogs/             # 功能模組，新增 .py 檔會自動載入
├── requirements.txt
└── .env.example      # 環境變數範本
```

## 快速開始

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
