resource "null_resource" "generate_k8s_ca" {
    provisioner "local-exec" {
        command = "chmod +x ../scripts/k8s/generate_certificate_authority.sh; ../scripts/k8s/generate_certificate_authority.sh"
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