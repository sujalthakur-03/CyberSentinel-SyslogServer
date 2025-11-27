"""
Tests for syslog parser.
"""
import pytest
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from syslog_parser import SyslogParser


class TestSyslogParser:
    """Test syslog message parsing."""

    def test_parse_priority(self):
        """Test priority parsing."""
        result = SyslogParser.parse_priority(134)

        assert result["facility"] == 16
        assert result["facility_name"] == "local0"
        assert result["severity"] == 6
        assert result["severity_name"] == "informational"

    def test_parse_rfc5424(self):
        """Test RFC 5424 message parsing."""
        message = "<134>1 2024-01-15T10:30:00.000Z webserver nginx 1234 - - User logged in"
        result = SyslogParser.parse_rfc5424(message)

        assert result is not None
        assert result["version"] == 1
        assert result["hostname"] == "webserver"
        assert result["app_name"] == "nginx"
        assert result["proc_id"] == "1234"
        assert result["message"] == "User logged in"
        assert result["facility"] == 16
        assert result["severity"] == 6

    def test_parse_rfc3164(self):
        """Test RFC 3164 message parsing."""
        message = "<134>Jan 15 10:30:00 webserver sshd[1234]: User logged in"
        result = SyslogParser.parse_rfc3164(message)

        assert result is not None
        assert result["hostname"] == "webserver"
        assert result["tag"] == "sshd"
        assert result["pid"] == "1234"
        assert result["message"] == "User logged in"
        assert result["facility"] == 16
        assert result["severity"] == 6

    def test_parse_with_metadata(self):
        """Test parsing with metadata enrichment."""
        message = "<134>1 2024-01-15T10:30:00.000Z webserver nginx - - - User logged in"
        result = SyslogParser.parse(message, "192.168.1.100", "udp")

        assert result["source_ip"] == "192.168.1.100"
        assert result["protocol"] == "udp"
        assert "received_at" in result
        assert result["raw"] == message

    def test_parse_invalid_message(self):
        """Test parsing of invalid message."""
        message = "This is not a valid syslog message"
        result = SyslogParser.parse(message, "192.168.1.100", "udp")

        assert result["format"] == "unknown"
        assert result["message"] == message
        assert result["source_ip"] == "192.168.1.100"

    def test_parse_priority_edge_cases(self):
        """Test priority parsing edge cases."""
        # Emergency
        result = SyslogParser.parse_priority(0)
        assert result["severity"] == 0
        assert result["severity_name"] == "emergency"

        # Debug
        result = SyslogParser.parse_priority(7)
        assert result["severity"] == 7
        assert result["severity_name"] == "debug"

        # High priority
        result = SyslogParser.parse_priority(191)
        assert result["facility"] == 23
        assert result["severity"] == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
