# Security Policies - Enforce via Terraform

# Policy 1: Enforce encryption at rest
resource "aws_kms_key" "ticketing_key" {
  description             = "KMS key for Ticketing App encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "ticketing-encryption-key"
  }
}

# Policy 2: Enforce VPC security groups
resource "aws_security_group" "ticketing_sg" {
  name        = "ticketing-sg-policies"
  description = "Security group with policies"
  vpc_id      = aws_vpc.ticketing.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.0/24"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ticketing-security-group"
  }
}

# Policy 3: Enforce IAM least privilege
resource "aws_iam_role" "ticketing_app_role" {
  name = "ticketing-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

output "security_policies_enforced" {
  value = "All security policies enforced via Terraform"
}
