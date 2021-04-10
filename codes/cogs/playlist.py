import asyncio
import codecs
import os
import random

# Get the globals from Settings
import codes.paths as path
import discord
import dotenv
import pymongo
from pprint import pprint
from discord.ext import commands
from discord.ext.commands import MissingPermissions, has_permissions
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
CONNECT_STRING = os.environ.get("MONGODB_URI")
timeout_limit = 15

# NOTE: Os comandos de Playlist não serão disponíveis para todos os membros dos servidores
# TODO Adicionar as permissões necessárias para utilizar os comandos


class Playlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, ctx: commands.Context, error):
        if isinstance(error, MissingPermissions):
            return f"Desculpe {ctx.author.mention}, você não tem permissão para fazer isso!"

    def _timeout_message(self, ctx: commands.Context):
        return f"Desculpe {ctx.author.mention}, parece que você demorou demais para informar o que foi solicitado... 😅"

    def _get_all_playlist_names(self, collection, ctx: commands.Context):
        playlist = collection.find_one(
            {"_id": ctx.guild.id}, {"settings.playlist": {"playlist_name": 1, "playlist_url": 1}}
        )
        playlists_names = " | ".join([item["playlist_name"] for item in playlist["settings"]["playlist"]])

        return playlists_names

    # WORKING
    @commands.command(name="add-playlist")
    @has_permissions(manage_channels=True, manage_guild=True)
    async def add_playlist(self, ctx: commands.Context):
        """!add-playlist => Adiciona um novo item à lista de playlists do servidor
        - É preciso permissão para gerenciar: canais, guilda
        """

        def check(message):
            return message.author == ctx.message.author

        await ctx.send(f"{ctx.author.mention}, qual o nome da nova Playlist?")

        try:
            playlist_name_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
            playlist_name = playlist_name_msg.content
        except asyncio.TimeoutError:
            return await ctx.send(self._timeout_message(ctx))

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")

                playlists_names = self._get_all_playlist_names(collection, ctx)

                if playlist_name.upper() in playlists_names.upper():
                    return await ctx.send(
                        f"Hmmm... Parece que a Playlist **{playlist_name}** já existe.\n"
                        "Por favor, execute o comando novamente e tente outro nome!"
                    )

                await ctx.send(f"{ctx.author.mention}, qual é o URL da Playlist?")

                try:
                    playlist_url_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                    playlist_url = playlist_url_msg.content
                except asyncio.TimeoutError:
                    return await ctx.send(self._timeout_message(ctx))

                collection = client.get_database("discordzada").get_collection("guilds_settings")
                collection.update_one(
                    {"_id": ctx.guild.id},
                    {
                        "$push": {
                            "settings.playlist": {
                                "playlist_name": playlist_name,
                                "playlist_url": playlist_url,
                            }
                        }
                    },
                )
                await ctx.send(f"A Playlist **{playlist_name}** foi salva 💾")

        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao salvar a **playlist** no banco de dados."
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor em {path.dev_contact}."
            )
            print(
                f"COMMAND >> 'add-playlist' ERROR: Não foi possível salvar a Playlist da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    @add_playlist.error
    async def add_playlist_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.command(name="del-playlist")
    @has_permissions(manage_channels=True, manage_guild=True)
    async def del_playlist(self, ctx: commands.Context):
        """!del-playlist => Remove um item da lista de playlists do servidor
        - É preciso permissão para gerenciar: canais, guilda
        """

        def check(message):
            return message.author == ctx.message.author

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                playlists_names = self._get_all_playlist_names(collection, ctx)

                await ctx.send(
                    f"Informe o nome da Playlist que deseja excluir. Abaixo, estão listadas todas as playlists em **{ctx.guild.name}**:"
                )
                await ctx.send(embed=discord.Embed(title=playlists_names))

                try:
                    playlist_to_delete_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                    playlist_to_delete = playlist_to_delete_msg.content
                except asyncio.TimeoutError:
                    return await ctx.send(
                        f"Desculpe {ctx.author.mention}, você demorou demais para informar o nome da Playlist 😅"
                    )

                try:
                    query_result = collection.find_one_and_update(
                        {"_id": ctx.guild.id, "settings.playlist.playlist_name": playlist_to_delete},
                        {"$pull": {"settings.playlist": {"playlist_name": playlist_to_delete}}},
                    )
                    if query_result is not None:
                        await ctx.send(f"A Playlist **{playlist_to_delete}** foi excluída com sucesso 👌")
                    else:
                        await ctx.send(
                            f"Hmmm... {ctx.author.mention}, parece que a playlist {playlist_to_delete} não existe 🙃"
                        )
                except Exception as e:
                    print(e)

        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao excluir a **playlist** no banco de dados."
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor {path.dev_contact}."
            )
            print(
                f"COMMAND >> 'del-playlist' ERROR: Não foi possível excluir a Playlist da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    @del_playlist.error
    async def del_playlist_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.command(name="edit-playlist")
    @has_permissions(manage_channels=True, manage_guild=True)
    async def edit_playlist(self, ctx: commands.Context):
        """!edit-playlist => Edita um item da lista de playlists do servidor.
        - É possível editar o nome, URL ou ambos
        - É preciso permissão para gerenciar: canais, guilda
        """

        def check(message):
            return message.author == ctx.message.author

        def choice_validate(choice):
            if choice.content != "1" and choice.content != "2" and choice.content != "3":
                if (
                    choice.content.upper() != "NOME"
                    and choice.content.upper() != "URL"
                    and choice.content.upper() != "AMBOS"
                ):
                    return False
            return True

        await ctx.send(
            f"Vamos lá, {ctx.author.mention}... O que deseja atualizar? \n**1)** Nome \n**2)** URL \n**3)** Ambos"
        )

        try:
            choice = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
        except asyncio.TimeoutError:
            return await ctx.send(self._timeout_message(ctx))

        if not choice_validate(choice):
            return await ctx.send(
                f"Desculpe {ctx.author.mention}, essa opção é inválida! Tente utilizar o comando novamente!"
            )

        try:
            with MongoClient(CONNECT_STRING) as client:
                collection = client.get_database("discordzada").get_collection("guilds_settings")
                playlists_names = self._get_all_playlist_names(collection, ctx)

                await ctx.send(
                    f"Informe o nome da Playlist que deseja atualizar. Abaixo, estão listadas todas as playlists em **{ctx.guild.name}**:"
                )
                await ctx.send(embed=discord.Embed(title=playlists_names))

                try:
                    playlist_to_update = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                    old_name = playlist_to_update.content
                except asyncio.TimeoutError:
                    return await ctx.send(self._timeout_message(ctx))

                if old_name.upper() not in playlists_names.upper():
                    return await ctx.send(
                        f"Hmmm... {ctx.author.mention}, parece que a playlist **{old_name}** não existe 🙃"
                    )

                if choice.content == "1" or choice.content.upper() == "NOME":
                    await ctx.send(f"Qual o novo nome para a Playlist **{old_name}**?")
                    try:
                        new_name_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                        new_name = new_name_msg.content
                    except asyncio.TimeoutError:
                        await ctx.send(self._timeout_message(ctx))

                    validate_query = collection.find_one_and_update(
                        {"_id": ctx.guild.id, "settings.playlist.playlist_name": old_name},
                        {"$set": {"settings.playlist.$.playlist_name": new_name}},
                    )

                    if validate_query is not None:
                        return await ctx.send(f"A Playlist **{old_name}** agora se chama **{new_name}** 👏")

                elif choice.content == "2" or choice.content.upper() == "URL":
                    await ctx.send(f"Qual o novo nome para a Playlist **{old_name}**?")
                    try:
                        new_url_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                        new_url = new_url_msg.content
                    except asyncio.TimeoutError:
                        await ctx.send(self._timeout_message(ctx))

                    validate_query = collection.find_one_and_update(
                        {"_id": ctx.guild.id, "settings.playlist.playlist_name": old_name},
                        {"$set": {"settings.playlist.$.playlist_url": new_url}},
                    )

                    if validate_query is not None:
                        return await ctx.send(f"A Playlist **{old_name}** agora se possui o **URL:**{new_url} 👏")

                elif choice.content == "3" or choice.content.upper() == "AMBOS":
                    await ctx.send(f"Qual o novo nome para a Playlist **{old_name}**?")
                    try:
                        new_name_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                        new_name = new_name_msg.content
                    except asyncio.TimeoutError:
                        await ctx.send(self._timeout_message(ctx))

                    await ctx.send(f"Qual o novo URL para a Playlist **{new_name}**?")
                    try:
                        new_url_msg = await self.bot.wait_for("message", check=check, timeout=timeout_limit)
                        new_url = new_url_msg.content
                    except asyncio.TimeoutError:
                        await ctx.send(self._timeout_message(ctx))

                    validate_query = collection.find_one_and_update(
                        {"_id": ctx.guild.id, "settings.playlist.playlist_name": old_name},
                        {"$set": {"settings.playlist.$": {"playlist_name": new_name, "playlist_url": new_url}}},
                    )

                    if validate_query is not None:
                        return await ctx.send(
                            f"A Playlist **{old_name}** agora se chama **{new_name}** e possui o **URL:**{new_url} 👏"
                        )
        except Exception as e:
            await ctx.send(
                f"Sinto muito {ctx.author.mention}, houve um problema ao excluir a **playlist** no banco de dados."
                f"Tente novamente mais tarde.\nSe o problema persistir, informe o desenvolvedor {path.dev_contact}."
            )
            print(
                f"COMMAND >> 'edit-playlist' ERROR: Não foi possível editar a Playlist da guilda ID:{ctx.guild.id} no database."
            )
            print(e)

    @edit_playlist.error
    async def edit_playlist_error(self, ctx: commands.Context, error):
        await ctx.send(self.error_message(ctx, error))

    # WORKING
    @commands.command(name="playlist")
    async def playlist(self, ctx: commands.Context):
        """!playlist => Lista as playlists feitas para o servidor"""

        embed = discord.Embed(
            title=":notes: **Playlists do Servidor** :notes:",
            colour=discord.Colour(0x32A852),
            description="Aqui estão os **links das playlists** elaboradas para este servidor:",
        )

        with MongoClient(CONNECT_STRING) as client:
            collection = client.get_database("discordzada").get_collection("guilds_settings")
            playlists = collection.find_one(
                {"_id": ctx.guild.id}, {"settings.playlist": {"playlist_name": 1, "playlist_url": 1}}
            )

            for playlist in playlists["settings"]["playlist"]:
                embed.add_field(
                    name=f":play_pause: {playlist['playlist_name']}:",
                    value=f"{playlist['playlist_url']}",
                    inline=False,
                )

            msg = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await msg.delete()


def setup(bot: commands.Bot):
    bot.add_cog(Playlist(bot))
