import os
from pathlib import Path
# This is a built-in package for validating data also suitable for loading environment variables
from pydantic import BaseSettings, Field
from functools import lru_cache


os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = '1'
class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent
    templates_dir: Path = base_dir / 'templates'
    keyspace: str = Field(..., env="ASTRADB_KEYSPACE")
    db_client_id: str = Field(..., env="DB_CLIENT_ID")
    db_client_secret: str = Field(..., env="DB_CLIENT_SECRET")
    secret_key: str = Field(..., env="SECRET_KEY")
    token_expiration_time: int = Field(default=86400 * 24)
    jwt_algorithm: str = Field(default='HS256')

    algolia_api_key: str
    algolia_app_id:str
    algolia_index_name: str

    class Config:
        env_file = '.env'


@lru_cache
def get_settings():
    return Settings()