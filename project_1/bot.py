import os
import itertools

import discord
from discord.ext import commands, tasks

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Token 從環境變數讀取，千萬不要寫在程式碼裡
TOKEN = os.getenv("DISCORD_TOKEN")

STATUSES = itertools.cycle([
    "☭ 革命進行中",
    "☭ 為人民服務",
    "☭ 已被國家徵用",
    "☭ 全世界無產者，聯合起來",
])

EXTENSIONS = ["menu_role", "welcome", "general"]


class SovietBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # 載入所有 cogs
        for ext in EXTENSIONS:
            await self.load_extension(ext)

        # 同步斜線指令（/ping、/menu-role ...）
        synced = await self.tree.sync()
        print(f"已同步 {len(synced)} 個斜線指令")

        rotate_status.start()

    async def on_ready(self):
        print(f"{self.user} 已上線（ID: {self.user.id}）")


bot = SovietBot()


@tasks.loop(seconds=30)
async def rotate_status():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(next(STATUSES))
    )


@rotate_status.before_loop
async def before_rotate_status():
    await bot.wait_until_ready()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.MissingAnyRole, commands.MissingPermissions)):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        await ctx.send(
            f"{ctx.author.mention} 你個畜生吉娃娃不要亂用指令好不好啊",
            delete_after=3
        )
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        raise error


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, (discord.app_commands.MissingAnyRole, discord.app_commands.MissingPermissions)):
        await interaction.response.send_message(
            "你個畜生吉娃娃不要亂用指令好不好啊", ephemeral=True
        )
    else:
        raise error


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("找不到 DISCORD_TOKEN，請在 .env 或環境變數中設定")
    bot.run(TOKEN)
