#!/bin/bash

{
echo && echo "$0: " && echo

KUBE_LATEST="v1.31.0"

sudo mkdir -p /etc/apt/keyrings
wget -qO- https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo apt-key add -
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install Dependencies
sudo apt-get update
sudo apt-get -y install ca-certificates
sudo apt-get install -y containerd kubernetes-cni kubectl


# Install/Configure Worker Dependencies
wget -q --show-progress --https-only --timestamping \
    https://dl.k8s.io/${KUBE_LATEST}/bin/linux/amd64/kube-proxy \
    https://dl.k8s.io/${KUBE_LATEST}/bin/linux/arm64/kubelet

sudo mkdir -p \
    /etc/cni/net.d \
    /opt/cni/bin \
    /var/lib/kubelet \
    /var/lib/kube-proxy \
    /var/lib/kubernetes \
    /var/run/kubernetes

chmod +x kube-proxy kubelet
sudo mv kube-proxy kubelet /usr/local/bin/
} >> install_worker.log