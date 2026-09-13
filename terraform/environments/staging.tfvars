# Staging Environment Configuration (Prod-like)

environment             = "staging"
aws_region              = "us-east-1"
cluster_name            = "ticketing-staging"
project_name            = "ticketing-app"

# Compute (Staging-like, but smaller)
node_groups = {
  compute = {
    name           = "compute"
    instance_types = ["t3.small"]
    desired_size   = 2
    min_size       = 2
    max_size       = 3
  }
}

# Database (Staging setup)
rds_config = {
  engine_version        = "14.7"
  instance_class        = "db.t3.small"
  allocated_storage     = 50
  backup_retention_days = 30
  multi_az              = true
  enabled_cloudwatch_logs_exports = ["postgresql"]
}

# Storage
s3_buckets = {
  artifacts = "ticketing-staging-artifacts"
  logs      = "ticketing-staging-logs"
}

# Tags
tags = {
  Environment = "staging"
  Project     = "ticketing"
  ManagedBy   = "terraform"
  Owner       = "platform-team"
}
