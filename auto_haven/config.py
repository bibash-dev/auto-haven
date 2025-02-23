from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    MONGODB_URL: Optional[str] = Field(default=None, alias="MONGODB_URL")
    MONGODB_NAME: Optional[str] = Field(default=None, alias="MONGODB_NAME")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
