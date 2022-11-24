import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic import BaseSettings

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class AppMode(str, enum.Enum):  # noqa: WPS600

    PRODUCT_CONSUMER = "PRODUCT_CONSUMER"
    DOCUMENT_CONSUMER = "DOCUMENT_CONSUMER"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    app_mode: AppMode


    kafka_bootstrap_servers: list[str] = ["msrdmeili-kafka:9092"]
    kafka_consumer_group: str = "msrd.meilisearchconsumer"
    kafka_schemaregistry_client: str = "http://schemaregistry0:8085"
    meilisearch_url: str = "http://meilisearch:7700"

    class Config:
        env_file = ".env"
        env_prefix = "MSRDMEILI_"
        env_file_encoding = "utf-8"


settings = Settings()
