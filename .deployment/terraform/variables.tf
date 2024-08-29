variable "name_prefix" {
    default = "ish-bot"
}

variable "vpc_cidr" {
    default = "10.0.0.0/16"
}

variable "availability_zone" {
    default = "us-east-1"
}
variable "master_node_type" {
    default = "t3a.xlarge"
}

variable "master_node_image" {
    default = "ami-064519b8c76274859" # Debian
}

variable "master_node_name" {
    default = "ish_bot_kube_master"
}

variable "master_node_root_storage_size" {
    default = 30
}

variable "master_node_root_storage_type" {
    default = "gp3"
}

variable "master_node_count" {
    default = 1
}

variable "worker_node_count" {
    default = 1
}