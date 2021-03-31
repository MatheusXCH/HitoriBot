import os
import random
import sys
from pprint import pprint

import discord
import dotenv
import pandas
from discord.ext import commands
from discord.utils import *
from dotenv import load_dotenv
from riotwatcher import ApiError, LolWatcher
from roleidentification import pull_data, get_roles

# Config the PYTHONPATH to import "codes.leaguecontent" without warnings
sys.path.append("D:\\python-codes\\Discordzada")
from codes.leaguecontent import dataDragon

load_dotenv()
RIOT_KEY = os.getenv("RIOT_KEY")
watcher = LolWatcher(RIOT_KEY)
region = "BR1"

dd = dataDragon.dataDragon()


class LeagueOfLegends(commands.Cog):
    """Obtém informações sobre o LOL direto da API da Riot Games"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # TODO Pensar em mais informações úteis para serem mostradas aqui
    # TODO Trocar a lógica do "Nothing Passed to Command" por algo mais elegante
    @commands.command(name="summ")
    async def get_summoner(
        self,
        ctx: commands.Context,
        *,
        name: str = "Nothing Passed to Command",
        current_champion=None,
        command_call_flag=0,
        msg=None,
    ):
        """!summ <summoner_name> => Retorna informações sobre o invocador"""

        if name == "Nothing passed to command":
            missing_name_embed = discord.Embed(
                description="É precisso passar um nome de invocador!\nEx. !summoner Pato Papão"
            )
            await ctx.send(embed=missing_name_embed)
        else:
            try:
                summoner = watcher.summoner.by_name(region, name)
            except Exception:
                no_summ_embed = discord.Embed(description=f"Não consegui encontrar o invocador **{name}**!")
                await ctx.send(embed=no_summ_embed)
                return

            try:
                ranks = watcher.league.by_summoner(region, summoner["id"])
                masteries = watcher.champion_mastery.by_summoner(region, summoner["id"])
            except Exception:
                ranks_masteries_except_embed = discord.Embed(
                    description=f'Houve um problema ao carregar informações sobre o invocador **{summoner["name"]}**'
                )
                await ctx.send(embed=ranks_masteries_except_embed)
                return

            top3_champions = []
            if len(masteries) < 3:
                for item in range(len(masteries)):
                    top3_champions.append(masteries[item])
            else:
                for item in range(3):
                    top3_champions.append(masteries[item])

            summoner_info_embed = discord.Embed(
                title=f'{summoner["name"]}',
                description=f'Level: {summoner["summonerLevel"]}\n',
                url="https://br.op.gg/summoner/userName=" + "+".join(name.split(" ")),
            )

            soloQ = ""
            flexQ = ""
            for item in ranks:
                if item["queueType"] == "RANKED_SOLO_5x5":
                    soloQ = f'{item["tier"]} {item["rank"]} ({item["leaguePoints"]}LP)\n*{item["wins"]}V {item["losses"]}D \nWRatio: {(item["wins"]/(item["wins"] + item["losses"]))*100:.2f}%*'
                else:
                    flexQ = f'{item["tier"]} {item["rank"]} ({item["leaguePoints"]}LP)\n*{item["wins"]}V {item["losses"]}D \nWRatio: {(item["wins"]/(item["wins"] + item["losses"]))*100:.2f}%*'
            if soloQ == "":
                soloQ = "UNRANKED"
            if flexQ == "":
                flexQ = "UNRANKED"

            summoner_info_embed.set_thumbnail(url=dd.get_profile_icon(iconID=summoner["profileIconId"]))

            summoner_info_embed.add_field(name="**Ranked Solo**: ", value=f"{soloQ}", inline=True)
            summoner_info_embed.add_field(name="**Ranked Flex:** ", value=f"{flexQ}", inline=True)

            summoner_info_embed.add_field(name="\u200b", value="_**CAMPEÕES MAIS MASTERIZADOS**_", inline=False)

            for i in range(len(top3_champions)):
                if top3_champions != []:
                    summoner_info_embed.add_field(
                        name=f'**{dd.get_champion_name(top3_champions[i]["championId"])}**',
                        value=f'{top3_champions[i]["championPoints"]} MP',
                        inline=True,
                    )

            if command_call_flag == 0:
                await ctx.send(embed=summoner_info_embed)

            if command_call_flag == 1:
                for item in masteries:
                    if item["championId"] == current_champion:
                        champion_name = dd.get_champion_name(current_champion)
                        champion_points = item.get("championPoints")
                try:
                    summoner_info_embed.add_field(
                        name="\u200b",
                        value=f"Maestria com **{champion_name}:**  {champion_points} MP",
                        inline=False,
                    )
                except Exception:
                    pass
                await msg.edit(embed=summoner_info_embed)

    # TODO Match History Command - Ainda não há nada feito aqui!
    # TODO Passar o nome do comando para o @commands.command
    # @commands.command(name = 'hist')
    # async def match_history(self, ctx, *, name: str = 'Empadão de Tatu'):
    #     """!hist <summoner_name>
    #     Retorna o histórico recente do invocador
    #     """
    #     champion_roles = pull_data()
    #     summoner = watcher.summoner.by_name(region, name)
    #     matches = watcher.match.matchlist_by_account(region, summoner['accountId'])

    #     matches_embed = discord.Embed(
    #         title = f'Histórico de {summoner["name"]}',
    #         url = f'https://br.op.gg/summoner/userName=' + '+'.join(name.split(' '))
    #     )

    #     matches_embed.set_thumbnail(url = dd.get_profile_icon(iconID = summoner["profileIconId"]))
    #     last_match = matches['matches'][0]
    #     match_detail = watcher.match.by_id(region, last_match['gameId'])

    # TODO Fazer o histórico da ÚLTIMA partida!!!
    # É preciso olhar o arquivo "match_Detail.txt" para ver a estrutura do dicionário de match_detail
    # Usar a função 'get_role(champion_roles, list_champion_in_match)' para pegar os dados dos campeões da última partida
    # O parâmetro 'list_champion_in_match' é uma lista de 5 elementos contendo o championId de cada um dos campeões na partida

    # TODO Tentar chamar a função dinamicamente através de um Listener
    @commands.command(name="live")
    async def live_match(self, ctx: commands.Context, *, name: str = "Empadão de Tatu"):
        """!live <summoner_name> => Retorna o lobby da partida ao vivo do invocador
        O invocador DEVE estar em uma partida ao vivo
        É possível obter informações sobre os participantes da partida em tempo real, utilizando dos botões disponíveis no Embed
        """

        try:
            summoner = watcher.summoner.by_name(region, name)
        except Exception:
            no_summ_embed = discord.Embed(description=f"Não consegui encontrar o invocador **{name}**!")
            await ctx.send(embed=no_summ_embed)
            return

        try:
            spec = watcher.spectator.by_summoner(region, summoner["id"])
        except Exception:
            no_live_match_embed = discord.Embed(
                description=f'Parece que o invocador **{summoner["name"]}** não está em uma partida no momento!'
            )
            await ctx.send(embed=no_live_match_embed)
            return

        participants = spec["participants"]
        blue_champion_id_list = []
        red_champion_id_list = []
        count = 0
        for row in participants:
            # Get list of champions in Blue/Red side
            if count < 5:
                blue_champion_id_list.append(row["championId"])
                count += 1
            else:
                red_champion_id_list.append(row["championId"])
                count += 1
        # Get the Blue/Red side champions roles
        champion_roles = pull_data()
        blue_team = get_roles(champion_roles, blue_champion_id_list)
        red_team = get_roles(champion_roles, red_champion_id_list)

        def get_rank(summonerId):
            current_rank = watcher.league.by_summoner(region, summonerId)
            player_rank = ""
            if current_rank == []:
                player_rank = "UNRANKED"
            else:
                for item in current_rank:
                    if item["queueType"] == "RANKED_SOLO_5x5":
                        player_rank = f'{item["tier"]} {item["rank"]} ({item["leaguePoints"]} LP)'
            return player_rank

        for row in participants:
            # BLUE TEAM
            if row["championId"] == blue_team["TOP"]:
                rank = get_rank(row["summonerId"])
                blue_team.update(
                    {
                        "TOP": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == blue_team["JUNGLE"]:
                rank = get_rank(row["summonerId"])
                blue_team.update(
                    {
                        "JUNGLE": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == blue_team["MIDDLE"]:
                rank = get_rank(row["summonerId"])
                blue_team.update(
                    {
                        "MIDDLE": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == blue_team["BOTTOM"]:
                rank = get_rank(row["summonerId"])
                blue_team.update(
                    {
                        "BOTTOM": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == blue_team["UTILITY"]:
                rank = get_rank(row["summonerId"])
                blue_team.update(
                    {
                        "UTILITY": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )

            # RED TEAM
            if row["championId"] == red_team["TOP"]:
                rank = get_rank(row["summonerId"])
                red_team.update(
                    {
                        "TOP": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == red_team["JUNGLE"]:
                rank = get_rank(row["summonerId"])
                red_team.update(
                    {
                        "JUNGLE": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == red_team["MIDDLE"]:
                rank = get_rank(row["summonerId"])
                red_team.update(
                    {
                        "MIDDLE": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == red_team["BOTTOM"]:
                rank = get_rank(row["summonerId"])
                red_team.update(
                    {
                        "BOTTOM": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )
            elif row["championId"] == red_team["UTILITY"]:
                rank = get_rank(row["summonerId"])
                red_team.update(
                    {
                        "UTILITY": {
                            "name": row["summonerName"],
                            "id": row["summonerId"],
                            "champion": dd.get_champion_name(row["championId"]),
                            "championId": row["championId"],
                            "rank": rank,
                        }
                    }
                )

        live_match_embed = discord.Embed(
            title=f'Partida ao vivo de {summoner["name"]}',
            url="https://br.op.gg/summoner/userName=" + "+".join(name.split(" ")),
        )

        live_match_embed.add_field(
            name="Summoner",
            value=f'🔹 {blue_team["TOP"]["name"]}\n'
            + f'🔹 {blue_team["JUNGLE"]["name"]}\n'
            + f'🔹 {blue_team["MIDDLE"]["name"]}\n'
            + f'🔹 {blue_team["BOTTOM"]["name"]}\n'
            + f'🔹 {blue_team["UTILITY"]["name"]}\n'
            + "\n"
            + f'🔸 {red_team["TOP"]["name"]}\n'
            + f'🔸 {red_team["JUNGLE"]["name"]}\n'
            + f'🔸 {red_team["MIDDLE"]["name"]}\n'
            + f'🔸 {red_team["BOTTOM"]["name"]}\n'
            + f'🔸 {red_team["UTILITY"]["name"]}\n',
            inline=True,
        )

        live_match_embed.add_field(
            name="Champion",
            value=f'{dd.EMOJI_TOP} {blue_team["TOP"]["champion"]}\n'
            + f'{dd.EMOJI_JUNGLE} {blue_team["JUNGLE"]["champion"]}\n'
            + f'{dd.EMOJI_MIDDLE} {blue_team["MIDDLE"]["champion"]}\n'
            + f'{dd.EMOJI_BOTTOM} {blue_team["BOTTOM"]["champion"]}\n'
            + f'{dd.EMOJI_UTILITY} {blue_team["UTILITY"]["champion"]}\n'
            + "\n"
            + f'{dd.EMOJI_TOP} {red_team["TOP"]["champion"]}\n'
            + f'{dd.EMOJI_JUNGLE} {red_team["JUNGLE"]["champion"]}\n'
            + f'{dd.EMOJI_MIDDLE} {red_team["MIDDLE"]["champion"]}\n'
            + f'{dd.EMOJI_BOTTOM} {red_team["BOTTOM"]["champion"]}\n'
            + f'{dd.EMOJI_UTILITY} {red_team["UTILITY"]["champion"]}\n',
            inline=True,
        )

        live_match_embed.add_field(
            name="Rank",
            value=f'® {blue_team["TOP"]["rank"]}\n'
            + f'® {blue_team["JUNGLE"]["rank"]}\n'
            + f'® {blue_team["MIDDLE"]["rank"]}\n'
            + f'® {blue_team["BOTTOM"]["rank"]}\n'
            + f'® {blue_team["UTILITY"]["rank"]}\n'
            + "\n"
            + f'® {red_team["TOP"]["rank"]}\n'
            + f'® {red_team["JUNGLE"]["rank"]}\n'
            + f'® {red_team["MIDDLE"]["rank"]}\n'
            + f'® {red_team["BOTTOM"]["rank"]}\n'
            + f'® {red_team["UTILITY"]["rank"]}\n',
            inline=True,
        )

        message = await ctx.send(embed=live_match_embed)

        # Lidando com os "botões"
        #
        await message.add_reaction("🔹")
        await message.add_reaction("🔸")
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")
        await message.add_reaction("3️⃣")
        await message.add_reaction("4️⃣")
        await message.add_reaction("5️⃣")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author

        reaction = None
        blue_flag = 1
        red_flag = 0
        command_call_flag_control = 1

        call_summ_msg_embed = discord.Embed(
            description="Utilize os botões acima para obter informações sobre os invocadores"
        )
        call_summ_msg = await ctx.send(embed=call_summ_msg_embed)
        while True:
            if str(reaction) == "🔹":
                blue_flag = 1
                red_flag = 0
            if str(reaction) == "🔸":
                blue_flag = 0
                red_flag = 1

            if str(reaction) == "1️⃣":
                if blue_flag:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=blue_team["TOP"]["name"],
                        current_champion=blue_team["TOP"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )
                else:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=red_team["TOP"]["name"],
                        current_champion=red_team["TOP"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )

            elif str(reaction) == "2️⃣":
                if blue_flag:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=blue_team["JUNGLE"]["name"],
                        current_champion=blue_team["JUNGLE"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )
                else:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=red_team["JUNGLE"]["name"],
                        current_champion=red_team["JUNGLE"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )

            elif str(reaction) == "3️⃣":
                if blue_flag:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=blue_team["MIDDLE"]["name"],
                        current_champion=blue_team["MIDDLE"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )
                else:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=red_team["MIDDLE"]["name"],
                        current_champion=red_team["MIDDLE"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )

            elif str(reaction) == "4️⃣":
                if blue_flag:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=blue_team["BOTTOM"]["name"],
                        current_champion=blue_team["BOTTOM"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )
                else:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=red_team["BOTTOM"]["name"],
                        current_champion=red_team["BOTTOM"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )

            elif str(reaction) == "5️⃣":
                if blue_flag:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=blue_team["UTILITY"]["name"],
                        current_champion=blue_team["UTILITY"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )
                else:
                    await ctx.invoke(
                        self.bot.get_command("summ"),
                        name=red_team["UTILITY"]["name"],
                        current_champion=red_team["UTILITY"]["championId"],
                        command_call_flag=command_call_flag_control,
                        msg=call_summ_msg,
                    )

            elif str(reaction) == "❌":
                await call_summ_msg.delete()
                await message.clear_reactions()
                await message.delete()
                return

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=90.0, check=check)

                if str(reaction) == "🔹" and not blue_flag:
                    await message.remove_reaction("🔸", user)
                elif str(reaction) == "🔸" and not red_flag:
                    await message.remove_reaction("🔹", user)
                else:
                    await message.remove_reaction(reaction, user)
            except Exception:
                break
        await message.clear_reactions()

    # TODO League Champions Info

    # TODO League Item Info


def setup(bot):
    bot.add_cog(LeagueOfLegends(bot))
