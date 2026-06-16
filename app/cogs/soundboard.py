import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path
import asyncio


class Soundboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sound", description="Play a sound in your voice channel")
    async def sound(self, interaction: discord.Interaction, name: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Você precisa estar em um canal de voz.", ephemeral=True)
            return
        row = await self.bot.pool.fetchrow(
            "SELECT file_path FROM guild_sounds WHERE guild_id = $1 AND name = $2",
            interaction.guild.id, name.lower(),
        )
        if not row:
            await interaction.response.send_message(f"❌ Som **{name}** não encontrado. Use `/sound-list` para ver os disponíveis.", ephemeral=True)
            return
        path = Path(row["file_path"])
        if not path.exists():
            await interaction.response.send_message("❌ Arquivo não encontrado no servidor.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        vc = await interaction.user.voice.channel.connect()
        try:
            source = discord.FFmpegPCMAudio(str(path))
            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(0.5)
        finally:
            await vc.disconnect()
        await interaction.followup.send(f"✅ Som **{name}** reproduzido.", ephemeral=True)

    @app_commands.command(name="sound-add", description="Add a sound — reply with a name and attach an audio file")
    async def sound_add(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"📎 Responda esta mensagem com o arquivo de áudio que deseja cadastrar como **{name}** (mp3, m4a ou wav).",
            ephemeral=False,
        )

    @app_commands.command(name="sound-list", description="List all sounds available in this server")
    async def sound_list(self, interaction: discord.Interaction):
        rows = await self.bot.pool.fetch(
            "SELECT name FROM guild_sounds WHERE guild_id = $1 ORDER BY name",
            interaction.guild.id,
        )
        embed = discord.Embed(title="🔊 Sons disponíveis", color=discord.Color.blurple())
        if rows:
            embed.description = " • ".join(f"`{r['name']}`" for r in rows)
        else:
            embed.description = "Nenhum som cadastrado. Use `/sound-add` para adicionar."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sound-delete", description="Delete a sound from the server library")
    @app_commands.default_permissions(manage_messages=True)
    async def sound_delete(self, interaction: discord.Interaction, name: str):
        row = await self.bot.pool.fetchrow(
            "SELECT file_path FROM guild_sounds WHERE guild_id = $1 AND name = $2",
            interaction.guild.id, name.lower(),
        )
        if not row:
            await interaction.response.send_message(f"❌ Som **{name}** não encontrado.", ephemeral=True)
            return
        Path(row["file_path"]).unlink(missing_ok=True)
        await self.bot.pool.execute(
            "DELETE FROM guild_sounds WHERE guild_id = $1 AND name = $2",
            interaction.guild.id, name.lower(),
        )
        await interaction.response.send_message(f"✅ Som **{name}** removido.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Soundboard(bot))
