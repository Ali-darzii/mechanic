import os
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Setting(BaseSettings):
    DOTENV_PATH: str = os.path.join(os.path.dirname(__file__), ".env")

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8",
    )

    APP_HOST: str
    APP_PORT: int
    DEBUG: bool

    SSL: int
    SSL_CERT: str | None
    SSL_KEY: str | None

    ROUTES_PREFIX: str = "/API"

    SECRET_KEY: str
    JWT_ALGORITHM: str

    ACCESS_EXPIRE: int
    REFRESH_EXPIRE: int
    OTP_EXPIRE: int

    SMS_PANEL:str
    SMS_ENDPOINT:str
    SMS_USER:str
    SMS_PASSWORD:str
    SMS_ORIGINATOR:str

    POSTGRE_HOST: str
    POSTGRE_PORT: str
    POSTGRE_USER: str
    POSTGRE_PASS: str
    POSTGRE_DB: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_BROKER_DB: str
    REDIS_CACHE_DB: str

    @computed_field
    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRE_USER}:{self.POSTGRE_PASS}@{self.POSTGRE_HOST}:{self.POSTGRE_PORT}/{self.POSTGRE_DB}"
    
    @computed_field
    @property
    def REDIS_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_BROKER_DB}"

    @computed_field
    @property
    def REDIS_CACHE_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_CACHE_DB}"
    

@lru_cache
def get_setting() -> Setting:
    return Setting()
