#!/bin/bash

{
echo && echo "$0: " && echo

# Install OS Dependencies
sudo apt-get update
sudo apt-get -y install socat conntrack ipset


# Install/Configure Worker Dependencies
wget -q --show-progress --https-only --timestamping \
    https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.31.1/crictl-v1.31.1-darwin-amd64.tar.gz \
    https://storage.googleapis.com/kubernetes-the-hard-way/runsc \
    https://github.com/opencontainers/runc/releases/download/v1.1.13/runc.amd64 \
    https://github.com/containernetworking/plugins/releases/download/v1.5.1/cni-plugins-linux-amd64-v1.5.1.tgz \
    https://github.com/containerd/containerd/releases/download/v1.7.21/containerd-1.7.21-linux-amd64.tar.gz \
    https://dl.k8s.io/v1.31.0/bin/darwin/amd64/kubectl \
    https://dl.k8s.io/v1.31.0/bin/linux/amd64/kube-proxy \
    https://dl.k8s.io/v1.31.0/bin/linux/arm64/kubelet

sudo mkdir -p \
    /etc/cni/net.d \
    /opt/cni/bin \
    /var/lib/kubelet \
    /var/lib/kube-proxy \
    /var/lib/kubernetes \
    /var/run/kubernetes

chmod +x kubectl kube-proxy kubelet runc.amd64 runsc
    sudo mv runc.amd64 runc
    sudo mv kubectl kube-proxy kubelet runc runsc /usr/local/bin/
    sudo tar -xvf crictl-v1.31.1-darwin-amd64.tar.gz -C /usr/local/bin/
    sudo tar -xvf cni-plugins-linux-amd64-v1.5.1.tgz -C /opt/cni/bin/
    sudo tar -xvf containerd-1.7.21-linux-amd64.tar.gz -C /
} >> install_worker.log