import discord
from discord import app_commands
from discord.ext import commands

import config

MAX_FIELD_LENGTH = 1024  # Embed 欄位字數上限


def join_limited(items: list[str], limit: int = MAX_FIELD_LENGTH) -> str:
    """把名單串起來，超過欄位上限時以「…等 N 人」結尾。"""
    if not items:
        return "—"
    text = ""
    suffix = f"…等 {len(items)} 人"
    for item in items:
        if len(text) + len(item) + 1 + len(suffix) > limit:
            return text + suffix
        text += item + " "
    return text


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
        present = [m for m in expected if m.id in present_ids]
        absent = [m for m in expected if m.id not in present_ids]

        embed = discord.Embed(
            title="📋 點名結果",
            description=f"頻道：{channel.mention}\n身分組：{role.mention}",
            color=0x2ECC71 if not absent else 0xCC0000,
        )
        embed.add_field(name="✅ 已到", value=f"`{len(present)} 人`", inline=True)
        embed.add_field(name="❌ 未到", value=f"`{len(absent)} 人`", inline=True)
        embed.add_field(name="👥 應到", value=f"`{len(expected)} 人`", inline=True)

        if absent:
            embed.add_field(
                name="❌ 未到名單", value=join_limited([m.mention for m in absent]), inline=False
            )
            embed.set_footer(text="未到同志請立即歸隊！")
        else:
            embed.set_footer(text="☭ 全員到齊，革命隊伍整裝待發！ ☭")

        # 先回覆（Discord 要求 3 秒內回應），再發送紀錄
        await interaction.response.send_message(embed=embed, ephemeral=True)
        warning = await self.send_log(interaction, channel, role, present, absent)
        if warning:
            await interaction.followup.send(warning, ephemeral=True)

    async def send_log(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel | discord.StageChannel,
        role: discord.Role,
        present: list[discord.Member],
        absent: list[discord.Member],
    ) -> str | None:
        """把點名結果發送到紀錄頻道，失敗時回傳要告知使用者的警告訊息。"""
        log_channel = self.bot.get_channel(config.ROLL_CALL_LOG_CHANNEL_ID)
        if log_channel is None:
            return "⚠️ 尚未設定點名紀錄頻道，這次結果沒有被紀錄。"

        embed = discord.Embed(
            title="🗂️ 點名紀錄",
            description=(
                f"時間：{discord.utils.format_dt(discord.utils.utcnow(), 'f')}\n"
                f"頻道：{channel.mention}\n"
                f"身分組：{role.mention}\n"
                f"點名者：{interaction.user.mention}"
            ),
            color=0x2ECC71 if not absent else 0xCC0000,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="👥 應到", value=f"`{len(present) + len(absent)} 人`", inline=True)
        embed.add_field(name="✅ 已到", value=f"`{len(present)} 人`", inline=True)
        embed.add_field(name="❌ 未到", value=f"`{len(absent)} 人`", inline=True)
        embed.add_field(
            name="❌ 未到名單", value=join_limited([m.mention for m in absent]), inline=False
        )

        try:
            # Embed 內的提及不會通知任何人，只會顯示名字
            await log_channel.send(embed=embed)
        except discord.HTTPException:
            return f"⚠️ 無法發送到紀錄頻道 {log_channel.mention}，請確認機器人有發言權限。"
        return None


async def setup(bot: commands.Bot):
    await bot.add_cog(RollCall(bot))
