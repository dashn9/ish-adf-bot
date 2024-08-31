#!/bin/bash
{
# Default output directory
OUTPUT_DIR=${1:-./certificates}

meta() { curl -s "http://169.254.169.254/latest/meta-data/$1"; }

HOSTNAME=${1:-$(meta hostname)}
INTERNAL_IP=${2:-$(meta local-ipv4)}
PUBLIC_IP=${3:-$(meta public-ipv4)}

echo "HOSTNAME: $HOSTNAME"
echo "INTERNAL_IP: $INTERNAL_IP"
echo "PUBLIC_IP: $PUBLIC_IP"

# Paths to the CA key and certificate
CA_KEY="$OUTPUT_DIR/k8s-ca.key"
CA_CERT="$OUTPUT_DIR/k8s-ca.crt"

# Ensure the CA key and certificate exist
if [[ ! -f "$CA_KEY" || ! -f "$CA_CERT" ]]; then
    echo "CA key or certificate not found in $OUTPUT_DIR. Please generate the CA first."
    exit 1
fi

./generate_cert.sh "kubelet-server" "$HOSTNAME" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" -ip $INTERNAL_IP
./generate_cert.sh "kubelet-client" "system:node:$HOSTNAME" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" ip $INTERNAL_IP

./generate_cert.sh "kubelet-proxy" "kube-proxy" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"
echo "Worker Certificates generated in $OUTPUT_DIR."
} >> worker_init.log