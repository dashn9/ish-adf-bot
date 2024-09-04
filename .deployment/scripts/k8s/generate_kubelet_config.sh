#!/bin/bash

echo && echo "$0: " && echo

# Static IP address provisioned in networking.tf passed as an argument
KUBERNETES_PUBLIC_ADDRESS=$1

# Get the instance's private DNS hostname in AWS
NODE_NAME=$(hostname -s)

echo "Kubernetes Public Address: $KUBERNETES_PUBLIC_ADDRESS"
echo "Node Name: $NODE_NAME"

# Set up kubeconfig for the node
kubectl config set-cluster ish-bot-kube \
    --certificate-authority=/var/lib/kubernetes/pki/k8s-ca.crt \
    --server=https://"${KUBERNETES_PUBLIC_ADDRESS}":6443 \
    --kubeconfig="${NODE_NAME}".kubeconfig

kubectl config set-credentials system:node:"${NODE_NAME}" \
    --client-certificate=/var/lib/kubernetes/pki/"${NODE_NAME}"-kubelet-server.crt \
    --client-key=/var/lib/kubernetes/pki/"${NODE_NAME}"-kubelet-server.key \
    --kubeconfig="${NODE_NAME}".kubeconfig

kubectl config set-context default \
    --cluster=ish-bot-kube \
    --user=system:node:"${NODE_NAME}" \
    --kubeconfig="${NODE_NAME}".kubeconfig

kubectl config use-context default --kubeconfig="${NODE_NAME}".kubeconfig
