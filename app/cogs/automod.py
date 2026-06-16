import discord
from discord.ext import commands
from discord import app_commands
from repositories.guild import get_settings


def contains_bad_word(message: str, bad_words: list[str]) -> bool:
    normalized = message.lower()
    return any(word.lower() in normalized for word in bad_words)


class Automod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        settings = await get_settings(self.bot.pool, message.guild.id)
        if not settings or not settings["bad_words"]:
            return
        if contains_bad_word(message.content, settings["bad_words"]):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, essa mensagem foi removida por conter conteúdo proibido.",
                    delete_after=5,
                )
            except discord.Forbidden:
                pass

    @app_commands.command(name="badword-add", description="Add words to the bad words filter")
    @app_commands.default_permissions(manage_messages=True)
    async def badword_add(self, interaction: discord.Interaction, words: str):
        new_words = [w.strip().lower() for w in words.split(",") if w.strip()]
        settings = await get_settings(self.bot.pool, interaction.guild.id)
        current = list(settings["bad_words"]) if settings else []
        combined = list(set(current + new_words))
        await self.bot.pool.execute(
            "UPDATE guild_settings SET bad_words = $1 WHERE guild_id = $2",
            combined, interaction.guild.id,
        )
        await interaction.response.send_message(f"✅ {len(new_words)} palavra(s) adicionada(s) ao filtro.", ephemeral=True)

    @app_commands.command(name="badword-remove", description="Remove words from the bad words filter")
    @app_commands.default_permissions(manage_messages=True)
    async def badword_remove(self, interaction: discord.Interaction, words: str):
        to_remove = {w.strip().lower() for w in words.split(",") if w.strip()}
        settings = await get_settings(self.bot.pool, interaction.guild.id)
        current = list(settings["bad_words"]) if settings else []
        updated = [w for w in current if w not in to_remove]
        await self.bot.pool.execute(
            "UPDATE guild_settings SET bad_words = $1 WHERE guild_id = $2",
            updated, interaction.guild.id,
        )
        await interaction.response.send_message("✅ Palavra(s) removida(s) do filtro.", ephemeral=True)

    @app_commands.command(name="badword-list", description="List all bad words for this server")
    @app_commands.default_permissions(manage_messages=True)
    async def badword_list(self, interaction: discord.Interaction):
        settings = await get_settings(self.bot.pool, interaction.guild.id)
        words = settings["bad_words"] if settings else []
        embed = discord.Embed(
            title="Palavras proibidas",
            description=", ".join(f"`{w}`" for w in words) if words else "Nenhuma palavra cadastrada.",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="badword-reset", description="Clear all bad words for this server")
    @app_commands.default_permissions(manage_messages=True)
    async def badword_reset(self, interaction: discord.Interaction):
        await self.bot.pool.execute(
            "UPDATE guild_settings SET bad_words = '{}' WHERE guild_id = $1",
            interaction.guild.id,
        )
        await interaction.response.send_message("✅ Lista de palavras proibidas limpa.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Automod(bot))
