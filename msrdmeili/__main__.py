import asyncio

from msrdmeili.kafka.consumers.documents_consumer import documents_consumer
from msrdmeili.kafka.consumers.products_consumer import products_consumer
from msrdmeili.settings import settings, AppMode


def main() -> None:
    """Entrypoint of the application."""

    if settings.app_mode == AppMode.DOCUMENT_CONSUMER:
        asyncio.run(documents_consumer())
        return

    if settings.app_mode == AppMode.PRODUCT_CONSUMER:
        asyncio.run(products_consumer())
        return


if __name__ == "__main__":
    main()
