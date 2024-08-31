#!/bin/bash

# Default output directory
OUTPUT_DIR=${1:-./certificates}
KUBERNETES_PUBLIC_ADDRESS=$2

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
./generate-cert.sh "kubernetes-apiserver" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" \
    --dns "kubernetes,kubernetes.default,kubernetes.default.svc,kubernetes.default.svc.cluster.local" \
    --ip "127.0.0.1,10.32.0.1,$KUBERNETES_PUBLIC_ADDRESS"

# Kubernetes API Server ETCD Client
./generate-cert.sh "kubernetes-apiserver-etcd-client" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubeernetes API Server Kubelet Client
./generate-cert.sh "kubernetes-apiserver-kubelet-client" "kube-apiserver" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Controller Manager
./generate-cert.sh "kube-controller-manager" "system:kube-controller-manager" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Scheduler
./generate-cert.sh "kube-scheduler" "system:kube-scheduler" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

# Kubernetes Admin
./generate-cert.sh "admin" "kube-admin" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" --group "system:masters"

# etcd
./generate-cert.sh "etcd-server" "etcd-server " "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT" 
./generate-cert.sh "etcd-peer" "etcd-peer" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

./generate_cert.sh "kubelet-proxy" "kube-proxy" "$OUTPUT_DIR" "$CA_KEY" "$CA_CERT"

echo "Control Plane Certificates generated in $OUTPUT_DIR."
