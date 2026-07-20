from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List


class CommonConfig(BaseSettings):
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


class BotConfig(CommonConfig):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    admins: List[int] = Field(default_factory=list, alias="ADMINS")
    channel_id: int = Field(..., alias="CHANNEL_ID")
    channel_link: str = Field(..., alias="CHANNEL_LINK")


class RedisConfig(CommonConfig):
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")


class DatabaseConfig(CommonConfig):
    db_name: str = Field(..., alias="DB_NAME")
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(..., alias="DB_PORT")

    def sqlalchemy_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class Settings:
    bot = BotConfig()
    redis = RedisConfig()
    database = DatabaseConfig()


config = Settings()
