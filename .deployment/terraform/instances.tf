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

    root_block_device {
        volume_size = var.master_node_root_storage_size
        volume_type = var.master_node_root_storage_type
    }

    ebs_block_device {
        device_name = "/chrome_profiles_store"
        volume_id   = aws_ebs_volume.chrome_profiles_store.id
    }
}

resource "local_file" "master_node_ssh_keys" {
    count    = var.master_node_count
    content  = tls_private_key.master_node_ssh_keys[count.index].private_key_pem
    filename = "${var.master_node_name}-${count.index}_key.pem"
}