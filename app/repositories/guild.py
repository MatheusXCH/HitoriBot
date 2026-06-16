import asyncpg


async def get_or_create_guild(pool: asyncpg.Pool, guild_id: int, guild_name: str) -> None:
    existing = await pool.fetchrow("SELECT guild_id FROM guilds WHERE guild_id = $1", guild_id)
    if existing:
        return
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO guilds (guild_id, guild_name) VALUES ($1, $2)",
                guild_id, guild_name,
            )
            await conn.execute(
                "INSERT INTO guild_settings (guild_id) VALUES ($1)",
                guild_id,
            )


async def delete_guild(pool: asyncpg.Pool, guild_id: int) -> None:
    await pool.execute("DELETE FROM guilds WHERE guild_id = $1", guild_id)


async def get_settings(pool: asyncpg.Pool, guild_id: int) -> asyncpg.Record | None:
    return await pool.fetchrow(
        "SELECT * FROM guild_settings WHERE guild_id = $1", guild_id
    )
