"""
Main entry point for Syslog Receiver Service.
"""
import asyncio
import signal
import sys
from typing import Optional
from config import settings
from logger import configure_logging, get_logger
from metrics import start_metrics_server
from kafka_producer import KafkaProducerManager
from receivers import UDPReceiver, TCPReceiver, TLSReceiver

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)


class SyslogReceiverService:
    """Main service orchestrator for syslog receivers."""

    def __init__(self):
        """Initialize the service."""
        self.kafka_producer: Optional[KafkaProducerManager] = None
        self.udp_receiver: Optional[UDPReceiver] = None
        self.tcp_receiver: Optional[TCPReceiver] = None
        self.tls_receiver: Optional[TLSReceiver] = None
        self.shutdown_event = asyncio.Event()

    async def message_handler(self, parsed_message: dict) -> None:
        """
        Handle parsed syslog messages by sending to Kafka.

        Args:
            parsed_message: Parsed message dictionary
        """
        if self.kafka_producer:
            await self.kafka_producer.send(parsed_message)
        else:
            logger.error("kafka_producer_not_initialized")

    async def start(self) -> None:
        """Start all service components."""
        logger.info("service_starting", environment=settings.environment)

        try:
            # Start metrics server
            start_metrics_server(settings.prometheus_port)

            # Initialize Kafka producer
            self.kafka_producer = KafkaProducerManager(
                bootstrap_servers=settings.kafka_servers_list,
                topic=settings.kafka_topic_raw_logs,
                compression_type=settings.kafka_compression_type,
                batch_size=settings.kafka_batch_size,
                linger_ms=settings.kafka_linger_ms,
            )
            await self.kafka_producer.start()

            # Start UDP receiver
            self.udp_receiver = UDPReceiver(
                host="0.0.0.0",
                port=settings.receiver_udp_port,
                message_handler=self.message_handler,
                max_message_size=settings.receiver_max_message_size,
            )
            await self.udp_receiver.start()

            # Start TCP receiver
            self.tcp_receiver = TCPReceiver(
                host="0.0.0.0",
                port=settings.receiver_tcp_port,
                message_handler=self.message_handler,
                max_message_size=settings.receiver_max_message_size,
            )
            await self.tcp_receiver.start()

            # Start TLS receiver if enabled
            if settings.receiver_tls_enabled:
                try:
                    self.tls_receiver = TLSReceiver(
                        host="0.0.0.0",
                        port=settings.receiver_tls_port,
                        message_handler=self.message_handler,
                        cert_path=settings.receiver_tls_cert_path,
                        key_path=settings.receiver_tls_key_path,
                        max_message_size=settings.receiver_max_message_size,
                    )
                    await self.tls_receiver.start()
                except Exception as e:
                    logger.warning(
                        "tls_receiver_disabled",
                        error=str(e),
                        message="Continuing without TLS support",
                    )

            logger.info("service_started", message="All receivers operational")

        except Exception as e:
            logger.error("service_start_failed", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop all service components gracefully."""
        logger.info("service_stopping")

        try:
            # Stop receivers
            if self.udp_receiver:
                await self.udp_receiver.stop()

            if self.tcp_receiver:
                await self.tcp_receiver.stop()

            if self.tls_receiver:
                await self.tls_receiver.stop()

            # Stop Kafka producer
            if self.kafka_producer:
                await self.kafka_producer.stop()

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
    service = SyslogReceiverService()

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
