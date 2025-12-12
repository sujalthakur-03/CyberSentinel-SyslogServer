"""
Log enrichment with GeoIP and additional metadata.
"""
import re
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from logger import get_logger
from metrics import enrichment_duration_seconds

logger = get_logger(__name__)


class LogEnricher:
    """Enrich log messages with additional metadata."""

    def __init__(self, geo_ip_enabled: bool = True):
        """
        Initialize log enricher.

        Args:
            geo_ip_enabled: Whether to enable GeoIP enrichment
        """
        self.geo_ip_enabled = geo_ip_enabled
        self.ip_pattern = re.compile(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        )

        # Common threat indicators
        self.threat_keywords = [
            "exploit", "malware", "ransomware", "trojan", "backdoor",
            "injection", "xss", "sql injection", "ddos", "brute force",
            "unauthorized", "breach", "intrusion", "anomaly"
        ]

    def extract_ips(self, message: str) -> list[str]:
        """
        Extract IP addresses from message.

        Args:
            message: Log message

        Returns:
            List of IP addresses found
        """
        return self.ip_pattern.findall(message)

    def detect_threat_indicators(self, message: str) -> Dict[str, Any]:
        """
        Detect potential threat indicators in message.

        Args:
            message: Log message

        Returns:
            Dictionary with threat detection results
        """
        message_lower = message.lower()
        detected_threats = [
            keyword for keyword in self.threat_keywords
            if keyword in message_lower
        ]

        return {
            "has_threat_indicators": len(detected_threats) > 0,
            "threat_keywords": detected_threats,
            "threat_score": min(len(detected_threats) * 10, 100),
        }

    def categorize_severity(self, severity: int) -> str:
        """
        Categorize severity into groups.

        Args:
            severity: Numeric severity (0-7)

        Returns:
            Severity category
        """
        if severity <= 2:
            return "critical"
        elif severity <= 4:
            return "high"
        elif severity <= 5:
            return "medium"
        else:
            return "low"

    def generate_fingerprint(self, log_data: Dict[str, Any]) -> str:
        """
        Generate unique fingerprint for log deduplication.

        Args:
            log_data: Log data dictionary

        Returns:
            SHA256 fingerprint
        """
        # Create fingerprint from key fields
        fingerprint_data = {
            "hostname": log_data.get("hostname", ""),
            "app_name": log_data.get("app_name", ""),
            "message": log_data.get("message", ""),
            "facility": log_data.get("facility", ""),
            "severity": log_data.get("severity", ""),
        }

        fingerprint_str = "|".join(str(v) for v in fingerprint_data.values())
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    def enrich(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich log data with additional metadata.

        Args:
            log_data: Raw log data

        Returns:
            Enriched log data
        """
        with enrichment_duration_seconds.labels(enrichment_type="full").time():
            enriched = log_data.copy()

            # Add processing timestamp
            enriched["processed_at"] = datetime.utcnow().isoformat()

            # Extract IPs from message
            message = log_data.get("message", "")
            extracted_ips = self.extract_ips(message)
            if extracted_ips:
                enriched["extracted_ips"] = extracted_ips

            # Add severity category
            severity = log_data.get("severity", 5)
            enriched["severity_category"] = self.categorize_severity(severity)

            # Detect threat indicators
            threat_info = self.detect_threat_indicators(message)
            enriched.update({
                "has_threat_indicators": threat_info["has_threat_indicators"],
                "threat_keywords": threat_info["threat_keywords"],
                "threat_score": threat_info["threat_score"],
            })

            # Generate fingerprint
            enriched["fingerprint"] = self.generate_fingerprint(log_data)

            # Add tags based on content
            tags = []
            if threat_info["has_threat_indicators"]:
                tags.append("security")
            if severity <= 3:
                tags.append("critical")
            if "error" in message.lower() or "fail" in message.lower():
                tags.append("error")
            if "auth" in message.lower() or "login" in message.lower():
                tags.append("authentication")

            enriched["tags"] = tags

            # Normalize timestamp format
            timestamp = log_data.get("timestamp", "")
            if timestamp:
                try:
                    # Try to parse various timestamp formats
                    from dateutil import parser as dateutil_parser
                    parsed_dt = dateutil_parser.parse(timestamp)
                    enriched["timestamp_normalized"] = parsed_dt.isoformat()
                    # Update the main timestamp field with the normalized version
                    enriched["timestamp"] = enriched["timestamp_normalized"]
                except Exception as e:
                    # If timestamp parsing fails, use received_at
                    logger.debug("timestamp_parse_failed", timestamp=timestamp, error=str(e))
                    enriched["timestamp_normalized"] = enriched["received_at"]
                    enriched["timestamp"] = enriched["received_at"]
            else:
                # No timestamp provided, use received_at
                enriched["timestamp_normalized"] = enriched.get("received_at", datetime.utcnow().isoformat())
                enriched["timestamp"] = enriched["timestamp_normalized"]

            # Add index metadata
            enriched["_index_date"] = datetime.utcnow().strftime("%Y.%m.%d")

            return enriched
