import asyncio
import json
import math
import os
import pprint
import random
import sys
from pprint import pprint
from urllib.parse import quote

import codes.settings as st
import discord
import dotenv
import requests
import steam
from discord.ext import commands
from discord.utils import *
from dotenv import load_dotenv

sys.path.append(
    "D:\\python-codes\\Discordzada"
)  # Config the PYTHONPATH to import "codes.leaguecontent" without warnings
from codes.steamcontent import steambigpicture

load_dotenv()
steam_key = os.getenv("STEAM_KEY")
big_picture = steambigpicture.SteamBigPicture()

# EMOJIS
EMOJI_ORANGE_BACK = "<:orange_back:821841259282956318>"
EMOJI_ORANGE_PLAY = "<:orange_play:821840997037244437>"


class StoreSteam(commands.Cog):
    """Módulo que permite a conexão do PyBOT com a Steam-BR"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="steam-update")
    async def steam_update(self, ctx):
        """!steam-update => Atualiza a base de dados da Steam"""

        try:
            msg = await ctx.send(embed=discord.Embed(title="Aguarde", description="Atualizando os dados da Steam..."))
            big_picture.request_all_games()
            await msg.edit(embed=discord.Embed(title="Sucesso!", description="Base de dados do Steam atualizada!"))
            await asyncio.sleep(5)
            await msg.delete()
        except:
            error_msg = await ctx.send(
                embed=discord.Embed(
                    title="Erro",
                    description="Desculpe, parece que houve um problema ao carregar a base de dados da Steam!\nTente novamente após alguns minutos!",
                )
            )
            await asyncio.sleep(5)
            await msg.delete()

    @commands.command(name="steam")
    async def search_game(self, ctx: commands.Context, *, game_title: str):
        """!game <game_title> => Retorna informações sobre um jogo na Steam"""

        def __get_reviews_label(reviews_perc):
            """Returns custom str labels accord to the value of <reviews_perc>"""

            if 0 <= reviews_perc <= 19:
                return "⛔ Muito negativas"
            if 20 <= reviews_perc <= 39:
                return "⛔ Levemente negativas"
            if 40 <= reviews_perc <= 69:
                return "⏹ Neutras"
            if 70 <= reviews_perc <= 79:
                return "☑ Levemente positivas"
            if 80 <= reviews_perc <= 94:
                return "✅ Muito positivas"
            if 95 <= reviews_perc <= 100:
                return "✅ Extremamente positivas"

        def steam_pages_layout(i: int, j: int):
            """Handles the Embed pages layout of the !Steam command

            Parameters
            ----------
            - i : int\\
                [Index used to iterate between games]
            - j : int\\
                [Index used to iterate between packages]

            Returns
            -------
            - steam_game_embed : discord.Embed \\
                [The discord.Embed page to show on text channel]
            """
            # Choosing Games and Packages by indexes
            steam_game = steam_games[i]
            steamspy_info = steamspy_games_info[i]
            package = packages[i][j]

            # Getting TAGS
            try:
                tags_list = steamspy_info["tags"]
                tags_dict = dict(sorted(tags_list.items(), key=lambda item: item[1])[-5:])
                tags = "\n".join([tag for tag in tags_dict])
                if tags == "":
                    raise Exception
            except:
                tags = "N/A"

            # Getting DEVELOPERS
            try:
                developers_list = [item for item in steam_game["developers"]]
                developers = "\n".join(developers_list)
                if developers == "":
                    raise Exception
            except:
                developers = "N/A"

            # Getting PUBLISHERS
            try:
                publishers_list = [item for item in steam_game["publishers"]]
                publishers = "\n".join(publishers_list)
                if publishers == "":
                    raise Exception
            except:
                publishers = "N/A"

            # Getting CATEGORIES (FEATURES)
            try:
                categories_list = [item["description"] for item in steam_game["categories"]]
                categories_list_filtered = [
                    item
                    for item in categories_list
                    if (
                        item == "Um jogador"
                        or item == "Multijogador"
                        or item == "Cooperativo"
                        or item == "Cooperativo online"
                        or item == "Conquistas Steam"
                        or item == "Compatibilidade total com controle"
                        or item == "Remote Play Together"
                        or item == "Cartas Colecionáveis Steam"
                        or item == "Multijogador entre plataformas"
                        or item == "Compatibilidade parcial com controle"
                        or item == "JxJ"
                        or item == "JxJ online"
                    )
                ]
                categories = "\n".join(categories_list_filtered)
                if categories == "":
                    raise Exception
            except:
                categories = "N/A"

            # Getting PRICE_OVERVIEW
            # TODO Arrumar os problemas possíveis de ocorrer no parâmetro 'Price_Overview'
            if not steam_game["is_free"]:
                try:
                    initial_value = str(steam_game["price_overview"]["initial"])
                    base_price = f"R$ {initial_value[:-2]},{initial_value[-2:]}"
                    final_price = steam_game["price_overview"]["final_formatted"]
                    discount = f'{steam_game["price_overview"]["discount_percent"]}%'
                except:
                    base_price = "N/A"
                    final_price = "N/A"
                    discount = "N/A"

            # Getting REVIEWS
            try:
                reviews_perc = math.floor(
                    (steamspy_info["positive"] / (steamspy_info["positive"] + steamspy_info["negative"])) * 100
                )
                reviews_label = __get_reviews_label(reviews_perc)
                reviews_dict = {"score": f"({reviews_perc}%)", "label": reviews_label}
            except:
                reviews_dict = {"score": "\u200b", "label": "N/A"}

            # Getting LANGUAGES
            try:
                languages_list = steamspy_info["languages"].split(", ")
                languages_list_filtered = [
                    lang
                    for lang in languages_list
                    if (
                        lang == "English"
                        or lang == "Japanese"
                        or lang == "Portuguese - Brazil"
                        or lang == "Spanish - Spain"
                    )
                ]
                languages = "\n".join(languages_list_filtered)
            except:
                languages = "N/A"

            # Getting METACRITIC
            try:
                metacritic_score = steam_game["metacritic"]["score"]
            except:
                metacritic_score = "---"

            # Included Items
            try:
                includes_list = [item["name"] for item in package["apps"]]
                includes = "\n".join(includes_list)
                if includes == "":
                    raise Exception
            except:
                includes = "\u200b"
                pass

            # Price
            try:
                if "price" in package:
                    initial = str(package["price"]["initial"])
                    base_price = f"R$ {initial[:-2]},{initial[-2:]}"
                    final = str(package["price"]["final"])
                    current_price = f"R$ {final[:-2]},{final[-2:]}"
                    discount = f'{package["price"]["discount_percent"]}%'
                    price = f"🔸 Base: {base_price} \n🔹 Atual: {current_price} \n 📉 Desconto: {discount}"
                else:
                    price = f"💸 GRATUITO"
            except:
                price = "\u200b"
                pass

            # # EMBED
            # Defining Embed
            steam_game_embed = discord.Embed(
                title=f'{steam_game["name"]}',
                colour=discord.Colour(0xFF3030),
                description=f'📆 **Data de lançamento:** {steam_game["release_date"]["date"]}\n'
                + f'🏷 **Tipo:** {steam_game["type"].upper()}\n'
                + f'{steam_game["short_description"]}',
                url=f'https://store.steampowered.com/app/{str(steam_game["steam_appid"])}/{quote(steam_game["name"])}',
            )

            # Setting Image and Footer
            steam_game_embed.set_image(url=f'{steam_game["header_image"]}')
            try:
                steam_game_embed.set_footer(text=f'{steam_game["legal_notice"]}')
                if steam_game_embed.footer.__len__ > 2048:
                    raise Exception
            except:
                steam_game_embed.set_footer(text=f'©{steam_game["name"]}')

            # Adding Fields
            steam_game_embed.add_field(name="📌 Desenvolvedor: ", value=developers, inline=True)
            steam_game_embed.add_field(name="📌 Publisher: ", value=publishers, inline=True)
            steam_game_embed.add_field(
                name="📌 Avaliações: ",
                value=f"{big_picture.EMOJI_METACRITIC} {metacritic_score}\n\n"
                + f'{reviews_dict["label"]}\n {reviews_dict["score"]}',
                inline=True,
            )

            steam_game_embed.add_field(name="📌 Tags: ", value=tags, inline=True)
            steam_game_embed.add_field(name="📌 Idiomas: ", value=languages, inline=True)
            steam_game_embed.add_field(name="📌 Recursos: ", value=categories, inline=True)

            # Separates the Game Info of the Package Info
            line = "------------------------------------------------------------------------------"
            steam_game_embed.add_field(name="\u200b", value=line, inline=False)

            if package != []:
                steam_game_embed.add_field(
                    name=f'**PACOTE**\n📌 {package["name"]}: ',
                    value=f"{includes}",
                    inline=False,
                )
                steam_game_embed.add_field(name="📌 Preço: ", value=price, inline=True)
            else:
                steam_game_embed.add_field(name="📌 Preço: ", value=f"---", inline=True)

            return steam_game_embed  # Return the resultant page

        # # # END OF INTERN FUNCTIONS
        #
        #

        steam_games = []
        steamspy_games_info = []
        packages = []
        # # Get steam_game
        try:
            steam_games = big_picture.get_steam_game(game_title=game_title)
            if steam_games == []:
                raise Exception

            steamspy_games_info = [big_picture.steamspy_complementary_info(app["steam_appid"]) for app in steam_games]

            # Packages can't be obtained by List Comprehension because 'Packages' is not a key that all items have
            for app in steam_games:
                try:
                    packages.append(big_picture.get_steam_package(app["packages"]))
                except:
                    packages.append([[]])
        except:
            await ctx.send(
                embed=discord.Embed(
                    title="Desculpe",
                    description=f'Não consegui encontrar esse jogo!\nCaso seja a primeira consulta do dia, considere executar o comando "!steam-update" para atualizar os dados',
                )
            )
            return

        # Start on Page 0, Package 0
        page = steam_pages_layout(i=0, j=0)

        message = await ctx.send(embed=page)

        # # Handling with Reactions
        await message.add_reaction(EMOJI_ORANGE_BACK)
        await message.add_reaction(EMOJI_ORANGE_PLAY)
        await message.add_reaction("◀")
        await message.add_reaction("▶")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author

        i = 0
        j = 0
        reaction = None

        while True:
            if str(reaction) == EMOJI_ORANGE_BACK:
                j = 0
                if i > 0:
                    i -= 1
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)
                elif i == 0:
                    i = len(steam_games) - 1
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)

            elif str(reaction) == EMOJI_ORANGE_PLAY:
                j = 0
                if i < len(steam_games) - 1:
                    i += 1
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)
                elif i == len(steam_games) - 1:
                    i = 0
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)

            elif str(reaction) == "◀":
                if j > 0:
                    j -= 1
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)
                elif j == 0:
                    j = len(packages[i]) - 1
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)

            elif str(reaction) == "▶":
                if j < len(packages[i]) - 1:
                    j += 1
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)
                elif j == len(packages[i]) - 1:
                    j = 0
                    page = steam_pages_layout(i, j)
                    await message.edit(embed=page)

            elif str(reaction) == "❌":
                await message.clear_reactions()
                await message.delete()

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
            except:
                break

        await message.clear_reactions()


def setup(bot):
    bot.add_cog(StoreSteam(bot))
