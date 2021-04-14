import asyncio
import os

import discord
from discord.ext import commands
from discord.ext.commands import (
    MissingPermissions,
    has_permissions,
    CommandNotFound,
    MissingRequiredArgument,
    BadArgument,
    TooManyArguments,
    MemberNotFound,
    NotOwner,
)


class Administrator(commands.Cog):
    """ Contém funções para uso apenas do Dono do Bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def clear_admin_messages(self, ctx: commands.Context, message: discord.Message):
        """Clean Administrator Module messages"""

        await asyncio.sleep(3)
        await message.delete()

    @commands.command(hidden=True, name="m-load")
    @commands.is_owner()
    async def load(self, ctx: commands.Context, *, module: str):
        """Load a module"""

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
        """Unload a module"""

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
        """Reload a module"""

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

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Defines some custom error handlers"""

        if isinstance(error, commands.CommandNotFound):
            msg = await ctx.send(
                f"Não reconheço o comando `{ctx.message.content}`, {ctx.author.mention}\n"
                f"Para saber quais são os comandos válidos, utilize `!help`"
            )
            await asyncio.sleep(5)
            return await msg.delete()
        else:
            raise error


def setup(bot):
    bot.add_cog(Administrator(bot))
