from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    SMTP_HOST: str= "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 2525
    SMTP_USERNAME: str = "e862c29c14dfe1"
    SMTP_PASSWORD: str = "4e8d80d497c8f2"
    EMAIL_FROM: str = "shaiksumiya401@gmail.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()