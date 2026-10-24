import random

import discord
from discord import app_commands
from discord.ext import commands

# ======================
# 自訂選項（名稱 + 身分組ID + 表情）
# ======================
ROLE_OPTIONS = [
    ("Minecraft", 1121616771925938236, "<:Minecraft:1121616616099156018>"),
    ("APEX", 1075339041517604935, "<:apex:1075339374251741205>"),
    ("Overwatch", 1057244921330941972, "<:Overwatch:1027860652880044052>"),
    ("Valorant", 1075340988366737419, "<:Valorant:1075341351211765770>"),
    ("League of Legends", 1125382270254067833, "<:LeagueofLegends:1125382589402861680>"),
    ("CSGO", 1451245428573081702, "♥️"),
]

IMAGE_POOL = [  # /menu-role 隨機圖片
    "https://i.meee.com.tw/BYigMCq.png",
    "https://i.meee.com.tw/0IsCCnA.png",
    "https://i.meee.com.tw/Fm1SQIk.png",
]

ALLOWED_ROLE_IDS = [
    1072779660347318322,  # 只有該身分組可以使用指令
]


# ======================
# Select Menu
# ======================
class RoleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=str(role_id), emoji=emoji)
            for name, role_id, emoji in ROLE_OPTIONS
        ]

        super().__init__(
            placeholder="選擇要領取 / 移除的身分組",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="role_select_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(int(self.values[0]))

        if not role:
            await interaction.response.send_message(
                "這個身分組不存在，問一下你的管理員在幹嘛。",
                ephemeral=True
            )
            return

        member = interaction.user

        try:
            if role in member.roles:
                await member.remove_roles(role)
                msg = f"您已移除 ❮{role.mention}❯ 再次點選即可領取：("
            else:
                await member.add_roles(role)
                msg = f"您已領取 ❮{role.mention}❯ 再次點選即可移除：D"
        except discord.Forbidden:
            msg = "Bot 權限不足，請把 Bot 的身分組拉到遊戲身分組上面。"

        await interaction.response.send_message(msg, ephemeral=True)


class RemoveAllRolesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="移除所有遊戲身分組",
            style=discord.ButtonStyle.danger,
            emoji="🧹",
            custom_id="remove_all_roles_button"
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild

        removed_roles = [
            role for _, role_id, _ in ROLE_OPTIONS
            if (role := guild.get_role(role_id)) and role in member.roles
        ]

        if not removed_roles:
            await interaction.response.send_message(
                "你目前沒有任何可移除的遊戲身分組。",
                ephemeral=True
            )
            return

        await member.remove_roles(*removed_roles)
        removed_mentions = " ".join(role.mention for role in removed_roles)

        await interaction.response.send_message(
            f"🧹 已移除以下身分組：\n{removed_mentions}",
            ephemeral=True
        )


# ======================
# View（Persistent，Bot 重開後舊選單仍可使用）
# ======================
class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleSelect())
        self.add_item(RemoveAllRolesButton())


async def send_role_menu(channel: discord.abc.Messageable):
    embed = discord.Embed(color=0xFFFF13)

    embed.set_author(
        name="中華蘇維埃共和國",
        icon_url="https://i.meee.com.tw/vPGC0xr.png",
    )
    embed.set_image(url=random.choice(IMAGE_POOL))
    embed.set_footer(text="〖點選下方選單領取遊戲身分組〗")

    await channel.send(embed=embed, view=RoleSelectView())
    print("身分組選單已發送")


class MenuRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(RoleSelectView())  # ⭐ 讓舊選單復活

    # 文字指令：!menu-role
    @commands.command(name="menu-role")
    @commands.has_any_role(*ALLOWED_ROLE_IDS)
    async def menu_role(self, ctx: commands.Context):
        await send_role_menu(ctx.channel)
        try:
            await ctx.message.delete()  # 刪掉指令訊息，畫面比較乾淨
        except discord.Forbidden:
            pass

    # 斜線指令：/menu-role
    @app_commands.command(name="menu-role", description="在此頻道發送遊戲身分組選單")
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(*ALLOWED_ROLE_IDS)
    async def menu_role_slash(self, interaction: discord.Interaction):
        await send_role_menu(interaction.channel)
        await interaction.response.send_message("身分組選單已發送 ✅", ephemeral=True)


async def setup(bot):
    await bot.add_cog(MenuRole(bot))
