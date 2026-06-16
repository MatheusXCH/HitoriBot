import discord
from discord.ext import commands, tasks
from discord import app_commands
from integrations import steam, itad, hltb, freegame
from repositories.guild import get_settings
from config import settings as cfg


class GameView(discord.ui.View):
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


class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.freegame_task.start()

    def cog_unload(self):
        self.freegame_task.cancel()

    @app_commands.command(name="game", description="Search for a game — Steam info and completion times")
    async def game(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        try:
            embeds = await steam.search_game(title)
        except Exception:
            await interaction.followup.send("❌ Erro ao buscar o jogo na Steam.")
            return
        if not embeds:
            await interaction.followup.send(f"❌ Nenhum jogo encontrado para **{title}**.")
            return
        hltb_embed = await hltb.get_completion_time(title)
        if hltb_embed:
            embeds[0].add_field(
                name="⏱️ Tempo para zerar",
                value=f"Campanha: {hltb_embed.fields[0].value} | Extras: {hltb_embed.fields[1].value} | 100%: {hltb_embed.fields[2].value}",
                inline=False,
            )
        
        if len(embeds) > 1:
            await interaction.followup.send(embed=embeds[0], view=GameView(embeds))
        else:
            await interaction.followup.send(embed=embeds[0])

    @app_commands.command(name="price", description="Get current price and historical low for a game")
    async def price(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        if not cfg.itad_api_key:
            await interaction.followup.send("❌ IsThereAnyDeal API key não configurada.")
            return
        try:
            embed = await itad.get_game_price(title)
        except Exception:
            await interaction.followup.send("❌ Erro ao buscar preços no IsThereAnyDeal.")
            return
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="freegame-channel", description="Set the current channel for free game alerts")
    @app_commands.default_permissions(administrator=True)
    async def freegame_channel(self, interaction: discord.Interaction):
        await self.bot.pool.execute(
            "UPDATE guild_settings SET freegame_channel_id = $1 WHERE guild_id = $2",
            interaction.channel.id, interaction.guild.id,
        )
        await interaction.response.send_message("✅ Alertas de jogos gratuitos serão enviados neste canal.", ephemeral=True)

    @app_commands.command(name="freegames", description="Show current free games")
    async def freegames(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = await freegame.get_free_games(self.bot.pool)
        await interaction.followup.send(embed=embed)

    @tasks.loop(hours=1)
    async def freegame_task(self):
        if not cfg.reddit_client_id:
            return
        try:
            games = await freegame.fetch_free_games(
                cfg.reddit_client_id, cfg.reddit_client_secret, cfg.reddit_user_agent
            )
        except Exception:
            return

        seen = {r["reddit_id"] for r in await self.bot.pool.fetch("SELECT reddit_id FROM freegame_seen")}
        new_games = [g for g in games if g["id"] not in seen]
        if not new_games:
            return

        for game in new_games:
            await self.bot.pool.execute(
                "INSERT INTO freegame_seen (reddit_id, title, url) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                game["id"], game["title"], game["url"],
            )

        guilds_data = await self.bot.pool.fetch(
            "SELECT guild_id, freegame_channel_id FROM guild_settings WHERE freegame_channel_id IS NOT NULL"
        )
        embed = discord.Embed(title="🎮 Novos Jogos Gratuitos!", color=discord.Color.green())
        for g in new_games[:10]:
            embed.add_field(name=g["title"], value=f"[Pegar aqui]({g['url']})", inline=False)
        embed.set_footer(text="Fonte: r/FreeGameFindings")

        for row in guilds_data:
            channel = self.bot.get_channel(row["freegame_channel_id"])
            if channel:
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass

    @freegame_task.before_loop
    async def before_freegame_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
