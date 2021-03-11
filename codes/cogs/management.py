import os, discord, time, codecs
from discord import Member
from discord import User
from discord import Role
from discord.utils import get
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext.commands import Bot, guild_only

import codes.settings as st #Get the globals from Settings

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
    
    def __init__(self, bot):
        self.bot = bot
    
    #TODO Criar estrutura de dados para as palavras indesejadas
    @commands.Cog.listener()
    async def on_message(self, message):
        """ Bad Words [Listener]
            - Monitora o chat de texto, identificando palavras indesejadas e limpando-as logo em sequência
        """
        
        bad_sentences = ["SAKDJLKASIOWEUOQIWESDHDHASWQOEUQWOIUFASJSALKQWEQEPWU"]
        
        for sentence in bad_sentences:
            if message.content.count(sentence) > 0:
                await message.channel.purge(limit=1)
                await message.channel.send(f'Mensagem deletada - Uso de expressão indevida! (||{sentence})||')

    @commands.command(name='rules')
    async def rules(self, ctx):
        """!rules
        Exibe as regras do servidor
        """
        
        with codecs.open(st.rule_path + 'rules.txt', 'r', encoding='utf8') as f:
            text = f.read()
        
        embed = discord.Embed(
            title = f'__**Regras do Servidor**__',
            colour = discord.Colour(0xe82e2e),
            description = "Leia as Regras atentamente"
        )
        
        embed.add_field(name='Regras', value=text, inline=False)
        file = discord.File(st.image_path + 'RH.png', filename='RH.png')
        embed.set_image(url='attachment://RH.png')
        await ctx.send(file=file, embed=embed)
    
    # !invite
    # - Gera um convite para o servidor, enviando-o ao autor do comando pela DM
    @commands.command(name='invite')
    async def invite(self, ctx):
        """!invite
        Recebe um convite para o servidor na DM
        """
        
        invitelink = await ctx.channel.create_invite(max_uses=1, unique=True, max_age=300)
        await ctx.author.send("Aqui está o seu convite para o servidor: ")
        await ctx.author.send(invitelink)

    # !nick [@Member] [newnick]
    #     - Troca o apelido de um membro do servidor por um novo
    #         - É necessário ter permissãoo para gerenciar apelidos, caso contrário o comando não estará disponível
    @commands.command(pass_context=True, name='nick')
    @has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, newnick):
        """!nick <@Member> <new_nick>
        Troca o nick do 'Membro' para 'new_nick'
        # É necessário ter permissão para trocar apelidos
        """
        
        await member.edit(nick=newnick)
        await ctx.send(f'Apelido de {member.name} mudado para {member.mention} com sucesso!')
    #Trata o erro de 'Nick'
    @nick.error
    async def nick_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            text = f'Desculpe {ctx.message.author}, você não tem permissão para fazer isso!'
            await ctx.send(text)
    
    # !kick [@Member]
    #     - Expulsa um membro do servidor
    #         - É necessário ter permissão para expulsar membros
    @commands.command(pass_context=True, name='kick')
    @has_permissions(manage_roles=True, kick_members=True)
    async def kick(self, ctx, member: Member):
        """!kick <@Member>
        Expulsa um membro do servidor
        # É necessário ter permissão para expulsar membros
        """
        
        await member.kick()
        await ctx.send(f'{member.mention} foi KICKADO pelo RH!')
        await ctx.send(file = discord.File(st.image_path + 'RH.png'))
    #Trata o erro de 'Nick'
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            text = f'Desculpe {ctx.message.author}, você não tem permissão para fazer isso!'
            await ctx.send(text)
    
    # !ban [@Member]
    #     - Bane um membro do servidor
    #             - É necessário ter permissão para banir membros
    @commands.command(pass_context=True, name='ban')
    @has_permissions(administrator=True)
    async def ban(self, ctx, member: Member):
        """!ban <@Member>
        Bane um membro do servidor
        # É necessário ter permissão para banir membros
        """
        
        await member.ban()
        await ctx.send(f'{member.mention} foi BANIDO pelo RH!')
        await ctx.send(file = discord.File(st.image_path + 'RH.png'))
    #Trata o erro de 'Ban'
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            text = f'Desculpe {ctx.message.author}, você não tem permissão para fazer isso!'
            await ctx.send(text)
    
    #TODO UNBAN - Não funciona! Função está com erros!
    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    @guild_only()
    async def unban(self, ctx, id: int):
        user = await bot.fetch_user(id)
        if(ctx.guild.fetch_ban(user)):
            await ctx.guild.unban(user)
        else:
            await ctx.send(f'O usuário {user} não está banido no servidor!')
    #Trata o erro de 'Unban'
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            text = f'Desculpe {ctx.message.author}, você não tem permissão para fazer isso!'
            await ctx.send(text)
    
    # !role [@Member]
    #         - Lista as roles de um membro da guilda
    #             - É necessário permissão de administrador
    @commands.command(pass_context=True, name='role')
    @has_permissions(administrator=True)
    async def get_role(self, ctx, member: Member):
        """!role <@Member>
        Lista as roles de um membro da guilda
        # É necessário ter permissão de administrador
        """
        
        list_roles = []
        for role in range(1, len(member.roles)):
            list_roles.append(member.roles[role].name)

        list_roles = ', '.join(list_roles)
        
        await ctx.send(f'As roles de {member.mention} são: {list_roles}') 
    
    
    #TODO Tornar possível setar mais de uma role por vez    
    # !set-role [@Member] Role
    #         - Define a role de um membro
    #             - É necessário permissão de administrador
    @commands.command(pass_context=True, name='set-role')
    @has_permissions(administrator=True)
    async def set_role(self, ctx, member: Member, *, role: Role):
        """!set-role <@Member> <Role>
        Troca a role de um membro
        # É necessário ter permissão de administrador
        """
        
        await member.add_roles(role)
        await ctx.send(f'A role de {member.mention} foi definida como: {role.name}')
     
     
    #TODO Tornar possível dropar mais de uma role por vez
    # !drop-role
    #         - Retira a role de um membro 
    #             - É necessário permissão de administrador
    @commands.command(pass_context=True, name='drop-role')
    @has_permissions(administrator=True)
    async def drop_role(self, ctx, member: Member, *, role: Role):    
        """!drop-role
        Retira uma role de um membro
        # É necessário ter permissão de administrador
        """
        
        await member.remove_roles(role)
        await ctx.send(f'A role "{role.name}" de {member.mention} foi retirada!')
        
    #TODO Arrumar - Função apenas envia o ID da permissão via DM 
    # Get Permissions - Envia a lista de permissões para o autor na DM
    @commands.command(pass_context=True)
    async def permissions(self, ctx, member: Member):
        perm = member.permissions_in(ctx.channel)
        await ctx.author.send(f'Solicitação atendida!\n{member.display_name} tem permissões para {perm}')
    
    
    # !clear *[number] *[@Member]
    #         - Limpa as últimas [number] mensagens do usuário [@Member] no chat
    #             - OBS: [number] e [@Member] são opcionais, sendo como padrão
    #                 - [number] = 5
    #                 - [@Member] = PyBOT
    #         #### Exemplos de uso:
    #         ##### !clear -> Limpa as últimas 5 mensagens do PyBOT
    #         ##### !clear 10 -> Limpa as últimas 10 mensagens do PyBOT
    #         ##### !clear 10 @Membro -> Limpa as últimas 10 mensagens do Membro
    @commands.command(pass_context=True, name='clear')
    @has_permissions(manage_messages=True, send_messages=True)
    async def clear(self, ctx, number = 5, member : Member = None):  
        """!clear [num] [@Member]
        Limpa as últimas [num] mensagens do usuário [@Member] no chat
        # [num] e [@Member] são opcionais, de modo que:
            !clear => Limpa 5 mensagens do bot
            !clear [num] => Limpa [num] mensagens do bot
            !clear [num] [@Member] => Limpa [num] mensagens de [@Member]
        """
              
        success = 0
        failed = 0
        
        #Verifica se o Member foi passado, caso não, escolhe o BOT como default
        if(member == None):
            member_id = self.bot.user.id
        else:
            member_id = member.id
            number += 1
        
        async for msg in ctx.message.channel.history(limit=100):
            if msg.author.id == member_id:
                number -= 1
                try:
                    await msg.delete()
                    success += 1
                except:
                    failed += 1
                    
                if number == 0:
                    break
        
        embed = discord.Embed(
            title = 'Completo!',
            description = f'Foram limpas {success} mensagens. Houveram {failed} falhas!'
        )
        await ctx.send(embed = embed)
        time.sleep(3)
        async for msg in ctx.message.channel.history(limit=100):
            if msg.author.id == self.bot.user.id:
                try:
                    await msg.delete()
                    break
                except:
                    break


def setup(bot):
    bot.add_cog(Management(bot))