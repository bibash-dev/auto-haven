from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    DB_URL: Optional[str] = Field(default=None, alias="DB_URL")
    DB_NAME: Optional[str] = Field(default=None, alias="DB_NAME")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
