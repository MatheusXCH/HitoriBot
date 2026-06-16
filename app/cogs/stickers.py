import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path
from repositories.server import register_sticker

STICKER_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


class Stickers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sticker", description="Send a sticker from the server library")
    async def sticker(self, interaction: discord.Interaction, name: str):
        row = await self.bot.pool.fetchrow(
            "SELECT file_path FROM guild_stickers WHERE guild_id = $1 AND name = $2",
            interaction.guild.id, name.lower(),
        )
        if not row:
            await interaction.response.send_message(f"❌ Sticker **{name}** não encontrado. Use `/sticker-list` para ver os disponíveis.", ephemeral=True)
            return
        path = Path(row["file_path"])
        if not path.exists():
            await interaction.response.send_message("❌ Arquivo não encontrado no servidor.", ephemeral=True)
            return
        await interaction.response.send_message(file=discord.File(path))

    @app_commands.command(name="sticker-add", description="Add a sticker — attach an image and give it a name")
    async def sticker_add(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(
            f"📎 Responda esta mensagem com a imagem que deseja cadastrar como **{name}** (png, jpg ou gif).",
        )
        bot_msg = await interaction.original_response()

        def check(m: discord.Message) -> bool:
            return (
                m.author.id == interaction.user.id
                and m.channel.id == interaction.channel.id
                and m.reference is not None
                and m.reference.message_id == bot_msg.id
                and any(Path(a.filename).suffix.lower() in STICKER_EXTS for a in m.attachments)
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            await bot_msg.edit(content=f"⏰ Tempo esgotado. Use `/sticker-add {name}` novamente.")
            return

        attachment = next(a for a in msg.attachments if Path(a.filename).suffix.lower() in STICKER_EXTS)
        try:
            result = await register_sticker(self.bot.pool, interaction.guild.id, name, attachment.url, attachment.filename)
            await msg.reply(result)
        except Exception as e:
            await msg.reply(f"❌ Erro ao salvar o sticker: {e}")

    @app_commands.command(name="sticker-list", description="List all stickers available in this server")
    async def sticker_list(self, interaction: discord.Interaction):
        rows = await self.bot.pool.fetch(
            "SELECT name FROM guild_stickers WHERE guild_id = $1 ORDER BY name",
            interaction.guild.id,
        )
        embed = discord.Embed(title="🖼️ Stickers disponíveis", color=discord.Color.blurple())
        embed.description = " • ".join(f"`{r['name']}`" for r in rows) if rows else "Nenhum sticker cadastrado. Use `/sticker-add` para adicionar."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sticker-delete", description="Delete a sticker from the server library")
    @app_commands.default_permissions(manage_messages=True)
    async def sticker_delete(self, interaction: discord.Interaction, name: str):
        row = await self.bot.pool.fetchrow(
            "SELECT file_path FROM guild_stickers WHERE guild_id = $1 AND name = $2",
            interaction.guild.id, name.lower(),
        )
        if not row:
            await interaction.response.send_message(f"❌ Sticker **{name}** não encontrado.", ephemeral=True)
            return
        Path(row["file_path"]).unlink(missing_ok=True)
        await self.bot.pool.execute(
            "DELETE FROM guild_stickers WHERE guild_id = $1 AND name = $2",
            interaction.guild.id, name.lower(),
        )
        await interaction.response.send_message(f"✅ Sticker **{name}** removido.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stickers(bot))
