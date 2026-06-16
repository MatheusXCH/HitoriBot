# HitoriBot V2

Bot Discord modular com agente IA integrado. Escrito em Python com discord.py, persistência em PostgreSQL e agente conversacional via OpenCode Go (DeepSeek V4 Flash).

## Estrutura do projeto

```
HitoriBot/
├── app/                        # Código-fonte Python
│   ├── bot.py                  # Entrypoint + classe HitoriBot
│   ├── config.py               # Configuração via variáveis de ambiente (Pydantic Settings)
│   │
│   ├── cogs/                   # Camada Discord — comandos slash e listeners
│   │   ├── admin.py            # Gestão de módulos com hot-reload (owner-only)
│   │   ├── ai.py               # Agente IA (menções) + /ai-toggle, /ai-clear
│   │   ├── anime.py            # /anime, /manga, /character — AniList GraphQL
│   │   ├── automod.py          # Filtro de palavras proibidas por guild
│   │   ├── events.py           # on_guild_join/remove, on_member_join
│   │   ├── games.py            # /game, /price, /freegames — Steam + ITAD + Reddit
│   │   ├── minigames.py        # /dice, /coin, /choose
│   │   ├── moderation.py       # kick, ban, unban, nick, roles, clear, purge
│   │   ├── playlist.py         # Catálogo de playlists por guild
│   │   ├── rules.py            # Regras do servidor por guild
│   │   ├── soundboard.py       # Biblioteca de sons por guild (áudio em VC)
│   │   └── stickers.py         # Biblioteca de stickers por guild
│   │
│   ├── core/                   # Infraestrutura do bot
│   │   ├── agent.py            # Orquestrador do agente IA — roteamento de tools, contexto, rate limit
│   │   └── database.py         # Pool asyncpg (PostgreSQL)
│   │
│   ├── repositories/           # Acesso a dados — SQL puro, sem lógica de negócio
│   │   ├── guild.py            # get_or_create_guild, delete_guild, get_settings
│   │   └── server.py           # Sons, stickers e playlists: leitura (embeds) + escrita (CRUD)
│   │
│   └── integrations/           # Wrappers de APIs externas → retornam discord.Embed
│       ├── anilist.py          # AniList GraphQL (anime, manga, personagem)
│       ├── freegame.py         # r/FreeGameFindings via AsyncPRAW
│       ├── hltb.py             # HowLongToBeat
│       ├── itad.py             # IsThereAnyDeal (preços + histórico)
│       ├── steam.py            # Steam Store API + SteamSpy
│       └── wikipedia.py        # Wikipedia REST API
│
├── db/
│   └── migrations/
│       └── 001_initial.sql     # Schema completo (guilds, settings, sons, stickers, playlists, IA)
│
├── tests/                      # Espelha app/
│   ├── core/test_agent.py
│   ├── integrations/test_steam.py
│   ├── repositories/
│   │   ├── test_guild.py
│   │   └── test_server.py
│   └── test_automod.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework Discord | discord.py 2.7.1 |
| Banco de dados | PostgreSQL (asyncpg 0.31.0) |
| Agente IA | OpenCode Go — DeepSeek V4 Flash (API OpenAI-compatible) |
| Deploy | Docker Compose |

## Configuração

Copie `.env.example` para `.env` e preencha:

```env
DISCORD_TOKEN=
DISCORD_OWNER_ID=

POSTGRES_HOST=192.168.15.206
POSTGRES_PORT=5432
POSTGRES_DB=hitoribot
POSTGRES_USER=hitoribot
POSTGRES_PASSWORD=

OPENCODE_API_KEY=
OPENCODE_BASE_URL=https://opencode.ai/zen/go/v1

ITAD_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
```

## Deploy

```bash
# Aplicar schema no PostgreSQL
psql -U hitoribot -d hitoribot < db/migrations/001_initial.sql

# Subir o container
docker compose up -d

# Verificar logs
docker logs -f hitoribot
```

## Desenvolvimento

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

O bot usa hot-reload de módulos — `/module-reload <cog>` atualiza um cog sem reiniciar o processo.

## Agente IA

O agente responde quando mencionado (`@HitoriBot`). Deve ser ativado por servidor com `/ai-toggle` (requer permissão de administrador). O contexto é mantido por canal (últimas 20 mensagens) com rate limit de 10 requisições por hora.

**Tools disponíveis:** Steam, ITAD, HowLongToBeat, jogos gratuitos, AniList (anime/manga/personagem), Wikipedia, regras do servidor, biblioteca de sons/stickers/playlists, e cadastro/remoção de sons, stickers e playlists via conversa.
