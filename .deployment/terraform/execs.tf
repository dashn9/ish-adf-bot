resource "null_resource" "generate_k8s_ca" {
    provisioner "local-exec" {
        command = "../scripts/k8s/generate-k8s-ca.sh"
    }

    # This will ensure the CA is regenerated only if there are changes
    triggers = {
        always_run = "${timestamp()}"
    }
}