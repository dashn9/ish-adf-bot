#!/bin/bash

{
echo && echo "$0: " && echo

meta() { curl -s "http://169.254.169.254/latest/meta-data/$1"; }

HOSTNAME=${1:-$(meta hostname)}
INTERNAL_IP=${2:-$(meta local-ipv4)}
CONTROLLER_IP=$(dig +short HOST_NAME)

# Configure API Server
sudo mkdir -p /var/lib/kubernetes/

sudo mv ca.crt ca-key.crt kubernetes.key kubernetes.crt \
    /var/lib/kubernetes/

cat <<EOF | sudo tee /etc/systemd/system/kube-apiserver.service
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-apiserver \\
    --advertise-address=${INTERNAL_IP} \\
    --allow-privileged=true \\
    --apiserver-count=1 \\
    --audit-log-maxage=30 \\
    --audit-log-maxbackup=3 \\
    --audit-log-maxsize=100 \\
    --audit-log-path=/var/log/audit.log \\
    --authorization-mode=Node,RBAC \\
    --bind-address=0.0.0.0 \\
    --client-ca-file=/var/lib/kubernetes/k8s-ca.crt \\
    --enable-admission-plugins=Initializers,NamespaceLifecycle,NodeRestriction,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota \\
    --enable-swagger-ui=true \\
    --etcd-cafile=/var/lib/kubernetes/k8a-ca.crt \\
    --etcd-certfile=/var/lib/kubernetes/kubernetes-apiserver-etcd-client.crt \\
    --etcd-keyfile=/var/lib/kubernetes/kubernetes-apiserver-etcd-client.key \\
    --etcd-servers=https://${CONTROLLER_IP}:2379 \\
    --event-ttl=1h \\
    --kubelet-certificate-authority=/var/lib/kubernetes/k8s-ca.crt \\
    --kubelet-client-certificate=/var/lib/kubernetes/kubernetes-apiserver-kubelet-client.crt \\
    --kubelet-client-key=/var/lib/kubernetes/kubernetes-apiserver-kubelet-client.key \\
    --kubelet-https=true \\
    --runtime-config=api/all \\
    --service-cluster-ip-range=10.32.0.0/24 \\
    --service-node-port-range=30000-32767 \\
    --tls-cert-file=/var/lib/kubernetes/kubernetes-apiserver.crt \\
    --tls-private-key-file=/var/lib/kubernetes/kubernetes-apiserver.key \\
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
    --cluster-signing-key-file=/var/lib/kubernetes/k8s-ca.key \\
    --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig \\
    --leader-elect=true \\
    --root-ca-file=/var/lib/kubernetes/ca.crt \\
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

} >> cloudinit.log