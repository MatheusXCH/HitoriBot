import os, discord, asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class Administrator(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    
    async def clear_admin_messages(self, ctx, message):
        """Limpa as mensagens do Módulo Administrator"""
        await asyncio.sleep(3)    
        await message.delete()


    @commands.command(hidden = True, name = 'm-load')
    @commands.is_owner()
    async def load(self, ctx, *, module : str):
        """Carrega um módulo"""
        await ctx.message.delete()
        try:
            self.bot.load_extension(module)
        except Exception as e:
            msg = await ctx.send(f'Falha ao carregar: {type(e).__name__} {e}')
        else:
            msg = await ctx.send(f'{module.upper()} carregado com sucesso!')
        
        await self.clear_admin_messages(ctx, msg)


    @commands.command(hidden = True, name = 'm-unload')
    @commands.is_owner()
    async def unload(self, ctx, *, module : str):
        """Descarrega um módulo"""
        await ctx.message.delete()
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            msg = await ctx.send(f'Falha ao descarregar: {type(e).__name__} {e}') 
        else:
            msg = await ctx.send(f'{module.upper()} descarregado com sucesso!')

        await self.clear_admin_messages(ctx, msg)


    @commands.command(hidden = True, name = 'm-reload')
    @commands.is_owner()
    async def reload(self, ctx, *, module : str):
        """Recarrega um módulo"""
        await ctx.message.delete()
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            msg = await ctx.send(f'Falha ao recarregar: {type(e).__name__} {e}') 
        else:
            msg = await ctx.send(f'{module.upper()} recarregado com sucesso!')

        await self.clear_admin_messages(ctx, msg)


def setup(bot):
    bot.add_cog(Administrator(bot))