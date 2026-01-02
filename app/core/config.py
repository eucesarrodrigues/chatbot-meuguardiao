from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Meu Guardião"
    DEBUG: bool = False
    
    # Database Config
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "postgres"
    DB_PORT: str = "5432"
    DB_NAME: str = "meuguardiao"
    
    # AI Config
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AI_PROVIDER: str = "gemini"  # openai or gemini

    # Evolution API Config
    EVOLUTION_API_URL: str = "http://evolution:8080"
    EVOLUTION_API_KEY: str = ""
    INSTANCE_NAME: str = "meuguardiao"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgres://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
