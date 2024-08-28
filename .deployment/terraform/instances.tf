resource "aws_instance" "ish_bot_kube_master" {
    count = var.master_node_count
    instance_type = var.master_node_type
    ami = var.master_node_image
    key_name = aws_key_pair.tf_master_node_ssh_keys[count.index].key_name
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