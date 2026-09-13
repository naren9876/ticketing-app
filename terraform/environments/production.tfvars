# Production Environment Configuration

environment             = "production"
aws_region              = "us-east-1"
cluster_name            = "ticketing-prod"
project_name            = "ticketing-app"

# Compute (Production grade)
node_groups = {
  compute = {
    name           = "compute"
    instance_types = ["m5.large"]
    desired_size   = 3
    min_size       = 3
    max_size       = 10
  }
  
  gpu = {
    name           = "gpu"
    instance_types = ["g4dn.xlarge"]
    desired_size   = 1
    min_size       = 1
    max_size       = 5
  }
}

# Database (Production HA setup)
rds_config = {
  engine_version        = "14.7"
  instance_class        = "db.r5.xlarge"
  allocated_storage     = 500
  backup_retention_days = 90
  multi_az              = true
  enabled_cloudwatch_logs_exports = ["postgresql"]
  deletion_protection   = true
}

# Storage
s3_buckets = {
  artifacts = "ticketing-prod-artifacts"
  logs      = "ticketing-prod-logs"
}

# Tags
tags = {
  Environment = "production"
  Project     = "ticketing"
  ManagedBy   = "terraform"
  Owner       = "platform-team"
  CostCenter  = "engineering"
}
