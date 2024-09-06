#!/bin/bash

echo && echo "$0: " && echo

KUBE_LATEST="v1.31.0"

sudo apt-get update
sudo apt-get install -y gnupg socat conntrack ipset ca-certificates

# Install/Configure Worker Dependencies
wget -q --show-progress --https-only --timestamping \
    https://dl.k8s.io/${KUBE_LATEST}/bin/linux/amd64/kube-proxy \
    https://dl.k8s.io/${KUBE_LATEST}/bin/linux/amd64/kubelet \
    https://dl.k8s.io/release/${KUBE_LATEST}/bin/linux/amd64/kubectl \
    https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.31.1/crictl-v1.31.1-linux-amd64.tar.gz \
    https://github.com/opencontainers/runc/releases/download/v1.1.14/runc.amd64 \
    https://github.com/containernetworking/plugins/releases/download/v1.5.1/cni-plugins-linux-amd64-v1.5.1.tgz \
    https://github.com/containerd/containerd/releases/download/v1.7.21/containerd-1.7.21-linux-amd64.tar.gz 

sudo mkdir -p \
    containerd \
    /etc/cni/net.d \
    /opt/cni/bin \
    /var/lib/kubelet \
    /var/lib/kube-proxy \
    /var/lib/kubernetes \
    /var/run/kubernetes



tar -xvf crictl-v1.31.1-linux-amd64.tar.gz
sudo tar -xvf containerd-1.7.21-linux-amd64.tar.gz -C containerd
sudo tar -xvf cni-plugins-linux-amd64-v1.5.1.tgz  -C /opt/cni/bin/
mv runc.amd64 runc
sudo chmod +x crictl kubectl kube-proxy kubelet runc 
sudo mv crictl kubectl kube-proxy kubelet runc /usr/local/bin/
sudo mv containerd/bin/* /bin/
