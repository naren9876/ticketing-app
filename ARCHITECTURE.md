# Movie Ticketing Platform - Microservices Architecture

## System Overview

A cloud-native movie ticketing application (Fandango-like) built with microservices architecture, designed for scalability and cloud deployment.

## System Components

### Microservices

1. **User Service** (Port: 3001)
   - User registration and authentication
   - Profile management
   - JWT token generation
   - Database: PostgreSQL

2. **Movie Service** (Port: 3002)
   - Movie catalog management
   - Theater and showtimes
   - Search and filter capabilities
   - Database: PostgreSQL

3. **Booking Service** (Port: 3003)
   - Ticket booking management
   - Seat selection and reservation
   - Booking confirmation
   - Database: PostgreSQL

4. **Payment Service** (Port: 3004)
   - Payment processing
   - Order creation and management
   - Refund handling
   - Database: PostgreSQL
   - External: Stripe API integration

5. **Notification Service** (Port: 3005)
   - Email notifications
   - SMS notifications
   - Booking confirmations
   - Queue: Redis for message queue
   - External: SendGrid/Twilio APIs

6. **API Gateway** (Port: 3000)
   - Request routing
   - Authentication middleware
   - Rate limiting
   - Load balancing

### Frontend Applications

1. **Web UI** (React)
   - Movie browsing
   - Booking interface
   - Payment integration
   - User dashboard
   - Responsive design

2. **Mobile App** (React Native / Mobile-responsive)
   - Native mobile experience
   - Push notifications
   - Mobile payment integration
   - Optimized UI/UX

### Supporting Infrastructure

- **Database**: PostgreSQL (shared for microservices)
- **Cache**: Redis (caching & message queue)
- **Message Queue**: RabbitMQ/Redis (async notifications)
- **API Documentation**: Swagger/OpenAPI
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack

## Technology Stack

- **Backend**: Node.js/Express
- **Frontend**: React.js
- **Mobile**: React Native (or React web with mobile-responsive design)
- **Container**: Docker
- **Orchestration**: Kubernetes
- **Cloud Platforms**: AWS/Azure/GCP compatible
- **Database**: PostgreSQL
- **Cache**: Redis
- **Messaging**: RabbitMQ
- **API Gateway**: Express/Kong

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Cloud Provider (AWS/Azure/GCP)   │
├─────────────────────────────────────────┤
│  Load Balancer / API Gateway            │
├─────────────────────────────────────────┤
│        Kubernetes Cluster                │
│  ┌─────────────────────────────────────┐ │
│  │  Microservices (Pods)               │ │
│  │  - User Service                     │ │
│  │  - Movie Service                    │ │
│  │  - Booking Service                  │ │
│  │  - Payment Service                  │ │
│  │  - Notification Service             │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │  Data Layer                         │ │
│  │  - PostgreSQL (RDS)                 │ │
│  │  - Redis Cache                      │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │
         ├── Frontend (S3 + CloudFront)
         ├── Mobile App (App Store/Play Store)
         └── CDN for static assets
```

## Key Features

1. **Scalability**: Horizontal scaling of microservices
2. **Resilience**: Service mesh for inter-service communication
3. **High Availability**: Multi-zone deployment
4. **Security**: JWT authentication, rate limiting, HTTPS
5. **Monitoring**: Prometheus metrics, centralized logging
6. **CI/CD**: Automated testing and deployment pipelines
7. **Database Replication**: Read replicas for scaling queries

## API Endpoints Summary

### User Service
- POST /api/users/register
- POST /api/users/login
- GET /api/users/profile
- PUT /api/users/profile

### Movie Service
- GET /api/movies
- GET /api/movies/:id
- GET /api/theaters
- GET /api/showtimes

### Booking Service
- POST /api/bookings
- GET /api/bookings/:id
- PUT /api/bookings/:id/cancel
- GET /api/bookings/user/:userId

### Payment Service
- POST /api/payments
- GET /api/payments/:id
- POST /api/payments/:id/refund

### Notification Service
- POST /api/notifications/email
- POST /api/notifications/sms

## Deployment Instructions

See deployment guides for:
- Docker Compose (Local Development)
- Kubernetes (Production)
- CI/CD Pipeline Configuration
