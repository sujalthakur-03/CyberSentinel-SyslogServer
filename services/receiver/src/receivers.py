"""
Syslog receivers for UDP, TCP, and TLS protocols.
"""
import asyncio
import ssl
from typing import Optional, Callable
from logger import get_logger
from metrics import (
    messages_received_total,
    message_size_bytes,
    active_connections,
    processing_duration_seconds,
)
from syslog_parser import SyslogParser

logger = get_logger(__name__)


class UDPReceiver:
    """UDP syslog receiver."""

    def __init__(
        self,
        host: str,
        port: int,
        message_handler: Callable,
        max_message_size: int = 8192,
    ):
        """
        Initialize UDP receiver.

        Args:
            host: Host to bind to
            port: Port to listen on
            message_handler: Async function to handle messages
            max_message_size: Maximum message size in bytes
        """
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.max_message_size = max_message_size
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional[asyncio.DatagramProtocol] = None

    async def start(self) -> None:
        """Start UDP receiver."""
        loop = asyncio.get_running_loop()

        class SyslogUDPProtocol(asyncio.DatagramProtocol):
            def __init__(self, handler, parser):
                self.handler = handler
                self.parser = parser

            def datagram_received(self, data: bytes, addr: tuple) -> None:
                asyncio.create_task(self._handle_datagram(data, addr))

            async def _handle_datagram(self, data: bytes, addr: tuple) -> None:
                source_ip = addr[0]
                try:
                    with processing_duration_seconds.labels(operation="udp_receive").time():
                        message = data.decode("utf-8", errors="replace")
                        message_size_bytes.observe(len(data))

                        parsed = self.parser.parse(message, source_ip, "udp")
                        await self.handler(parsed)

                        messages_received_total.labels(protocol="udp", status="success").inc()
                except Exception as e:
                    logger.error("udp_message_processing_failed", error=str(e), source_ip=source_ip)
                    messages_received_total.labels(protocol="udp", status="failed").inc()

        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: SyslogUDPProtocol(self.message_handler, SyslogParser()),
            local_addr=(self.host, self.port),
        )

        logger.info("udp_receiver_started", host=self.host, port=self.port)

    async def stop(self) -> None:
        """Stop UDP receiver."""
        if self.transport:
            self.transport.close()
            logger.info("udp_receiver_stopped")


class TCPReceiver:
    """TCP syslog receiver."""

    def __init__(
        self,
        host: str,
        port: int,
        message_handler: Callable,
        max_message_size: int = 8192,
    ):
        """
        Initialize TCP receiver.

        Args:
            host: Host to bind to
            port: Port to listen on
            message_handler: Async function to handle messages
            max_message_size: Maximum message size in bytes
        """
        self.host = host
        self.port = port
        self.message_handler = message_handler
        self.max_message_size = max_message_size
        self.server: Optional[asyncio.Server] = None
        self.parser = SyslogParser()

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Handle TCP client connection.

        Args:
            reader: Stream reader
            writer: Stream writer
        """
        addr = writer.get_extra_info("peername")
        source_ip = addr[0] if addr else "unknown"

        active_connections.labels(protocol="tcp").inc()
        logger.info("tcp_client_connected", source_ip=source_ip)

        try:
            buffer = b""
            while True:
                chunk = await reader.read(self.max_message_size)
                if not chunk:
                    break

                buffer += chunk

                # Process complete messages (newline-delimited)
                while b"\n" in buffer:
                    message_bytes, buffer = buffer.split(b"\n", 1)

                    try:
                        with processing_duration_seconds.labels(operation="tcp_receive").time():
                            message = message_bytes.decode("utf-8", errors="replace").strip()
                            if not message:
                                continue

                            message_size_bytes.observe(len(message_bytes))
                            parsed = self.parser.parse(message, source_ip, "tcp")
                            await self.message_handler(parsed)

                            messages_received_total.labels(protocol="tcp", status="success").inc()
                    except Exception as e:
                        logger.error(
                            "tcp_message_processing_failed",
                            error=str(e),
                            source_ip=source_ip,
                        )
                        messages_received_total.labels(protocol="tcp", status="failed").inc()

        except asyncio.CancelledError:
            logger.info("tcp_client_disconnected_cancelled", source_ip=source_ip)
        except Exception as e:
            logger.error("tcp_client_error", error=str(e), source_ip=source_ip)
        finally:
            active_connections.labels(protocol="tcp").dec()
            writer.close()
            await writer.wait_closed()
            logger.info("tcp_client_disconnected", source_ip=source_ip)

    async def start(self) -> None:
        """Start TCP receiver."""
        self.server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        logger.info("tcp_receiver_started", host=self.host, port=self.port)

    async def stop(self) -> None:
        """Stop TCP receiver."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("tcp_receiver_stopped")


class TLSReceiver(TCPReceiver):
    """TLS-encrypted syslog receiver."""

    def __init__(
        self,
        host: str,
        port: int,
        message_handler: Callable,
        cert_path: str,
        key_path: str,
        max_message_size: int = 8192,
    ):
        """
        Initialize TLS receiver.

        Args:
            host: Host to bind to
            port: Port to listen on
            message_handler: Async function to handle messages
            cert_path: Path to TLS certificate
            key_path: Path to TLS private key
            max_message_size: Maximum message size in bytes
        """
        super().__init__(host, port, message_handler, max_message_size)
        self.cert_path = cert_path
        self.key_path = key_path

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle TLS client with protocol label override."""
        addr = writer.get_extra_info("peername")
        source_ip = addr[0] if addr else "unknown"

        active_connections.labels(protocol="tls").inc()
        logger.info("tls_client_connected", source_ip=source_ip)

        try:
            buffer = b""
            while True:
                chunk = await reader.read(self.max_message_size)
                if not chunk:
                    break

                buffer += chunk

                while b"\n" in buffer:
                    message_bytes, buffer = buffer.split(b"\n", 1)

                    try:
                        with processing_duration_seconds.labels(operation="tls_receive").time():
                            message = message_bytes.decode("utf-8", errors="replace").strip()
                            if not message:
                                continue

                            message_size_bytes.observe(len(message_bytes))
                            parsed = self.parser.parse(message, source_ip, "tls")
                            await self.message_handler(parsed)

                            messages_received_total.labels(protocol="tls", status="success").inc()
                    except Exception as e:
                        logger.error(
                            "tls_message_processing_failed",
                            error=str(e),
                            source_ip=source_ip,
                        )
                        messages_received_total.labels(protocol="tls", status="failed").inc()

        except asyncio.CancelledError:
            logger.info("tls_client_disconnected_cancelled", source_ip=source_ip)
        except Exception as e:
            logger.error("tls_client_error", error=str(e), source_ip=source_ip)
        finally:
            active_connections.labels(protocol="tls").dec()
            writer.close()
            await writer.wait_closed()
            logger.info("tls_client_disconnected", source_ip=source_ip)

    async def start(self) -> None:
        """Start TLS receiver with SSL context."""
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.cert_path, self.key_path)
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

            self.server = await asyncio.start_server(
                self._handle_client, self.host, self.port, ssl=ssl_context
            )
            logger.info(
                "tls_receiver_started",
                host=self.host,
                port=self.port,
                cert_path=self.cert_path,
            )
        except Exception as e:
            logger.error("tls_receiver_start_failed", error=str(e))
            raise
