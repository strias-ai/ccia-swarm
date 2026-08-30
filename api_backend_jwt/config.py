import sys
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database configuration
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Logging configuration
    LOGGING_LEVEL: str = "INFO"
    LOGGING_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    LOGGING_FILE: str = "app.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

if __name__ == "__main__":
    config = Config()
    print(f"Configured with SECRET_KEY: {config.SECRET_KEY}")
    print(f"Configured with SQLALCHEMY_DATABASE_URL: {config.SQLALCHEMY_DATABASE_URL}")
    print(f"Configured with LOGGING_LEVEL: {config.LOGGING_LEVEL}")