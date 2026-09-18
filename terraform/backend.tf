terraform {
  backend "s3" {
    bucket         = "ticketing-terraform-state-840080485121"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}
