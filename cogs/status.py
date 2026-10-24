import itertools

import discord
from discord.ext import commands, tasks

import config


class Status(commands.Cog):
    """每隔一段時間輪換機器人的「正在玩」狀態。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.statuses = itertools.cycle(config.STATUSES)
        self.rotate.change_interval(seconds=config.STATUS_INTERVAL_SECONDS)
        self.rotate.start()

    def cog_unload(self):
        self.rotate.cancel()

    @tasks.loop(seconds=30)
    async def rotate(self):
        await self.bot.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(next(self.statuses)),
        )

    @rotate.before_loop
    async def before_rotate(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
