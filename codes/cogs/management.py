import codecs
import os
import time
import asyncio

# Get the globals from Paths
import codes.paths as path
import discord
from pprint import pprint
from discord import Member, Role, User
from discord.ext import commands
from discord.ext.commands import Bot, MissingPermissions, guild_only, has_permissions
from discord.utils import get

# Módulo: Management
#     - O presente módulo possui comandos de gerenciamento do servidor de forma abrangente
#     - Contém funções de administrador (como Kick, Ban)
#     - Contém um Listener responsável por filtrar palavras indevidas no servidor
#     - Contém funções para administrar roles (set e drop)
#     - Contém o comando !clear, responsável por limpar as mensagens do próprio PyBOT ou de algum membro da guilda


class Management(commands.Cog):
    """Módulo contendo diversas funções de gerenciamento
    OBS: É preciso ter permissão para utilizar alguns dos comandos deste módulo
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, ctx: commands.Context, error):
        if isinstance(error, MissingPermissions):
            return f"Desculpe {ctx.author.mention}, você não tem permissão para fazer isso!"

    @commands.command(name="invite")
    async def invite(self, ctx: commands.Context):
        """!invite => Recebe um convite para o servidor na DM"""

        invitelink = await ctx.channel.create_invite(max_uses=1, unique=True, max_age=300)
        await ctx.author.send("Aqui está o seu convite para o servidor: ")
        await ctx.author.send(invitelink)

    @commands.command(name="nick")
    @has_permissions(manage_nicknames=True)
    async def nick(self, ctx: commands.Context, member: discord.Member, *, newnick=None):
        """!nick <@Member> <new_nick> => Troca o nick do 'Membro' para 'new_nick'
        - É necessário ter permissão para trocar apelidos
        """
        if newnick is None:
            await member.edit(nick="")

        await member.edit(nick=newnick)
        await ctx.send(f"Apelido de **{member.name}** mudado para {member.mention} com sucesso!")

    @nick.error
    async def nick_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="kick")
    @has_permissions(manage_roles=True, kick_members=True)
    async def kick(self, ctx: commands.Context, member: Member):
        """!kick <@Member> => Expulsa um membro do servidor
        - É necessário ter permissão para expulsar membros
        """

        await member.kick()
        await ctx.send(f"**{member.mention}** foi KICKADO pelo RH!")
        await ctx.send(file=discord.File(path.image_path + "RH.png"))

    @kick.error
    async def kick_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="ban")
    @has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: Member):
        """!ban <@Member> => Bane um membro do servidor
        - É necessário ter permissão para banir membros
        """

        await member.ban()
        await ctx.send(f"{member.mention} foi BANIDO pelo RH!")
        await ctx.send(file=discord.File(path.image_path + "RH.png"))

    @ban.error
    async def ban_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.command(name="unban")
    @has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context):
        """!unban => Permite desbanir um usuário da lista de banidos do servidor
        - É necessário permissão para banir membros
        """

        def check(message):
            return message.author == ctx.author

        bans = await ctx.guild.bans()
        banned_users_list = [ban_tuple[1] for ban_tuple in bans]
        banned_users = [{"id": user.id, "name_tag": f"{user.name}#{user.discriminator}"} for user in banned_users_list]
        show_banneds = " | ".join([user["name_tag"] for user in banned_users])

        if not show_banneds:
            return await ctx.send(
                embed=discord.Embed(title="Usuários banidos:", description="**Não há ninguém banido no servidor**")
            )

        await ctx.send(embed=discord.Embed(title="Usuários banidos:", description=f"{show_banneds}"))
        await ctx.send("Informe quem deseja desbanir:")

        try:
            user_name_msg = await self.bot.wait_for("message", check=check, timeout=30)
            user_name = user_name_msg.content
        except asyncio.TimeoutError:
            await ctx.send(
                f"Desculpe {ctx.author.mention}, parece que você demorou demais para informar o que foi solicitado... 😅"
            )

        for item in banned_users:
            if user_name.upper() == item["name_tag"].upper():
                user = self.bot.get_user(int(item["id"]))
                await ctx.guild.unban(user)
                return await ctx.send(
                    f"O usuário **{user.name}** foi desbanido 🛠\nAgora basta notificá-lo da novidade via DM 😁"
                )

        await ctx.send(f"Parece que o usuário **{user_name}** não está banido no servidor 🤔")

    @unban.error
    async def unban_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="role")
    @has_permissions(manage_roles=True)
    async def get_role(self, ctx: commands.Context, member: Member):
        """!role <@Member> => Lista as roles de um membro da guilda
        - É necessário ter permissão para gerenciar Roles
        """

        list_roles = []
        for role in range(1, len(member.roles)):
            list_roles.append(member.roles[role].name)

        list_roles = ", ".join(list_roles)

        await ctx.send(f"As roles de {member.mention} são: {list_roles}")

    @get_role.error
    async def get_role_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="set-role")
    @has_permissions(manage_roles=True)
    async def set_role(self, ctx: commands.Context, member: Member, *, role: Role):
        """!set-role <@Member> <Role> => Troca a role de um membro
        - É necessário ter permissão de administrador
        """

        await member.add_roles(role)
        await ctx.send(f"A role de {member.mention} foi definida como: {role.name}")

    @set_role.error
    async def set_role_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="drop-role")
    @has_permissions(manage_roles=True)
    async def drop_role(self, ctx: commands.Context, member: Member, *, role: Role):
        """!drop-role => Retira uma role de um membro
        - É necessário ter permissão de administrador
        """

        await member.remove_roles(role)
        await ctx.send(f'A role "{role.name}" de {member.mention} foi retirada!')

    @drop_role.error
    async def drop_role_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="perms", hidden=True)
    async def permissions(self, ctx: commands.Context, member: Member = None):
        """!perms [@Member]* => Retorna as permissões de um membro
        - As permissões de outros membros estão disponíveis apenas para aqueles que podem gerir Roles
        """

        if member is not None:
            permissions = ctx.author.permissions_in(ctx.channel)
            if not permissions.manage_roles:
                return await ctx.send(
                    f"Desculpe {ctx.author.mention}, você não pode ver a permissão de outros usuários"
                )

        if member is None:
            member = ctx.author

        roles = member.roles
        permissions_set = set()
        for role in roles:
            role_perms = [perm[0] for perm in role.permissions if perm[1]]
            for perm in role_perms:
                permissions_set.add(perm)

        permissions_list = sorted(list(permissions_set))
        permissions = "\n▫".join(permissions_list).title()
        await ctx.author.send(
            f"**SOLICITAÇÃO ATENDIDA!**\n__**{member.display_name}**__ tem as seguintes permissões na guilda **{ctx.guild.name}:**\n"
            f"▫{permissions}"
        )

    @commands.command(name="clear")
    @has_permissions(manage_messages=True, send_messages=True)
    async def clear(self, ctx: commands.Context, number=5, member: Member = None):
        """!clear [num] [@Member] => Limpa as últimas [num] mensagens do usuário [@Member] no chat
        - [num] e [@Member] são opcionais, de modo que:\\
            !clear => Limpa 5 mensagens do bot\\
            !clear [num] => Limpa [num] mensagens do bot\\
            !clear [num] [@Member] => Limpa [num] mensagens de [@Member]
        """
        await ctx.message.delete()
        success = 0

        # Verifica se o Member foi passado, caso não, escolhe o BOT como default
        if member is None:
            member = self.bot.user

        async for msg in ctx.message.channel.history(limit=100):
            if msg.author.id == member.id:
                number -= 1
                try:
                    await msg.delete()
                    success += 1
                except Exception:
                    pass

                if number == 0:
                    break

        embed = discord.Embed(title=f"♻ Foram limpas {success} mensagens!")
        msg = await ctx.send(embed=embed)
        time.sleep(3)
        await msg.delete()

    @clear.error
    async def clear_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="clean")
    @has_permissions(manage_messages=True, send_messages=True)
    async def clean(self, ctx: commands.Context, limit: int = 100):
        """!clean [limit] => Avalia as últimas [limit] mensagens e deleta todas que foram enviadas pelo bot
        - O atribuito [limit] é opcional e, por padrão, está definido como limit=100.
        """

        def check(message):
            return message.author == self.bot.user

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=limit, check=check)
        msg = await ctx.send(
            embed=discord.Embed(
                title=f"♻ Foram limpas {len(deleted)} mensagens de {ctx.guild.get_member(self.bot.user.id).nick}!"
            )
        )
        await asyncio.sleep(5)
        await msg.delete()

    @clean.error
    async def clean_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    @commands.command(name="purge")
    @has_permissions(administrator=True)
    async def channel_purge(self, ctx: commands.Context, limit: int = 20):
        """!purge [limit] => Deleta as últimas [limit] mensagens do canal, independente de quem as tenha enviado. Admin Only
        - O atributo [limit] é opcioanl e, por padrão, está definido como limit=20. Apenas Administradores podem utilizar este comando.
        """

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=limit)
        msg = await ctx.send(
            embed=discord.Embed(
                title=f"♻ As últimas {len(deleted)} mensagens do canal {ctx.channel.name} foram limpas!"
            )
        )
        await asyncio.sleep(5)
        await msg.delete()

    @channel_purge.error
    async def channel_purge_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))


def setup(bot):
    bot.add_cog(Management(bot))
