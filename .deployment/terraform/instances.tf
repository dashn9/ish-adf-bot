resource "aws_instance" "ish_bot_kube_master" {
    instance_type = "${var.master_node_type}"
    tags = {
        name = "ish_bot_kube_master-${count.index}"
    }

    root_block_device {
        volume_size = 30
        volume_type = "gp3"
    }

    ebs_block_device {
        device_name = "/chrome_profiles_store"
        volume_id   = aws_ebs_volume.chrome_profiles_store.id
    }
}

resource "aws_instance" "ish_bot_kube_worker" {
    instance_type = "${var.worker_node_type}"
    
}