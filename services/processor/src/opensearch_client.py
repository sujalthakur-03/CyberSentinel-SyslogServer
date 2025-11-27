"""
OpenSearch client for indexing logs.
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from opensearchpy import OpenSearch, helpers
from opensearchpy.exceptions import OpenSearchException
from logger import get_logger
from metrics import messages_indexed_total, opensearch_errors

logger = get_logger(__name__)


class OpenSearchClient:
    """Manages OpenSearch connection and indexing."""

    def __init__(
        self,
        host: str,
        port: int,
        scheme: str = "http",
        user: str = "admin",
        password: str = "admin",
        index_prefix: str = "cybersentinel-logs",
        index_rotation: str = "daily",
        bulk_size: int = 500,
        bulk_timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize OpenSearch client.

        Args:
            host: OpenSearch host
            port: OpenSearch port
            scheme: http or https
            user: Username for authentication
            password: Password for authentication
            index_prefix: Prefix for index names
            index_rotation: Index rotation strategy (daily, weekly, monthly)
            bulk_size: Number of documents per bulk request
            bulk_timeout: Timeout for bulk operations in seconds
            max_retries: Maximum number of retry attempts
        """
        self.host = host
        self.port = port
        self.scheme = scheme
        self.index_prefix = index_prefix
        self.index_rotation = index_rotation
        self.bulk_size = bulk_size
        self.bulk_timeout = bulk_timeout
        self.max_retries = max_retries

        self.client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=(user, password),
            scheme=scheme,
            verify_certs=False,
            ssl_show_warn=False,
            timeout=30,
            max_retries=max_retries,
            retry_on_timeout=True,
        )

        self._index_cache = set()

    def _get_index_name(self, date: datetime = None) -> str:
        """
        Get index name based on rotation strategy.

        Args:
            date: Date for index (defaults to now)

        Returns:
            Index name
        """
        if date is None:
            date = datetime.utcnow()

        if self.index_rotation == "daily":
            suffix = date.strftime("%Y.%m.%d")
        elif self.index_rotation == "weekly":
            suffix = date.strftime("%Y.%U")
        elif self.index_rotation == "monthly":
            suffix = date.strftime("%Y.%m")
        else:
            suffix = "default"

        return f"{self.index_prefix}-{suffix}"

    def _ensure_index_exists(self, index_name: str) -> None:
        """
        Ensure index exists with proper mapping.

        Args:
            index_name: Index name
        """
        if index_name in self._index_cache:
            return

        try:
            if not self.client.indices.exists(index=index_name):
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "received_at": {"type": "date"},
                            "processed_at": {"type": "date"},
                            "source_ip": {"type": "ip"},
                            "hostname": {"type": "keyword"},
                            "facility": {"type": "integer"},
                            "facility_name": {"type": "keyword"},
                            "severity": {"type": "integer"},
                            "severity_name": {"type": "keyword"},
                            "severity_category": {"type": "keyword"},
                            "message": {"type": "text"},
                            "raw": {"type": "text"},
                            "protocol": {"type": "keyword"},
                            "app_name": {"type": "keyword"},
                            "proc_id": {"type": "keyword"},
                            "format": {"type": "keyword"},
                            "extracted_ips": {"type": "ip"},
                            "has_threat_indicators": {"type": "boolean"},
                            "threat_keywords": {"type": "keyword"},
                            "threat_score": {"type": "integer"},
                            "tags": {"type": "keyword"},
                            "fingerprint": {"type": "keyword"},
                        }
                    },
                    "settings": {
                        "number_of_shards": 3,
                        "number_of_replicas": 1,
                        "refresh_interval": "5s",
                    },
                }

                self.client.indices.create(index=index_name, body=mapping)
                logger.info("opensearch_index_created", index=index_name)

            self._index_cache.add(index_name)

        except Exception as e:
            logger.error("opensearch_index_creation_failed", error=str(e), index=index_name)
            opensearch_errors.labels(error_type="index_creation").inc()

    async def index_logs(self, logs: List[Dict[str, Any]]) -> int:
        """
        Index logs into OpenSearch using bulk API.

        Args:
            logs: List of log documents

        Returns:
            Number of successfully indexed documents
        """
        if not logs:
            return 0

        index_name = self._get_index_name()
        self._ensure_index_exists(index_name)

        # Prepare bulk actions
        actions = [
            {
                "_index": index_name,
                "_source": log,
            }
            for log in logs
        ]

        try:
            # Run bulk operation in thread pool (opensearch-py is sync)
            loop = asyncio.get_running_loop()
            success, failed = await loop.run_in_executor(
                None,
                lambda: helpers.bulk(
                    self.client,
                    actions,
                    chunk_size=self.bulk_size,
                    request_timeout=self.bulk_timeout,
                    raise_on_error=False,
                ),
            )

            messages_indexed_total.labels(status="success").inc(success)
            if failed:
                messages_indexed_total.labels(status="failed").inc(len(failed))
                logger.warning(
                    "opensearch_bulk_partial_failure",
                    success=success,
                    failed=len(failed),
                )

            return success

        except OpenSearchException as e:
            logger.error("opensearch_bulk_failed", error=str(e))
            opensearch_errors.labels(error_type="bulk_operation").inc()
            messages_indexed_total.labels(status="failed").inc(len(logs))
            return 0
        except Exception as e:
            logger.error("opensearch_unexpected_error", error=str(e))
            opensearch_errors.labels(error_type="unexpected").inc()
            messages_indexed_total.labels(status="failed").inc(len(logs))
            return 0

    def close(self) -> None:
        """Close OpenSearch connection."""
        try:
            self.client.close()
            logger.info("opensearch_connection_closed")
        except Exception as e:
            logger.error("opensearch_close_failed", error=str(e))
