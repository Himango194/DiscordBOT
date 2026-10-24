import asyncio
import logging
import pathlib

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import Database

log = logging.getLogger("bot")
COGS_DIR = pathlib.Path(__file__).parent / "cogs"


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # 歡迎訊息、人數統計需要
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.db = Database(config.DATABASE_PATH)

    async def setup_hook(self):
        await self.db.connect()
        log.info("已連接資料庫 %s", config.DATABASE_PATH)

        # 自動載入 cogs/ 底下所有模組
        for file in sorted(COGS_DIR.glob("*.py")):
            if file.stem.startswith("_"):
                continue
            await self.load_extension(f"cogs.{file.stem}")
            log.info("已載入模組 %s", file.stem)

        # 同步斜線指令
        if config.GUILD_ID:
            guild = discord.Object(id=config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
        else:
            synced = await self.tree.sync()
        log.info("已同步 %d 個斜線指令", len(synced))

        self.tree.on_error = self.on_app_command_error

    async def close(self):
        await self.db.close()
        await super().close()

    async def on_ready(self):
        log.info("%s 已上線（ID: %s）", self.user, self.user.id)

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, (app_commands.MissingAnyRole, app_commands.CheckFailure)):
            msg = "你個畜生吉娃娃不要亂用指令好不好啊"
        else:
            log.exception("指令執行錯誤", exc_info=error)
            msg = "指令執行時發生錯誤，請稍後再試。"

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


async def main():
    if not config.TOKEN:
        raise SystemExit("找不到 DISCORD_TOKEN，請先建立 .env（參考 .env.example）")

    discord.utils.setup_logging()
    async with Bot() as bot:
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
