from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bs4_parser: str = "lxml"


settings = Settings()
