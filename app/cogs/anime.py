import logging
import discord
from discord.ext import commands
from discord import app_commands
from integrations import anilist

log = logging.getLogger("hitoribot.anime")


class MediaView(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed]):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.index = 0
        self._update_buttons()

    def _update_buttons(self):
        self.prev_btn.disabled = self.index == 0
        self.next_btn.disabled = self.index >= len(self.embeds) - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)


async def _send_embed_list(interaction: discord.Interaction, embeds: list[discord.Embed]) -> None:
    if len(embeds) > 1:
        await interaction.followup.send(embed=embeds[0], view=MediaView(embeds))
    else:
        await interaction.followup.send(embed=embeds[0])


class Anime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="anime", description="Search for an anime on AniList")
    async def anime(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        log.info("/anime title=%r guild=%s", title, interaction.guild_id)
        try:
            embeds = await anilist.search_anime(title)
        except Exception:
            log.exception("/anime search failed")
            await interaction.followup.send("❌ Erro ao buscar no AniList. Tente novamente.")
            return
        if not embeds:
            await interaction.followup.send(f"❌ Nenhum anime encontrado para **{title}**.")
            return
        await _send_embed_list(interaction, embeds)

    @app_commands.command(name="manga", description="Search for a manga on AniList")
    async def manga(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        log.info("/manga title=%r guild=%s", title, interaction.guild_id)
        try:
            embeds = await anilist.search_manga(title)
        except Exception:
            log.exception("/manga search failed")
            await interaction.followup.send("❌ Erro ao buscar no AniList. Tente novamente.")
            return
        if not embeds:
            await interaction.followup.send(f"❌ Nenhum mangá encontrado para **{title}**.")
            return
        await _send_embed_list(interaction, embeds)

    @app_commands.command(name="character", description="Search for an anime/manga character on AniList")
    async def character(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        log.info("/character name=%r guild=%s", name, interaction.guild_id)
        try:
            embeds = await anilist.search_character(name)
        except Exception:
            log.exception("/character search failed")
            await interaction.followup.send("❌ Erro ao buscar no AniList. Tente novamente.")
            return
        if not embeds:
            await interaction.followup.send(f"❌ Nenhum personagem encontrado para **{name}**.")
            return
        await _send_embed_list(interaction, embeds)


async def setup(bot: commands.Bot):
    await bot.add_cog(Anime(bot))
