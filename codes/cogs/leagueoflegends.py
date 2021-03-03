import os, discord, dotenv, sys
from dotenv import load_dotenv
from pprint import pprint
from discord.ext import commands
from discord.utils import *

import random, pandas, pprint
from pprint import pprint
from riotwatcher import LolWatcher, ApiError

sys.path.append("D:\\python-codes\\Discordzada") #Config the PYTHONPATH to import "codes.leaguecontent" without warnings
from codes.leaguecontent import dataDragon

load_dotenv()
RIOT_KEY = os.getenv('RIOT_KEY')
watcher = LolWatcher(RIOT_KEY)
region = 'BR1'

dd = dataDragon.dataDragon()

class LeagueOfLegends(commands.Cog):
    """Obtém informações sobre o LOL direto da API da Riot Games
    """
    def __init__(self, bot):
        self.bot = bot
    
    #TODO Pensar em mais informações úteis para serem mostradas aqui
    @commands.command(pass_context = True, name = 'summ')
    async def get_summoner(self, ctx, *, name: str = 'Nothing Passed to Command', current_champion = None):
        """!summ <summoner_name>
        Retorna informações sobre o invocador
        """
        
        if name == 'Nothing passed to command':
            missing_name_embed = discord.Embed(description = 'É precisso passar um nome de invocador!\nEx. !summoner Pato Papão')
            await ctx.send(embed = missing_name_embed)
        else:
            try:
                summoner = watcher.summoner.by_name(region, name)
            except:
                no_summ_embed = discord.Embed(description = f'Não consegui encontrar o invocador **{name}**!')
                await ctx.send(embed = no_summ_embed)
                return
            
            try:
                ranks = watcher.league.by_summoner(region, summoner["id"])
                masteries = watcher.champion_mastery.by_summoner(region, summoner["id"])
            except:
                ranks_masteries_except_embed = discord.Embed(description = f'Houve um problema ao carregar informações sobre o invocador **{summoner["name"]}**')
                await ctx.send(embed = ranks_masteries_except_embed)
                return
    
            top3_champions = []
            if len(masteries) < 3:
                for item in range(len(masteries)):
                    top3_champions.append(masteries[item])
            else:
                for item in range(3):
                    top3_champions.append(masteries[item])
                
            summoner_info_embed = discord.Embed(
                title = f'{summoner["name"]}',
                description =  f'Level: {summoner["summonerLevel"]}\n',
                url = f'https://br.op.gg/summoner/userName=' + '+'.join(name.split(' '))
                )
                
            soloQ = ''
            flexQ = ''
            for item in ranks:
                if item["queueType"] == 'RANKED_SOLO_5x5':
                    soloQ = f'{item["tier"]} {item["rank"]} ({item["leaguePoints"]}LP)\n*{item["wins"]}V {item["losses"]}D \nWRatio: {(item["wins"]/(item["wins"] + item["losses"]))*100:.2f}%*'
                else:
                    flexQ = f'{item["tier"]} {item["rank"]} ({item["leaguePoints"]}LP)\n*{item["wins"]}V {item["losses"]}D \nWRatio: {(item["wins"]/(item["wins"] + item["losses"]))*100:.2f}%*'
            if soloQ == '': soloQ = 'UNRANKED'
            if flexQ == '': flexQ = 'UNRANKED'
                        
            summoner_info_embed.set_thumbnail(url = dd.get_profile_icon(iconID = summoner["profileIconId"]))
                
            summoner_info_embed.add_field(name = '**Ranked Solo**: ', value = f'{soloQ}', inline = True)
            summoner_info_embed.add_field(name = '**Ranked Flex:** ', value = f'{flexQ}', inline = True)
                
            summoner_info_embed.add_field(name = f'\u200b', value = '_**CAMPEÕES MAIS MASTERIZADOS**_', inline = False)
                
            for i in range(len(top3_champions)):
                if top3_champions != []:
                    summoner_info_embed.add_field(name = f'**{dd.get_champion_name(top3_champions[i]["championId"])}**', value = f'{top3_champions[i]["championPoints"]} MP' , inline = True)
            
            if current_champion != None:
                for item in masteries:
                    if item["championId"] == current_champion["championId"]:
                        champion_points = item.get("championPoints")
                try:        
                    summoner_info_embed.add_field(name = f'\u200b', value = f'Maestria com **{current_champion["championName"]}:**  {champion_points} MP', inline = False)
                except:
                    pass
            await ctx.send(embed = summoner_info_embed)    

    #TODO Match History Command - Ainda não há nada feito aqui!
    #TODO Passar o nome do comando para o @commands.command
    @commands.command(pass_context = True)
    async def match_history(self, ctx, *, name: str = 'Empadão de Tatu'):
        """!hist <summoner_name>
        Retorna o histórico recente do invocador
        """
        
        summoner = watcher.summoner.by_name(region, name)
        summ_matches = watcher.match.matchlist_by_account(region, summoner['accountId'])
        
        last_match = summ_matches['matches'][0]
        match_detail = watcher.match.by_id(region, last_match['gameId'])
        
        pprint(match_detail)
        
        # participants = []
        # for row in match_detail['participants']:
        #     participants_row = {}
        #     participants_row['champion'] = row['championId']
        #     participants_row['spell1'] = row['spell1Id']
        #     participants_row['spell2'] = row['spell2Id']
        #     participants_row['win'] = row['stats']['win']
        #     participants_row['kills'] = row['stats']['kills']
        #     participants_row['deaths'] = row['stats']['deaths']
        #     participants_row['assists'] = row['stats']['assists']
        #     participants_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
        #     participants_row['goldEarned'] = row['stats']['goldEarned']
        #     participants_row['champLevel'] = row['stats']['champLevel']
        #     participants_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']
        #     participants_row['item0'] = row['stats']['item0']
        #     participants_row['item1'] = row['stats']['item1']
        #     participants.append(participants_row)
        
        # match_label = pandas.DataFrame(participants)
        # print(match_label)
        # await ctx.send(match_label)
            
    #TODO Tentar ordenar o layout pelas lanes
    #TODO Tentar chamar a função dinamicamente através de um Listener
    @commands.command(pass_context = True, name = 'live')
    async def live_match(self, ctx, *, name: str = 'Empadão de Tatu'):
        """!live <summoner_name>
        Retorna o lobby da partida a qual o invocador está participando
        """
        
        try:
            summoner = watcher.summoner.by_name(region, name)
        except:
            no_summ_embed = discord.Embed(description = f'Não consegui encontrar o invocador **{name}**!')
            await ctx.send(embed = no_summ_embed)
            return
        
        try:
            spec = watcher.spectator.by_summoner(region, summoner['id'])
        except:
            no_live_match_embed = discord.Embed(description = f'Parece que o invocador **{summoner["name"]}** não está em uma partida no momento!')
            await ctx.send(embed = no_live_match_embed)
            return
        
        participants = spec["participants"]
        
        player_list = []
        champion_list = []
        for row in participants:
            player_list.append({'name': row['summonerName'], 'id': row['summonerId']})
            champ_name = dd.get_champion_name(row['championId'])
            champion_list.append({'championName': champ_name, 'championId': row['championId']})
        
        soloQ_list = []
        for player in player_list:
            rank = watcher.league.by_summoner(region, player['id'])
            if rank == []:
                soloQ_list.append(f'UNRANKED')
            else:
                for item in rank:
                    if item["queueType"] == 'RANKED_SOLO_5x5':
                        soloQ_list.append(f'{item["tier"]} {item["rank"]}')
                    
        
        live_match_embed = discord.Embed(
            title = f'Partida ao vivo de {summoner["name"]}',
            url = f'https://br.op.gg/summoner/userName=' + '+'.join(name.split(' '))
        )

        live_match_embed.add_field(name = 'Summoner', value = 
                                                      f'🔹 {player_list[0]["name"]}\n' + 
                                                      f'🔹 {player_list[1]["name"]}\n' +
                                                      f'🔹 {player_list[2]["name"]}\n' +
                                                      f'🔹 {player_list[3]["name"]}\n' +
                                                      f'🔹 {player_list[4]["name"]}\n\n' +
                                                      f'🔸 {player_list[5]["name"]}\n' + 
                                                      f'🔸 {player_list[6]["name"]}\n' +
                                                      f'🔸 {player_list[7]["name"]}\n' +
                                                      f'🔸 {player_list[8]["name"]}\n' +
                                                      f'🔸 {player_list[9]["name"]}\n',
                                                      inline = True)
        
        live_match_embed.add_field(name = 'Champion', value = 
                                                      f'{champion_list[0]["championName"]}\n' + 
                                                      f'{champion_list[1]["championName"]}\n' +
                                                      f'{champion_list[2]["championName"]}\n' +
                                                      f'{champion_list[3]["championName"]}\n' +
                                                      f'{champion_list[4]["championName"]}\n\n' +
                                                      f'{champion_list[5]["championName"]}\n' + 
                                                      f'{champion_list[6]["championName"]}\n' +
                                                      f'{champion_list[7]["championName"]}\n' +
                                                      f'{champion_list[8]["championName"]}\n' +
                                                      f'{champion_list[9]["championName"]}\n',
                                                      inline = True)
        
        live_match_embed.add_field(name = 'Rank', value = 
                                                      f'® {soloQ_list[0]}\n' + 
                                                      f'® {soloQ_list[1]}\n' +
                                                      f'® {soloQ_list[2]}\n' +
                                                      f'® {soloQ_list[3]}\n' +
                                                      f'® {soloQ_list[4]}\n\n' +
                                                      f'® {soloQ_list[5]}\n' +
                                                      f'® {soloQ_list[6]}\n' +
                                                      f'® {soloQ_list[7]}\n' +
                                                      f'® {soloQ_list[8]}\n' +
                                                      f'® {soloQ_list[9]}\n',
                                                      inline = True)
        
        message = await ctx.send(embed = live_match_embed)
        
        #Lidando com os "botões"
        #
        await message.add_reaction('🔹')
        await message.add_reaction('🔸')
        await message.add_reaction('1️⃣')
        await message.add_reaction('2️⃣')
        await message.add_reaction('3️⃣')
        await message.add_reaction('4️⃣')
        await message.add_reaction('5️⃣')
        
        def check(reaction, user):
            return user == ctx.author

        reaction = None
        control = None
        blue_flag = 1
        red_flag = 0
        
        while True:
            if str(reaction) == '🔹':
                blue_flag = 1
                red_flag = 0
            if str(reaction) == '🔸':
                blue_flag = 0
                red_flag = 1
            
            if str(reaction) == '1️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[0]["name"], current_champion = champion_list[0])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[5]["name"], current_champion = champion_list[5])
            elif str(reaction) == '2️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[1]["name"], current_champion = champion_list[1])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[6]["name"], current_champion = champion_list[6])
            elif str(reaction) == '3️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[2]["name"], current_champion = champion_list[2])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[7]["name"], current_champion = champion_list[7])
            elif str(reaction) == '4️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[3]["name"], current_champion = champion_list[3])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[8]["name"], current_champion = champion_list[8])
            elif str(reaction) == '5️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[4]["name"], current_champion = champion_list[4])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_list[9]["name"], current_champion = champion_list[9])
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout = 60.0, check = check)
                    
                if str(reaction) == '🔹' and not blue_flag:
                    await message.remove_reaction('🔸', user)
                elif str(reaction) == '🔸' and not red_flag:
                    await message.remove_reaction('🔹', user)
                else:
                    await message.remove_reaction(reaction, user)
            except:
                break
        await message.clear_reactions()
    
    
    #TODO League Champions Info
    
    
    #TODO League Item Info


def setup(bot):
    bot.add_cog(LeagueOfLegends(bot))