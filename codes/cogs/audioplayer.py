import os, discord, asyncio
import codes.settings as st
from discord.ext import commands
from discord.utils import *

#TODO É preciso configurar o FFmpeg no Heroku !!!!!
class AudioPlayer(commands.Cog):
    """Conecta o Bot em canais de voz para tocar áudios (similar ao Soundpad)"""

    def __init__(self, bot):
        self.bot = bot


    async def not_in_channel_msg(self, ctx):
        """ Define mensagem padrão exibida sempre que o usuário utiliza um comando de voz sem estar conectado a um canal aproriado"""
        
        except_message = await ctx.send(f'{ctx.author.mention}, você deve estar em um **canal de voz** para usar este comando!')
        await asyncio.sleep(5)
        await except_message.delete()
        return


    async def audio_play(self, ctx, audio_name):
        """Função responsável por gerenciar o áudio que deve ser tocado pelo Bot"""
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await self.not_in_channel_msg(ctx)
            return
    
        vc = await voice_channel.connect()
        join_message = await ctx.send(f'Conectado ao canal **{voice_channel.name}**')
        vc.play(discord.FFmpegPCMAudio(source = st.audio_path + f'{audio_name}'))
        while vc.is_playing():
            await asyncio.sleep(0.1)
        await vc.disconnect()
        await join_message.delete()


    @commands.command(pass_context = True, name = 'join', invoke_without_subcommand=True)
    async def join(self, ctx: commands.Context):
        """!join -> Conecta o bot ao canal de voz do usuário"""
        
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
        except:
            await self.not_in_channel_msg(ctx)
            
            
    @commands.command(pass_context = True, name = 'leave')
    async def leave(self, ctx):
        """!leave -> Desconecta o bot do canal de voz"""
        
        try:
            guild = ctx.message.guild
            voice_client = guild.voice_client
            await voice_client.disconnect()
        except:
            await self.not_in_channel_msg(ctx)
    
    
    # # A partir desse ponto começam os comandos de áudio mp3
    #
    #
    
    #TODO Baixar mais áudios 
    @commands.command(pass_context = True, name = 'rogers')
    async def rogers(self, ctx):
        """!rogers -> Toca o rogers do Grongos"""
        
        await self.audio_play(ctx, 'rogers.mp3')
    
    
def setup(bot):
    bot.add_cog(AudioPlayer(bot))