#!/bin/bash

# Default output directory
OUTPUT_DIR=~/ish_bot_kube_cluster_certificates
IPS="127.0.0.1"  # Default internal IP
PUBLIC_IP=""     # Default public IP (empty by default)

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -ip|--ips)
            IPS="$2"
            shift 2
            ;;
        -p|--public-ip)
            PUBLIC_IP="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [-o|--output <output_directory>] [-ip|--ips <internal_ip_list>] [-p|--public-ip <public_ip>]"
            exit 1
            ;;
    esac
done

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

# Make sure the generate_certificate.sh script is executable
chmod +x ./generate_certificate.sh

# Kubernetes API Server with separate DNS and IP SANs
./generate_certificate.sh "kubernetes-apiserver" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" \
    --dns "kubernetes,kubernetes.default,kubernetes.default.svc,kubernetes.default.svc.cluster.local" \
    --ip "$IPS,$PUBLIC_IP"

# Kubernetes API Server Kubelet Client
./generate_certificate.sh "kubernetes-apiserver-kubelet-client" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Controller Manager
./generate_certificate.sh "kube-controller-manager" "system:kube-controller-manager" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Scheduler
./generate_certificate.sh "kube-scheduler" "system:kube-scheduler" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Admin
./generate_certificate.sh "admin" "admin" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" --group "system:masters"

# etcd with specified IPs
./generate_certificate.sh "etcd" "etcd" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" --ip "$IPS"

# Kube Proxy
./generate_certificate.sh "kube-proxy" "system:kube-proxy" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Service Account
./generate_certificate.sh "service-accounts" "service-accounts" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

echo "Control Plane Certificates generated in $OUTPUT_DIR."
