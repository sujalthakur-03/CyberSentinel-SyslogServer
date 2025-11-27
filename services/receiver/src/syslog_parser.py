"""
Syslog message parsing and validation.
"""
import re
from datetime import datetime
from typing import Optional, Dict, Any
from logger import get_logger

logger = get_logger(__name__)

# RFC 5424 Syslog message pattern
RFC5424_PATTERN = re.compile(
    r"^<(?P<priority>\d+)>(?P<version>\d+)\s+"
    r"(?P<timestamp>\S+)\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?P<app_name>\S+)\s+"
    r"(?P<proc_id>\S+)\s+"
    r"(?P<msg_id>\S+)\s+"
    r"(?P<structured_data>(?:\[.*?\]|-)+)\s*"
    r"(?P<message>.*)$",
    re.DOTALL
)

# RFC 3164 Syslog message pattern - flexible timestamp matching
RFC3164_PATTERN = re.compile(
    r"^<(?P<priority>\d+)>"
    r"(?P<timestamp>(?:\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\S+))\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?:(?P<tag>[^:\s]+)(?:\[(?P<pid>\d+)\])?:\s*)?"
    r"(?P<message>.*)$",
    re.DOTALL
)


class SyslogParser:
    """Parse and validate syslog messages."""

    @staticmethod
    def parse_priority(priority: int) -> Dict[str, Any]:
        """
        Extract facility and severity from priority.

        Args:
            priority: Syslog priority value

        Returns:
            Dictionary with facility and severity
        """
        facility = priority >> 3
        severity = priority & 0x07

        facility_names = {
            0: "kern", 1: "user", 2: "mail", 3: "daemon",
            4: "auth", 5: "syslog", 6: "lpr", 7: "news",
            8: "uucp", 9: "cron", 10: "authpriv", 11: "ftp",
            12: "ntp", 13: "security", 14: "console", 15: "solaris-cron",
            16: "local0", 17: "local1", 18: "local2", 19: "local3",
            20: "local4", 21: "local5", 22: "local6", 23: "local7",
        }

        severity_names = {
            0: "emergency", 1: "alert", 2: "critical", 3: "error",
            4: "warning", 5: "notice", 6: "informational", 7: "debug",
        }

        return {
            "facility": facility,
            "facility_name": facility_names.get(facility, "unknown"),
            "severity": severity,
            "severity_name": severity_names.get(severity, "unknown"),
        }

    @staticmethod
    def parse_rfc5424(raw_message: str) -> Optional[Dict[str, Any]]:
        """
        Parse RFC 5424 format syslog message.

        Args:
            raw_message: Raw syslog message

        Returns:
            Parsed message dictionary or None if parsing fails
        """
        match = RFC5424_PATTERN.match(raw_message)
        if not match:
            return None

        data = match.groupdict()
        priority = int(data["priority"])
        priority_info = SyslogParser.parse_priority(priority)

        return {
            "version": int(data["version"]),
            "timestamp": data["timestamp"],
            "hostname": data["hostname"],
            "app_name": data["app_name"] if data["app_name"] != "-" else None,
            "proc_id": data["proc_id"] if data["proc_id"] != "-" else None,
            "msg_id": data["msg_id"] if data["msg_id"] != "-" else None,
            "structured_data": data["structured_data"] if data["structured_data"] != "-" else None,
            "message": data["message"].strip(),
            "priority": priority,
            **priority_info,
            "format": "RFC5424",
        }

    @staticmethod
    def parse_rfc3164(raw_message: str) -> Optional[Dict[str, Any]]:
        """
        Parse RFC 3164 format syslog message.

        Args:
            raw_message: Raw syslog message

        Returns:
            Parsed message dictionary or None if parsing fails
        """
        match = RFC3164_PATTERN.match(raw_message)
        if not match:
            return None

        data = match.groupdict()
        priority = int(data["priority"])
        priority_info = SyslogParser.parse_priority(priority)

        return {
            "timestamp": data["timestamp"],
            "hostname": data["hostname"],
            "tag": data.get("tag"),
            "pid": data.get("pid"),
            "message": data["message"].strip(),
            "priority": priority,
            **priority_info,
            "format": "RFC3164",
        }

    @classmethod
    def parse(cls, raw_message: str, source_ip: str, protocol: str) -> Dict[str, Any]:
        """
        Parse syslog message and enrich with metadata.

        Args:
            raw_message: Raw syslog message
            source_ip: Source IP address
            protocol: Protocol used (udp, tcp, tls)

        Returns:
            Parsed and enriched message dictionary
        """
        # Try RFC 5424 first, then RFC 3164
        parsed = cls.parse_rfc5424(raw_message) or cls.parse_rfc3164(raw_message)

        if not parsed:
            # Fallback for unparseable messages
            logger.warning(
                "syslog_parse_failed",
                raw_message=raw_message[:100],
                source_ip=source_ip,
            )
            parsed = {
                "message": raw_message,
                "format": "unknown",
                "priority": 13,  # Default: user.notice
                "facility": 1,
                "facility_name": "user",
                "severity": 5,
                "severity_name": "notice",
            }

        # Add metadata
        parsed.update({
            "raw": raw_message,
            "source_ip": source_ip,
            "protocol": protocol,
            "received_at": datetime.utcnow().isoformat(),
        })

        return parsed
