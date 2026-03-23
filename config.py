# config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str = "sk-dummy-key"
    telegram_token: str = "8756799497:AAEkWuu6pp0o0Gxe2YENPDyoVo-HNKexMNk"
    admin_id: int = 6792300623
    
    class Config:
        env_file = ".env"


settings = Settings()
