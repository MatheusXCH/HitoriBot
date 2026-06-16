import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path
from repositories.server import register_sound

SOUND_EXTS = {".mp3", ".m4a", ".wav", ".ogg"}


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

    @app_commands.command(name="sound-add", description="Add a sound — attach an audio file and give it a name")
    async def sound_add(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"📎 Responda esta mensagem com o arquivo de áudio que deseja cadastrar como **{name}** (mp3, m4a ou wav).",
        )
        bot_msg = await interaction.original_response()

        def check(m: discord.Message) -> bool:
            return (
                m.author.id == interaction.user.id
                and m.channel.id == interaction.channel.id
                and m.reference is not None
                and m.reference.message_id == bot_msg.id
                and any(Path(a.filename).suffix.lower() in SOUND_EXTS for a in m.attachments)
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            await bot_msg.edit(content=f"⏰ Tempo esgotado. Use `/sound-add {name}` novamente.")
            return

        attachment = next(a for a in msg.attachments if Path(a.filename).suffix.lower() in SOUND_EXTS)
        try:
            result = await register_sound(self.bot.pool, interaction.guild.id, name, attachment.url, attachment.filename)
            await msg.reply(result)
        except Exception as e:
            await msg.reply(f"❌ Erro ao salvar o som: {e}")

    @app_commands.command(name="sound-list", description="List all sounds available in this server")
    async def sound_list(self, interaction: discord.Interaction):
        rows = await self.bot.pool.fetch(
            "SELECT name FROM guild_sounds WHERE guild_id = $1 ORDER BY name",
            interaction.guild.id,
        )
        embed = discord.Embed(title="🔊 Sons disponíveis", color=discord.Color.blurple())
        embed.description = " • ".join(f"`{r['name']}`" for r in rows) if rows else "Nenhum som cadastrado. Use `/sound-add` para adicionar."
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
