aws_region            = "us-east-1"
environment           = "dev"
project_name          = "ticketing"
cluster_name          = "ticketing-dev"
eks_version           = "1.36"
desired_capacity      = 2
min_capacity          = 2
max_capacity          = 3
instance_type         = "t3.medium"
db_allocated_storage  = 20
db_engine_version     = "14.7"
db_instance_class     = "db.t3.micro"
db_name               = "ticketing_db"
enable_nat_gateway    = true
single_nat_gateway    = true

tags = {
  Environment = "dev"
  ManagedBy   = "Terraform"
  Project     = "TicketingApp"
  CreatedAt   = "2026-09-17"
}
