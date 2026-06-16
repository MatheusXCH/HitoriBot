import json
import asyncpg
import discord
from openai import AsyncOpenAI
from config import settings

from integrations.steam import search_game
from integrations.itad import get_game_price
from integrations.hltb import get_completion_time
from integrations.freegame import get_free_games
from integrations.anilist import search_anime, search_manga, search_character
from integrations.wikipedia import wikipedia_summary
from repositories.server import (
    get_server_rules,
    get_server_info,
    get_sounds_library,
    get_stickers_library,
    get_playlists,
    register_sound,
    delete_sound,
    register_sticker,
    delete_sticker,
    register_playlist,
    delete_playlist,
)

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.opencode_api_key, base_url=settings.opencode_base_url)
    return _client


SYSTEM_PROMPT = """You are HitoriBot, a friendly Discord assistant for this server.
You speak in the same language as the user (pt-BR by default).

You have access to tools that retrieve information and manage server resources.
When the user asks about something, pick the right tool and use it.
For registrations (sounds, stickers, playlists), guide the user step-by-step:
  ask for the name, ask them to attach a file if needed, then call the write tool.
Do NOT handle administrative commands (bans, kicks, module reload, etc.).

## Regra crítica sobre resultados de ferramentas
Quando uma ferramenta retorna dados (info de jogo, preços, anime, personagem, tempos HLTB,
listas de biblioteca, etc.), esses dados JÁ estão exibidos ao usuário como um embed do Discord.
NUNCA repita, resuma ou reformule o conteúdo do embed no seu texto.
NUNCA diga coisas como "O embed apareceu" ou "Como você pode ver acima".
Após uma chamada de ferramenta que retorna dados:
- Diga no MÁXIMO uma frase curtíssima (ex: "Aqui estão! 🎮") — ou não diga nada.
Após uma operação de escrita (cadastro, remoção), confirme em uma frase.
Se não puder ajudar, diga educadamente e sugira o slash command relevante."""

