# VPC
resource "aws_vpc" "ticketing" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ticketing-vpc-dev"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "ticketing" {
  vpc_id = aws_vpc.ticketing.id

  tags = {
    Name = "ticketing-igw-dev"
  }
}

# Public Subnet 1
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.ticketing.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "ticketing-public-1"
  }
}

# Public Subnet 2
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.ticketing.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "ticketing-public-2"
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.ticketing.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.ticketing.id
  }

  tags = {
    Name = "ticketing-rt-public"
  }
}

# Route Table Association
resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "ticketing" {
  name        = "ticketing-sg-dev"
  description = "Ticketing App Security Group"
  vpc_id      = aws_vpc.ticketing.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
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
    Name = "ticketing-sg-dev"
  }
}

# Outputs
output "vpc_id" {
  value       = aws_vpc.ticketing.id
  description = "VPC ID"
}

output "public_subnet_1_id" {
  value       = aws_subnet.public_1.id
  description = "Public Subnet 1 ID"
}

output "public_subnet_2_id" {
  value       = aws_subnet.public_2.id
  description = "Public Subnet 2 ID"
}

output "security_group_id" {
  value       = aws_security_group.ticketing.id
  description = "Security Group ID"
}
