from pydantic import BaseSettings


class Settings(BaseSettings):
    bs4_parser: str = "lxml"


settings = Settings()
