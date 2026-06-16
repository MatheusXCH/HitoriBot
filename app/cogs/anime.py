import discord
from discord.ext import commands
from discord import app_commands
from integrations import anilist


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


class Anime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="anime", description="Search for an anime on AniList")
    async def anime(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        try:
            embeds = await anilist.search_anime(title)
        except Exception:
            await interaction.followup.send("❌ Erro ao buscar no AniList. Tente novamente.")
            return
        if not embeds:
            await interaction.followup.send(f"❌ Nenhum anime encontrado para **{title}**.")
            return
        view = MediaView(embeds) if len(embeds) > 1 else None
        await interaction.followup.send(embed=embeds[0], view=view)

    @app_commands.command(name="manga", description="Search for a manga on AniList")
    async def manga(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        try:
            embeds = await anilist.search_manga(title)
        except Exception:
            await interaction.followup.send("❌ Erro ao buscar no AniList. Tente novamente.")
            return
        if not embeds:
            await interaction.followup.send(f"❌ Nenhum mangá encontrado para **{title}**.")
            return
        view = MediaView(embeds) if len(embeds) > 1 else None
        await interaction.followup.send(embed=embeds[0], view=view)

    @app_commands.command(name="character", description="Search for an anime/manga character on AniList")
    async def character(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        try:
            embeds = await anilist.search_character(name)
        except Exception:
            await interaction.followup.send("❌ Erro ao buscar no AniList. Tente novamente.")
            return
        if not embeds:
            await interaction.followup.send(f"❌ Nenhum personagem encontrado para **{name}**.")
            return
        view = MediaView(embeds) if len(embeds) > 1 else None
        await interaction.followup.send(embed=embeds[0], view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Anime(bot))
