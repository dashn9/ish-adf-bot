#!/bin/bash

# Default output directory
OUTPUT_DIR=${1:-~/ish_bot_kube_cluster_certificates}

# Paths to the CA key and certificate
CA_KEY="$OUTPUT_DIR/certs/k8s-ca.key"
CA_CERT="$OUTPUT_DIR/certs/k8s-ca.crt"

# Ensure the CA key and certificate exist
if [[ ! -f "$CA_KEY" || ! -f "$CA_CERT" ]]; then
    echo "CA key or certificate not found in $OUTPUT_DIR. Please generate the CA first."
    exit 1
fi

# Get the directory of the currently running script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Change to that directory
cd "$SCRIPT_DIR"

# # Generate certificates for each component using the separate script
chmod +x ./generate_certificate.sh

# Kubernetes API Server with separate DNS and IP SANs
./generate_certificate.sh "kubernetes-apiserver" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" \
    --dns "kubernetes,kubernetes.default,kubernetes.default.svc,kubernetes.default.svc.cluster.local" \
    --ip "127.0.0.1,10.32.0.1"

# Kubernetes API Server ETCD Client
./generate_certificate.sh "kubernetes-apiserver-etcd-client" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubeernetes API Server Kubelet Client
./generate_certificate.sh "kubernetes-apiserver-kubelet-client" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Controller Manager
./generate_certificate.sh "kube-controller-manager" "system:kube-controller-manager" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Scheduler
./generate_certificate.sh "kube-scheduler" "system:kube-scheduler" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Admin
./generate_certificate.sh "admin" "kube-admin" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" --group "system:masters"

# etcd
./generate_certificate.sh "etcd-server" "etcd-server " "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" 
./generate_certificate.sh "etcd-peer" "etcd-peer" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

./generate_certificate.sh "kube-proxy" "kube-proxy" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

echo "Control Plane Certificates generated in $OUTPUT_DIR."
