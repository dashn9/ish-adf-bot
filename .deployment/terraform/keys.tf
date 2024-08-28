resource "tls_private_key" "master_node_ssh_keys" {
    algorithm = "RSA"
    rsa_bits  = 4096
    count = var.master_node_count
}

resource "aws_key_pair" "tf_master_node_ssh_keys" {
    count = var.master_node_count
    key_name   = "${var.master_node_name}-${count.index}_key"
    public_key = tls_private_key.master_node_ssh_keys[count.index].public_key_openssh
}