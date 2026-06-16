import asyncio
import discord
from discord.ext import commands
from core.database import get_pool, close_pool
from config import settings

INITIAL_COGS = [
    "cogs.admin",
    "cogs.events",
    "cogs.moderation",
    "cogs.automod",
    "cogs.rules",
    "cogs.games",
    "cogs.anime",
    "cogs.minigames",
    "cogs.stickers",
    "cogs.soundboard",
    "cogs.playlist",
    "cogs.ai",
]


class HitoriBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.pool = await get_pool()
        for cog in INITIAL_COGS:
            await self.load_extension(cog)
        await self.tree.sync()

    async def close(self):
        await close_pool()
        await super().close()

    async def on_ready(self):
        print(f"HitoriBot V2 online — {self.user} ({self.user.id})")


async def main():
    async with HitoriBot() as bot:
        await bot.start(settings.discord_token)


asyncio.run(main())
