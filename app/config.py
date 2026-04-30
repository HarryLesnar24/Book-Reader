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
    QDRANT_HOST: str
    QDRANT_PORT: int
    COLLECTION_NAME: str
    EMBEDDING_MODEL: str
    S3_BUCKET: str
    S3_ENDPOINT: str
    AWS_ACCESS_KEY_ID: str
    AWS_ACCESS_SECRET_KEY: str
    REGION: str

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"), extra="ignore"
    )


Config = Settings()  # type: ignore
