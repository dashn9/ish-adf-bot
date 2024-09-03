#!/bin/bash

echo && echo "$0: " && echo

meta() { curl -s "http://169.254.169.254/latest/meta-data/$1"; }

HOSTNAME=$(hostname -s)
INTERNAL_IP=${1:-$(meta local-ipv4)}
CONTROLLER_IP=$(meta public-ipv4)

# Configure API Server
sudo mkdir -p /var/lib/kubernetes/pki

sudo mv k8s-ca.crt k8s-sa-ca.crt k8s-sa-ca.key \
    etcd.key etcd.crt /var/lib/kubernetes/pki \
    kubernetes-apiserver-kubelet-client.crt kubernetes-apiserver-kubelet-client.key \
    kubernetes-apiserver.key kubernetes-apiserver.crt service-account.crt \
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
    --service-cluster-ip-range=10.32.0.0/24 \\
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
    --address=0.0.0.0 \\
    --cluster-cidr=10.32.0.0/24 \\
    --cluster-name=ish-bot-kube \\
    --cluster-signing-cert-file=/var/lib/kubernetes/k8s-ca.crt \\
    --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig \\
    --leader-elect=true \\
    --root-ca-file=/var/lib/kubernetes/k8s-ca.crt \\
    --service-cluster-ip-range=10.32.0.0/24 \\
    --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configure Scheduler
sudo mv kube-scheduler.kubeconfig /var/lib/kubernetes/

cat <<EOF | sudo tee /etc/kubernetes/config/kube-scheduler.yaml
apiVersion: componentconfig/v1alpha1
kind: KubeSchedulerConfiguration
clientConnection:
    kubeconfig: "/var/lib/kubernetes/kube-scheduler.kubeconfig"
leaderElection:
    leaderElect: true
EOF

cat <<EOF | sudo tee /etc/systemd/system/kube-scheduler.service
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-scheduler \\
    --config=/etc/kubernetes/config/kube-scheduler.yaml \\
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
