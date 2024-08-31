resource "aws_eip" "ish_bot_kube_master_eip" {
    count = var.master_node_count
    instance = aws_instance.ish_bot_kube_master[count.index].id
}

resource "aws_instance" "ish_bot_kube_master" {
    count = var.master_node_count
    instance_type = var.master_node_type
    ami = var.master_node_image
    key_name = aws_key_pair.tf_master_node_ssh_keys[count.index].key_name
    subnet_id = aws_subnet.k8s_subnets[count.index].id
    security_groups = [ aws_security_group.k8s_sg.name ]
    tags = {
        Name = "${var.master_node_name}-${count.index}"
    }

    provisioner "file" {
        source      = "${var.certificates_path}/k8s-ca.crt"
        destination = "/home/${var.master_node_user}/k8s-ca.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    } 

    # Upload Kubernetes API Server key and certificate
    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver.key"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    } 

    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver.crt"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
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
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver-etcd-client.crt"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver-etcd-client.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
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
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kubernetes-apiserver-kubelet-client.crt"
        destination = "/home/${var.master_node_user}/kubernetes-apiserver-kubelet-client.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
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
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kube-controller-manager.crt"
        destination = "/home/${var.master_node_user}/kube-controller-manager.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
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
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kube-scheduler.crt"
        destination = "/home/${var.master_node_user}/kube-scheduler.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
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
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/admin.crt"
        destination = "/home/${var.master_node_user}/admin.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
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
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/etcd-server.crt"
        destination = "/home/${var.master_node_user}/etcd-server.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
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
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/etcd-client.crt"
        destination = "/home/${var.master_node_user}/etcd-client.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/generate_admin_config.sh"
        destination = "/home/${var.master_node_user}/generate_admin_config.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/generate_controller_manager_config.sh"
        destination = "/home/${var.master_node_user}/generate_controller_manager_config.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/generate_scheduler_config.sh"
        destination = "/home/${var.master_node_user}/generate_scheduler_config.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/install_control_plane.sh"
        destination = "/home/${var.master_node_user}/install_control_plane.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/start_control_plane.sh"
        destination = "/home/${var.master_node_user}/start_control_plane.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/start_etcd.sh"
        destination = "/home/${var.master_node_user}/start_etcd.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }


    provisioner "remote-exec" {

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }

        inline = [
            "sleep 30",
            "sudo chmod +x generate_admin_config.sh generate_controller_manager_config.sh generate_scheduler_config.sh install_control_plane.sh start_control_plane.sh start_etcd.sh",
            "./install_control_plane.sh",
            "./gen_controller_manager_config.sh",
            "./gen_scheduler_config.sh",
            "./gen_admin_config.sh",
            "./start_etcd.sh",
            "./start_control_plane.sh",
        ]
    }

    root_block_device {
        volume_size = var.master_node_root_storage_size
        volume_type = var.master_node_root_storage_type
    }

}






resource "aws_instance" "ish_bot_kube_worker" {
    count = var.worker_node_count
    instance_type = var.worker_node_type
    ami = var.worker_node_image
    key_name = aws_key_pair.tf_worker_node_ssh_keys[count.index].key_name
    subnet_id = aws_subnet.k8s_subnets[count.index].id
    security_groups = [ aws_security_group.k8s_sg.name ]

    provisioner "file" {
        source      = "${var.certificates_path}/kube-proxy.key"
        destination = "/home/${var.master_node_user}/kube-proxy.key"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.certificates_path}/kube-proxy.crt"
        destination = "/home/${var.master_node_user}/kube-proxy.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }
    provisioner "file" {
        source      = "${var.certificates_path}/k8s-ca.crt"
        destination = "/home/${var.master_node_user}/k8s-ca.crt"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    } 

    provisioner "file" {
        source      = "${var.scripts_path}/generate_proxy_config.sh"
        destination = "/home/${var.master_node_user}/generate_proxy_config.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

    provisioner "file" {
        source      = "${var.scripts_path}/generate_kubelet_config.sh"
        destination = "/home/${var.master_node_user}/generate_kubelet_config.sh"

        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }
    }

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

    provisioner "remote-exec" {
        connection {
            type        = "ssh"
            user        = var.master_node_user
            private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
            host        = self.public_ip
        }

        inline = [
            "sleep 30",
            "sudo chmod +x generate_cluster_worker_certificates.sh generate_kubelet_config.sh generarte_proxy_config.sh install_worker.sh start_worker.sh",
            "./install_worker.sh",
            "./generate_cluster_worker_certificates.sh",
            # This below would be an issue if I build this cluster to have multiple master nodes
            "./generate_kubelet_config.sh ${join(" ", toset(aws_eip.ish_bot_kube_master_eip.*.public_ip))}",
            "./generate_proxy_config.sh ${join(" ", toset(aws_eip.ish_bot_kube_master_eip.*.public_ip))}",
            "./start_worker.sh",
        ]
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