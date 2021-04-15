import asyncio
import os

import codes.paths as path
import discord
from discord.ext import commands
from discord.utils import *

# # # Módulo: Audioplayer
# # - Utiliza as bibliotecas 'FFmpeg' e 'Libopus' (via PyNaCl) para tornar possível que o bot toque áudios
# # em canais de voz dos servidores

# # # Utiliza:
# # - Discord.py API (by Rapptz on: https://github.com/Rapptz/discord.py)
# # - FFmpeg (on: https://www.ffmpeg.org/)
# # - PyNaCl (by pyca on: https://github.com/pyca/pynacl/)


class AudioPlayer(commands.Cog):
    """Conecta o Bot em canais de voz para tocar áudios (similar ao Soundpad)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def not_in_channel_msg(self, ctx: commands.Context):
        """Define mensagem padrão exibida sempre que o usuário utiliza um comando de voz sem estar conectado a um canal apropriado"""

        except_message = await ctx.send(
            f"{ctx.author.mention}, você deve estar em um **canal de voz** para usar este comando!"
        )
        await asyncio.sleep(5)
        await except_message.delete()
        return

    async def audio_play(self, ctx: commands.Context, audio_name: str):
        """Função responsável por gerenciar o áudio que deve ser tocado pelo Bot"""

        try:
            voice_channel = ctx.author.voice.channel
        except Exception:
            await self.not_in_channel_msg(ctx)
            return

        vc = await voice_channel.connect()
        join_message = await ctx.send(embed=discord.Embed(title=f"Conectado ao canal *{voice_channel.name}*"))
        vc.play(discord.FFmpegPCMAudio(source=path.audio_path + f"{audio_name}"))
        while vc.is_playing():
            await asyncio.sleep(0.1)
        await vc.disconnect()
        await join_message.delete()
        await ctx.message.delete()

    @commands.command(name="join", invoke_without_subcommand=True)
    async def join(self, ctx: commands.Context):
        """!join => Conecta o bot ao canal de voz do usuário"""

        try:
            channel = ctx.author.voice.channel
            await channel.connect()
        except Exception:
            await self.not_in_channel_msg(ctx)

    @commands.command(name="leave")
    async def leave(self, ctx: commands.Context):
        """!leave => Desconecta o bot do canal de voz"""

        try:
            guild = ctx.message.guild
            voice_client = guild.voice_client
            await voice_client.disconnect()
        except Exception:
            await self.not_in_channel_msg(ctx)

    # # A partir desse ponto começam os comandos de áudio mp3
    #
    #

    @commands.command(name="rogers")
    async def rogers(self, ctx: commands.Context):
        """!rogers => Toca o rogers do Grongos"""

        await self.audio_play(ctx, "rogers.mp3")

    @commands.command(name="monke")
    async def monkey_flip(self, ctx: commands.Context):
        """!monke => Monkey Flip!!!"""

        await self.audio_play(ctx, "monkey_flip.mp3")

    @commands.command(name="tiltado")
    async def tiltado(self, ctx: commands.Context):
        """!tiltado => Gratão tiltado"""

        await self.audio_play(ctx, "tiltado.m4a")

    @commands.command(name="naruto")
    async def naruto_triste(self, ctx: commands.Context):
        """!naruto => Tururuuuuuuuu"""

        await self.audio_play(ctx, "sadness_and_sorrow.m4a")

    @commands.command(name="roblox")
    async def roblox_ouf(self, ctx: commands.Context):
        """!roblox => Ouf"""

        await self.audio_play(ctx, "roblox.m4a")

    @commands.command(name="xaropinho")
    async def xaropinho(self, ctx: commands.Context):
        """!xaropinho => Rapaaaaaiz"""

        await self.audio_play(ctx, "xaropinho.m4a")


def setup(bot):
    bot.add_cog(AudioPlayer(bot))
