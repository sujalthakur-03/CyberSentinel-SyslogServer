"""
OpenSearch service for querying logs.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from opensearchpy import OpenSearch
from opensearchpy.exceptions import OpenSearchException
from logger import get_logger

logger = get_logger(__name__)


class OpenSearchService:
    """Service for querying logs from OpenSearch."""

    def __init__(
        self,
        host: str,
        port: int,
        scheme: str = "http",
        user: str = "admin",
        password: str = "admin",
        index_prefix: str = "cybersentinel-logs",
    ):
        """
        Initialize OpenSearch service.

        Args:
            host: OpenSearch host
            port: OpenSearch port
            scheme: http or https
            user: Username for authentication
            password: Password for authentication
            index_prefix: Prefix for index names
        """
        self.index_prefix = index_prefix
        self.client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=(user, password),
            scheme=scheme,
            verify_certs=False,
            ssl_show_warn=False,
            timeout=30,
        )

    def _get_index_pattern(self, days: int = 7) -> str:
        """
        Get index pattern for date range.

        Args:
            days: Number of days to look back

        Returns:
            Index pattern
        """
        return f"{self.index_prefix}-*"

    async def search_logs(
        self,
        query: Optional[str] = None,
        severity: Optional[List[str]] = None,
        facility: Optional[List[str]] = None,
        hostname: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "received_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Search logs with filters.

        Args:
            query: Full-text search query
            severity: List of severity names to filter
            facility: List of facility names to filter
            hostname: Hostname to filter
            start_time: Start time for time range
            end_time: End time for time range
            page: Page number (1-indexed)
            page_size: Number of results per page
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)

        Returns:
            Search results with pagination
        """
        # Build query
        must_clauses = []
        filter_clauses = []

        # Full-text search
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["message", "hostname", "app_name"],
                    "type": "best_fields",
                }
            })

        # Filters
        if severity:
            filter_clauses.append({"terms": {"severity_name.keyword": severity}})

        if facility:
            filter_clauses.append({"terms": {"facility_name.keyword": facility}})

        if hostname:
            filter_clauses.append({"term": {"hostname.keyword": hostname}})

        # Time range
        if start_time or end_time:
            time_range = {}
            if start_time:
                time_range["gte"] = start_time.isoformat()
            if end_time:
                time_range["lte"] = end_time.isoformat()
            filter_clauses.append({"range": {"received_at": time_range}})

        # Construct query
        query_body = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            },
            "sort": [{sort_by: {"order": sort_order}}],
            "from": (page - 1) * page_size,
            "size": page_size,
        }

        try:
            response = self.client.search(
                index=self._get_index_pattern(),
                body=query_body,
            )

            hits = response["hits"]
            total = hits["total"]["value"]

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "logs": [hit["_source"] for hit in hits["hits"]],
            }

        except OpenSearchException as e:
            logger.error("opensearch_search_failed", error=str(e))
            raise

    async def get_log_by_id(self, doc_id: str, index: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific log by ID.

        Args:
            doc_id: Document ID
            index: Index name

        Returns:
            Log document or None if not found
        """
        try:
            response = self.client.get(index=index, id=doc_id)
            return response["_source"]
        except OpenSearchException as e:
            logger.error("opensearch_get_failed", error=str(e), doc_id=doc_id)
            return None

    async def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get log statistics.

        Args:
            start_time: Start time for statistics
            end_time: End time for statistics

        Returns:
            Statistics data
        """
        # Default to last 24 hours
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=1)
        if not end_time:
            end_time = datetime.utcnow()

        query_body = {
            "query": {
                "range": {
                    "received_at": {
                        "gte": start_time.isoformat(),
                        "lte": end_time.isoformat(),
                    }
                }
            },
            "size": 0,
            "aggs": {
                "by_severity": {
                    "terms": {"field": "severity_name.keyword"}
                },
                "by_facility": {
                    "terms": {"field": "facility_name.keyword"}
                },
                "by_hostname": {
                    "terms": {"field": "hostname.keyword", "size": 10}
                },
                "by_hour": {
                    "date_histogram": {
                        "field": "received_at",
                        "fixed_interval": "1h",
                    }
                },
                "threat_logs": {
                    "filter": {"term": {"has_threat_indicators": True}}
                },
            },
        }

        try:
            response = self.client.search(
                index=self._get_index_pattern(),
                body=query_body,
            )

            aggs = response["aggregations"]

            return {
                "total_logs": response["hits"]["total"]["value"],
                "by_severity": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs["by_severity"]["buckets"]
                },
                "by_facility": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs["by_facility"]["buckets"]
                },
                "top_hosts": [
                    {"hostname": bucket["key"], "count": bucket["doc_count"]}
                    for bucket in aggs["by_hostname"]["buckets"]
                ],
                "timeline": [
                    {
                        "timestamp": bucket["key_as_string"],
                        "count": bucket["doc_count"],
                    }
                    for bucket in aggs["by_hour"]["buckets"]
                ],
                "threat_logs_count": aggs["threat_logs"]["doc_count"],
            }

        except OpenSearchException as e:
            logger.error("opensearch_statistics_failed", error=str(e))
            raise

    def close(self) -> None:
        """Close OpenSearch connection."""
        try:
            self.client.close()
        except Exception as e:
            logger.error("opensearch_close_failed", error=str(e))
