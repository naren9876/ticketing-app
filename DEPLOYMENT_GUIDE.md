# Movie Ticketing Platform - Cloud Deployment Guide

Complete guide for deploying the microservices application to major cloud providers.

## Table of Contents
- [Local Development](#local-development)
- [AWS Deployment](#aws-deployment)
- [Azure Deployment](#azure-deployment)
- [GCP Deployment](#gcp-deployment)
- [Monitoring & Logging](#monitoring--logging)
- [CI/CD Pipeline](#cicd-pipeline)

## Local Development

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- PostgreSQL client
- Redis CLI

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd movie-ticketing-platform

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Initialize sample data
docker exec ticketing_postgres psql -U postgres -d ticketing_db -f init-data.sql

# Access services
# API Gateway: http://localhost:3000
# Frontend: http://localhost:3100
# RabbitMQ Management: http://localhost:15672
```

### Environment Variables

Create `.env` file:
```env
# Database
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ticketing_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your-secret-key

# Payment
STRIPE_SECRET_KEY=sk_test_xxx

# Service URLs
USER_SERVICE_URL=http://user-service:3001
MOVIE_SERVICE_URL=http://movie-service:3002
BOOKING_SERVICE_URL=http://booking-service:3003
PAYMENT_SERVICE_URL=http://payment-service:3004
NOTIFICATION_SERVICE_URL=http://notification-service:3005
```

## AWS Deployment

### Architecture
- **Compute**: ECS Fargate or EKS (Kubernetes)
- **Database**: Amazon RDS PostgreSQL
- **Cache**: Amazon ElastiCache Redis
- **Load Balancer**: Application Load Balancer (ALB)
- **Storage**: S3 for static assets
- **CDN**: CloudFront
- **Monitoring**: CloudWatch

### Steps

#### 1. Create RDS PostgreSQL Database

```bash
# Using AWS CLI
aws rds create-db-instance \
  --db-instance-identifier ticketing-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password <secure-password> \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx
```

#### 2. Create ElastiCache Redis Cluster

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id ticketing-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

#### 3. Deploy to EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name ticketing-cluster \
  --version 1.27 \
  --region us-east-1 \
  --nodegroup-name ticketing-nodes \
  --nodes 3 \
  --node-type t3.medium

# Configure kubectl
aws eks update-kubeconfig --name ticketing-cluster --region us-east-1

# Apply Kubernetes manifests
kubectl apply -f kubernetes-deployment.yaml

# Verify deployment
kubectl get pods -n ticketing
```

#### 4. Set up ALB Ingress Controller

```bash
# Install ALB controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system

# Create Ingress
kubectl apply -f aws-ingress.yaml
```

#### 5. Deploy Frontend to S3 + CloudFront

```bash
# Build React app
cd frontend
npm run build

# Upload to S3
aws s3 sync build/ s3://ticketing-frontend-bucket/

# Create CloudFront distribution (via AWS Console)
```

### AWS Infrastructure as Code (CloudFormation)

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Movie Ticketing Platform Infrastructure

Parameters:
  DBPassword:
    Type: String
    NoEcho: true

Resources:
  # RDS PostgreSQL
  TicketingDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: ticketing-db
      Engine: postgres
      DBInstanceClass: db.t3.micro
      MasterUsername: postgres
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      VPCSecurityGroups:
        - !Ref DBSecurityGroup

  # ElastiCache Redis
  TicketingCache:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheClusterIdentifier: ticketing-cache
      Engine: redis
      CacheNodeType: cache.t3.micro
      NumCacheNodes: 1

  # Security Groups
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: RDS Security Group
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          CidrIp: 0.0.0.0/0
```

## Azure Deployment

### Architecture
- **Compute**: Azure Container Instances or AKS
- **Database**: Azure Database for PostgreSQL
- **Cache**: Azure Cache for Redis
- **Load Balancer**: Azure Application Gateway
- **Storage**: Azure Blob Storage
- **CDN**: Azure Front Door
- **Monitoring**: Azure Monitor

### Steps

#### 1. Create Azure Kubernetes Service

```bash
# Create resource group
az group create --name ticketing-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group ticketing-rg \
  --name ticketing-aks \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard

# Get credentials
az aks get-credentials --resource-group ticketing-rg --name ticketing-aks
```

#### 2. Create Azure Database for PostgreSQL

```bash
az postgres server create \
  --resource-group ticketing-rg \
  --name ticketing-db \
  --location eastus \
  --admin-user postgres \
  --admin-password <secure-password> \
  --sku-name B_Gen5_1 \
  --storage-size 51200
```

#### 3. Create Azure Cache for Redis

```bash
az redis create \
  --resource-group ticketing-rg \
  --name ticketing-cache \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

#### 4. Deploy to AKS

```bash
# Update kubernetes manifests with Azure resources
kubectl apply -f kubernetes-deployment.yaml

# Verify
kubectl get deployments -n ticketing
```

#### 5. Deploy Frontend to Blob Storage + Front Door

```bash
# Create storage account
az storage account create \
  --resource-group ticketing-rg \
  --name ticketingfrontend \
  --location eastus \
  --sku Standard_LRS

# Upload files
az storage blob upload-batch \
  --destination-path / \
  --source ./frontend/build \
  --account-name ticketingfrontend \
  --destination-container '$web'

# Enable static website hosting
az storage account update \
  --resource-group ticketing-rg \
  --name ticketingfrontend \
  --set 'staticWebsite={"enabled":true}'
```

## GCP Deployment

### Architecture
- **Compute**: Google Kubernetes Engine (GKE)
- **Database**: Cloud SQL PostgreSQL
- **Cache**: Cloud Memorystore Redis
- **Load Balancer**: Cloud Load Balancing
- **Storage**: Cloud Storage
- **CDN**: Cloud CDN
- **Monitoring**: Cloud Monitoring

### Steps

#### 1. Create GKE Cluster

```bash
# Set project
gcloud config set project PROJECT_ID

# Create GKE cluster
gcloud container clusters create ticketing-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-1

# Get credentials
gcloud container clusters get-credentials ticketing-cluster --zone us-central1-a
```

#### 2. Create Cloud SQL PostgreSQL

```bash
gcloud sql instances create ticketing-db \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region us-central1

# Create database
gcloud sql databases create ticketing_db --instance=ticketing-db

# Create user
gcloud sql users create postgres \
  --instance=ticketing-db \
  --password=<secure-password>
```

#### 3. Create Memorystore Redis

```bash
gcloud redis instances create ticketing-cache \
  --size=1 \
  --region=us-central1 \
  --redis-version=7.0
```

#### 4. Deploy to GKE

```bash
# Create GKE secrets
kubectl create secret generic cloud-sql-credentials \
  --from-file=key.json=path/to/service-account-key.json

# Apply manifests
kubectl apply -f kubernetes-deployment.yaml

# Verify
kubectl get deployments
```

#### 5. Deploy Frontend

```bash
# Build and push to Container Registry
docker build -t gcr.io/PROJECT_ID/ticketing-frontend:latest ./frontend
docker push gcr.io/PROJECT_ID/ticketing-frontend:latest

# Deploy to Cloud Run (optional)
gcloud run deploy ticketing-frontend \
  --image gcr.io/PROJECT_ID/ticketing-frontend:latest \
  --platform managed \
  --region us-central1
```

## Monitoring & Logging

### Prometheus & Grafana

```yaml
# prometheus-values.yaml
prometheus:
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    retention: 24h
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi

grafana:
  enabled: true
  adminPassword: secure-password
```

Install:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -f prometheus-values.yaml -n monitoring
```

### Application Logging

Configure application services to output structured logs:

```javascript
// Log to stdout for container log collection
console.log(JSON.stringify({
  timestamp: new Date().toISOString(),
  level: 'INFO',
  service: 'booking-service',
  message: 'Booking created',
  bookingId: booking.id,
  userId: userId
}));
```

### Health Checks

All services expose `/health` endpoint:
```bash
curl http://localhost:3000/health
# {"status": "API Gateway running"}
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t gcr.io/${{ secrets.GCP_PROJECT }}/api-gateway:${{ github.sha }} -f Dockerfile .
        docker push gcr.io/${{ secrets.GCP_PROJECT }}/api-gateway:${{ github.sha }}
    
    - name: Deploy to GKE
      uses: google-github-actions/get-gke-credentials@main
      with:
        cluster_name: ticketing-cluster
        zone: us-central1-a
    
    - name: Update Kubernetes
      run: |
        kubectl set image deployment/api-gateway \
          api-gateway=gcr.io/${{ secrets.GCP_PROJECT }}/api-gateway:${{ github.sha }} \
          -n ticketing
```

## Troubleshooting

### Pod Not Starting
```bash
kubectl describe pod <pod-name> -n ticketing
kubectl logs <pod-name> -n ticketing
```

### Database Connection Issues
```bash
# Test connectivity
kubectl exec -it <pod-name> -n ticketing -- \
  psql -h postgres -U postgres -d ticketing_db -c "SELECT 1;"
```

### Check Service Discovery
```bash
# Test DNS resolution
kubectl exec -it <pod-name> -n ticketing -- \
  nslookup user-service.ticketing.svc.cluster.local
```

## Performance Tuning

### Database
- Enable query caching with Redis
- Add indexes on frequently queried columns
- Use read replicas for scaling reads
- Connection pooling with PgBouncer

### Microservices
- Implement circuit breakers
- Add request timeouts
- Enable gzip compression
- Use CDN for static assets

### Kubernetes
- Set resource requests and limits
- Enable horizontal pod autoscaling
- Use pod disruption budgets
- Implement rate limiting

## Security Best Practices

1. **Secrets Management**
   - Use cloud provider secret managers
   - Rotate secrets regularly
   - Never commit secrets to repository

2. **Network Security**
   - Use NetworkPolicies in Kubernetes
   - Enable TLS/SSL for all communications
   - Implement WAF (Web Application Firewall)

3. **Access Control**
   - Use RBAC (Role-Based Access Control)
   - Implement pod security policies
   - Enable audit logging

4. **Data Protection**
   - Enable encryption at rest
   - Use encryption in transit
   - Regular backups
   - Comply with data protection regulations

## Cost Optimization

1. **Resource Optimization**
   - Right-size container resources
   - Use spot instances/preemptible VMs
   - Implement pod autoscaling

2. **Storage Optimization**
   - Use object storage for media files
   - Implement lifecycle policies
   - Compress backups

3. **Network Optimization**
   - Use CDN for static content
   - Implement caching strategies
   - Optimize data transfer

## Next Steps

1. Update cloud provider credentials in CI/CD
2. Configure custom domain and SSL certificates
3. Set up monitoring and alerting
4. Implement backup and disaster recovery
5. Conduct security audit
6. Load testing and performance optimization
7. Set up auto-scaling policies
