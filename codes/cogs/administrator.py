import asyncio
import os

import discord
from discord.ext import commands
from discord.ext.commands import MissingPermissions, has_permissions


class Administrator(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def clear_admin_messages(self, ctx: commands.Context, message: discord.Message):
        """Limpa as mensagens do Módulo Administrator"""

        await asyncio.sleep(3)
        await message.delete()

    @commands.command(hidden=True, name="m-load")
    @commands.is_owner()
    async def load(self, ctx: commands.Context, *, module: str):
        """Carrega um módulo"""

        await ctx.message.delete()
        try:
            self.bot.load_extension(module)
        except Exception as e:
            msg = await ctx.send(f"Falha ao carregar: {type(e).__name__} {e}")
        else:
            msg = await ctx.send(f"{module.upper()} carregado com sucesso!")

        await self.clear_admin_messages(ctx, msg)

    @commands.command(hidden=True, name="m-unload")
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, *, module: str):
        """Descarrega um módulo"""

        await ctx.message.delete()
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            msg = await ctx.send(f"Falha ao descarregar: {type(e).__name__} {e}")
        else:
            msg = await ctx.send(f"{module.upper()} descarregado com sucesso!")

        await self.clear_admin_messages(ctx, msg)

    @commands.command(hidden=True, name="m-reload")
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, *, module: str):
        """Recarrega um módulo"""

        await ctx.message.delete()
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            msg = await ctx.send(f"Falha ao recarregar: {type(e).__name__} {e}")
        else:
            msg = await ctx.send(f"{module.upper()} recarregado com sucesso!")

        await self.clear_admin_messages(ctx, msg)

    @commands.command(name="get-guilds", hidden=True)
    async def get_guilds(self, ctx: commands.Context):
        """Return information about the Guilds that the BOT is connected to

        Parameters
        ----------
        ctx : commands.Context
            [Discord commands context]
        """

        guilds = [guild for guild in self.bot.guilds]

        guilds_id = [guild.id for guild in guilds]
        guilds_name = [guild.name for guild in guilds]
        guilds_bot_nickname = [guild.get_member(self.bot.user.id).nick for guild in guilds]
        guilds_member_count = [guild.member_count for guild in guilds]
        guilds_region = [guild.region for guild in guilds]

        # Creating the message
        line = ""
        guilds_info = ""
        for item in range(len(guilds)):
            line = f"ID: {guilds_id[item]}, Name: {guilds_name[item]}\nBot Nick: {guilds_bot_nickname[item]}, #Members: {guilds_member_count[item]}, Region: {guilds_region[item]}\n\n"
            guilds_info += line

        embed = discord.Embed(title=f"Listing Guilds **{self.bot.user}** is ON!")
        embed.add_field(name="Guilds", value=f"```{guilds_info}```")
        embed.set_footer(text=self.bot.user)

        await ctx.send(embed=embed)

        # # FIXME A função atrapalha a identificar erros
        # # TODO Buscar formas de melhoras o Listener responsável por notificar o usuário que o comando não existe
        # @commands.Cog.listener()
        # async def on_command_error(self, ctx, error):
        #     """Envia mensagem padrão caso seja utilizado um comando inválido"""

        #     unknown_command_msg = await ctx.send(embed = discord.Embed(title = f'Comando {ctx.message.content} desconhecido', description = 'Para saber quais são os comandos válidos, utilize "!help"'))
        #     await asyncio.sleep(5)
        #     await unknown_command_msg.delete()


def setup(bot):
    bot.add_cog(Administrator(bot))
