import discord
import asyncio
import itertools
from discord.ext import commands

TOKEN = "MTQ1MTEyOTE3NjMwNzUzNTk0NQ.GKyZ0S.lyqLgEZJ-ZSpnQizBK6spo0873dfY5wLZk6gdI"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

STATUSES = [
    "☭ 革命進行中",
    "☭ 為人民服務",
    "☭ 已被國家徵用",
    "☭ 全世界無產者，聯合起來",
]

@bot.event
async def on_ready():
    print("狀態輪換啟動（Playing）")

    while True:
        for text in STATUSES:
            await bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Game(text)
            )
            await asyncio.sleep(30)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        await ctx.send(
            f"{ctx.author.mention} 你個畜生吉娃娃不要亂用指令好不好啊",
            delete_after=3
        )


# 載入所有 cogs
async def setup():
    await bot.load_extension("menu_role")
    await bot.load_extension("welcome")

import asyncio
asyncio.run(setup())
bot.run(TOKEN)