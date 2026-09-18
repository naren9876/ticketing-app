#!/bin/bash
export AWS_ACCOUNT="840080485121"
export AWS_REGION="us-east-1"
export ECR_REGISTRY="$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com"

services=("api-gateway" "user-service" "movie-service" "booking-service" "payment-service" "notification-service")

for service in "${services[@]}"; do
  echo "Building $service..."
  docker build -t ticketing-$service:latest \
    --build-arg SERVICE_NAME=$service \
    -f Dockerfile .
  
  echo "Tagging $service..."
  docker tag ticketing-$service:latest $ECR_REGISTRY/ticketing-$service:latest
  
  echo "Pushing $service to ECR..."
  docker push $ECR_REGISTRY/ticketing-$service:latest
  
  echo "✅ $service deployed!"
done

echo "🎉 All 6 services built and pushed!"
