resource "null_resource" "generate_k8s_ca" {
    provisioner "local-exec" {
        command = "../scripts/k8s/generate-k8s-ca.sh ${aws_eip.ish_bot_kube_master_eip.public_ip}"
    }

    # This will ensure the CA is regenerated only if there are changes
    triggers = {
        always_run = "${timestamp()}"
    }
}

resource "null_resource" "generate_k8s_ca" {
    provisioner "local-exec" {
        command = "../scripts/k8s/generate_cluster_control_plane_certificates.sh ./certificates ${aws_eip.ish_bot_kube_master_eip.public_ip}"
    }

    # This will ensure the CA is regenerated only if there are changes
    triggers = {
        always_run = "${timestamp()}"
    }
}