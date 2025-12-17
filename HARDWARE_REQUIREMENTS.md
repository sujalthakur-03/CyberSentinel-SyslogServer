# Hardware Requirements - CyberSentinel SyslogServer

## Overview

This document provides comprehensive hardware requirements for deploying CyberSentinel SyslogServer configured to handle **1000+ network devices** with **180-day log retention**.

---

## Executive Summary

### Recommended Production Configuration

| Component | Specification |
|-----------|--------------|
| **CPU** | 16 cores (32 threads) @ 2.5GHz+ |
| **RAM** | 32 GB DDR4/DDR5 |
| **Storage** | 500 GB NVMe SSD (minimum) |
| **Network** | 1 Gbps NIC (10 Gbps recommended) |
| **OS** | Ubuntu 22.04 LTS or later |

### Minimum Configuration (Not Recommended for Production)

| Component | Specification |
|-----------|--------------|
| **CPU** | 8 cores @ 2.0GHz |
| **RAM** | 16 GB DDR4 |
| **Storage** | 200 GB SSD |
| **Network** | 1 Gbps NIC |

---

## Detailed Requirements

### 1. CPU Requirements

#### Recommended: 16 Cores (32 Threads)
- **Receiver Service**: 2-4 cores for handling UDP/TCP/TLS syslog traffic
- **Processor Services**: 8-12 cores (4 replicas × 8 workers each)
- **OpenSearch**: 4-6 cores for indexing and search operations
- **Kafka**: 2-4 cores for message queue processing
- **Other Services**: 2-4 cores (API, Frontend, Redis, PostgreSQL, Prometheus)

#### Minimum: 8 Cores
- Suitable for testing or low-volume deployments (<500 devices)
- May experience performance degradation under peak load

#### Processor Type Recommendations
- **Intel**: Xeon E5/Scalable series, Core i7/i9 (11th gen+)
- **AMD**: EPYC 7002/7003 series, Ryzen 9 (5000 series+)
- **Clock Speed**: 2.5 GHz base, 3.5+ GHz boost

---

### 2. Memory (RAM) Requirements

#### Component Breakdown (Recommended: 32 GB Total)

| Service | Memory Allocation | Purpose |
|---------|------------------|---------|
| **OpenSearch** | 4 GB | Log storage and search engine |
| **Processor** (4 replicas) | 8 GB total (2GB each) | Log processing and enrichment |
| **Kafka** | 2 GB | Message queue buffering |
| **Receiver** | 1 GB | Syslog ingestion |
| **PostgreSQL** | 1 GB | User database |
| **Redis** | 512 MB | Caching and deduplication |
| **API** | 512 MB | REST API service |
| **Frontend** | 256 MB | Web interface |
| **Alerting** | 256 MB | Threat detection and alerts |
| **Prometheus** | 512 MB | Metrics collection |
| **System Reserve** | 13 GB | Operating system and buffers |

#### Memory Type
- **DDR4**: 2666 MHz or faster
- **DDR5**: 4800 MHz or faster (recommended for new builds)
- **ECC RAM**: Strongly recommended for production to prevent data corruption

#### Minimum Configuration (16 GB)
Requires reducing service resources:
- OpenSearch: 2 GB (reduced performance)
- Processor: 4 GB total (2 replicas instead of 4)
- Kafka: 1 GB
- System reserve: 7-8 GB

---

### 3. Storage Requirements

#### Capacity Calculation for 180-Day Retention

**Assumptions:**
- 1000 network devices
- Average 100 logs/device/day (varies by device type)
- Average log size: 1 KB/log

**Calculation:**
```
Daily logs: 1000 devices × 100 logs/day = 100,000 logs/day
Total logs (180 days): 100,000 × 180 = 18,000,000 logs
Raw data size: 18M logs × 1 KB = 18 GB
```

**With OpenSearch overhead:**
- Index metadata: +20% = 3.6 GB
- Replication (1 replica): ×2 = 43.2 GB
- Compression savings (best_compression): -30% = 30.2 GB
- Daily indices overhead: +10% = 33.2 GB
- System and services: +50 GB base
- **Kafka buffer**: +10 GB
- **PostgreSQL**: +5 GB
- **Logs and backups**: +20 GB

**Total Storage Required:**
- **Minimum**: 200 GB SSD
- **Recommended**: 500 GB NVMe SSD
- **Optimal**: 1 TB NVMe SSD (with growth headroom)

#### Storage Type

| Type | Use Case | Performance |
|------|----------|-------------|
| **NVMe SSD** (Recommended) | Production deployment | 3000+ MB/s read/write, <0.1ms latency |
| **SATA SSD** (Acceptable) | Budget deployment | 500+ MB/s read/write, <1ms latency |
| **HDD** (Not Recommended) | Not suitable | Too slow for real-time log processing |

