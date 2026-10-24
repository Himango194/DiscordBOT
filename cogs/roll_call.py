from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

MAX_CONTENT_LENGTH = 2000  # Discord 單則訊息字數上限
MAX_FIELD_LENGTH = 1024  # Embed 欄位字數上限


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


def join_limited(items: list[str], limit: int = MAX_FIELD_LENGTH) -> str:
    """把名單串起來，超過欄位上限時以「…等 N 人」結尾。"""
    if not items:
        return "—"
    text = ""
    for i, item in enumerate(items):
        suffix = f"…等 {len(items)} 人"
        if len(text) + len(item) + 1 + len(suffix) > limit:
            return text + suffix
        text += item + " "
    return text


def format_time(iso: str) -> str:
    # Discord 時間戳記會依照每個人的時區顯示
    return discord.utils.format_dt(datetime.fromisoformat(iso), "f")


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

        record_id = await self.bot.db.add_roll_call(
            guild_id=interaction.guild_id,
            channel_id=channel.id,
            channel_name=channel.name,
            role_id=role.id,
            role_name=role.name,
            called_by=interaction.user.id,
            present=[(m.id, m.display_name) for m in present],
            absent=[(m.id, m.display_name) for m in absent],
        )

        embed = discord.Embed(
            title="📋 點名結果",
            description=f"頻道：{channel.mention}\n身分組：{role.mention}",
            color=0x2ECC71 if not absent else 0xCC0000,
        )
        embed.add_field(name="✅ 已到", value=f"`{len(present)} 人`", inline=True)
        embed.add_field(name="❌ 未到", value=f"`{len(absent)} 人`", inline=True)
        embed.add_field(name="👥 應到", value=f"`{len(expected)} 人`", inline=True)

        if not absent:
            embed.set_footer(text=f"☭ 全員到齊，革命隊伍整裝待發！ ☭ · 紀錄 #{record_id}")
            await interaction.response.send_message(embed=embed)
            return

        # Embed 內的提及不會通知，所以未到名單另外用訊息內容提及
        embed.set_footer(text=f"未到同志請立即歸隊！ · 紀錄 #{record_id}")
        await interaction.response.send_message(embed=embed)
        for chunk in chunk_mentions(absent):
            await interaction.followup.send(
                chunk, allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False)
            )

    @app_commands.command(name="點名紀錄", description="查看點名紀錄（輸入編號可查看該次詳細名單）")
    @app_commands.rename(record_id="編號", role="身分組")
    @app_commands.describe(record_id="紀錄編號，留空則列出最近 10 筆", role="只列出此身分組的紀錄")
    @app_commands.guild_only()
    async def roll_call_history(
        self,
        interaction: discord.Interaction,
        record_id: int | None = None,
        role: discord.Role | None = None,
    ):
        if record_id is not None:
            await self.send_record_detail(interaction, record_id)
            return

        records = await self.bot.db.recent_roll_calls(
            interaction.guild_id, limit=10, role_id=role.id if role else None
        )
        if not records:
            await interaction.response.send_message("目前沒有任何點名紀錄。", ephemeral=True)
            return

        embed = discord.Embed(title="🗂️ 最近的點名紀錄", color=0xCC0000)
        for r in records:
            embed.add_field(
                name=f"#{r['id']} · {r['role_name']} @ {r['channel_name']}",
                value=(
                    f"{format_time(r['called_at'])}\n"
                    f"應到 `{r['expected']}` · 已到 `{r['present']}` · 未到 `{r['absent']}`"
                ),
                inline=False,
            )
        embed.set_footer(text="使用 /點名紀錄 編號:<數字> 查看詳細名單")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def send_record_detail(self, interaction: discord.Interaction, record_id: int):
        record, members = await self.bot.db.get_roll_call(interaction.guild_id, record_id)
        if record is None:
            await interaction.response.send_message(f"找不到紀錄 #{record_id}。", ephemeral=True)
            return

        present = [m["display_name"] for m in members if m["is_present"]]
        absent = [m["display_name"] for m in members if not m["is_present"]]

        embed = discord.Embed(
            title=f"📋 點名紀錄 #{record['id']}",
            description=(
                f"時間：{format_time(record['called_at'])}\n"
                f"頻道：<#{record['channel_id']}>（{record['channel_name']}）\n"
                f"身分組：<@&{record['role_id']}>（{record['role_name']}）\n"
                f"點名者：<@{record['called_by']}>"
            ),
            color=0x2ECC71 if not absent else 0xCC0000,
        )
        embed.add_field(name="👥 應到", value=f"`{record['expected']} 人`", inline=True)
        embed.add_field(name="✅ 已到", value=f"`{record['present']} 人`", inline=True)
        embed.add_field(name="❌ 未到", value=f"`{record['absent']} 人`", inline=True)
        embed.add_field(name="❌ 未到名單", value=join_limited(absent), inline=False)
        embed.add_field(name="✅ 已到名單", value=join_limited(present), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RollCall(bot))
