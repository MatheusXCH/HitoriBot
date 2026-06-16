from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    discord_token: str
    discord_owner_id: int

    postgres_host: str = "192.168.15.206"
    postgres_port: int = 5432
    postgres_db: str = "hitoribot"
    postgres_user: str
    postgres_password: str

    opencode_api_key: str = ""
    opencode_base_url: str = "https://opencode.ai/zen/go/v1"

    itad_api_key: str = ""

    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "HitoriBot/2.0"

    sounds_path: str = "/app/data/sounds"
    stickers_path: str = "/app/data/stickers"

    model_config = {"env_file": ".env"}


settings = Settings()
