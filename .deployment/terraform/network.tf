# Variables
# There might be a potential issue in this cluster where pods on different nodes might not be able to communicate with each
resource "aws_vpc" "k8s_vpc" {
    cidr_block           = var.vpc_cidr
    enable_dns_hostnames = true
    enable_dns_support   = true

    tags = {
        Name = "${var.name_prefix}-kube-vpc"
    }
}

# Subnets
resource "aws_subnet" "k8s_subnets" {
    count                   = sum([var.master_node_count, var.worker_node_count])
    vpc_id                  = aws_vpc.k8s_vpc.id
    cidr_block              = "10.0.${count.index+1}.0/24"
    # Please endeavour to switch  this to use multiple availability zones
    availability_zone       = "${var.availability_zone}a"
    map_public_ip_on_launch = true

    tags = {
        Name = "${var.name_prefix}-kubernetes-subnet-${count.index}"
    }
}

# Internet Gateway
resource "aws_internet_gateway" "k8s_igw" {
    vpc_id = aws_vpc.k8s_vpc.id

    tags = {
        Name = "${var.name_prefix}-kubernetes-igw"
    }
}

# Route Table
resource "aws_route_table" "k8s_rt" {
    vpc_id = aws_vpc.k8s_vpc.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.k8s_igw.id
    }

    tags = {
        Name = "${var.name_prefix}-kubernetes-rt"
    }
}

# Route Table Association
resource "aws_route_table_association" "k8s_rta" {
    count          = length(aws_subnet.k8s_subnets)
    subnet_id      = aws_subnet.k8s_subnets[count.index].id
    route_table_id = aws_route_table.k8s_rt.id
}

# Security Group
resource "aws_security_group" "k8s_sg" {
    name        = "${var.name_prefix}-kubernetes-sg"
    description = "Allow inbound traffic for Kubernetes"
    vpc_id      = aws_vpc.k8s_vpc.id

    ingress {
        description = "Allow all internal traffic"
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = [var.vpc_cidr]
    }

    ingress {
        description = "Allow SSH from anywhere"
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        description = "Allow API server"
        from_port   = 6443
        to_port     = 6443
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "${var.name_prefix}-kubernetes-sg"
    }
}
