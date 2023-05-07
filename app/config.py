from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, Field


class Setting(BaseSettings):
    db_uri: str = Field(..., env='MONGODB_URI')
    secret_key: str = Field(...)
    base_dir: Path = Path(__file__).resolve().parent
    algolia_app_id: str = Field(...)
    algolia_api_key: str = Field(...)
    algolia_index_name: str = Field(...)

    class Config:
        env_file = '.env'


@lru_cache
def get_settings():
    return Setting()
