resource "aws_eip" "ish_bot_kube_master_eip" {
    instance = aws_instance.ish_bot_kube_master
}

resource "aws_instance" "ish_bot_kube_master" {
    count = var.master_node_count
    instance_type = var.master_node_type
    ami = var.master_node_image
    key_name = aws_key_pair.tf_master_node_ssh_keys[count.index].key_name
    subnet_id = aws_subnet.k8s_subnets[count.index].id
    security_groups = [ aws_security_group.k8s_sg ]
    tags = {
        Name = "${var.master_node_name}-${count.index}"
    }

    # Upload Kubernetes API Server key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver.key"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    } 

    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver.crt"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    # Upload Kubernetes API Server ETCD client key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver-etcd-client.key"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver-etcd-client.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver-etcd-client.crt"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver-etcd-client.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    # Upload Kubernetes API Server Kubelet client key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver-kubelet-client.key"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver-kubelet-client.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver-kubelet-client.crt"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver-kubelet-client.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    # Upload Kubernetes Controller Manager key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/kube-controller-manager.key"
        destination = "/home/${var.master_node_user}/kube-controller-manager.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kube-controller-manager.crt"
        destination = "/home/${var.master_node_user}/kube-controller-manager.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    # Upload Kubernetes Scheduler key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/kube-scheduler.key"
        destination = "/home/${var.master_node_user}/kube-scheduler.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kube-scheduler.crt"
        destination = "/home/${var.master_node_user}/kube-scheduler.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    # Upload Admin key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/admin.key"
        destination = "/home/${var.master_node_user}/admin.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/admin.crt"
        destination = "/home/${var.master_node_user}/admin.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    # Upload ETCD server key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/etcd-server.key"
        destination = "/home/${var.master_node_user}/etcd-server.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/etcd-server.crt"
        destination = "/home/${var.master_node_user}/etcd-server.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    # Upload ETCD client key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/etcd-client.key"
        destination = "/home/${var.master_node_user}/etcd-client.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/etcd-client.crt"
        destination = "/home/${var.master_node_user}/etcd-client.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}_key.pem")
            host        = self.public_ip
        }
    }


    root_block_device {
        volume_size = var.master_node_root_storage_size
        volume_type = var.master_node_root_storage_type
    }

}

resource "local_file" "master_node_ssh_keys" {
    count    = var.master_node_count
    content  = tls_private_key.master_node_ssh_keys[count.index].private_key_pem
    filename = "${var.master_node_name}-${count.index}_key.pem"
}

resource "aws_instance" "ish_bot_kube_worker" {
    count = var.worker_node_count
    instance_type = var.worker_node_type
    ami = var.worker_node_image
    key_name = aws_key_pair.tf_worker_node_ssh_keys[count.index].key_name
    subnet_id = aws_subnet.k8s_subnets[count.index].id
    security_groups = [ aws_security_group.k8s_sg ]

    provisioner "file" {
        source      = "${var.scripts_path}/generate_certificate.sh"
        destination = "/home/${var.master_node_user}/generate_certificate.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/generate_cluster_worker_certificates.sh"
        destination = "/home/${var.master_node_user}/generate_cluster_worker_certificates.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    tags = {
        Name = "${var.worker_node_name}-${count.index}"
    }
    root_block_device {
        volume_size = var.worker_node_root_storage_size
        volume_type = var.worker_node_root_storage_type
    }

    ebs_block_device {
        device_name = "/chrome_profiles_store"
        volume_id   = aws_ebs_volume.chrome_profiles_store.id
    }
}

resource "local_file" "master_node_ssh_keys" {
    count    = var.master_node_count
    content  = tls_private_key.master_node_ssh_keys[count.index].private_key_pem
    filename = "${var.master_node_name}-${count.index}.key"
}

resource "local_file" "worker_node_ssh_keys" {
    count    = var.worker_node_count
    content  = tls_private_key.worker_node_ssh_keys[count.index].private_key_pem
    filename = "${var.worker_node_name}-${count.index}.key"
}