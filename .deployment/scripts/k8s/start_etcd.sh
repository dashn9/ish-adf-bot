#!/bin/bash

{
echo && echo "$0: " && echo

# Set the project name from the first argument
PROJ_NAME=$1
ETCD_NAME=$(hostname -s)
# Fetch the internal IP address using the AWS EC2 metadata service
INTERNAL_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)

# Create necessary directories and copy certificates
sudo mkdir -p /etc/etcd /var/lib/etcd
sudo cp ca.crt kubernetes-key.crt kubernetes.crt /etc/etcd/

# Create the systemd service file for etcd
cat <<EOF | sudo tee /etc/systemd/system/etcd.service
[Unit]
Description=etcd
Documentation=https://github.com/coreos

[Service]
ExecStart=/usr/local/bin/etcd \\
  --name ${ETCD_NAME} \\
  --cert-file=/etc/etcd/kubernetes.crt \\
  --key-file=/etc/etcd/kubernetes-key.crt \\
  --peer-cert-file=/etc/etcd/kubernetes.crt \\
  --peer-key-file=/etc/etcd/kubernetes-key.crt \\
  --trusted-ca-file=/etc/etcd/ca.crt \\
  --peer-trusted-ca-file=/etc/etcd/ca.crt \\
  --peer-client-cert-auth \\
  --client-cert-auth \\
  --initial-advertise-peer-urls https://${INTERNAL_IP}:2380 \\
  --listen-peer-urls https://${INTERNAL_IP}:2380 \\
  --listen-client-urls https://${INTERNAL_IP}:2379,https://127.0.0.1:2379 \\
  --advertise-client-urls https://${INTERNAL_IP}:2379 \\
  --initial-cluster-token etcd-cluster-0 \\
  --initial-cluster ${ETCD_NAME}=https://${INTERNAL_IP}:2380 \\
  --initial-cluster-state new \\
  --data-dir=/var/lib/etcd
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable, and start etcd
sudo systemctl daemon-reload
sudo systemctl enable etcd
sudo systemctl start etcd

# Verify that everything is working
sudo ETCDCTL_API=3 etcdctl member list \
    --endpoints=https://127.0.0.1:2379 \
    --cacert=/etc/etcd/ca.crt \
    --cert=/etc/etcd/kubernetes.crt \
    --key=/etc/etcd/kubernetes-key.crt

} >> cloudinit.log 2>&1
