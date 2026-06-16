import discord
from discord.ext import commands
from discord import app_commands
from repositories.guild import get_settings


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rule-set", description="Set the server rules")
    @app_commands.default_permissions(administrator=True)
    async def rule_set(self, interaction: discord.Interaction, *, rules: str):
        await self.bot.pool.execute(
            "UPDATE guild_settings SET rules_text = $1 WHERE guild_id = $2",
            rules, interaction.guild.id,
        )
        await interaction.response.send_message("✅ Regras atualizadas.", ephemeral=True)

    @app_commands.command(name="rule-clear", description="Clear the server rules")
    @app_commands.default_permissions(administrator=True)
    async def rule_clear(self, interaction: discord.Interaction):
        await self.bot.pool.execute(
            "UPDATE guild_settings SET rules_text = NULL WHERE guild_id = $1",
            interaction.guild.id,
        )
        await interaction.response.send_message("✅ Regras removidas.", ephemeral=True)

    @app_commands.command(name="rules", description="Show the server rules")
    async def rules(self, interaction: discord.Interaction):
        settings = await get_settings(self.bot.pool, interaction.guild.id)
        rules_text = settings["rules_text"] if settings and settings["rules_text"] else "Nenhuma regra cadastrada."
        embed = discord.Embed(title="📋 Regras do Servidor", description=rules_text, color=discord.Color.gold())
        try:
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("📬 Regras enviadas no privado.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Rules(bot))