#### IOPS Requirements
- **Minimum**: 5,000 IOPS
- **Recommended**: 15,000+ IOPS
- NVMe drives typically provide 100,000+ IOPS

#### Storage Layout
```
/var/lib/docker/volumes/
├── opensearch-data/     # 150-400 GB (largest volume)
├── kafka-data/          # 10-50 GB
├── postgres-data/       # 5-10 GB
├── redis-data/          # 1-5 GB
├── prometheus-data/     # 10-20 GB
└── [other volumes]      # 5-10 GB
```

---

### 4. Network Requirements

#### Network Interface Card (NIC)

| Configuration | Specification | Use Case |
|--------------|---------------|----------|
| **Recommended** | 10 Gbps | Large deployments (1000+ devices) |
| **Acceptable** | 1 Gbps | Standard deployments |
| **Minimum** | 1 Gbps | Small deployments (<500 devices) |

#### Bandwidth Estimation

**Syslog Traffic:**
- 100,000 logs/day = 1.16 logs/second average
- Peak traffic (5× average): ~6 logs/second
- Average log size: 1 KB
- **Sustained throughput**: ~10 KB/s (~0.08 Mbps)
- **Peak throughput**: ~50 KB/s (~0.4 Mbps)

**Total Network Usage:**
- Syslog ingestion: 0.4 Mbps peak
- API queries: 1-5 Mbps (varies with usage)
- Frontend access: 0.5-2 Mbps
- Internal communication: 2-5 Mbps
- **Total peak**: ~10-15 Mbps

**Conclusion:** 1 Gbps NIC is more than sufficient, but 10 Gbps provides headroom for:
- Sudden traffic spikes (DDoS events, mass reboots)
- Future expansion
- Backup/restore operations

#### Port Requirements
Ensure these ports are accessible:
- **514/UDP & 514/TCP**: Syslog ingestion
- **6514/TCP**: Syslog over TLS
- **3000/TCP**: Frontend web interface
- **8000/TCP**: REST API
- **9090/TCP**: Prometheus (optional)

---

### 5. Operating System Requirements

#### Recommended OS
- **Ubuntu 22.04 LTS** or **24.04 LTS** (official support)
- **Debian 12** (Bookworm)
- **CentOS Stream 9** / **Rocky Linux 9**
- **Red Hat Enterprise Linux 9**

#### Kernel Requirements
- Linux kernel 5.15+ (Ubuntu 22.04 default)
- Supports Docker and containerization
- Memory management optimizations

#### System Dependencies
The installation script will install:
- **Docker Engine** 24.0+
- **Docker Compose** 2.20+
- Standard Linux utilities (curl, git, etc.)

#### System Settings
Required kernel parameters (set automatically by Docker):
```bash
vm.max_map_count=262144        # For OpenSearch
fs.file-max=65536              # Open file limits
net.core.somaxconn=65535       # Network connections
```

---

### 6. Virtualization Considerations

#### Bare Metal vs Virtual Machines

| Platform | Suitability | Notes |
|----------|-------------|-------|
| **Bare Metal** | Excellent | Best performance, full resource access |
| **VMware ESXi** | Excellent | Near-native performance with proper allocation |
| **Proxmox** | Excellent | KVM-based, good performance |
| **Hyper-V** | Good | Ensure nested virtualization if using Docker |
| **AWS EC2** | Good | See cloud recommendations below |
| **Azure VMs** | Good | Use Dv4/Ev4 series or higher |
| **Google Cloud** | Good | Use n2-standard-8 or higher |

#### VM Configuration Tips
1. **CPU**: Pin vCPUs to physical cores (CPU affinity)
2. **Memory**: Disable memory ballooning, use dedicated RAM
3. **Storage**: Use SSD-backed datastores
4. **Network**: Use virtio or VMXnet3 drivers
5. **Docker**: Ensure nested virtualization is enabled

---

### 7. Cloud Deployment Recommendations

#### AWS (Amazon Web Services)

| Instance Type | vCPU | RAM | Storage | Use Case |
|--------------|------|-----|---------|----------|
| **m6i.2xlarge** (Recommended) | 8 | 32 GB | EBS gp3 | Production |
| **m6i.xlarge** (Minimum) | 4 | 16 GB | EBS gp3 | Testing |
| **m6i.4xlarge** (High-Scale) | 16 | 64 GB | EBS gp3 | 2000+ devices |

**Storage:**
- EBS gp3: 500 GB, 3000 IOPS, 125 MB/s throughput
- Alternative: io2 for mission-critical workloads

**Cost Estimate (m6i.2xlarge):** ~$300-350/month (us-east-1)

#### Microsoft Azure

