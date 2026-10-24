import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="查看 Bot 延遲")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong！延遲 `{round(self.bot.latency * 1000)} ms`"
        )

    @app_commands.command(name="userinfo", description="查看成員資訊")
    @app_commands.guild_only()
    @app_commands.describe(member="要查看的成員（不填則為自己）")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user

        embed = discord.Embed(title=f"同志檔案 · {member.display_name}", color=0xCC0000)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=False)
        embed.add_field(name="📅 帳號建立", value=discord.utils.format_dt(member.created_at, "D"), inline=True)
        if member.joined_at:
            embed.add_field(name="🕒 入黨時間", value=discord.utils.format_dt(member.joined_at, "D"), inline=True)

        roles = [r.mention for r in reversed(member.roles) if r != interaction.guild.default_role]
        embed.add_field(name=f"🎖️ 身分組（{len(roles)}）", value=" ".join(roles[:20]) or "無", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="刪除最近的訊息")
    @app_commands.guild_only()
    @app_commands.describe(amount="要刪除的訊息數量（1-100）")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 已刪除 {len(deleted)} 則訊息", ephemeral=True)

    @app_commands.command(name="help", description="顯示指令列表")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="☭ 指令列表 ☭", color=0xCC0000)
        embed.add_field(name="/ping", value="查看 Bot 延遲", inline=False)
        embed.add_field(name="/userinfo [成員]", value="查看成員資訊", inline=False)
        embed.add_field(name="/clear <數量>", value="刪除最近的訊息（需管理訊息權限）", inline=False)
        embed.add_field(name="/menu-role", value="發送遊戲身分組選單（限指定身分組）", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(General(bot))
