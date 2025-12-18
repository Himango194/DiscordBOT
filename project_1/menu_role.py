import discord
import random
from discord.ext import commands

CHANNEL_ID = 1160626478363443424  # 指定頻道

# ======================
# 自訂選項（名稱 + 身分組ID）
# ======================
ROLE_OPTIONS = [
    ("Minecraft", 1121616771925938236, "<:Minecraft:1121616616099156018>"),
    ("APEX", 1075339041517604935, "<:apex:1075339374251741205>"),
    ("Overwatch", 1057244921330941972, "<:Overwatch:1027860652880044052>"),
    ("Valorant", 1075340988366737419, "<:Valorant:1075341351211765770>"),
    ("League of Legends", 1125382270254067833, "<:LeagueofLegends:1125382589402861680>"),
    ("CSGO", 1451245428573081702,"♥️"),
]


IMAGE_POOL = [           #/menu-role 隨機圖片
    "https://i.meee.com.tw/BYigMCq.png",
    "https://i.meee.com.tw/0IsCCnA.png",
    "https://i.meee.com.tw/Fm1SQIk.png",
]

ALLOWED_ROLE_IDS = [
    1072779660347318322,  # 只有該身分組可以使用指令
]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  

bot = commands.Bot(command_prefix="/", intents=intents)

class MenuRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(RoleSelectView())  # Persistent View

    @commands.command(name="menu-role")
    @commands.has_any_role(1072779660347318322)
    async def menu_role(self, ctx):
        await send_role_menu(ctx.channel)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(MenuRole(bot))
    
# ======================
# Select Menu
# ======================
class RoleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=name,
                value=str(role_id),
                emoji=emoji
            )
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
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message(
                "這個身分組不存在，問一下你的管理員在幹嘛。",
                ephemeral=True
            )
            return

        member = interaction.user

        if role in member.roles:
            await member.remove_roles(role)
            msg = f"您已移除 ❮{role.mention}❯ 再次點選即可領取：("
        else:
            await member.add_roles(role)
            msg = f"您已領取 ❮{role.mention}❯ 再次點選即可移除：D"

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

        removed_roles = []

        for _, role_id, _ in ROLE_OPTIONS:
            role = guild.get_role(role_id)
            if role and role in member.roles:
                removed_roles.append(role)
                await member.remove_roles(role)

        if not removed_roles:
            await interaction.response.send_message(
                "你目前沒有任何可移除的遊戲身分組。",
                ephemeral=True
            )
            return
        removed_mentions = " ".join(role.mention for role in removed_roles)

        await interaction.response.send_message(
             f"🧹 已移除以下身分組：\n{removed_mentions}",
             ephemeral=True
    )


# ======================
# View
# ======================
class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleSelect())
        self.add_item(RemoveAllRolesButton()) 


# ======================
# Bot ready 時送出 Embed
# ======================
@bot.event
async def send_role_menu(channel: discord.TextChannel):
    embed = discord.Embed(
        title=" ",
        description=" ",
        color=0xFFFF13
    )

    embed.set_author(
        name="中華蘇維埃共和國",
        icon_url="https://i.meee.com.tw/vPGC0xr.png",
    )

    embed.set_image(
    url=random.choice(IMAGE_POOL)
    )

    embed.set_footer(
        text="〖點選下方選單領取遊戲身分組〗"
    )

    await channel.send(
        embed=embed,
        view=RoleSelectView()
    )

    print("身分組選單已發送")

@bot.command(name="menu-role")
@commands.has_any_role(*ALLOWED_ROLE_IDS)  # 不想給所有人亂叫就留著
async def menu_role(ctx: commands.Context):
    await send_role_menu(ctx.channel)
    await ctx.message.delete()  # 可選：刪掉指令訊息，畫面比較乾淨

@menu_role.error
async def menu_role_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(
            f"{ctx.author.mention} ⚠️ 你沒有這個指令的使用權限。",
            delete_after=3
        )


@bot.event
async def on_ready():
    bot.add_view(RoleSelectView())  # ⭐ 讓舊選單復活
    print(f"{bot.user} 已上線，Persistent View 已註冊")
    print(f"{bot.user} 已上線")

