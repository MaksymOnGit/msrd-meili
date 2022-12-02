import asyncio

from confluent_kafka import DeserializingConsumer
import meilisearch
from meilisearch import Client

from msrdmeili.dto.product_dto import Product
from msrdmeili.kafka.dependencies import get_kafka_consumer
from msrdmeili.kafka.models.mongo_base import MongoBase
from msrdmeili.settings import settings
from loguru import logger


async def products_consumer():
    async with get_kafka_consumer() as consumer:
        des_cons: DeserializingConsumer = consumer
        des_cons.subscribe(["MsrdProducts.products"])
        client = meilisearch.Client(settings.meilisearch_url)
        client.index('products').update_settings({
            'sortableAttributes': ['id', 'name', 'quantity', 'created_at', 'updated_at']
        })
        while True:
            msg = des_cons.poll(timeout=1)
            if msg is None:
                continue

            mongo_base: MongoBase = msg.value()

            if mongo_base.operation_type == 'insert' or \
                    mongo_base.operation_type == 'update' or \
                    mongo_base.operation_type == 'replace':
                try:
                    product = Product(**mongo_base.full_document)
                    result = await process_document(client, product)
                    if not result:
                        continue
                except Exception:
                    raise

            consumer.commit(asynchronous=True)


async def process_document(client: Client, product: Product) -> bool:
    task = client.index('products').add_documents(product.dict())

    retry_count = 0
    while task.task_uid is None and retry_count < 5:
        task = client.index('products').add_documents(product.dict())
        retry_count = retry_count + 1

    if task.task_uid is None:
        return False

    task_uid = task.task_uid

    while True:
        await asyncio.sleep(0.1)
        task = task.parse_obj(client.get_task(task_uid))
        if task.status == "succeeded":
            logger.info("Successfully added/updated meilisearch product with: {}", product)
            return True
        if task.status == "failed":
            logger.error("Failed to add/update meilisearch product: {} status: {}", product, task)
            return False

    return False
