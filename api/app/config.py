from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    site_name: str = "ContexteTech"
    public_origin: str = "https://localhost"
    cookie_secure: bool = True
    session_days: int = 30

    # PostgreSQL (Scaleway Managed Database)
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "contextec"
    postgres_user: str = "contextec"
    postgres_password: str = ""
    postgres_sslmode: str = "require"          # disable | require | verify-full
    postgres_sslrootcert: str = ""

    redis_url: str = "redis://redis:6379/0"

    # Bac à sable
    llm_provider: str = ""                     # anthropic | openai | ""
    anthropic_api_key: str = ""
    llm_base_url: str = "http://ollama:11434/v1"
    llm_api_key: str = ""
    llm_model_quick: str = ""
    llm_model_default: str = ""
    llm_model_complex: str = ""
    llm_max_tokens: int = 1024
    sample_rate_per_min: int = 10

    # Stockage objet (Scaleway Object Storage, compatible S3) pour les gros datasets
    s3_endpoint: str = ""                      # ex. https://s3.fr-par.scw.cloud
    s3_region: str = "fr-par"
    s3_bucket: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""

    # E-mails (SMTP de Proton) : vide = aucun envoi
    smtp_host: str = ""                        # smtp.protonmail.ch
    smtp_port: int = 587
    smtp_starttls: bool = True                 # False uniquement pour un serveur de test local
    smtp_user: str = ""                        # coucou@contextetech.com
    smtp_password: str = ""                    # jeton SMTP généré dans Proton
    smtp_from: str = ""                        # ContexteTech <coucou@contextetech.com>
    mail_bcc: str = ""                         # copie cachée des e-mails d'inscription et de connexion
    max_resource_kb: int = 256
    max_dataset_mb: int = 50

    # Administrateur créé au démarrage
    admin_username: str = ""
    admin_password: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def s3_enabled(self) -> bool:
        return bool(self.s3_endpoint and self.s3_bucket and self.s3_access_key and self.s3_secret_key)

    @property
    def llm_models(self) -> dict[str, str]:
        defaults = {
            "anthropic": {"quick": "claude-haiku-4-5", "default": "claude-sonnet-5", "complex": "claude-opus-5-5"},
            "openai": {"quick": "qwen2.5:7b-instruct", "default": "qwen2.5:7b-instruct", "complex": "qwen2.5:7b-instruct"},
        }.get(self.llm_provider, {})
        return {
            "quick": self.llm_model_quick or defaults.get("quick", ""),
            "default": self.llm_model_default or defaults.get("default", ""),
            "complex": self.llm_model_complex or defaults.get("complex", ""),
        }

    @property
    def llm_enabled(self) -> bool:
        if self.llm_provider == "anthropic":
            return bool(self.anthropic_api_key)
        return self.llm_provider == "openai"


@lru_cache
def get_settings() -> Settings:
    return Settings()
