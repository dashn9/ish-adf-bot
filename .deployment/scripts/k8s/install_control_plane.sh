#!/bin/bash

{
echo && echo "$0: " && echo

# Install/prepare etcd
wget -q --show-progress --https-only --timestamping \
    "https://storage.googleapis.com/etcd/v3.5.15/etcd-v3.5.15-linux-amd64.tar.gz"
tar -xvf etcd-v3.5.15-linux-amd64.tar.gz
sudo mv etcd-v3.5.15-linux-amd64/etcd* /usr/local/bin/

# Provision Kubernetes Control Plane
sudo mkdir -p /etc/kubernetes/config
wget -q --show-progress --https-only --timestamping \
  "http://dl.k8s.io/v1.31.0/bin/linux/amd64/kube-apiserver" \
  "https://dl.k8s.io/v1.31.0/bin/linux/amd64/kube-controller-manager" \
  "https://dl.k8s.io/v1.31.0/bin/linux/amd64/kube-scheduler" \
  "https://dl.k8s.io/v1.31.0/bin/linux/amd64/kubectl"
chmod +x kube-apiserver kube-controller-manager kube-scheduler kubectl
sudo mv kube-apiserver kube-controller-manager kube-scheduler kubectl /usr/local/bin/
} >> ./control_plane_installation.log