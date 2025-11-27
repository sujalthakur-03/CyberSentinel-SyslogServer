"""
Alert delivery channels (Email, Slack, PagerDuty).
"""
import asyncio
from typing import Dict, Any
from datetime import datetime
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
from logger import get_logger
from metrics import alerts_sent_total, alert_delivery_duration_seconds

logger = get_logger(__name__)


class EmailChannel:
    """Email alert channel."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        to_emails: list[str],
    ):
        """
        Initialize email channel.

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
            to_emails: List of recipient email addresses
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.to_emails = to_emails

    async def send(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert via email.

        Args:
            alert: Alert data

        Returns:
            True if sent successfully, False otherwise
        """
        with alert_delivery_duration_seconds.labels(channel="email").time():
            try:
                # Create message
                message = MIMEMultipart("alternative")
                message["Subject"] = f"[{alert['severity'].upper()}] {alert['rule_name']}"
                message["From"] = self.from_email
                message["To"] = ", ".join(self.to_emails)

                # Plain text body
                text_body = f"""
CyberSentinel Alert

Severity: {alert['severity'].upper()}
Rule: {alert['rule_name']}
Description: {alert['description']}
Timestamp: {alert['timestamp']}

Log Details:
- Hostname: {alert['log_data'].get('hostname', 'N/A')}
- Source IP: {alert['log_data'].get('source_ip', 'N/A')}
- Facility: {alert['log_data'].get('facility_name', 'N/A')}
- Severity: {alert['log_data'].get('severity_name', 'N/A')}
- Message: {alert['log_data'].get('message', 'N/A')}

Threat Score: {alert['log_data'].get('threat_score', 0)}
Threat Indicators: {', '.join(alert['log_data'].get('threat_keywords', [])) or 'None'}
                """

                # HTML body
                html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <div style="background-color: #f44336; color: white; padding: 20px; border-radius: 5px;">
      <h2>CyberSentinel Alert</h2>
      <p><strong>Severity:</strong> {alert['severity'].upper()}</p>
    </div>

    <div style="padding: 20px; background-color: #f5f5f5; margin-top: 20px; border-radius: 5px;">
      <h3>{alert['rule_name']}</h3>
      <p>{alert['description']}</p>
      <p><strong>Timestamp:</strong> {alert['timestamp']}</p>
    </div>

    <div style="padding: 20px; margin-top: 20px;">
      <h3>Log Details</h3>
      <table style="width: 100%; border-collapse: collapse;">
        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Hostname:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{alert['log_data'].get('hostname', 'N/A')}</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Source IP:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{alert['log_data'].get('source_ip', 'N/A')}</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Facility:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{alert['log_data'].get('facility_name', 'N/A')}</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Severity:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{alert['log_data'].get('severity_name', 'N/A')}</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Message:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{alert['log_data'].get('message', 'N/A')}</td></tr>
        <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Threat Score:</strong></td><td style="padding: 8px; border: 1px solid #ddd;">{alert['log_data'].get('threat_score', 0)}</td></tr>
      </table>
    </div>
  </body>
</html>
                """

                # Attach parts
                part1 = MIMEText(text_body, "plain")
                part2 = MIMEText(html_body, "html")
                message.attach(part1)
                message.attach(part2)

                # Send email
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_user,
                    password=self.smtp_password,
                    start_tls=True,
                    timeout=30,
                )

                logger.info(
                    "email_alert_sent",
                    rule_name=alert["rule_name"],
                    to_emails=self.to_emails,
                )
                alerts_sent_total.labels(channel="email", status="success").inc()
                return True

            except Exception as e:
                logger.error("email_alert_failed", error=str(e), rule_name=alert["rule_name"])
                alerts_sent_total.labels(channel="email", status="failed").inc()
                return False


class SlackChannel:
    """Slack alert channel."""

    def __init__(self, webhook_url: str):
        """
        Initialize Slack channel.

        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url

    async def send(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert to Slack.

        Args:
            alert: Alert data

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            logger.warning("slack_webhook_not_configured")
            return False

        with alert_delivery_duration_seconds.labels(channel="slack").time():
            try:
                # Build Slack message
                color_map = {
                    "critical": "#ff0000",
                    "high": "#ff6600",
                    "medium": "#ffcc00",
                    "low": "#00cc00",
                }

                payload = {
                    "text": f":rotating_light: *CyberSentinel Alert* - {alert['rule_name']}",
                    "attachments": [
                        {
                            "color": color_map.get(alert["severity"], "#cccccc"),
                            "fields": [
                                {
                                    "title": "Severity",
                                    "value": alert["severity"].upper(),
                                    "short": True,
                                },
                                {
                                    "title": "Rule",
                                    "value": alert["rule_name"],
                                    "short": True,
                                },
                                {
                                    "title": "Description",
                                    "value": alert["description"],
                                    "short": False,
                                },
                                {
                                    "title": "Hostname",
                                    "value": alert["log_data"].get("hostname", "N/A"),
                                    "short": True,
                                },
                                {
                                    "title": "Source IP",
                                    "value": alert["log_data"].get("source_ip", "N/A"),
                                    "short": True,
                                },
                                {
                                    "title": "Message",
                                    "value": alert["log_data"].get("message", "N/A")[:200],
                                    "short": False,
                                },
                                {
                                    "title": "Threat Score",
                                    "value": str(alert["log_data"].get("threat_score", 0)),
                                    "short": True,
                                },
                            ],
                            "footer": "CyberSentinel",
                            "ts": int(datetime.utcnow().timestamp()),
                        }
                    ],
                }

                # Send to Slack
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.webhook_url, json=payload, timeout=10) as resp:
                        if resp.status == 200:
                            logger.info("slack_alert_sent", rule_name=alert["rule_name"])
                            alerts_sent_total.labels(channel="slack", status="success").inc()
                            return True
                        else:
                            logger.error(
                                "slack_alert_failed",
                                status=resp.status,
                                rule_name=alert["rule_name"],
                            )
                            alerts_sent_total.labels(channel="slack", status="failed").inc()
                            return False

            except Exception as e:
                logger.error("slack_alert_exception", error=str(e), rule_name=alert["rule_name"])
                alerts_sent_total.labels(channel="slack", status="failed").inc()
                return False


class AlertChannelManager:
    """Manage multiple alert channels."""

    def __init__(self):
        """Initialize alert channel manager."""
        self.channels = []

    def add_channel(self, channel) -> None:
        """
        Add an alert channel.

        Args:
            channel: Alert channel instance
        """
        self.channels.append(channel)

    async def send_alert(self, alert: Dict[str, Any]) -> None:
        """
        Send alert through all configured channels.

        Args:
            alert: Alert data
        """
        if not self.channels:
            logger.warning("no_alert_channels_configured")
            return

        # Send to all channels in parallel
        tasks = [channel.send(alert) for channel in self.channels]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        logger.info(
            "alert_sent_to_channels",
            rule_name=alert["rule_name"],
            total_channels=len(self.channels),
            successful=success_count,
        )
