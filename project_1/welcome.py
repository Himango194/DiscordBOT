import discord
from discord.ext import commands
from datetime import timezone, timedelta

WELCOME_CHANNEL_ID = 1352133950998450388  # 換成你的歡迎頻道

class DeleteWelcomeView(discord.ui.View):
    def __init__(self, target_user_id: int):
        super().__init__(timeout=300)  # 5 分鐘後按鈕自動失效
        self.target_user_id = target_user_id

    @discord.ui.button(
        label=" ",
        style=discord.ButtonStyle.secondary,
        emoji="🗑️"
    )
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 只允許被歡迎的本人刪除
        if interaction.user.id != self.target_user_id:
            await interaction.response.send_message(
                "關你屁事啊 管好你自己",
                ephemeral=True
            )
            return

        await interaction.message.delete()


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
        title="☭ 同志，歡迎加入中華蘇維埃共和國 ☭",
        description=(
        f"🟥 **新同志 {member.mention} 已正式報到！** 🟥\n\n"
        "你已踏入革命的集體。\n"
        "個人將不再孤單，意志將融入人民。\n\n"
        "請遵循黨的指示，完成以下程序，\n"
        "以確保共和國秩序與榮耀得以延續。"
    ),
    color=0xCC0000  # 深紅，比金色更蘇維埃
)

        # 左上角：新成員名稱 + 頭像
        embed.set_author(
        name="人民委員會 · 成員登記處",
        icon_url=member.display_avatar.url
)

        # 右側大頭像
        embed.set_thumbnail(
        url=member.display_avatar.url
)

# 革命指示
        embed.add_field(
        name="📜 革 命 指 令",
        value=(
        "▫️ 閱讀並遵守《伺服器紀律守則》\n"
        "▫️ 前往<#1451266846593515610>領取勞動編制\n"
        "▫️ 積極參與集體討論與語音會議\n\n"
        "**不服從者，將被歷史遺忘。**"
    ),
    inline=False
)

        human_count = sum(1 for m in member.guild.members if not m.bot)
        embed.add_field(
        name="👥 人民總數",
        value=f"`{human_count} 位同志`",
        inline=True
)
        join_time = member.joined_at.astimezone(
        timezone(timedelta(hours=8))
        ).strftime("`%Y.%m.%d %p %I:%M`")
        embed.add_field(
        name="🕒 入黨時間",
        value=join_time,
        inline=True
)

        # 底部
        embed.set_footer(
        text="☭ 全世界無產者，聯合起來！ ☭",
        icon_url=member.guild.icon.url if member.guild.icon else None
)
        await channel.send(
         embed=embed,
         view=DeleteWelcomeView(member.id)
)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
