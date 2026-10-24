import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    """通用指令。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="查看機器人延遲")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong！延遲 `{round(self.bot.latency * 1000)} ms`", ephemeral=True
        )

    @app_commands.command(name="help", description="列出所有指令")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 指令列表", color=0xCC0000)
        for cmd in self.bot.tree.get_commands():
            embed.add_field(name=f"/{cmd.name}", value=cmd.description or "—", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
