#!/bin/bash

# Default output directory
OUTPUT_DIR=${1:-./certificates}

meta() { curl -s "http://169.254.169.254/latest/meta-data/$1"; }

HOSTNAME=$(hostname -s)
INTERNAL_IP=${2:-$(meta local-ipv4)}

# Please consider using TLS bootstrapping in the future, for automated certificate signings on nodes
# Paths to the CA key and certificate
CA_KEY="$OUTPUT_DIR/k8s-ca.key"
CA_CERT="$OUTPUT_DIR/k8s-ca.crt"

# Ensure the CA key and certificate exist
if [[ ! -f "$CA_KEY" || ! -f "$CA_CERT" ]]; then
    echo "CA key or certificate not found in $OUTPUT_DIR. Please generate the CA first."
    exit 1
fi

chmod +x ./generate_certificate.sh

./generate_certificate.sh "${HOSTNAME}-kubelet-server" "system:node:$HOSTNAME" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" --dns $HOSTNAME,$(meta public-ipv4),$(meta hostname) --ip $INTERNAL_IP --group "system:nodes"

# mv certs to base dirs

sudo mv ./certs/* .


# There is no reason for this key to be lingering on the instance after cert creation
sudo rm -r k8s-ca.key
echo "Worker Certificates generated in $OUTPUT_DIR."