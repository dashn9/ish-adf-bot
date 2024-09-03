#!/bin/bash

echo && echo "$0: " && echo

meta() { curl -s "http://169.254.169.254/latest/meta-data/$1"; }

HOSTNAME=$(hostname -s)
INTERNAL_IP=${1:-$(meta local-ipv4)}
CONTROLLER_IP=$(meta public-ipv4)

# Configure API Server
sudo mkdir -p /var/lib/kubernetes/pki
sudo chown root:root /var/lib/kubernetes/pki/*
sudo chmod 600 /var/lib/kubernetes/pki/*

POD_CIDR=10.244.0.0/16
SERVICE_CIDR=10.96.0.0/16

sudo mv k8s-ca.crt k8s-sa-ca.crt \
    k8s-sa-ca.key \
    etcd.key etcd.crt \
    kubernetes-apiserver-kubelet-client.crt kubernetes-apiserver-kubelet-client.key \
    kube-controller-manager.crt kube-controller-manager.key \
    kube-scheduler.crt kube-scheduler.key \
    kubernetes-apiserver.key kubernetes-apiserver.crt \
    service-account.crt service-account.key \
    /var/lib/kubernetes/pki

# Take a look at the --service-account-signing-key-file
cat <<EOF | sudo tee /etc/systemd/system/kube-apiserver.service
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-apiserver \\
    --advertise-address=${INTERNAL_IP} \\
    --allow-privileged=true \\
    --audit-log-maxage=30 \\
    --audit-log-maxbackup=3 \\
    --audit-log-maxsize=100 \\
    --audit-log-path=/var/log/audit.log \\
    --authorization-mode=Node,RBAC \\
    --bind-address=0.0.0.0 \\
    --client-ca-file=/var/lib/kubernetes/pki/k8s-ca.crt \\
    --enable-admission-plugins=NodeRestriction,ServiceAccount \\
    --etcd-cafile=/var/lib/kubernetes/pki/k8s-ca.crt \\
    --etcd-certfile=/var/lib/kubernetes/pki/etcd.crt \\
    --etcd-keyfile=/var/lib/kubernetes/pki/etcd.key \\
    --etcd-servers=https://${INTERNAL_IP}:2379 \\
    --event-ttl=1h \\
    --kubelet-certificate-authority=/var/lib/kubernetes/pki/k8s-ca.crt \\
    --kubelet-client-certificate=/var/lib/kubernetes/pki/kubernetes-apiserver-kubelet-client.crt \\
    --kubelet-client-key=/var/lib/kubernetes/pki/kubernetes-apiserver-kubelet-client.key \\
    --runtime-config="v1=true" \\
    --service-account-key-file=/var/lib/kubernetes/pki/service-account.crt \\
    --service-account-signing-key-file=/var/lib/kubernetes/pki/k8s-sa-ca.key \\
    --service-account-issuer="kubernetes-sa-ca" \\
    --service-cluster-ip-range=${SERVICE_CIDR} \\
    --service-node-port-range=30000-32767 \\
    --tls-cert-file=/var/lib/kubernetes/pki/kubernetes-apiserver.crt \\
    --tls-private-key-file=/var/lib/kubernetes/pki/kubernetes-apiserver.key \\
    --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configure Controller Manager
sudo mv kube-controller-manager.kubeconfig /var/lib/kubernetes/

cat <<EOF | sudo tee /etc/systemd/system/kube-controller-manager.service
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-controller-manager \\
    --allocate-node-cidrs=true \\
    --authentication-kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig \\
    --authorization-kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig \\
    --bind-address=127.0.0.1 \\
    --client-ca-file=/var/lib/kubernetes/pki/k8s-ca.crt \\
    --cluster-cidr=${POD_CIDR} \\
    --cluster-name=kubernetes \\
    --cluster-signing-cert-file=/var/lib/kubernetes/pki/k8s-ca.crt \\
    --cluster-signing-key-file=/var/lib/kubernetes/pki/k8s-ca.key \\
    --controllers=*,bootstrapsigner,tokencleaner \\
    --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig \\
    --leader-elect=true \\
    --node-cidr-mask-size=24 \\
    --requestheader-client-ca-file=/var/lib/kubernetes/pki/k8s-ca.crt \\
    --root-ca-file=/var/lib/kubernetes/pki/k8s-ca.crt \\
    --service-account-private-key-file=/var/lib/kubernetes/pki/service-account.key \\
    --service-cluster-ip-range=${SERVICE_CIDR} \\
    --use-service-account-credentials=true \\
    --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configure Scheduler
sudo mv kube-scheduler.kubeconfig /var/lib/kubernetes/

cat <<EOF | sudo tee /etc/systemd/system/kube-scheduler.service
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-scheduler \\
    --kubeconfig=/var/lib/kubernetes/kube-scheduler.kubeconfig \\
    --leader-elect=true \\
    --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Start Controller Services
sudo systemctl daemon-reload
sudo systemctl enable kube-apiserver kube-controller-manager kube-scheduler
sudo systemctl start kube-apiserver kube-controller-manager kube-scheduler
