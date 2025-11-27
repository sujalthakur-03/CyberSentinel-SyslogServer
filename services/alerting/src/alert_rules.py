"""
Alert rule definitions and evaluation.
"""
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class AlertRule:
    """Alert rule definition."""
    name: str
    description: str
    severity: str  # critical, high, medium, low
    condition: Callable[[Dict[str, Any]], bool]
    enabled: bool = True


class AlertRuleEngine:
    """Evaluate logs against alert rules."""

    def __init__(self):
        """Initialize alert rule engine."""
        self.rules: List[AlertRule] = []
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default alert rules."""

        # Rule 1: Critical severity logs
        self.rules.append(AlertRule(
            name="critical_severity",
            description="Alert on critical severity logs (emergency, alert, critical)",
            severity="critical",
            condition=lambda log: log.get("severity", 7) <= 2,
        ))

        # Rule 2: High threat score
        self.rules.append(AlertRule(
            name="high_threat_score",
            description="Alert on logs with high threat score",
            severity="high",
            condition=lambda log: log.get("threat_score", 0) >= 50,
        ))

        # Rule 3: Authentication failures
        self.rules.append(AlertRule(
            name="auth_failure",
            description="Alert on authentication failures",
            severity="medium",
            condition=lambda log: (
                "authentication" in log.get("tags", []) and
                any(word in log.get("message", "").lower()
                    for word in ["failed", "failure", "denied", "rejected"])
            ),
        ))

        # Rule 4: Security events
        self.rules.append(AlertRule(
            name="security_event",
            description="Alert on security-related events",
            severity="high",
            condition=lambda log: (
                "security" in log.get("tags", []) or
                log.get("has_threat_indicators", False)
            ),
        ))

        # Rule 5: Multiple errors from same host
        self.rules.append(AlertRule(
            name="error_spike",
            description="Alert on error severity from specific host",
            severity="medium",
            condition=lambda log: (
                log.get("severity_name") == "error" and
                log.get("hostname") is not None
            ),
        ))

        # Rule 6: Brute force indicators
        self.rules.append(AlertRule(
            name="brute_force",
            description="Alert on potential brute force attempts",
            severity="high",
            condition=lambda log: (
                "brute force" in log.get("message", "").lower() or
                "brute_force" in log.get("threat_keywords", [])
            ),
        ))

        # Rule 7: Malware indicators
        self.rules.append(AlertRule(
            name="malware_detected",
            description="Alert on malware-related keywords",
            severity="critical",
            condition=lambda log: any(
                keyword in log.get("message", "").lower()
                for keyword in ["malware", "ransomware", "trojan", "virus"]
            ),
        ))

        # Rule 8: Unauthorized access
        self.rules.append(AlertRule(
            name="unauthorized_access",
            description="Alert on unauthorized access attempts",
            severity="high",
            condition=lambda log: any(
                keyword in log.get("message", "").lower()
                for keyword in ["unauthorized", "forbidden", "access denied"]
            ),
        ))

        # Rule 9: SQL injection attempts
        self.rules.append(AlertRule(
            name="sql_injection",
            description="Alert on potential SQL injection attempts",
            severity="critical",
            condition=lambda log: (
                "sql injection" in log.get("message", "").lower() or
                "sql_injection" in log.get("threat_keywords", []) or
                any(pattern in log.get("message", "").lower()
                    for pattern in ["union select", "' or '1'='1", "drop table"])
            ),
        ))

        # Rule 10: DDoS indicators
        self.rules.append(AlertRule(
            name="ddos_attack",
            description="Alert on DDoS attack indicators",
            severity="critical",
            condition=lambda log: (
                "ddos" in log.get("message", "").lower() or
                "ddos" in log.get("threat_keywords", [])
            ),
        ))

    def add_rule(self, rule: AlertRule) -> None:
        """
        Add a custom alert rule.

        Args:
            rule: Alert rule to add
        """
        self.rules.append(rule)
        logger.info("alert_rule_added", rule_name=rule.name)

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove an alert rule by name.

        Args:
            rule_name: Name of rule to remove

        Returns:
            True if rule was removed, False if not found
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                logger.info("alert_rule_removed", rule_name=rule_name)
                return True
        return False

    def enable_rule(self, rule_name: str) -> bool:
        """
        Enable an alert rule.

        Args:
            rule_name: Name of rule to enable

        Returns:
            True if rule was enabled, False if not found
        """
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info("alert_rule_enabled", rule_name=rule_name)
                return True
        return False

    def disable_rule(self, rule_name: str) -> bool:
        """
        Disable an alert rule.

        Args:
            rule_name: Name of rule to disable

        Returns:
            True if rule was disabled, False if not found
        """
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info("alert_rule_disabled", rule_name=rule_name)
                return True
        return False

    def evaluate(self, log: Dict[str, Any]) -> List[AlertRule]:
        """
        Evaluate a log against all enabled rules.

        Args:
            log: Log data to evaluate

        Returns:
            List of triggered alert rules
        """
        triggered_rules = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            try:
                if rule.condition(log):
                    triggered_rules.append(rule)
                    logger.debug(
                        "alert_rule_triggered",
                        rule_name=rule.name,
                        severity=rule.severity,
                        log_id=log.get("fingerprint", "unknown"),
                    )
            except Exception as e:
                logger.error(
                    "alert_rule_evaluation_failed",
                    rule_name=rule.name,
                    error=str(e),
                )

        return triggered_rules

    def get_all_rules(self) -> List[Dict[str, Any]]:
        """
        Get all alert rules.

        Returns:
            List of rule definitions
        """
        return [
            {
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity,
                "enabled": rule.enabled,
            }
            for rule in self.rules
        ]
