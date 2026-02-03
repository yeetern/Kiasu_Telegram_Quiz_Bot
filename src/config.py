"""
Configuration Management - Project Kancil
Uses Pydantic Settings to manage environment variables, secrets, 
and database connection strings with type safety.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """
    # Telegram Bot Token (Wrapped in SecretStr to prevent accidental logging)
    BOT_TOKEN: SecretStr
    
    # Database Connection Credentials
    POSTGRES_USER: str = "kiasu_user"
    POSTGRES_PASSWORD: str = "kiasu_password"
    POSTGRES_DB: str = "kiasu_db"
    POSTGRES_HOST: str = "db"  # Defaults to Docker service name 'db'
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        """
        Constructs the SQLAlchemy asynchronous connection string.
        Uses the asyncpg driver for non-blocking database I/O.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Configuration for .env file loading
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Export as a singleton instance for global use
config = Settings()