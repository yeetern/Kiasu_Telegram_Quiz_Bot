from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Bot Token (从 .env 读取)
    BOT_TOKEN: SecretStr
    
    # Database Config
    POSTGRES_USER: str = "kiasu_user"
    POSTGRES_PASSWORD: str = "kiasu_password"
    POSTGRES_DB: str = "kiasu_db"
    POSTGRES_HOST: str = "db"  # Docker service name
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        # 构造 SQLAlchemy 连接字符串
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 单例模式导出配置
config = Settings()