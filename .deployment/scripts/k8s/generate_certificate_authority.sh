#!/bin/bash

echo && echo "$0: " && echo

# Set the directory to store the CA files
OUTPUT_DIR=${3:-~/ish_bot_kube_cluster_certificates}
KEY_NAME=${1:-ca}
CN=${2:-CN}
# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR/certs"
mkdir -p "$OUTPUT_DIR/configs"

# Variables
CA_KEY="$OUTPUT_DIR/certs/${KEY_NAME}.key"
CA_CERT="$OUTPUT_DIR/certs/${KEY_NAME}.crt"
CA_CONFIG="$OUTPUT_DIR/configs/${KEY_NAME}-config.cnf"
CA_SUBJECT="/CN=kubernetes-ca"
VALIDITY_DAYS=3650  # 10 years

# Create the CA configuration file
cat > $CA_CONFIG <<EOF
[ req ]
default_bits       = 4096
prompt             = no
default_md         = sha256
req_extensions     = v3_req
distinguished_name = dn

[ dn ]
CN = ${CN}

[ v3_req ]
keyUsage = critical, digitalSignature, keyEncipherment, keyCertSign
basicConstraints = critical, CA:true
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kubernetes
DNS.2 = kubernetes.default
DNS.3 = kubernetes.default.svc
DNS.4 = kubernetes.default.svc.cluster.local
EOF

# Generate the CA private key
echo "Generating private key for the ${CN}..."
openssl genrsa -out $CA_KEY 4096

# Generate the CA certificate
echo "Generating self-signed certificate for the ${CN}..."
openssl req -x509 -new -nodes -key $CA_KEY -sha256 -days $VALIDITY_DAYS -out $CA_CERT -subj "$CA_SUBJECT" -config $CA_CONFIG

# Output details
echo "${CN} private key and certificate generated:"
echo "Private Key: $CA_KEY"
echo "Certificate: $CA_CERT"