| Instance Type | vCPU | RAM | Use Case |
|--------------|------|-----|----------|
| **Standard_D8s_v4** (Recommended) | 8 | 32 GB | Production |
| **Standard_D4s_v4** (Minimum) | 4 | 16 GB | Testing |
| **Standard_E8s_v4** (Memory-Optimized) | 8 | 64 GB | Large deployments |

**Storage:** Premium SSD (P30: 1 TB, 5000 IOPS)

#### Google Cloud Platform

| Instance Type | vCPU | RAM | Use Case |
|--------------|------|-----|----------|
| **n2-standard-8** (Recommended) | 8 | 32 GB | Production |
| **n2-standard-4** (Minimum) | 4 | 16 GB | Testing |
| **n2-highmem-8** (Memory-Optimized) | 8 | 64 GB | Large deployments |

**Storage:** SSD persistent disk (500 GB)

---

### 8. Performance Scaling Guidelines

#### Horizontal Scaling Options

| Scenario | Devices | Logs/Day | Processor Replicas | OpenSearch Memory | Total RAM |
|----------|---------|----------|-------------------|------------------|-----------|
| **Small** | 100-500 | 10K-50K | 2 | 2 GB | 16 GB |
| **Medium** | 500-1000 | 50K-100K | 4 | 4 GB | 32 GB |
| **Large** | 1000-2000 | 100K-200K | 6 | 6 GB | 48 GB |
| **Enterprise** | 2000-5000 | 200K-500K | 8 | 8 GB | 64 GB |
| **Massive** | 5000+ | 500K+ | 10+ | 16 GB | 128 GB+ |

#### When to Upgrade

**Signs you need more resources:**
- CPU usage consistently >80%
- Memory usage >90%
- Kafka lag increasing (check with `docker logs`)
- OpenSearch JVM heap >85% used
- Log processing delays >5 minutes
- Search queries taking >3 seconds

**Scaling Actions:**
1. **CPU bottleneck**: Increase `PROCESSOR_REPLICAS` in `.env`
2. **Memory bottleneck**: Increase `OPENSEARCH_MAX_MEMORY` or add more RAM
3. **Storage bottleneck**: Add faster disks or expand volume
4. **Network bottleneck**: Upgrade NIC or check for network issues

---

### 9. Storage Growth Calculator

#### Estimate Your Storage Needs

Use this formula to calculate storage for your environment:

```
Total Storage (GB) = (Devices × Logs/Device/Day × Log_Size_KB × Retention_Days × 1.5) / 1,000,000 + 100
```

**Example Calculations:**

| Devices | Logs/Day Each | Log Size | Retention | Calculation | Total Storage |
|---------|--------------|----------|-----------|-------------|---------------|
| 500 | 100 | 1 KB | 180 days | (500×100×1×180×1.5)/1M + 100 | **114 GB** |
| 1000 | 100 | 1 KB | 180 days | (1000×100×1×180×1.5)/1M + 100 | **127 GB** |
| 1000 | 200 | 1 KB | 180 days | (1000×200×1×180×1.5)/1M + 100 | **154 GB** |
| 2000 | 100 | 1 KB | 180 days | (2000×100×1×180×1.5)/1M + 100 | **154 GB** |
| 1000 | 100 | 2 KB | 180 days | (1000×100×2×180×1.5)/1M + 100 | **154 GB** |
| 5000 | 100 | 1 KB | 180 days | (5000×100×1×180×1.5)/1M + 100 | **235 GB** |

*1.5× factor accounts for replication, indexing overhead, and compression*

**Recommendation:** Add 50-100% buffer for growth and operational headroom.

---

### 10. Cost Estimates

#### On-Premises Server (One-Time Cost)

| Component | Specification | Est. Cost |
|-----------|--------------|-----------|
| CPU | AMD EPYC 7313 (16-core) | $800 |
| Motherboard | Server-grade ATX | $400 |
| RAM | 64 GB DDR4 ECC (4×16GB) | $350 |
| Storage | 1TB NVMe SSD (Samsung 980 Pro) | $120 |
| Storage | 2TB SATA SSD (backup) | $150 |
| Case + PSU | Server chassis, 850W PSU | $250 |
| Network | 10 Gbps NIC | $100 |
| **Total** | | **~$2,170** |

*Prices as of 2025, USD. Does not include rack, UPS, cooling.*

#### Cloud Hosting (Monthly Cost)

| Provider | Instance Type | Monthly Cost |
|----------|--------------|--------------|
| **AWS** | m6i.2xlarge + 500GB gp3 | ~$350 |
| **Azure** | Standard_D8s_v4 + P30 disk | ~$400 |
| **GCP** | n2-standard-8 + 500GB SSD | ~$320 |
| **DigitalOcean** | 8vCPU/32GB + 500GB SSD | ~$280 |
| **Linode** | Dedicated 16GB + 500GB SSD | ~$180 |

