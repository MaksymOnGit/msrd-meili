import asyncio

import meilisearch
from confluent_kafka import DeserializingConsumer
from meilisearch import Client

from msrdmeili.dto.document_dto import Document
from msrdmeili.kafka.dependencies import get_kafka_consumer
from msrdmeili.kafka.models.mongo_base import MongoBase
from msrdmeili.settings import settings
from loguru import logger


async def documents_consumer():
    async with get_kafka_consumer() as consumer:
        des_cons: DeserializingConsumer = consumer
        des_cons.subscribe(["MsrdDocuments.documents"])
        client = meilisearch.Client(settings.meilisearch_url)
        while True:
            msg = des_cons.poll(timeout=1)
            if msg is None:
                continue

            mongo_base: MongoBase = msg.value()

            if mongo_base.operation_type == 'insert' or mongo_base.operation_type == 'update':
                try:
                    doc = Document(**mongo_base.full_document)
                    result = await process_document(client, doc)
                    if not result:
                        continue
                except Exception:
                    raise

            consumer.commit(asynchronous=True)


async def process_document(client: Client, doc: Document) -> bool:
    task = client.index('documents').add_documents(doc.dict())
    while True:
        await asyncio.sleep(0.1)
        task = task.parse_obj(client.get_task(task.task_uid))
        if task.status == "succeeded":
            logger.info("Successfully added/updated meilisearch document with: {}", doc)
            return True
        if task.status == "failed":
            logger.error("Failed to add/update meilisearch document: {} status: {}", doc, task)
            return False

    return False
