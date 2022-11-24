
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

from msrdmeili.kafka.util import commit_completed, map_to_base
from msrdmeili.settings import settings
from loguru import logger


@asynccontextmanager
async def get_kafka_consumer() -> AsyncGenerator[DeserializingConsumer, None]:
    sr_client = SchemaRegistryClient({'url': settings.kafka_schemaregistry_client})

    deserializer = AvroDeserializer(sr_client, from_dict=map_to_base)

    conf = {'bootstrap.servers': ",".join(settings.kafka_bootstrap_servers),
            'group.id': settings.kafka_consumer_group,
            'enable.auto.commit': False,
            'auto.offset.reset': 'earliest',
            'on_commit': commit_completed,
            'value.deserializer': deserializer
            }

    consumer = DeserializingConsumer(conf)
    logger.info("Consumer created: " + str(conf))

    try:
        yield consumer
    except Exception as e:
        logger.error("Kafka consumer error. Exception {}", e)
        raise
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
        logger.info("Consumer closed: " + str(conf))
