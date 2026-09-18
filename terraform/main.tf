terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "ticketing-dev"
  
  default_tags {
    tags = {
      Project     = "ticketing"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}

output "aws_region" {
  value = "us-east-1"
}

output "environment" {
  value = "dev"
}
