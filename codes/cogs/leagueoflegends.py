import os, discord, dotenv, sys
from dotenv import load_dotenv
from pprint import pprint
from discord.ext import commands
from discord.utils import *

import random, pandas, pprint
from pprint import pprint
from riotwatcher import LolWatcher, ApiError

sys.path.append("D:\\python-codes\\Discordzada") #Config the PYTHONPATH to import "codes.leaguecontent" without warnings
from codes.leaguecontent import dataDragon as dd

load_dotenv()
RIOT_KEY = os.getenv('RIOT_KEY')
watcher = LolWatcher(RIOT_KEY)
region = 'BR1'

class LeagueOfLegends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #TODO Pensar em mais informações úteis para serem mostradas aqui
    @commands.command(pass_context = True, name = 'summ')
    async def get_summoner(self, ctx, *, name: str = 'Nothing Passed to Command'):
        if name == 'Nothing passed to command':
            missing_name_embed = discord.Embed(description = 'É precisso passar um nome de invocador!\nEx. !summoner Pato Papão')
            await ctx.send(embed = missing_name_embed)
        else:
            try:
                summoner = watcher.summoner.by_name(region, name)
                ranks = watcher.league.by_summoner(region, summoner["id"])
                masteries = watcher.champion_mastery.by_summoner(region, summoner["id"])
                
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
                        soloQ = f'{item["tier"]} {item["rank"]} - {item["leaguePoints"]}LP\n*{item["wins"]}V {item["losses"]}D \n(WRatio: {(item["wins"]/(item["wins"] + item["losses"]))*100:.2f}%)*'
                    else:
                        flexQ = f'{item["tier"]} {item["rank"]} - {item["leaguePoints"]}LP\n*{item["wins"]}V {item["losses"]}D \n(WRatio: {(item["wins"]/(item["wins"] + item["losses"]))*100:.2f}%)*'
                if soloQ == '': soloQ = 'Unranked'
                if flexQ == '': flexQ = 'Unranked'
                        
                summoner_info_embed.set_thumbnail(url = dd.get_profile_icon(iconID = summoner["profileIconId"]))
                
                summoner_info_embed.add_field(name = '**Ranked Solo**: ', value = f'{soloQ}', inline = True)
                summoner_info_embed.add_field(name = '**Ranked Flex:** ', value = f'{flexQ}', inline = True)
                
                summoner_info_embed.add_field(name = f'\u200b', value = '_**CHAMPIONS MASTERIES**_', inline = False)
                
                for i in range(len(top3_champions)):
                    if top3_champions != []:
                        summoner_info_embed.add_field(name = f'**{dd.get_champion_name(top3_champions[i]["championId"])}**', value = f'{top3_champions[i]["championPoints"]} MP' , inline = True)
                
                await ctx.send(embed = summoner_info_embed)
            except:
                summ_not_found_embed = discord.Embed(title = 'OPS!', description = f'Não consegui encontrar nenhum invocador com nome {name} no servidor {region}')
                await ctx.send(embed = summ_not_found_embed)
            

    #TODO Match History Command - Ainda não há nada feito aqui!
    #TODO Passar o nome do comando para o @commands.command
    @commands.command(pass_context = True)
    async def match_history(self, ctx, *, name: str = 'Empadão de Tatu'):
        summoner = watcher.summoner.by_name(region, name)
        summ_matches = watcher.match.matchlist_by_account(region, summoner['accountId'])
        
        last_match = summ_matches['matches'][0]
        match_detail = watcher.match.by_id(region, last_match['gameId'])
        
        participants = []
        for row in match_detail['participants']:
            participants_row = {}
            participants_row['champion'] = row['championId']
            participants_row['spell1'] = row['spell1Id']
            participants_row['spell2'] = row['spell2Id']
            participants_row['win'] = row['stats']['win']
            participants_row['kills'] = row['stats']['kills']
            participants_row['deaths'] = row['stats']['deaths']
            participants_row['assists'] = row['stats']['assists']
            participants_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
            participants_row['goldEarned'] = row['stats']['goldEarned']
            participants_row['champLevel'] = row['stats']['champLevel']
            participants_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']
            participants_row['item0'] = row['stats']['item0']
            participants_row['item1'] = row['stats']['item1']
            participants.append(participants_row)
        
        match_label = pandas.DataFrame(participants)
        print(match_label)
        await ctx.send(match_label)
            
    #TODO Tentar ordenar o layout pelas lanes
    #TODO Tentar chamar a função dinamicamente através de um Listener
    @commands.command(pass_context = True, name = 'live')
    async def live_match(self, ctx, *, name: str = 'Empadão de Tatu'):
        summoner = watcher.summoner.by_name(region, name)
        spec = watcher.spectator.by_summoner(region, summoner['id'])
        
        participants = spec["participants"]
        player_dict = {'name': [] , 'id': []}
        champion_list = []
        for row in participants:
            player_dict['name'].append(row['summonerName'])
            player_dict['id'].append(row['summonerId'])
            champ_name = dd.get_champion_name(row['championId'])
            champion_list.append(champ_name)
        
        soloQ_list = []
        for row in player_dict['id']:
            rank = watcher.league.by_summoner(region, row)
            for item in rank:
                if item["queueType"] == 'RANKED_SOLO_5x5':
                    soloQ_list.append(f'{item["tier"]} {item["rank"]}')
        
        live_match_embed = discord.Embed(
            title = f'Partida ao vivo de {summoner["name"]}',
            url = f'https://br.op.gg/summoner/userName=' + '+'.join(name.split(' '))
        )

        live_match_embed.add_field(name = 'Summoner', value = 
                                                      f'🔹 {player_dict["name"][0]}\n' + 
                                                      f'🔹 {player_dict["name"][1]}\n' +
                                                      f'🔹 {player_dict["name"][2]}\n' +
                                                      f'🔹 {player_dict["name"][3]}\n' +
                                                      f'🔹 {player_dict["name"][4]}\n\n' +
                                                      f'🔸 {player_dict["name"][5]}\n' + 
                                                      f'🔸 {player_dict["name"][6]}\n' +
                                                      f'🔸 {player_dict["name"][7]}\n' +
                                                      f'🔸 {player_dict["name"][8]}\n' +
                                                      f'🔸 {player_dict["name"][9]}\n',
                                                      inline = True)
        
        live_match_embed.add_field(name = 'Champion', value = 
                                                      f'{champion_list[0]}\n' + 
                                                      f'{champion_list[1]}\n' +
                                                      f'{champion_list[2]}\n' +
                                                      f'{champion_list[3]}\n' +
                                                      f'{champion_list[4]}\n\n' +
                                                      f'{champion_list[5]}\n' + 
                                                      f'{champion_list[6]}\n' +
                                                      f'{champion_list[7]}\n' +
                                                      f'{champion_list[8]}\n' +
                                                      f'{champion_list[9]}\n',
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
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][0])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][5])
            elif str(reaction) == '2️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][1])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][6])
            elif str(reaction) == '3️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][2])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][7])
            elif str(reaction) == '4️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][3])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][8])
            elif str(reaction) == '5️⃣':
                if(blue_flag):
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][4])
                else:
                    await ctx.invoke(self.bot.get_command('summ'), name = player_dict["name"][9])
            
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