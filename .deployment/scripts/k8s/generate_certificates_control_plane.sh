#!/bin/bash

# Default output directory
OUTPUT_DIR=${1:-./certificates}

# Paths to the CA key and certificate
CA_KEY="$OUTPUT_DIR/k8s-ca.key"
CA_CERT="$OUTPUT_DIR/k8s-ca.crt"

# Ensure the CA key and certificate exist
if [[ ! -f "$CA_KEY" || ! -f "$CA_CERT" ]]; then
    echo "CA key or certificate not found in $OUTPUT_DIR. Please generate the CA first."
    exit 1
fi

# Generate certificates for each component using the separate script

# Kubernetes API Server with separate DNS and IP SANs
./generate-cert.sh "kubernetes-apiserver" "kubernetes" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" \
    --dns "kubernetes,kubernetes.default,kubernetes.default.svc,kubernetes.default.svc.cluster.local" \
    --ip "127.0.0.1,10.0.0.1"

# Kubernetes API Server ETCD Client
./generate-cert.sh "kubernetes-apiserver-etcd-client" "kubernetes" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubeernetes API Server Kubelet Client
./generate-cert.sh "kubernetes-apiserver-kubelet-client" "kubernetes" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubelet Client
./generate-cert.sh "kubelet-client" "kubelet" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Controller Manager
./generate-cert.sh "kube-controller-manager" "system:kube-controller-manager" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Scheduler
./generate-cert.sh "kube-scheduler" "system:kube-scheduler" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Admin
./generate-cert.sh "admin" "admin" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# etcd
./generate-cert.sh "etcd-server" "etcd" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"
./generate-cert.sh "etcd-client" "etcd-client" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

echo "Certificates generated in $OUTPUT_DIR."
