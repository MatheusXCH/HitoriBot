import discord
from discord.ext import commands
from discord import app_commands


class Playlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="playlist-add", description="Add a playlist to the server catalog")
    @app_commands.default_permissions(manage_messages=True)
    async def playlist_add(self, interaction: discord.Interaction, name: str, url: str):
        await self.bot.pool.execute(
            "INSERT INTO guild_playlists (guild_id, name, url) VALUES ($1, $2, $3) "
            "ON CONFLICT (guild_id, name) DO UPDATE SET url = $3",
            interaction.guild.id, name, url,
        )
        await interaction.response.send_message(f"✅ Playlist **{name}** adicionada.", ephemeral=True)

    @app_commands.command(name="playlist-edit", description="Edit a playlist name or URL")
    @app_commands.default_permissions(manage_messages=True)
    async def playlist_edit(self, interaction: discord.Interaction, name: str, new_name: str = "", new_url: str = ""):
        if not new_name and not new_url:
            await interaction.response.send_message("❌ Forneça um novo nome ou URL.", ephemeral=True)
            return
        if new_url:
            await self.bot.pool.execute(
                "UPDATE guild_playlists SET url = $1 WHERE guild_id = $2 AND name = $3",
                new_url, interaction.guild.id, name,
            )
        if new_name:
            await self.bot.pool.execute(
                "UPDATE guild_playlists SET name = $1 WHERE guild_id = $2 AND name = $3",
                new_name, interaction.guild.id, name,
            )
        await interaction.response.send_message(f"✅ Playlist **{name}** atualizada.", ephemeral=True)

    @app_commands.command(name="playlist-delete", description="Remove a playlist from the catalog")
    @app_commands.default_permissions(manage_messages=True)
    async def playlist_delete(self, interaction: discord.Interaction, name: str):
        result = await self.bot.pool.execute(
            "DELETE FROM guild_playlists WHERE guild_id = $1 AND name = $2",
            interaction.guild.id, name,
        )
        if result == "DELETE 0":
            await interaction.response.send_message(f"❌ Playlist **{name}** não encontrada.", ephemeral=True)
        else:
            await interaction.response.send_message(f"✅ Playlist **{name}** removida.", ephemeral=True)

    @app_commands.command(name="playlists", description="Show all playlists in this server")
    async def playlists(self, interaction: discord.Interaction):
        rows = await self.bot.pool.fetch(
            "SELECT name, url FROM guild_playlists WHERE guild_id = $1 ORDER BY name",
            interaction.guild.id,
        )
        embed = discord.Embed(title="🎵 Playlists do servidor", color=discord.Color.green())
        if rows:
            for row in rows:
                embed.add_field(name=row["name"], value=row["url"], inline=False)
        else:
            embed.description = "Nenhuma playlist cadastrada. Use `/playlist-add` para adicionar."
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Playlist(bot))
