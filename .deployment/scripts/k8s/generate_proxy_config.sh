#!/bin/bash

echo && echo "$0: " && echo

KUBERNETES_PUBLIC_ADDRESS=$1 # Static IP address provisioned in networking.tf

kubectl config set-cluster ish-bot-kube \
    --certificate-authority=/var/lib/kubernetes/pki/k8s-ca.crt \
    --server=https://"${KUBERNETES_PUBLIC_ADDRESS}":6443 \
    --kubeconfig=kube-proxy.kubeconfig
    
kubectl config set-credentials system:kube-proxy \
    --client-certificate=/var/lib/kubernetes/pki/kube-proxy.crt \
    --client-key=/var/lib/kubernetes/pki/kube-proxy.key \
    --kubeconfig=kube-proxy.kubeconfig
    
kubectl config set-context default \
    --cluster=ish-bot-kube \
    --user=system:kube-proxy \
    --kubeconfig=kube-proxy.kubeconfig
    
kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig