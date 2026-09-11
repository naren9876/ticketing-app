# Movie Ticketing Platform - Microservices Application

A production-ready, cloud-native movie ticketing application (Fandango-like) built with microservices architecture. Designed for deployment practice and demonstrating best practices for scalable cloud applications.

## 🎬 Project Overview

This is a complete implementation of an online movie ticket booking platform featuring:

- **5 Microservices** for modular, independently deployable components
- **React Web Application** with modern UI
- **React Native Mobile App** for iOS/Android
- **API Gateway** for unified access and authentication
- **Containerized Architecture** with Docker & Docker Compose
- **Kubernetes Ready** with comprehensive manifests
- **Multi-Cloud Support** (AWS, Azure, GCP)
- **Production-Grade Features** (monitoring, logging, security)

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Load Balancer                     │
├─────────────────────────────────────────────────────┤
│              API Gateway (Port 3000)                │
├─────────────────────────────────────────────────────┤
│  Microservices (Independent containers/pods)       │
│  ├─ User Service (3001)        - Auth & Profiles   │
│  ├─ Movie Service (3002)       - Catalog & Search  │
│  ├─ Booking Service (3003)     - Reservations      │
│  ├─ Payment Service (3004)     - Transactions      │
│  └─ Notification Service (3005)- Events & Alerts   │
├─────────────────────────────────────────────────────┤
│  Data & Caching Layer                              │
│  ├─ PostgreSQL Database        - Persistent Data   │
│  ├─ Redis Cache                - Performance       │
│  └─ RabbitMQ                   - Async Messaging   │
└─────────────────────────────────────────────────────┘
         ↓              ↓              ↓
    Frontend (Web)  Mobile App     Admin Portal
```

## 📁 Project Structure

```
movie-ticketing-platform/
├── ARCHITECTURE.md                    # System design
├── README.md                          # This file
├── DEPLOYMENT_GUIDE.md                # Cloud deployment guide
│
├── Microservices
├── api-gateway.js                     # Request routing & auth
├── user-service.js                    # User management
├── movie-service.js                   # Movie catalog
├── booking-service.js                 # Ticket booking
├── payment-service.js                 # Payment processing
│
├── Frontend Applications
├── frontend-app.jsx                   # React web UI
├── mobile-app.tsx                     # React Native app
├── App.css                            # Styling
│
├── Deployment & Infrastructure
├── docker-compose.yml                 # Local development
├── Dockerfile                         # Container image
├── kubernetes-deployment.yaml         # K8s manifests
├── package.json                       # Dependencies
└── .env.example                       # Environment template
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (for local development)
- Node.js 18+ (for development)
- Git
- Terminal/Command line

### Local Development (Recommended)

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/movie-ticketing-platform.git
cd movie-ticketing-platform
```

#### 2. Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### 3. Initialize Database
```bash
# Connect to PostgreSQL and create tables
docker exec ticketing_postgres psql -U postgres -d ticketing_db -c "
  CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  
  CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    genre VARCHAR(100),
    duration INT,
    rating DECIMAL(3,1),
    poster_url VARCHAR(500),
    release_date DATE
  );
"
```

#### 4. Access Services

| Service | URL |
|---------|-----|
| **API Gateway** | http://localhost:3000 |
| **Frontend (Web)** | http://localhost:3100 |
| **RabbitMQ Management** | http://localhost:15672 (guest/guest) |
| **User Service** | http://localhost:3001/health |
| **Movie Service** | http://localhost:3002/health |
| **Booking Service** | http://localhost:3003/health |
| **Payment Service** | http://localhost:3004/health |
| **Notification Service** | http://localhost:3005/health |

#### 5. Test API
```bash
# Register a new user
curl -X POST http://localhost:3000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe"
  }'

# Login
curl -X POST http://localhost:3000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Get movies
curl http://localhost:3000/api/movies
```

### Stop Services
```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

## 🌐 API Endpoints

### User Service
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register` | Create new user |
| POST | `/api/users/login` | User authentication |
| GET | `/api/users/profile` | Get user profile |
| PUT | `/api/users/profile` | Update profile |
| POST | `/api/users/verify-token` | Verify JWT token |

### Movie Service
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/movies` | Get all movies |
| GET | `/api/movies/:id` | Get movie details |
| GET | `/api/movies/search` | Search movies |
| GET | `/api/theaters` | Get all theaters |
| GET | `/api/showtimes` | Get showtimes |

### Booking Service
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bookings` | Create booking |
| GET | `/api/bookings/:id` | Get booking |
| GET | `/api/bookings/user/:userId` | Get user bookings |
| PUT | `/api/bookings/:id/confirm` | Confirm booking |
| PUT | `/api/bookings/:id/cancel` | Cancel booking |

### Payment Service
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/payments` | Process payment |
| GET | `/api/payments/:id` | Get payment |
| POST | `/api/payments/:id/refund` | Refund payment |

## 🔧 Technology Stack

### Backend
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: PostgreSQL
- **Cache**: Redis
- **Message Queue**: RabbitMQ

### Frontend
- **Web**: React.js
- **Mobile**: React Native
- **HTTP Client**: Axios
- **Styling**: CSS3 + React

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Cloud**: AWS / Azure / GCP
- **CI/CD**: GitHub Actions

## 📦 Environment Variables

Create `.env` file in project root:

```env
# Database Configuration
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ticketing_db

# Cache Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Security
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# External Services
STRIPE_SECRET_KEY=sk_test_your_stripe_key
SENDGRID_API_KEY=your-sendgrid-api-key

# Service URLs
USER_SERVICE_URL=http://user-service:3001
MOVIE_SERVICE_URL=http://movie-service:3002
BOOKING_SERVICE_URL=http://booking-service:3003
PAYMENT_SERVICE_URL=http://payment-service:3004
NOTIFICATION_SERVICE_URL=http://notification-service:3005

# Environment
NODE_ENV=development
```

## ☁️ Cloud Deployment

### Quick Deploy to Kubernetes

```bash
# Update Kubernetes manifests with your cloud provider details
# Then apply:
kubectl apply -f kubernetes-deployment.yaml

# Verify deployment
kubectl get pods -n ticketing
kubectl get svc -n ticketing
```

For detailed instructions for each cloud provider, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### AWS EKS
```bash
# Create cluster
eksctl create cluster --name ticketing-cluster --region us-east-1

# Deploy
kubectl apply -f kubernetes-deployment.yaml
```

### Azure AKS
```bash
# Create cluster
az aks create --resource-group ticketing --name ticketing-aks

# Deploy
kubectl apply -f kubernetes-deployment.yaml
```

### Google GKE
```bash
# Create cluster
gcloud container clusters create ticketing-cluster --zone us-central1-a

# Deploy
kubectl apply -f kubernetes-deployment.yaml
```

## 🔐 Security Features

- ✅ JWT Token-based authentication
- ✅ Password hashing with bcrypt
- ✅ Rate limiting on API endpoints
- ✅ HTTPS/TLS encryption
- ✅ SQL injection prevention
- ✅ CORS protection
- ✅ Secrets management
- ✅ Network policies (in Kubernetes)
- ✅ Pod security policies

## 📊 Monitoring & Logging

### Application Metrics
- Request latency
- Error rates
- Service health
- Database performance
- Cache hit rates

### Logging
All services output structured JSON logs to stdout, which can be collected by:
- CloudWatch (AWS)
- Log Analytics (Azure)
- Cloud Logging (GCP)
- ELK Stack (self-hosted)

### Health Checks
```bash
curl http://localhost:3000/health  # API Gateway
curl http://localhost:3001/health  # User Service
curl http://localhost:3002/health  # Movie Service
# ... etc for other services
```

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### Load Testing
```bash
npm run test:load
```

## 📈 Performance Optimization

- Horizontal Pod Autoscaling (HPA)
- Vertical Pod Autoscaling (VPA)
- Database query optimization
- Redis caching strategy
- CDN for static assets
- gzip compression
- Connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design and components
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Cloud deployment guide
- [API Documentation](docs/API.md) - Detailed API endpoints
- [Development Guide](docs/DEVELOPMENT.md) - Setup and development

## 🐛 Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs user-service
docker-compose logs api-gateway

# Restart services
docker-compose restart
```

### Database Connection Issues
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Connect directly
docker exec -it ticketing_postgres psql -U postgres
```

### Port Already in Use
```bash
# Check what's using ports
lsof -i :3000
# Kill process
kill -9 <PID>
```

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 💡 Learning Resources

- [Microservices Architecture](https://microservices.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Cloud Architecture Patterns](https://cloud.google.com/architecture/patterns)

## 🎯 Roadmap

- [ ] GraphQL API alternative
- [ ] Real-time notifications with WebSockets
- [ ] Advanced search and filtering
- [ ] Analytics dashboard
- [ ] Admin portal
- [ ] Mobile app optimization
- [ ] Machine learning recommendations
- [ ] Blockchain payment integration

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🌟 Show Your Support

If this project helped you, please give it a ⭐️

---

**Happy Coding! 🚀**
