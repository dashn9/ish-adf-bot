#!/bin/bash

echo && echo "$0: " && echo

KEY_NAME=${1:-"ca"}
CN=${2:-"kubernetes-ca"}
OUTPUT_DIR=${3:-~/ish_bot_kube_cluster_certificates}
# Create the directory if it doesn't exist
mkdir -p "$OUTPUT_DIR/certs"
mkdir -p "$OUTPUT_DIR/configs"

# Variables
CA_KEY="$OUTPUT_DIR/certs/${KEY_NAME}.key"
CA_CSR="$OUTPUT_DIR/certs/${KEY_NAME}.csr"
CA_CERT="$OUTPUT_DIR/certs/${KEY_NAME}.crt"
CA_CONFIG="$OUTPUT_DIR/configs/${KEY_NAME}-config.cnf"
VALIDITY_DAYS=3650  # 10 years

# Generate the CA private key
echo "Generating private key for $KEY_NAME..."
openssl genrsa -out $CA_KEY 4096

openssl req -x509 -new -sha512 -noenc -key $CA_KEY -days 3653 -subj "/CN=$CN" -out $CA_CERT

# Generate the CA certificate

# Output details
echo "$KEY_NAME private key and certificate generated:"
echo "Private Key: $CA_KEY"
echo "Certificate: $CA_CERT"