TOOLS = [
    {"type": "function", "function": {"name": "search_game", "description": "Search Steam for a game and return details + HowLongToBeat times.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "get_game_price", "description": "Get current and historical prices from IsThereAnyDeal for a game.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "get_completion_time", "description": "Get HowLongToBeat completion times for a game.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "get_free_games", "description": "List current free games from r/FreeGameFindings.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "search_anime", "description": "Search AniList for an anime.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "search_manga", "description": "Search AniList for a manga.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "search_character", "description": "Search AniList for an anime/manga character.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "wikipedia_summary", "description": "Get a Wikipedia article summary.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "get_server_rules", "description": "Return the server rules.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_server_info", "description": "Return server stats (members, sounds, stickers, playlists count).", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_sounds_library", "description": "List all registered sounds in this server.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_stickers_library", "description": "List all registered stickers in this server.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_playlists", "description": "List all registered playlists in this server.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "register_sound", "description": "Register a new sound in the server library. Requires the user to attach an audio file.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "attachment_url": {"type": "string"}, "filename": {"type": "string"}}, "required": ["name", "attachment_url", "filename"]}}},
    {"type": "function", "function": {"name": "delete_sound", "description": "Delete a sound from the server library.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "register_sticker", "description": "Register a new sticker in the server library. Requires the user to attach an image file.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "attachment_url": {"type": "string"}, "filename": {"type": "string"}}, "required": ["name", "attachment_url", "filename"]}}},
    {"type": "function", "function": {"name": "delete_sticker", "description": "Delete a sticker from the server library.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "register_playlist", "description": "Register a playlist with a name and URL.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "url": {"type": "string"}}, "required": ["name", "url"]}}},
    {"type": "function", "function": {"name": "delete_playlist", "description": "Delete a playlist from the server catalog.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
]


async def get_channel_context(pool: asyncpg.Pool, guild_id: int, channel_id: int, limit: int = 20) -> list[dict]:
    rows = await pool.fetch(
        "SELECT role, content FROM ai_context "
        "WHERE guild_id = $1 AND channel_id = $2 "
        "ORDER BY created_at DESC LIMIT $3",
        guild_id, channel_id, limit,
    )
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


async def save_message(pool: asyncpg.Pool, guild_id: int, channel_id: int, role: str, content: str) -> None:
    await pool.execute(
        "INSERT INTO ai_context (guild_id, channel_id, role, content) VALUES ($1, $2, $3, $4)",
        guild_id, channel_id, role, content,
    )


async def is_rate_limited(pool: asyncpg.Pool, guild_id: int, channel_id: int, limit: int = 10) -> bool:
    count = await pool.fetchval(
        "SELECT COUNT(*) FROM ai_context "
        "WHERE guild_id = $1 AND channel_id = $2 AND role = 'user' "
        "AND created_at > NOW() - INTERVAL '1 hour'",
        guild_id, channel_id,
    )
    return count >= limit


async def call_agent(
    pool: asyncpg.Pool,
    guild_id: int,
    channel_id: int,
    user_message: str,
    bot,
    attachments: list[dict] | None = None,
    user_id: int = 0,
) -> tuple[str | None, list[discord.Embed]]:
    content = user_message
    if attachments:
        attachment_info = "\n".join(f"[Attachment: {a['filename']} → {a['url']}]" for a in attachments)
        content = f"{user_message}\n{attachment_info}"

    await save_message(pool, guild_id, channel_id, "user", content)
    history = await get_channel_context(pool, guild_id, channel_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    embeds: list[discord.Embed] = []
    client = _get_client()

    response = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    message = response.choices[0].message

    if message.tool_calls:
        tool_results = []
        for tc in message.tool_calls:
            fn = tc.function.name
            args = json.loads(tc.function.arguments)
            result_text, embed = await _dispatch_tool(fn, args, pool, guild_id, channel_id, bot, user_id)
            if embed:
                embeds.extend(embed if isinstance(embed, list) else [embed])
            tool_results.append({"tool_call_id": tc.id, "role": "tool", "content": result_text or "done"})

        followup = await client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages + [message.model_dump()] + tool_results,
        )
        reply = followup.choices[0].message.content
    else:
        reply = message.content

    if reply:
        await save_message(pool, guild_id, channel_id, "assistant", reply)

    return reply, embeds


async def _dispatch_tool(
    name: str,
    args: dict,
    pool: asyncpg.Pool,
    guild_id: int,
    channel_id: int,
    bot,
    user_id: int = 0,
) -> tuple[str, discord.Embed | list[discord.Embed] | None]:
    match name:
        case "search_game":
            embeds = await search_game(args["title"])
            if not embeds:
                return "No results found on Steam for this title.", None
            return f"Found {len(embeds)} result(s) — embed displayed to user.", embeds
        case "get_game_price":
            embed = await get_game_price(args["title"])
            return "Price info retrieved — embed displayed to user.", embed
        case "get_completion_time":
            embed = await get_completion_time(args["title"])
            if not embed:
                return "No results found on HowLongToBeat. Try using the full/exact title, with Roman numerals for sequels (e.g. 'III' instead of '3').", None
            return "HLTB data retrieved — embed displayed to user.", embed
        case "get_free_games":
            embed = await get_free_games(pool)
            return "Free games listed — embed displayed to user.", embed
        case "search_anime":
            embeds = await search_anime(args["title"])
            if not embeds:
                return "No anime found for this title.", None
            return f"Found {len(embeds)} result(s) — embed displayed to user.", embeds
        case "search_manga":
            embeds = await search_manga(args["title"])
            if not embeds:
                return "No manga found for this title.", None
            return f"Found {len(embeds)} result(s) — embed displayed to user.", embeds
        case "search_character":
            embeds = await search_character(args["name"])
            if not embeds:
                return "No character found for this name.", None
            return f"Found {len(embeds)} result(s) — embed displayed to user.", embeds
        case "wikipedia_summary":
            embed = await wikipedia_summary(args["query"])
            if not embed:
                return "No Wikipedia article found.", None
            return "Wikipedia article retrieved — embed displayed to user.", embed
        case "get_server_rules":
            embed = await get_server_rules(pool, guild_id)
            return "Rules retrieved — embed displayed to user.", embed
        case "get_server_info":
            embed = await get_server_info(pool, guild_id, bot)
            return "Server info retrieved — embed displayed to user.", embed
        case "get_sounds_library":
            embed = await get_sounds_library(pool, guild_id)
            return "Sounds library listed — embed displayed to user.", embed
        case "get_stickers_library":
            embed = await get_stickers_library(pool, guild_id)
            return "Stickers library listed — embed displayed to user.", embed
        case "get_playlists":
            embed = await get_playlists(pool, guild_id)
            return "Playlists listed — embed displayed to user.", embed
        case "register_sound":
            text = await register_sound(pool, guild_id, args["name"], args["attachment_url"], args["filename"], uploaded_by=user_id)
            return text, None
        case "delete_sound":
            text = await delete_sound(pool, guild_id, args["name"])
            return text, None
        case "register_sticker":
            text = await register_sticker(pool, guild_id, args["name"], args["attachment_url"], args["filename"], uploaded_by=user_id)
            return text, None
        case "delete_sticker":
            text = await delete_sticker(pool, guild_id, args["name"])
            return text, None
        case "register_playlist":
            text = await register_playlist(pool, guild_id, args["name"], args["url"])
            return text, None
        case "delete_playlist":
            text = await delete_playlist(pool, guild_id, args["name"])
            return text, None
        case _:
            return f"Unknown tool: {name}", None
