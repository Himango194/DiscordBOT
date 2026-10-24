# DiscordBOT

使用 [discord.py](https://discordpy.readthedocs.io/) 製作的 Discord Bot。

## 功能

| 功能 | 說明 |
| --- | --- |
| 歡迎訊息 | 新成員加入時，在歡迎頻道發送 Embed（附本人可刪除的 🗑️ 按鈕） |
| 身分組選單 | `/menu-role` 或 `!menu-role` 發送遊戲身分組下拉選單，Bot 重開後舊選單仍可用 |
| 狀態輪換 | 每 30 秒切換一次「正在玩」狀態 |
| `/ping` | 查看延遲 |
| `/userinfo [成員]` | 查看成員資訊 |
| `/clear <數量>` | 刪除最近訊息（需「管理訊息」權限） |
| `/help` | 指令列表 |

## 檔案結構

```
project_1/
├── bot.py         # 主程式：建立 Bot、載入 cogs、狀態輪換、錯誤處理
├── welcome.py     # 歡迎訊息（改 WELCOME_CHANNEL_ID）
├── menu_role.py   # 身分組選單（改 ROLE_OPTIONS / ALLOWED_ROLE_IDS）
├── general.py     # 一般指令
├── requirements.txt
└── .env.example
```

## 1. 建立 Bot

1. 到 [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**
2. 左側 **Bot** → **Reset Token**，複製 Token
3. 同一頁開啟 **Privileged Gateway Intents** 中的 **Server Members Intent** 與 **Message Content Intent**
4. 左側 **OAuth2 → URL Generator**：Scopes 勾 `bot`、`applications.commands`；
   權限勾 `Manage Roles`、`Manage Messages`、`Send Messages`、`Embed Links`、`Read Message History`，用產生的網址邀請 Bot
5. 伺服器設定中，把 **Bot 的身分組拉到遊戲身分組上面**，否則無法發放身分組

## 2. 本機執行

```bash
cd project_1
pip install -r requirements.txt
cp .env.example .env      # 然後把 Token 填進 .env
python bot.py
```

## 3. 部署到 Render

`render.yaml` 已設定好一個 Background Worker：在 Render 選 **New → Blueprint** 連結此 repo，
並在環境變數 `DISCORD_TOKEN` 填入 Token 即可。

> ⚠️ Token 只能放在 `.env` 或環境變數，**不要寫進程式碼或上傳到 GitHub**。
