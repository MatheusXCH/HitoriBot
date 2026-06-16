import discord
from discord.ext import commands
from discord import app_commands
from config import settings


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _is_owner(self, user_id: int) -> bool:
        return user_id == settings.discord_owner_id

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Pong! `{round(self.bot.latency * 1000)}ms`", ephemeral=True
        )

    @app_commands.command(name="module-load", description="Load a cog module [owner only]")
    async def module_load(self, interaction: discord.Interaction, module: str):
        if not self._is_owner(interaction.user.id):
            return await interaction.response.send_message("Not authorized.", ephemeral=True)
        try:
            await self.bot.load_extension(f"cogs.{module}")
            await self.bot.tree.sync()
            await interaction.response.send_message(f"✅ `{module}` loaded.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ `{e}`", ephemeral=True)

    @app_commands.command(name="module-unload", description="Unload a cog module [owner only]")
    async def module_unload(self, interaction: discord.Interaction, module: str):
        if not self._is_owner(interaction.user.id):
            return await interaction.response.send_message("Not authorized.", ephemeral=True)
        try:
            await self.bot.unload_extension(f"cogs.{module}")
            await interaction.response.send_message(f"✅ `{module}` unloaded.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ `{e}`", ephemeral=True)

    @app_commands.command(name="module-reload", description="Reload a cog module [owner only]")
    async def module_reload(self, interaction: discord.Interaction, module: str):
        if not self._is_owner(interaction.user.id):
            return await interaction.response.send_message("Not authorized.", ephemeral=True)
        try:
            await self.bot.reload_extension(f"cogs.{module}")
            await self.bot.tree.sync()
            await interaction.response.send_message(f"✅ `{module}` reloaded.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ `{e}`", ephemeral=True)

    @app_commands.command(name="get-guilds", description="List all guilds the bot is in [owner only]")
    async def get_guilds(self, interaction: discord.Interaction):
        if not self._is_owner(interaction.user.id):
            return await interaction.response.send_message("Not authorized.", ephemeral=True)
        lines = [
            f"`{g.id}` — **{g.name}** ({g.member_count} members)"
            for g in self.bot.guilds
        ]
        await interaction.response.send_message("\n".join(lines) or "No guilds.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
