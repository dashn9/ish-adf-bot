resource "null_resource" "generate_cluster_encryption_config_yaml" {

    depends_on = [ null_resource.generate_k8s_ca ]
    provisioner "local-exec" {
        command = "chmod +x ../scripts/k8s/generate_configs.sh; ../scripts/k8s/generate_configs.sh"
    }

    # This will ensure the CA is regenerated only if there are changes
    triggers = {
        always_run = "${timestamp()}"
    }
}
resource "null_resource" "generate_k8s_ca" {
    provisioner "local-exec" {
        command = "chmod +x ../scripts/k8s/generate_certificate_authority.sh; ../scripts/k8s/generate_certificate_authority.sh k8s-ca 'kubernetes-ca'"
    }

    # This will ensure the CA is regenerated only if there are changes
    triggers = {
        always_run = "${timestamp()}"
    }
}

resource "null_resource" "generate_cluster_control_plane_certificates" {

    depends_on = [ null_resource.generate_k8s_ca ]
    provisioner "local-exec" {
        command = "chmod +x ../scripts/k8s/generate_cluster_control_plane_certificates.sh; ../scripts/k8s/generate_cluster_control_plane_certificates.sh"
    }

    # This will ensure the CA is regenerated only if there are changes
    triggers = {
        always_run = "${timestamp()}"
    }
}

# Regenerate Control Plane certs again (This is because the kube-apiserver and etcd certs needs to have the IP altNames added)
resource "null_resource" "regenerate_cluster_control_plane_certificates" {
    provisioner "local-exec" {
        command = "../scripts/k8s/generate_cluster_control_plane_certificates.sh -ip 127.0.0.1,${join(",", aws_instance.ish_bot_kube_master.*.private_ip)} -p ${aws_eip.ish_bot_kube_master_eip[0].public_ip}"
    }

    depends_on = [ aws_instance.ish_bot_kube_master ]
}

resource "null_resource" "redistribute_regenerated_certs_on_master" {
    depends_on = [null_resource.regenerate_cluster_control_plane_certificates]
    count      = length(aws_instance.ish_bot_kube_master)

    connection {
        type        = "ssh"
        user        = var.master_node_user
        private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
        host        = aws_eip.ish_bot_kube_master_eip[count.index].public_ip
    }

    provisioner "file" {
        source      = var.certificates_path
        destination = "/tmp/certificates"
    }

    provisioner "remote-exec" {
        inline = [
            "sudo cp /tmp/certificates/etcd.crt /etc/etcd/etcd.crt",
            "sudo cp /tmp/certificates/etcd.key /etc/etcd/etcd.key",
            "sudo mv /tmp/certificates/etcd.crt /var/lib/kubernetes/pki/etcd.crt",
            "sudo mv /tmp/certificates/etcd.key /var/lib/kubernetes/pki/etcd.key",
            "sudo mv /tmp/certificates/kubernetes-apiserver.crt /var/lib/kubernetes/pki/kubernetes-apiserver.crt",
            "sudo mv /tmp/certificates/kubernetes-apiserver.key /var/lib/kubernetes/pki/kubernetes-apiserver.key",
        ]
    }
}

# Reason for this, is the worker nodes has to be provisioned before creating the rbac
resource "null_resource" "create_rbac_on_master_nodes" {
    depends_on = [aws_instance.ish_bot_kube_worker]
    count      = length(aws_instance.ish_bot_kube_master)

    connection {
        type        = "ssh"
        user        = var.master_node_user
        private_key = file("${var.ssh_path}/${var.master_node_name}-${count.index}.key")
        host        = aws_eip.ish_bot_kube_master_eip[count.index].public_ip
    }

    provisioner "remote-exec" {
        inline = [
            "sudo chmod +x create_rbac.sh",
            "./create_rbac.sh"
        ]
    }
}