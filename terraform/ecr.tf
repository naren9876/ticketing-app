resource "aws_ecr_repository" "api_gateway" {
  name                 = "ticketing-api-gateway"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "user_service" {
  name                 = "ticketing-user-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "movie_service" {
  name                 = "ticketing-movie-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "booking_service" {
  name                 = "ticketing-booking-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "payment_service" {
  name                 = "ticketing-payment-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "notification_service" {
  name                 = "ticketing-notification-service"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
}

output "ecr_repositories" {
  value = {
    api_gateway          = aws_ecr_repository.api_gateway.repository_url
    user_service         = aws_ecr_repository.user_service.repository_url
    movie_service        = aws_ecr_repository.movie_service.repository_url
    booking_service      = aws_ecr_repository.booking_service.repository_url
    payment_service      = aws_ecr_repository.payment_service.repository_url
    notification_service = aws_ecr_repository.notification_service.repository_url
  }
}
