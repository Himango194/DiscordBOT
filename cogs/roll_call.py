from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

MAX_FIELD_LENGTH = 1024  # Embed 欄位字數上限
MAX_EMBED_FIELDS = 25  # Embed 欄位數量上限
MAX_EMBED_TOTAL = 5800  # Embed 總字數上限為 6000，保留一些餘裕
TAIPEI = timezone(timedelta(hours=8))
DATE_FORMATS = ("%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d")


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


def parse_date(text: str) -> datetime | None:
    """解析 2026/10/24、2026-10-24、10/24（今年）等格式，回傳台灣時間當天 00:00。"""
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=TAIPEI)
        except ValueError:
            pass
    for fmt in ("%m/%d", "%m-%d"):
        try:
            parsed = datetime.strptime(f"{datetime.now(TAIPEI).year}/{text}", "%Y/" + fmt)
            return parsed.replace(tzinfo=TAIPEI)
        except ValueError:
            pass
    return None


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

        if absent:
            embed.add_field(
                name="❌ 未到名單", value=join_limited([m.mention for m in absent]), inline=False
            )
            embed.set_footer(text=f"未到同志請立即歸隊！ · 紀錄 #{record_id}")
        else:
            embed.set_footer(text=f"☭ 全員到齊，革命隊伍整裝待發！ ☭ · 紀錄 #{record_id}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="點名紀錄", description="查看點名紀錄（可依日期、身分組篩選，或輸入編號查看詳細名單）")
    @app_commands.rename(date="日期", record_id="編號", role="身分組")
    @app_commands.describe(
        date="查詢某一天的紀錄，例如 2026/10/24 或 10/24",
        record_id="紀錄編號，查看該次詳細名單",
        role="只列出此身分組的紀錄",
    )
    @app_commands.guild_only()
    async def roll_call_history(
        self,
        interaction: discord.Interaction,
        date: str | None = None,
        record_id: int | None = None,
        role: discord.Role | None = None,
    ):
        if record_id is not None:
            await self.send_record_detail(interaction, record_id)
            return

        if date is not None:
            day = parse_date(date)
            if day is None:
                await interaction.response.send_message(
                    f"看不懂日期「{date}」，請使用 2026/10/24 或 10/24 這種格式。", ephemeral=True
                )
                return
            records = await self.bot.db.recent_roll_calls(
                interaction.guild_id,
                limit=MAX_EMBED_FIELDS,
                role_id=role.id if role else None,
                since=day,
                until=day + timedelta(days=1),
            )
            title = f"🗂️ {day:%Y/%m/%d} 的點名紀錄"
            empty_msg = f"{day:%Y/%m/%d} 沒有任何點名紀錄。"
        else:
            records = await self.bot.db.recent_roll_calls(
                interaction.guild_id, limit=10, role_id=role.id if role else None
            )
            title = "🗂️ 最近的點名紀錄"
            empty_msg = "目前沒有任何點名紀錄。"

        if not records:
            await interaction.response.send_message(empty_msg, ephemeral=True)
            return

        absent_names = await self.bot.db.absent_names([r["id"] for r in records])
        footer = "使用 /點名紀錄 編號:<數字> 查看詳細名單"
        fields = [
            (
                f"#{r['id']} · {r['role_name']} @ {r['channel_name']}",
                f"{format_time(r['called_at'])}\n"
                f"應到 `{r['expected']}` · 已到 `{r['present']}` · 未到 `{r['absent']}`\n"
                "❌ 未到：",
                absent_names[r["id"]],
            )
            for r in records
        ]

        # 把剩餘字數平均分給每筆紀錄的未到名單，避免超過 Embed 總字數上限
        used = len(title) + len(footer) + sum(len(name) + len(base) for name, base, _ in fields)
        names_budget = max(20, (MAX_EMBED_TOTAL - used) // len(fields))

        embed = discord.Embed(title=title, color=0xCC0000)
        for name, base, names in fields:
            if not names:
                value = base.replace("❌ 未到：", "✅ 全員到齊")
            else:
                value = base + join_limited(names, min(names_budget, MAX_FIELD_LENGTH - len(base)))
            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(text=footer)
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
