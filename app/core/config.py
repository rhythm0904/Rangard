"""
app/core/config.py
──────────────────
Central configuration. All settings are read from environment variables
(or the .env file). Pydantic validates types automatically — if DATABASE_URL
is missing, the app crashes immediately with a clear error rather than
silently misbehaving later.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────
    APP_NAME: str = "RANGARD"
    APP_ENV: str = "development"
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # ── Database ───────────────────────────────────────────
    DATABASE_URL: str
    DATABASE_SYNC_URL: str

    # ── Redis ──────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # ── Email ──────────────────────────────────────────────
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "alerts@rangard.local"
    EMAIL_FROM_NAME: str = "RANGARD Security"

    # ── Blockchain ─────────────────────────────────────────
    INFURA_PROJECT_ID: str = ""
    ETHEREUM_NETWORK: str = "sepolia"
    CONTRACT_ADDRESS: str = "0x0000000000000000000000000000000000000000"
    WALLET_PRIVATE_KEY: str = ""

    # ── Storage ────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "rangard-files"
    IPFS_PROJECT_ID: str = ""
    IPFS_PROJECT_SECRET: str = ""

    # ── File scanning ──────────────────────────────────────
    QUARANTINE_DIR: str = "/tmp/rangard_quarantine"
    MAX_FILE_SIZE_MB: int = 50

    # ── Derived helpers ────────────────────────────────────
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def infura_rpc_url(self) -> str:
        return f"https://{self.ETHEREUM_NETWORK}.infura.io/v3/{self.INFURA_PROJECT_ID}"

    @property
    def max_file_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Use @lru_cache so Settings() is only instantiated once per process.
# Call `get_settings()` everywhere — never import Settings directly.
@lru_cache
def get_settings() -> Settings:
    return Settings()
