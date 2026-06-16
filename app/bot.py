import asyncio
import logging
import discord
from discord.ext import commands
from core.database import get_pool, close_pool
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("hitoribot")

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

    async def on_ready(self):
        log.info(f"HitoriBot V2 online — {self.user} ({self.user.id})")

    async def close(self):
        await close_pool()
        await super().close()


async def on_tree_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    log.error(
        "App command error in /%s (guild=%s channel=%s): %s",
        interaction.command.name if interaction.command else "?",
        interaction.guild_id,
        interaction.channel_id,
        error,
        exc_info=error,
    )
    try:
        if interaction.response.is_done():
            await interaction.followup.send("❌ Ocorreu um erro inesperado.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Ocorreu um erro inesperado.", ephemeral=True)
    except Exception:
        pass


async def main():
    bot = HitoriBot()
    bot.tree.on_error = on_tree_error
    async with bot:
        await bot.start(settings.discord_token)


asyncio.run(main())
