variable "name_prefix" {
    default = "ish-bot"
}

variable "vpc_cidr" {
    default = "10.0.0.0/16"
}

variable "availability_zone" {
    default = "us-east-1"
}

variable "ssh_path" {
    default = "./nodes_ssh_keys"
}

variable "certificates_path" {
    default = "~/ish_bot_kube_cluster_certificates/certs"
}

variable "scripts_path" {
    default = "../scripts/k8s"
}

variable "master_node_type" {
    default = "t3a.medium"
}

variable "master_node_image" {
    default = "ami-064519b8c76274859" # Debian
}

variable "master_node_name" {
    default = "ish_bot_kube_master"
}

variable "master_node_user" {
    default =  "admin"
}

variable "master_node_root_storage_size" {
    default = 10
}

variable "master_node_root_storage_type" {
    default = "gp3"
}

variable "master_node_count" {
    default = 1
}


variable "worker_node_type" {
    default = "t3a.xlarge"
}

variable "worker_node_image" {
    default = "ami-064519b8c76274859" # Debian
}

variable "worker_node_name" {
    default = "ish_bot_kube_worker"
}

variable "worker_node_user" {
    default =  "admin"
}

variable "worker_node_root_storage_size" {
    default = 30
}

variable "worker_node_root_storage_type" {
    default = "gp3"
}

variable "worker_node_count" {
    default = 2
}
