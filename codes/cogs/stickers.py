import os

# Get the globals from Settings
import codes.paths as path
import discord
from discord.ext import commands


# Módulo: Stickers
#     - Responsável por todos os comandos relacionados aos stickers disponibilizados pelo PyBOT
#     - Sempre que um dos comandos por chamado, o PyBOT responderá com o sticker (imagem) correspondente
#     - Todos os Stickers está disponível no diretório '/misc/stickers'
class Stickers(commands.Cog):
    """Módulo contendo todos os stickers disponíveis para uso"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="bebero")
    async def bebero(self, ctx: commands.Context):
        """!bebero"""
        await ctx.send(file=discord.File(path.image_path + "Bebero.png"))

    @commands.command(name="analise")
    async def analise(self, ctx: commands.Context):
        """!analise"""
        await ctx.send(file=discord.File(path.image_path + "Analise.png"))

    @commands.command(name="bença")
    async def bença(self, ctx: commands.Context):
        """!bença"""
        await ctx.send(file=discord.File(path.image_path + "Bença.png"))

    @commands.command(name="broxa")
    async def broxa(self, ctx: commands.Context):
        """!broxa"""
        await ctx.send(file=discord.File(path.image_path + "Broxa.png"))

    @commands.command(name="entendi")
    async def entendi(self, ctx: commands.Context):
        """!entendi"""
        await ctx.send(file=discord.File(path.image_path + "Entendi.png"))

    @commands.command(name="perdemoS")
    async def perdemoS(self, ctx: commands.Context):
        """!perdemoS"""
        await ctx.send(file=discord.File(path.image_path + "PerdemoS.png"))

    @commands.command(name="pexe")
    async def pexe(self, ctx: commands.Context):
        """!pexe"""
        await ctx.send(file=discord.File(path.image_path + "Pexe.png"))

    @commands.command(name="sabo")
    async def sabo(self, ctx: commands.Context):
        """!sabo"""
        await ctx.send(file=discord.File(path.image_path + "Sabo.png"))

    @commands.command(name="sorriso")
    async def sorriso(self, ctx: commands.Context):
        """!sorriso"""
        await ctx.send(file=discord.File(path.image_path + "Sorriso.png"))

    @commands.command(name="rh")
    async def rh(self, ctx: commands.Context):
        """!rh"""
        await ctx.send(file=discord.File(path.image_path + "RH.png"))

    @commands.command(name="perdemo")
    async def perdemo(self, ctx: commands.Context):
        """!perdemo"""
        await ctx.send(file=discord.File(path.image_path + "Perdemo.png"))

    @commands.command(name="soninho")
    async def soninho(self, ctx: commands.Context):
        """!soninho"""
        await ctx.send(file=discord.File(path.image_path + "Soninho.gif"))


def setup(bot):
    bot.add_cog(Stickers(bot))
