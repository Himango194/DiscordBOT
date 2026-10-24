import discord
from discord import app_commands
from discord.ext import commands

MAX_CONTENT_LENGTH = 2000  # Discord 單則訊息字數上限


def chunk_mentions(members: list[discord.Member]) -> list[str]:
    """把提及字串切成多段，避免超過單則訊息上限。"""
    chunks, current = [], ""
    for member in members:
        mention = member.mention + " "
        if len(current) + len(mention) > MAX_CONTENT_LENGTH:
            chunks.append(current)
            current = ""
        current += mention
    if current:
        chunks.append(current)
    return chunks


class RollCall(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="點名", description="檢查指定身分組的成員是否都在語音頻道內")
    @app_commands.rename(channel="語音頻道", role="身分組")
    @app_commands.describe(channel="要點名的語音頻道", role="要點名的身分組")
    @app_commands.guild_only()
    async def roll_call(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel | discord.StageChannel,
        role: discord.Role,
    ):
        expected = [m for m in role.members if not m.bot]
        if not expected:
            await interaction.response.send_message(
                f"{role.mention} 底下沒有任何成員，無從點名。", ephemeral=True
            )
            return

        present_ids = {m.id for m in channel.members}
        absent = [m for m in expected if m.id not in present_ids]
        present_count = len(expected) - len(absent)

        embed = discord.Embed(
            title="📋 點名結果",
            description=f"頻道：{channel.mention}\n身分組：{role.mention}",
            color=0x2ECC71 if not absent else 0xCC0000,
        )
        embed.add_field(name="✅ 已到", value=f"`{present_count} 人`", inline=True)
        embed.add_field(name="❌ 未到", value=f"`{len(absent)} 人`", inline=True)
        embed.add_field(name="👥 應到", value=f"`{len(expected)} 人`", inline=True)

        if not absent:
            embed.set_footer(text="☭ 全員到齊，革命隊伍整裝待發！ ☭")
            await interaction.response.send_message(embed=embed)
            return

        # Embed 內的提及不會通知，所以未到名單另外用訊息內容提及
        embed.set_footer(text="未到同志請立即歸隊！")
        await interaction.response.send_message(embed=embed)
        for chunk in chunk_mentions(absent):
            await interaction.followup.send(
                chunk, allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False)
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(RollCall(bot))
