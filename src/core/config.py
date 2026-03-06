import logging
import multiprocessing
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# Defaults values
# =========================
LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)16s:%(lineno)-3d %(levelname)-8s - %(message)s"
)
LOG_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATABASE_DEFAULT_URL = "sqlite+aiosqlite:///db.sqlite3"


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    users_prefix: str = "/users"


class ApiPrefixSettings(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseSettings(BaseModel):
    url: str = DATABASE_DEFAULT_URL
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "pk": "pk_%(table_name)s",
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }


class GunicornSettings(BaseModel):
    workers: Optional[int] = None
    timeout: int = 900
    keepalive: int = 5
    preload_app: bool = False

    @property
    def resolved_workers(self) -> int:
        return self.workers or (multiprocessing.cpu_count() * 2 + 1)


class LoggingSettings(BaseModel):
    level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"

    fmt: str = LOG_DEFAULT_FORMAT
    date_fmt: str = LOG_DEFAULT_DATE_FORMAT

    access: bool = True
    file_enabled: bool = False
    file_path: Path = Path("app.log")

    @property
    def resolved_level(self) -> int:
        return getattr(
            logging,
            self.level.upper(),
            logging.INFO,
        )


class RunSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


# =========================
# Root settings
# =========================
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="CONFIG__",
        env_file=".env",
        env_nested_delimiter="__",
    )

    api: ApiPrefixSettings = ApiPrefixSettings()
    db: DatabaseSettings = DatabaseSettings()
    gunicorn: GunicornSettings = GunicornSettings()
    logging: LoggingSettings = LoggingSettings()
    run: RunSettings = RunSettings()


settings = Settings()
