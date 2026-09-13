# Development Environment Configuration

environment             = "dev"
aws_region              = "us-east-1"
cluster_name            = "ticketing-dev"
project_name            = "ticketing-app"

# Compute (Minimal for dev)
node_groups = {
  compute = {
    name           = "compute"
    instance_types = ["t3.micro"]
    desired_size   = 1
    min_size       = 1
    max_size       = 1
  }
}

# Database (Minimal for dev)
rds_config = {
  engine_version        = "14.7"
  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  backup_retention_days = 7
  multi_az              = false
  enabled_cloudwatch_logs_exports = ["postgresql"]
}

# Storage
s3_buckets = {
  artifacts = "ticketing-dev-artifacts"
  logs      = "ticketing-dev-logs"
}

# Tags
tags = {
  Environment = "dev"
  Project     = "ticketing"
  ManagedBy   = "terraform"
  Owner       = "platform-team"
}
