from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    description: str = 'Сервис для поддержки котиков'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'

    secret: str = 'SECRET_KEY'

    superuser_email: str = 'admin@qrkot.ru'
    superuser_password: str = 'admin123'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()