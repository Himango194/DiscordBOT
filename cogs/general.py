import discord
from discord import app_commands
from discord.ext import commands

HELP_SECTIONS = [
    (
        "📋 點名",
        "**`/點名 語音頻道 身分組`**\n"
        "檢查該身分組成員是否都在語音頻道內，顯示已到 / 未到 / 應到人數，"
        "並列出未到成員（不計入 Bot），同時將結果紀錄發送到點名紀錄頻道。",
    ),
    (
        "🎮 身分組",
        "**`/menu-role`**（限管理員）\n"
        "在此頻道發送遊戲身分組選單：下拉選單點一下領取、再點一下移除，"
        "🧹 按鈕一次移除所有遊戲身分組。",
    ),
    (
        "⚙️ 通用",
        "**`/ping`** 查看機器人延遲\n"
        "**`/help`** 顯示這份說明",
    ),
    (
        "🤖 自動功能",
        "👋 新成員加入時發送歡迎訊息（本人可按 🗑️ 刪除）\n"
        "🔄 每 30 秒輪換機器人狀態",
    ),
]


class General(commands.Cog):
    """通用指令。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="查看機器人延遲")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong！延遲 `{round(self.bot.latency * 1000)} ms`", ephemeral=True
        )

    @app_commands.command(name="help", description="列出所有指令與功能說明")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 指令說明",
            description="輸入 `/` 即可看到所有指令，選擇後依提示填入參數。\n所有指令的結果只有你自己看得到。",
            color=0xCC0000,
        )
        for name, value in HELP_SECTIONS:
            embed.add_field(name=name, value=value, inline=False)
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="☭ 全世界無產者，聯合起來！ ☭")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
