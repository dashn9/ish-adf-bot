output "ish_bot_kube_master_eip" {
    value = aws_eip.ish_bot_kube_master_eip[*].public_ip
}

output "ish_bot_kube_master_public_ips" {
    value = aws_instance.ish_bot_kube_master[*].public_ip
}

output "ish_bot_kube_worker_public_ips" {
    value = aws_instance.ish_bot_kube_worker[*].public_ip
}