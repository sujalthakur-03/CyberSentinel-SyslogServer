#!/bin/bash
# Generate self-signed TLS certificates for syslog TLS receiver

set -e

CERT_DIR="./certs"
DAYS=365
COUNTRY="US"
STATE="State"
CITY="City"
ORG="CyberSentinel"
CN="syslog.cybersentinel.local"

echo "Generating TLS certificates for CyberSentinel..."

# Create certs directory
mkdir -p ${CERT_DIR}

# Generate private key
openssl genrsa -out ${CERT_DIR}/server.key 2048

# Generate certificate signing request
openssl req -new -key ${CERT_DIR}/server.key -out ${CERT_DIR}/server.csr \
    -subj "/C=${COUNTRY}/ST=${STATE}/L=${CITY}/O=${ORG}/CN=${CN}"

# Generate self-signed certificate
openssl x509 -req -days ${DAYS} -in ${CERT_DIR}/server.csr \
    -signkey ${CERT_DIR}/server.key -out ${CERT_DIR}/server.crt

# Set proper permissions
chmod 600 ${CERT_DIR}/server.key
chmod 644 ${CERT_DIR}/server.crt

echo "✓ TLS certificates generated successfully!"
echo "  Certificate: ${CERT_DIR}/server.crt"
echo "  Private Key: ${CERT_DIR}/server.key"
echo "  Valid for: ${DAYS} days"
echo ""
echo "To use TLS, set RECEIVER_TLS_ENABLED=true in .env"
