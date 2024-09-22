#!/bin/bash

echo && echo "$0: " && echo

kubectl config set-cluster ish-bot-kube \
    --certificate-authority=k8s-ca.crt \
    --embed-certs=true \
    --server=https://127.0.0.1:6443 \
    --kubeconfig=admin.kubeconfig

kubectl config set-credentials admin \
    --client-certificate=admin.crt \
    --embed-certs=true \
    --client-key=admin.key \
    --kubeconfig=admin.kubeconfig

kubectl config set-context default \
    --cluster=ish-bot-kube \
    --user=admin \
    --kubeconfig=admin.kubeconfig

kubectl config use-context default --kubeconfig=admin.kubeconfig