from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Application Agent"
    app_env: str = "development"
    app_debug: bool = False

    mysql_host: str = ""
    mysql_port: int = 0
    mysql_database: str = ""
    mysql_user: str = ""
    mysql_password: str = ""

    greenhouse_enabled: bool = False
    greenhouse_board_tokens: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def greenhouse_boards(self) -> tuple[str, ...]:
        """Return configured Greenhouse board tokens."""
        return tuple(
            token.strip() for token in self.greenhouse_board_tokens.split(",") if token.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
