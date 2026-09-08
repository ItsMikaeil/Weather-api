from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    weather_api_key: str
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()