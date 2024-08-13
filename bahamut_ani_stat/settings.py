from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bs4_parser: str = "lxml"


settings = Settings()
