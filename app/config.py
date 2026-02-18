from pydantic_settings import SettingsConfigDict, BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_KEY: str
    JWT_ALGORITHM: str
    REFRESH_TOKEN_EXPIRE: int
    ACCESS_TOKEN_EXPIRE: int
    MAX_FILE_SIZE: int
    MAX_FILE_UPLOAD: int
    DOMAIN: str
    API_VERSION: str
    RANGE: int

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"), extra="ignore"
    )


Config = Settings()  # type: ignore
