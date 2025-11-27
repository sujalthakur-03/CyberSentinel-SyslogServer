"""
Main entry point for Log Processor Service.
"""
import asyncio
import signal
import sys
from typing import Optional, List, Dict, Any
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
import json
from config import settings
from logger import configure_logging, get_logger
from metrics import (
    start_metrics_server,
    messages_consumed_total,
    messages_processed_total,
    processing_duration_seconds,
    batch_size,
)
from enricher import LogEnricher
from opensearch_client import OpenSearchClient

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)


class LogProcessorService:
    """Main service for processing and enriching logs."""

    def __init__(self):
        """Initialize the service."""
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.opensearch: Optional[OpenSearchClient] = None
        self.enricher: Optional[LogEnricher] = None
        self.shutdown_event = asyncio.Event()
        self._processing_tasks: List[asyncio.Task] = []

    async def start_consumer(self) -> None:
        """Start Kafka consumer."""
        retry_count = 0
        max_retries = 10

        while retry_count < max_retries:
            try:
                self.consumer = AIOKafkaConsumer(
                    settings.kafka_topic_raw_logs,
                    bootstrap_servers=settings.kafka_servers_list,
                    group_id=settings.kafka_consumer_group_processor,
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    auto_commit_interval_ms=5000,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    max_poll_records=settings.processor_batch_size,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000,
                )
                await self.consumer.start()
                logger.info("kafka_consumer_started", topic=settings.kafka_topic_raw_logs)
                return
            except Exception as e:
                retry_count += 1
                logger.error(
                    "kafka_consumer_start_failed",
                    error=str(e),
                    retry_count=retry_count,
                    max_retries=max_retries,
                )
                if retry_count < max_retries:
                    await asyncio.sleep(5)
                else:
                    raise

    async def start_producer(self) -> None:
        """Start Kafka producer for processed logs."""
        retry_count = 0
        max_retries = 10

        while retry_count < max_retries:
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka_servers_list,
                    compression_type=settings.kafka_compression_type,
                    max_batch_size=settings.kafka_batch_size,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    acks="all",
                    enable_idempotence=True,
                )
                await self.producer.start()
                logger.info("kafka_producer_started", topic=settings.kafka_topic_processed_logs)
                return
            except Exception as e:
                retry_count += 1
                logger.error(
                    "kafka_producer_start_failed",
                    error=str(e),
                    retry_count=retry_count,
                    max_retries=max_retries,
                )
                if retry_count < max_retries:
                    await asyncio.sleep(5)
                else:
                    raise

    async def process_batch(self, messages: List[Dict[str, Any]]) -> None:
        """
        Process a batch of messages.

        Args:
            messages: List of raw log messages
        """
        if not messages:
            return

        with processing_duration_seconds.labels(operation="batch_processing").time():
            batch_size.observe(len(messages))

            # Enrich messages
            enriched_messages = []
            for msg in messages:
                try:
                    enriched = self.enricher.enrich(msg)
                    enriched_messages.append(enriched)
                    messages_processed_total.labels(status="success").inc()
                except Exception as e:
                    logger.error("message_enrichment_failed", error=str(e), message=str(msg)[:100])
                    messages_processed_total.labels(status="failed").inc()

            if not enriched_messages:
                return

            # Index to OpenSearch
            try:
                indexed_count = await self.opensearch.index_logs(enriched_messages)
                logger.info(
                    "batch_indexed",
                    total=len(enriched_messages),
                    indexed=indexed_count,
                )
            except Exception as e:
                logger.error("batch_indexing_failed", error=str(e))

            # Send to processed logs topic
            try:
                for enriched in enriched_messages:
                    await self.producer.send(
                        settings.kafka_topic_processed_logs,
                        value=enriched,
                    )
            except Exception as e:
                logger.error("batch_kafka_send_failed", error=str(e))

    async def consume_and_process(self) -> None:
        """Main consumption loop."""
        logger.info("starting_consumption_loop")

        try:
            async for msg_batch in self.consumer:
                if self.shutdown_event.is_set():
                    break

                messages_consumed_total.labels(status="success").inc()

                # Process message
                try:
                    message_data = msg_batch.value
                    await self.process_batch([message_data])
                except Exception as e:
                    logger.error("message_processing_failed", error=str(e))
                    messages_consumed_total.labels(status="failed").inc()

        except KafkaError as e:
            logger.error("kafka_consumption_error", error=str(e))
        except Exception as e:
            logger.error("consumption_loop_error", error=str(e))

    async def start(self) -> None:
        """Start all service components."""
        logger.info("service_starting", environment=settings.environment)

        try:
            # Start metrics server
            start_metrics_server(settings.prometheus_port)

            # Initialize components
            self.enricher = LogEnricher(
                geo_ip_enabled=settings.processor_geo_ip_enabled
            )

            self.opensearch = OpenSearchClient(
                host=settings.opensearch_host,
                port=settings.opensearch_port,
                scheme=settings.opensearch_scheme,
                user=settings.opensearch_user,
                password=settings.opensearch_password,
                index_prefix=settings.opensearch_index_prefix,
                index_rotation=settings.opensearch_index_rotation,
                bulk_size=settings.opensearch_bulk_size,
                bulk_timeout=settings.opensearch_bulk_timeout,
                max_retries=settings.opensearch_max_retries,
            )

            # Start Kafka components
            await self.start_consumer()
            await self.start_producer()

            # Start processing workers
            for i in range(settings.processor_workers):
                task = asyncio.create_task(self.consume_and_process())
                self._processing_tasks.append(task)
                logger.info("processing_worker_started", worker_id=i)

            logger.info("service_started", workers=settings.processor_workers)

        except Exception as e:
            logger.error("service_start_failed", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop all service components gracefully."""
        logger.info("service_stopping")

        try:
            # Cancel processing tasks
            for task in self._processing_tasks:
                task.cancel()

            # Wait for tasks to complete
            if self._processing_tasks:
                await asyncio.gather(*self._processing_tasks, return_exceptions=True)

            # Stop Kafka components
            if self.consumer:
                await self.consumer.stop()

            if self.producer:
                await self.producer.stop()

            # Close OpenSearch connection
            if self.opensearch:
                self.opensearch.close()

            logger.info("service_stopped")

        except Exception as e:
            logger.error("service_stop_failed", error=str(e))

    async def run(self) -> None:
        """Run the service until shutdown signal."""
        await self.start()

        # Wait for shutdown signal
        await self.shutdown_event.wait()

        await self.stop()

    def shutdown(self) -> None:
        """Signal shutdown."""
        logger.info("shutdown_signal_received")
        self.shutdown_event.set()


async def main() -> None:
    """Main entry point."""
    service = LogProcessorService()

    # Setup signal handlers
    loop = asyncio.get_running_loop()

    def signal_handler(sig):
        logger.info("signal_received", signal=sig)
        service.shutdown()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))

    try:
        await service.run()
    except Exception as e:
        logger.error("service_fatal_error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("service_interrupted")
        sys.exit(0)
