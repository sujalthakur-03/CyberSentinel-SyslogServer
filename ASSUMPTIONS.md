# CyberSentinel SyslogServer - Assumptions and Prerequisites

## System Assumptions

### Infrastructure Requirements

1. **Operating System**
   - Linux-based OS (Ubuntu 20.04+, CentOS 8+, Debian 11+, or similar)
   - Docker and Docker Compose installed and running
   - Sufficient permissions to run Docker containers
   - Port availability: 514 (UDP/TCP), 6514 (TCP), 8000, 9090, 3001

2. **Hardware Resources**
   - Minimum 4 CPU cores (8+ recommended for production)
   - Minimum 8 GB RAM (16+ GB recommended)
   - Minimum 50 GB disk space (SSD preferred)
   - Network connectivity for container orchestration

3. **Network Configuration**
   - Firewall allows inbound traffic on syslog ports (514, 6514)
   - Firewall allows outbound SMTP (587) for email alerts
   - Firewall allows outbound HTTPS (443) for Slack webhooks
   - No conflicting services on required ports

### Software Versions

1. **Container Platform**
   - Docker Engine 24.0 or later
   - Docker Compose 2.0 or later
   - Compatible with docker-compose.yml v3.8 specification

2. **External Dependencies**
   - OpenSSL for certificate generation
   - netcat (nc) for testing
   - curl for health checks and API testing
   - bash 4.0+ for scripts

### Security Assumptions

1. **TLS/SSL**
   - Self-signed certificates acceptable for testing/development
   - Production deployments should use proper CA-signed certificates
   - TLS 1.2+ required for encrypted syslog

2. **Authentication**
   - Default credentials (admin/admin, user/user) MUST be changed in production
   - JWT secrets MUST be randomly generated and kept secure
   - API tokens expire after configured time (default 60 minutes)

3. **Network Security**
   - Services run in isolated Docker network
   - Only necessary ports exposed to host
   - Production deployments should use additional firewall rules
   - Consider using reverse proxy (nginx/Traefik) for HTTPS API access

### Data Management

1. **Storage**
   - Docker volumes used for persistent data
   - Data persists across container restarts
   - Regular backups required for production
   - Index rotation configured to manage disk usage

2. **Retention**
   - Default log retention: 7 days (configurable via Kafka settings)
   - OpenSearch indices rotated daily by default
   - Alert deduplication window: 1 hour (configurable via Redis TTL)

3. **Scalability**
   - Single-node deployment by default
   - Processor service can be scaled horizontally
   - Kafka configured for single broker (suitable for <10k logs/sec)
   - OpenSearch single-node (can be clustered for production)

### Log Sources

1. **Syslog Formats**
   - RFC 3164 (BSD syslog) supported
   - RFC 5424 (Syslog Protocol) supported
   - Non-standard formats handled with best-effort parsing
   - Maximum message size: 8192 bytes (configurable)

2. **Protocol Support**
   - UDP: Best-effort delivery, no reliability guarantees
   - TCP: Connection-oriented, more reliable but requires connection management
   - TLS: Encrypted transport, requires certificate configuration

3. **Source Compatibility**
   - Standard syslog daemons (rsyslog, syslog-ng)
   - Network devices (firewalls, routers, switches)
   - Applications using standard syslog libraries
   - Custom integrations via syslog protocol

### Alerting

1. **Email Notifications**
   - SMTP server accessible from container network
   - Credentials configured in .env file
   - Gmail App Passwords recommended for Gmail SMTP
   - HTML email support assumed in recipients' clients

2. **Slack Integration**
   - Webhook URL obtained from Slack workspace
   - Internet connectivity required
   - Webhook must be active and valid

3. **Alert Deduplication**
   - Redis used for storing alert state
   - Same alert not sent more than once per hour (default)
   - Fingerprint-based deduplication

### Monitoring

1. **Prometheus**
   - Metrics retained for 30 days by default
   - All services expose /metrics endpoints
   - Pull-based scraping model

2. **Grafana**
   - Prometheus configured as data source
   - Default credentials must be changed in production
   - Dashboard persistence via volumes

### Development vs Production

1. **Development**
   - Self-signed certificates acceptable
   - Default credentials usable
   - Single instance of each service
   - Debug logging enabled
   - Smaller resource allocations

2. **Production**
   - Valid SSL/TLS certificates required
   - Strong, unique credentials mandatory
   - Multiple processor instances recommended
   - INFO or WARNING log level
   - Appropriate resource limits set
   - Regular backups configured
   - Monitoring actively reviewed
   - Security hardening applied

## Known Limitations

1. **Single-Node Architecture**
   - Default configuration is single-node
   - Kafka single broker (no high availability)
   - OpenSearch single node (no replication)
   - Not suitable for mission-critical HA requirements without modification

2. **Processing Capacity**
   - Default configuration handles ~5,000-10,000 logs/second
   - Higher volumes require scaling and tuning
   - Processor workers configurable but limited by available resources

3. **Storage**
   - No automatic cleanup of old indices (manual/script required)
   - Disk usage grows with log volume
   - Monitor disk space proactively

4. **GeoIP**
   - GeoIP database not included (enrichment placeholder)
   - Requires GeoLite2 or commercial database for production
   - IP extraction regex-based (may miss complex formats)

5. **Threat Intelligence**
   - Basic keyword-based threat detection
   - No integration with threat feeds by default
   - Should be enhanced with commercial threat intel in production

## Recommendations

1. **Before Production Deployment**
   - Review and update all default credentials
   - Generate proper SSL/TLS certificates
   - Configure appropriate resource limits
   - Set up automated backups
   - Test disaster recovery procedures
   - Enable TLS for syslog reception
   - Configure firewall rules
   - Review alert rules and thresholds
   - Set up log rotation and retention policies

2. **Monitoring**
   - Configure alerts in Grafana
   - Monitor disk usage actively
   - Set up log shipping for system logs
   - Review metrics regularly
   - Test alert delivery channels

3. **Security**
   - Run security scans on containers
   - Keep images updated
   - Use secrets management (not .env) in production
   - Implement network segmentation
   - Enable audit logging
   - Use reverse proxy with rate limiting

4. **Performance**
   - Tune JVM heap sizes based on available memory
   - Adjust Kafka partition count for volume
   - Scale processor workers based on CPU
   - Monitor and optimize OpenSearch queries
   - Configure appropriate bulk indexing settings

5. **Maintenance**
   - Schedule regular backups
   - Plan for log rotation
   - Update Docker images periodically
   - Review and update alert rules
   - Clean up old indices
   - Monitor and rotate logs

## Environment-Specific Considerations

### Cloud Deployments

- Consider managed services (Managed Kafka, Elasticsearch/OpenSearch)
- Use cloud-native storage for volumes
- Implement proper IAM roles and policies
- Use cloud monitoring integration
- Consider auto-scaling configurations

### On-Premises

- Ensure adequate network bandwidth
- Plan for hardware maintenance
- Implement proper backup infrastructure
- Consider clustering for HA
- Plan for capacity growth

### Edge Deployments

- May need reduced resource configurations
- Consider local caching and buffering
- Plan for intermittent connectivity
- Implement local alerting failover
- Consider log forwarding to central location

## Support and Documentation

For questions about these assumptions or to request modifications:
- Open an issue on GitHub
- Consult the main README.md
- Review service-specific documentation
- Check Docker logs for troubleshooting

These assumptions may be updated as the project evolves.