*Estimated costs, actual may vary by region and usage*

---

### 11. Recommended Server Configurations

#### Budget Build (~$1,500)
```
CPU: AMD Ryzen 9 5900X (12-core)
RAM: 32 GB DDR4 (2×16GB)
Storage: 500 GB NVMe SSD
Network: 1 Gbps NIC (onboard)
OS: Ubuntu 22.04 LTS
Use Case: 500-1000 devices, 180-day retention
```

#### Recommended Build (~$2,500)
```
CPU: AMD EPYC 7313 (16-core) or Intel Xeon Silver 4314
RAM: 64 GB DDR4 ECC (4×16GB)
Storage: 1 TB NVMe SSD (primary) + 2TB SATA SSD (backup)
Network: 10 Gbps NIC
OS: Ubuntu 22.04 LTS
Use Case: 1000-2000 devices, 180-day retention
```

#### Enterprise Build (~$5,000+)
```
CPU: AMD EPYC 7543 (32-core) or Intel Xeon Gold 6338
RAM: 128 GB DDR4 ECC (8×16GB)
Storage: 2 TB NVMe SSD (RAID 1) + 4TB SATA SSD (backup)
Network: Dual 10 Gbps NICs (bonded)
RAID Controller: Hardware RAID with BBU
OS: Ubuntu 22.04 LTS or RHEL 9
Use Case: 5000+ devices, 180-day+ retention
```

---

### 12. Monitoring Resource Usage

After deployment, monitor these metrics:

#### CPU Monitoring
```bash
# Overall CPU usage
docker stats --no-stream

# Top CPU-consuming containers
docker stats --format "table {{.Container}}\t{{.CPUPerc}}" | sort -k2 -hr
```

#### Memory Monitoring
```bash
# Memory usage by container
docker stats --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Check OpenSearch heap usage
curl http://localhost:9200/_nodes/stats/jvm?pretty
```

#### Storage Monitoring
```bash
# Disk usage by volume
docker system df -v

# OpenSearch index sizes
curl http://localhost:9200/_cat/indices?v&s=store.size:desc
```

#### Network Monitoring
```bash
# Network traffic by container
docker stats --format "table {{.Container}}\t{{.NetIO}}"

# Check syslog receiver stats
curl http://localhost:9100/metrics | grep receiver
```

---

### 13. FAQ

#### Q: Can I run this on a Raspberry Pi?
**A:** No. Insufficient CPU, RAM, and storage. Minimum is an x86_64 server with 8 cores and 16 GB RAM.

#### Q: Can I use HDD instead of SSD?
**A:** Not recommended. HDDs are too slow for real-time log indexing. OpenSearch requires fast I/O.

#### Q: What if I have 10,000 devices?
**A:** Scale up to:
- 32 cores CPU
- 64-128 GB RAM
- 8+ processor replicas
- 8-16 GB OpenSearch memory
- 1+ TB storage

#### Q: Can I reduce memory to 8 GB?
**A:** Only for testing <100 devices. Production requires minimum 16 GB, recommended 32 GB.

#### Q: Do I need a GPU?
**A:** No. CyberSentinel doesn't use GPU acceleration.

#### Q: Can I deploy across multiple servers?
**A:** Not out-of-the-box. You'd need to set up Kafka cluster, OpenSearch cluster, and load balancers. Contact for enterprise clustering options.

---

## Quick Reference Card

| Requirement | Minimum | Recommended | Enterprise |
|-------------|---------|-------------|------------|
| **CPU** | 8 cores | 16 cores | 32+ cores |
| **RAM** | 16 GB | 32 GB | 64-128 GB |
| **Storage** | 200 GB SSD | 500 GB NVMe | 1-2 TB NVMe |
| **Network** | 1 Gbps | 1-10 Gbps | 10 Gbps bonded |
| **Devices** | <500 | 1000-2000 | 5000+ |
| **Logs/Day** | <50K | 100K-200K | 500K+ |
| **Retention** | 90 days | 180 days | 365+ days |
| **IOPS** | 5K | 15K+ | 50K+ |

---

## Summary

For **1000+ network devices with 180-day log retention**, the recommended configuration is:

```
CPU: 16 cores @ 2.5 GHz (AMD EPYC or Intel Xeon)
RAM: 32 GB DDR4 ECC
Storage: 500 GB NVMe SSD
Network: 10 Gbps NIC
OS: Ubuntu 22.04 LTS
Estimated Cost: $2,500 (on-prem) or $300/month (cloud)
```

This configuration provides comfortable headroom for growth and ensures reliable, high-performance log management for your SOC environment.

---

**Document Version:** 1.0
**Last Updated:** 2025-12-17
**Author:** CyberSentinel Team
