#!/bin/bash

{
echo && echo "$0: " && echo

# Static IP address provisioned in networking.tf passed as an argument
KUBERNETES_PUBLIC_ADDRESS=$1

# Get the instance's private DNS hostname in AWS
NODE_NAME=$(curl -s http://169.254.169.254/latest/meta-data/local-hostname | cut -d. -f1)

echo "Kubernetes Public Address: $KUBERNETES_PUBLIC_ADDRESS"
echo "Node Name: $NODE_NAME"

# Set up kubeconfig for the node
kubectl config set-cluster ish-bot-kube \
    --certificate-authority=k8s-ca.pem \
    --embed-certs=true \
    --server=https://"${KUBERNETES_PUBLIC_ADDRESS}":6443 \
    --kubeconfig="${NODE_NAME}".kubeconfig

kubectl config set-credentials system:node:"${NODE_NAME}" \
    --client-certificate="${NODE_NAME}-kubelet-client".pem \
    --client-key="${NODE_NAME}-kubelet-client".key \
    --embed-certs=true \
    --kubeconfig="${NODE_NAME}".kubeconfig

kubectl config set-context default \
    --cluster=ish-bot-kube \
    --user=system:node:"${NODE_NAME}" \
    --kubeconfig="${NODE_NAME}".kubeconfig

kubectl config use-context default --kubeconfig="${NODE_NAME}".kubeconfig
} >> generate_kubelet_config.log
