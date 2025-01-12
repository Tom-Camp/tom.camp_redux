from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Tom.Camp"
    database_url: str
    database_name: str
    secret_key: str
    hash_algorithm: str

    class Config:
        env_file = ".env"


settings = Settings()
