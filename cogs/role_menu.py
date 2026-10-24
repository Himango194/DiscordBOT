import random

import discord
from discord import app_commands
from discord.ext import commands

import config


class RoleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=str(role_id), emoji=emoji)
            for name, role_id, emoji in config.ROLE_OPTIONS
        ]
        super().__init__(
            placeholder="選擇要領取 / 移除的身分組",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="role_select_menu",
        )

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(int(self.values[0]))
        if role is None:
            await interaction.response.send_message(
                "這個身分組不存在，問一下你的管理員在幹嘛。", ephemeral=True
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
            custom_id="remove_all_roles_button",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        option_ids = {role_id for _, role_id, _ in config.ROLE_OPTIONS}
        removed = [role for role in member.roles if role.id in option_ids]

        if not removed:
            await interaction.response.send_message(
                "你目前沒有任何可移除的遊戲身分組。", ephemeral=True
            )
            return

        await member.remove_roles(*removed)
        mentions = " ".join(role.mention for role in removed)
        await interaction.response.send_message(f"🧹 已移除以下身分組：\n{mentions}", ephemeral=True)


class RoleSelectView(discord.ui.View):
    """Persistent View：機器人重啟後舊的選單依然可以使用。"""

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleSelect())
        self.add_item(RemoveAllRolesButton())


def build_role_menu_embed() -> discord.Embed:
    embed = discord.Embed(color=0xFFFF13)
    embed.set_author(name="中華蘇維埃共和國", icon_url=config.ROLE_MENU_AUTHOR_ICON)
    embed.set_image(url=random.choice(config.ROLE_MENU_IMAGES))
    embed.set_footer(text="〖點選下方選單領取遊戲身分組〗")
    return embed


class RoleMenu(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(RoleSelectView())

    @app_commands.command(name="menu-role", description="在此頻道發送遊戲身分組選單")
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(*config.ADMIN_ROLE_IDS)
    async def menu_role(self, interaction: discord.Interaction):
        await interaction.channel.send(embed=build_role_menu_embed(), view=RoleSelectView())
        await interaction.response.send_message("✅ 身分組選單已發送", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RoleMenu(bot))
