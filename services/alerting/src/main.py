"""
Main entry point for Alerting Service.
"""
import asyncio
import signal
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
import json
import redis
from config import settings
from logger import configure_logging, get_logger
from metrics import (
    start_metrics_server,
    logs_evaluated_total,
    alerts_triggered_total,
    alert_processing_duration_seconds,
)
from alert_rules import AlertRuleEngine
from alert_channels import EmailChannel, SlackChannel, AlertChannelManager

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)


class AlertingService:
    """Main service for alert evaluation and delivery."""

    def __init__(self):
        """Initialize the service."""
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.redis_client: Optional[redis.Redis] = None
        self.rule_engine: Optional[AlertRuleEngine] = None
        self.channel_manager: Optional[AlertChannelManager] = None
        self.shutdown_event = asyncio.Event()

    def _initialize_redis(self) -> None:
        """Initialize Redis client for alert deduplication."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("redis_connected")
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            self.redis_client = None

    def _is_duplicate_alert(self, alert_key: str, ttl: int = 3600) -> bool:
        """
        Check if alert is duplicate using Redis.

        Args:
            alert_key: Unique alert key
            ttl: Time-to-live in seconds

        Returns:
            True if duplicate, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            if self.redis_client.exists(alert_key):
                return True

            # Set key with TTL
            self.redis_client.setex(alert_key, ttl, "1")
            return False

        except Exception as e:
            logger.error("redis_duplicate_check_failed", error=str(e))
            return False

    async def start_consumer(self) -> None:
        """Start Kafka consumer."""
        retry_count = 0
        max_retries = 10

        while retry_count < max_retries:
            try:
                self.consumer = AIOKafkaConsumer(
                    settings.kafka_topic_processed_logs,
                    bootstrap_servers=settings.kafka_servers_list,
                    group_id=settings.kafka_consumer_group_alerting,
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    auto_commit_interval_ms=5000,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000,
                )
                await self.consumer.start()
                logger.info("kafka_consumer_started", topic=settings.kafka_topic_processed_logs)
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
        """Start Kafka producer for alert events."""
        retry_count = 0
        max_retries = 10

        while retry_count < max_retries:
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka_servers_list,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    compression_type="lz4",
                )
                await self.producer.start()
                logger.info("kafka_producer_started", topic=settings.kafka_topic_alerts)
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

    async def process_log(self, log: Dict[str, Any]) -> None:
        """
        Process a log and trigger alerts if needed.

        Args:
            log: Log data
        """
        with alert_processing_duration_seconds.labels(operation="evaluation").time():
            logs_evaluated_total.inc()

            # Evaluate against all rules
            triggered_rules = self.rule_engine.evaluate(log)

            for rule in triggered_rules:
                # Create alert
                alert = {
                    "rule_name": rule.name,
                    "description": rule.description,
                    "severity": rule.severity,
                    "timestamp": datetime.utcnow().isoformat(),
                    "log_data": log,
                }

                # Check for duplicates
                alert_key = f"alert:{rule.name}:{log.get('fingerprint', 'unknown')}"
                if self._is_duplicate_alert(alert_key, ttl=3600):
                    logger.debug("alert_deduplicated", rule_name=rule.name, alert_key=alert_key)
                    continue

                # Record alert
                alerts_triggered_total.labels(
                    rule_name=rule.name,
                    severity=rule.severity,
                ).inc()

                logger.info(
                    "alert_triggered",
                    rule_name=rule.name,
                    severity=rule.severity,
                    hostname=log.get("hostname"),
                    source_ip=log.get("source_ip"),
                )

                # Send alert through channels
                await self.channel_manager.send_alert(alert)

                # Publish to alerts topic
                try:
                    await self.producer.send(settings.kafka_topic_alerts, value=alert)
                except Exception as e:
                    logger.error("alert_publish_failed", error=str(e), rule_name=rule.name)

    async def consume_and_evaluate(self) -> None:
        """Main consumption loop."""
        logger.info("starting_alerting_loop")

        try:
            async for msg in self.consumer:
                if self.shutdown_event.is_set():
                    break

                try:
                    log_data = msg.value
                    await self.process_log(log_data)
                except Exception as e:
                    logger.error("log_processing_failed", error=str(e))

        except KafkaError as e:
            logger.error("kafka_consumption_error", error=str(e))
        except Exception as e:
            logger.error("alerting_loop_error", error=str(e))

    async def start(self) -> None:
        """Start all service components."""
        logger.info("service_starting", environment=settings.environment)

        try:
            # Start metrics server
            start_metrics_server(settings.prometheus_port)

            # Initialize Redis
            self._initialize_redis()

            # Initialize rule engine
            self.rule_engine = AlertRuleEngine()
            logger.info("alert_rules_loaded", count=len(self.rule_engine.rules))

            # Initialize alert channels
            self.channel_manager = AlertChannelManager()

            # Add email channel
            if settings.to_emails_list:
                email_channel = EmailChannel(
                    smtp_host=settings.alerting_smtp_host,
                    smtp_port=settings.alerting_smtp_port,
                    smtp_user=settings.alerting_smtp_user,
                    smtp_password=settings.alerting_smtp_password,
                    from_email=settings.alerting_from_email,
                    to_emails=settings.to_emails_list,
                )
                self.channel_manager.add_channel(email_channel)
                logger.info("email_channel_configured", to_emails=settings.to_emails_list)

            # Add Slack channel
            if settings.alerting_slack_webhook_url:
                slack_channel = SlackChannel(
                    webhook_url=settings.alerting_slack_webhook_url
                )
                self.channel_manager.add_channel(slack_channel)
                logger.info("slack_channel_configured")

            # Start Kafka components
            await self.start_consumer()
            await self.start_producer()

            logger.info("service_started")

        except Exception as e:
            logger.error("service_start_failed", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop all service components gracefully."""
        logger.info("service_stopping")

        try:
            # Stop Kafka components
            if self.consumer:
                await self.consumer.stop()

            if self.producer:
                await self.producer.stop()

            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()

            logger.info("service_stopped")

        except Exception as e:
            logger.error("service_stop_failed", error=str(e))

    async def run(self) -> None:
        """Run the service until shutdown signal."""
        await self.start()

        # Start alerting loop
        alerting_task = asyncio.create_task(self.consume_and_evaluate())

        # Wait for shutdown signal
        await self.shutdown_event.wait()

        # Cancel alerting task
        alerting_task.cancel()
        try:
            await alerting_task
        except asyncio.CancelledError:
            pass

        await self.stop()

    def shutdown(self) -> None:
        """Signal shutdown."""
        logger.info("shutdown_signal_received")
        self.shutdown_event.set()


async def main() -> None:
    """Main entry point."""
    service = AlertingService()

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
