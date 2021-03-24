import asyncio
import codecs
import os
import random

import codes.settings as st  # Get the globals from Settings
import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, has_permissions

# Módulo: Messages
#     - Contém alguns comandos simples, os quais consitem apenas de algumas mensagens que são exibidas pelo PyBOT
class Messages(commands.Cog):
    """Módulo que contém alguns comandos simples, que retornam apenas mensagens de texto"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx: commands.Context, *, text: str):
        """!say <text> => O Bot repete o que for passado para ele como <text>
        Passa um texto para o Bot repetir. A mensagem original enviada é deletada.
        """

        await ctx.message.delete()
        await ctx.send(text)

    @commands.command(name="familia")
    async def familia(self, ctx):
        """!familia => Pergunta pro BRTT se isso é uma família"""

        response = (
            f"Isso aqui não é uma família, é um time!\n"
            + f"Se vai deixar morrer, teu irmão???\n\n"
            + f"*CLARO QUE VAI NÉ, PORRA!*"
        )
        familia_embed = discord.Embed(description=response)
        await ctx.send(embed=familia_embed)

    @commands.command(name="playlist")
    async def playlist(self, ctx: commands.Context):
        """!playlist => Lista as playlists feitas para o Servidor"""

        embed = discord.Embed(
            title=":notes: **Playlists do Servidor** :notes:",
            colour=discord.Colour(0x32A852),
            description="Aqui estão os **links das playlists** elaboradas para este servidor:",
        )
        embed.add_field(
            name=":play_pause: Animezada:",
            value="https://www.youtube.com/playlist?list=PLlOJh8D_rbtt3u1U3XScS8iL-EvNOf_ap",
            inline=False,
        )
        embed.add_field(
            name=":play_pause: Biruta:",
            value="https://www.youtube.com/playlist?list=PLlOJh8D_rbtsYBFZWDPCqG4gqXSSkSj_m",
            inline=False,
        )
        embed.add_field(
            name=":play_pause: É o Ericks:",
            value="https://www.youtube.com/playlist?list=PLUou7E06dGsYeCeFykeBHCG7bXgx_VC4e",
            inline=False,
        )
        embed.add_field(
            name=":play_pause: Só o HYPE:",
            value="https://www.youtube.com/playlist?list=PLeOu0isxutGI693o9yg6d3BGSUbPPgU4X",
            inline=False,
        )

        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener - Diz ao usuário que não é pra dirigir a palavra ao BOT"""

        if self.bot.user.mentioned_in(message) and message.author != self.bot.user and not message.mention_everyone:
            await message.channel.send(f"Aí {message.author.mention}, não me dirige a palavra não. Faz favor!")


def setup(bot):
    bot.add_cog(Messages(bot))
