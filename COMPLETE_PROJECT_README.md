# 🎬 Movie Ticketing Platform - Complete DevOps MLOps AI Stack

[![CI/CD Pipeline](https://github.com/your-org/movie-ticketing/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-org/movie-ticketing/actions)
[![Code Coverage](https://codecov.io/gh/your-org/movie-ticketing/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/movie-ticketing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **production-grade, end-to-end implementation** of an online movie ticketing platform covering **18 modules** of the DevOps MLOps AI curriculum.

```
✅ Microservices Architecture     ✅ Kubernetes Orchestration
✅ Full CI/CD Pipeline            ✅ Machine Learning Models
✅ MLOps Infrastructure           ✅ Generative AI Chatbot
✅ Data Engineering Pipeline      ✅ Production Monitoring
✅ Multi-Cloud Deployment         ✅ Security & Compliance
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# Required
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+
- kubectl (for Kubernetes)
```

### One-Command Setup
```bash
# Make the script executable
chmod +x init.sh

# Run initialization
./init.sh

# Follow on-screen instructions
```

### Alternative Step-by-Step Setup
```bash
# 1. Install dependencies
make install

# 2. Setup environment
make setup

# 3. Start development environment
make dev

# 4. Access services
# Frontend: http://localhost:3100
# API: http://localhost:3000
# MLflow: http://localhost:5000
# Airflow: http://localhost:8080
```

---

## 📊 Project Structure

```
movie-ticketing-platform/
├── 📱 Frontend Applications
│   ├── frontend-app.jsx          React web application
│   ├── mobile-app.tsx            React Native mobile
│   └── App.css                   Styling
│
├── 🔧 Microservices (Node.js)
│   ├── api-gateway.js            API Gateway & routing
│   ├── user-service.js           Authentication & profiles
│   ├── movie-service.js          Movie catalog
│   ├── booking-service.js        Seat reservations
│   ├── payment-service.js        Payment processing
│   └── notification-service.js   Notifications
│
├── 🤖 Machine Learning
│   ├── recommendation_model.py   Recommendation system
│   ├── fraud_detection_model.py  Fraud detection
│   ├── demand_forecasting_model.py Time series forecast
│   ├── model_serving_api.py      FastAPI model server
│   ├── mlflow_setup.py           MLOps pipeline
│   ├── model_monitoring.py       Drift detection
│   ├── airflow_etl_dag.py        Data pipeline
│   └── llm_chatbot_rag.py        LLM chatbot
│
├── 📦 Infrastructure
│   ├── Dockerfile                Container image
│   ├── docker-compose.yml        Local services
│   ├── docker-compose-ml.yml     ML/data services
│   ├── kubernetes-deployment.yaml Microservices K8s
│   ├── kubernetes_ai_workloads.yaml ML workloads K8s
│   ├── package.json              NPM dependencies
│   └── requirements.txt          Python dependencies
│
├── 🔄 CI/CD
│   ├── .github/workflows/ci-cd.yml GitHub Actions
│   ├── Makefile                  Common commands
│   ├── init.sh                   Project initialization
│   └── .gitignore                Git ignore rules
│
├── 📚 Documentation
│   ├── README_18_MODULES.md      18-module overview
│   ├── COMPLETE_18_MODULES_DOCUMENTATION.md Full guide
│   ├── CURRICULUM_MAPPING_SUMMARY.md Executive summary
│   ├── ARCHITECTURE.md           System design
│   ├── DEPLOYMENT_GUIDE.md       Deployment steps
│   ├── ENTERPRISE_DEPLOYMENT_PATTERNS.md Strategies
│   └── FILE_PURPOSES_QUICK_GUIDE.md File reference
│
├── 🧪 Tests
│   ├── tests/unit/              Unit tests
│   ├── tests/integration/       Integration tests
│   └── tests/ml/                ML model tests
│
├── 📊 Data & Models
│   ├── data/raw/                Raw data
│   ├── data/processed/          Processed data
│   ├── data/features/           Feature data
│   ├── models/                  Trained models
│   ├── artifacts/               MLflow artifacts
│   └── notebooks/               Jupyter notebooks
│
└── ⚙️ Configuration
    ├── .env.example             Environment template
    ├── airflow/dags/            Airflow DAGs
    ├── monitoring/              Prometheus/Grafana
    └── logs/                    Application logs
```

---

## 🎯 What's Included

### Microservices (6 Services)
| Service | Port | Purpose |
|---------|------|---------|
| API Gateway | 3000 | Authentication, rate limiting, routing |
| User Service | 3001 | User registration, profiles |
| Movie Service | 3002 | Movie catalog, showtimes |
| Booking Service | 3003 | Seat reservations |
| Payment Service | 3004 | Payment processing |
| Notification Service | 3005 | Email/SMS notifications |

### ML Models (3 Models)
| Model | Technology | Purpose |
|-------|-----------|---------|
| Recommendation | Hybrid (Collaborative + Content) | Movie recommendations |
| Fraud Detection | XGBoost | Detect fraudulent transactions |
| Demand Forecast | LSTM | Predict ticket demand |

### Data & MLOps
| Component | Purpose |
|-----------|---------|
| Airflow | ETL pipeline orchestration |
| MLflow | Experiment tracking & model registry |
| FastAPI | Model serving API |
| Monitoring | Drift detection & performance tracking |

### Frontend (2 Apps)
| App | Technology | Purpose |
|-----|-----------|---------|
| Web | React.js | Desktop booking interface |
| Mobile | React Native | Mobile booking app |

---

## 📖 Usage Guide

### Local Development

```bash
# Start all services
make dev

# View logs
make logs

# Run tests
make test

# Run linters
make lint

# Format code
make format

# Stop services
make dev-stop
```

### Kubernetes Deployment

```bash
# Create namespaces
make k8s-create-ns

# Deploy services
make k8s-deploy

# Check status
make k8s-status

# View logs
kubectl logs -f -n ticketing deployment/api-gateway

# Delete deployment
make k8s-delete
```

### ML Model Training

```bash
# Start MLflow server
make mlflow-start

# Train all models
make train-models

# Start model serving
make model-serve

# Access model API
curl http://localhost:8000/docs
```

### Data Pipeline

```bash
# Start Airflow
make airflow-start

# Access Airflow UI
# http://localhost:8080

# Trigger DAG
airflow dags trigger movie_ticketing_etl_pipeline
```

---

## 🛠️ Available Commands

```bash
make help                 # Show all commands
make init                 # First-time setup
make install             # Install dependencies
make setup               # Setup environment files
make dev                 # Start development
make test                # Run all tests
make lint                # Run linters
make format              # Format code
make docker-build        # Build Docker image
make docker-up           # Start Docker containers
make docker-down         # Stop containers
make k8s-deploy          # Deploy to Kubernetes
make train-models        # Train ML models
make mlflow-start        # Start MLflow server
make model-serve         # Start model API
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  USER INTERFACE LAYER                   │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────┐ │
│  │ React Web    │  │ React Native   │  │ LLM Chatbot │ │
│  │ (3100)       │  │ Mobile         │  │ (RAG)       │ │
│  └──────────────┘  └────────────────┘  └─────────────┘ │
└────────────────────────────────────────────────────────┬┘
                            ↓
┌────────────────────────────────────────────────────────┐
│              API GATEWAY & SERVICES LAYER               │
│  ┌────────────────────────────────────────────────────┐ │
│  │  API Gateway (3000) - Auth, Rate Limit, Routing   │ │
│  ├────┬────────────┬────────────┬──────────┬────────┤ │
│  │    │            │            │          │        │ │
│  ▼    ▼            ▼            ▼          ▼        ▼ │
│ User Movie        Booking      Payment   Notification │
│ (3001) (3002)    (3003)        (3004)     (3005)      │
└────────────────────────────────────────────────────────┬┘
                            ↓
┌────────────────────────────────────────────────────────┐
│              ML MODEL SERVING LAYER                     │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │Recommend.  │  │Fraud Detect. │  │Demand Forecast │ │
│  │(Hybrid)    │  │(XGBoost)     │  │(LSTM)          │ │
│  └────────────┘  └──────────────┘  └─────────────────┘ │
└────────────────────────────────────────────────────────┬┘
                            ↓
┌────────────────────────────────────────────────────────┐
│              DATA & INFRASTRUCTURE LAYER                │
│  ┌─────────────┐  ┌──────────┐  ┌─────────────────────┤
│  │PostgreSQL   │  │Redis     │  │RabbitMQ             │
│  │(Transactions)│  │(Cache)   │  │(Message Queue)      │
│  └─────────────┘  └──────────┘  └─────────────────────┤
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │Airflow ETL   │  │MLflow        │  │Prometheus   │ │
│  │(Pipeline)    │  │(Experiments) │  │(Monitoring) │ │
│  └──────────────┘  └──────────────┘  └─────────────┘ │
└────────────────────────────────────────────────────────┬┘
                            ↓
┌────────────────────────────────────────────────────────┐
│           CONTAINER ORCHESTRATION LAYER                │
│         Kubernetes (Microservices + AI)                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Pods, Services, Deployments, StatefulSets        │ │
│  │  KServe (Model Serving), GPU Support             │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┬┘
                            ↓
┌────────────────────────────────────────────────────────┐
│              CLOUD PLATFORMS (MULTI-CLOUD)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │AWS (EKS)     │  │Azure (AKS)   │  │GCP (GKE)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Features

- ✅ JWT-based authentication
- ✅ Rate limiting per endpoint
- ✅ HTTPS/TLS encryption
- ✅ SQL injection prevention (parameterized queries)
- ✅ CORS security headers
- ✅ Input validation (Joi/Pydantic)
- ✅ Secrets management (environment variables)
- ✅ RBAC in Kubernetes
- ✅ Network policies
- ✅ Security scanning in CI/CD

---

## 📊 Monitoring & Observability

### Metrics & Dashboards
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **MLflow**: Model experiment tracking
- **OpenTelemetry**: Distributed tracing

### Logs
- **Application logs**: JSON format to stdout
- **Access logs**: Apache combined format
- **Error logs**: Structured logging with context

---

## 🚀 Deployment Strategies

### Blue-Green Deployment
```bash
# Deploy to green environment
kubectl apply -f kubernetes-deployment.yaml -n production-green

# Switch traffic
kubectl patch service api-gateway -p '{"spec":{"selector":{"version":"green"}}}'

# Rollback if needed
kubectl patch service api-gateway -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Canary Deployment
```bash
# Deploy new version to 10% of traffic
kubectl set image deployment/api-gateway api-gateway=image:new --record

# Monitor metrics
kubectl top pods -n ticketing

# Gradually increase to 100%
# (Typically done with Flagger or Istio)
```

---

## 🧪 Testing

### Test Structure
```
tests/
├── unit/                   Unit tests
├── integration/            Integration tests with services
└── ml/                     ML model tests
```

### Running Tests
```bash
make test                   # All tests
make test-unit             # Unit tests only
make test-integration      # Integration tests
make test-ml               # ML model tests
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README_18_MODULES.md** | Quick overview of 18 modules |
| **COMPLETE_18_MODULES_DOCUMENTATION.md** | Detailed 50+ page guide |
| **ARCHITECTURE.md** | System design & components |
| **DEPLOYMENT_GUIDE.md** | Step-by-step deployment |
| **ENTERPRISE_DEPLOYMENT_PATTERNS.md** | Deployment strategies |
| **FILE_PURPOSES_QUICK_GUIDE.md** | File reference guide |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

All PRs must pass:
- ✅ Unit tests
- ✅ Integration tests
- ✅ Code linting
- ✅ Security scanning

---

## 📞 Support

### Getting Help
- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues for bugs/features
- **Discussion**: GitHub Discussions for questions
- **Slack**: [Join our community](https://slack.example.com)

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- Built for the complete DevOps MLOps AI curriculum (18 modules)
- Covers production patterns and best practices
- Follows Cloud Native Computing Foundation guidelines
- Incorporates security and compliance standards

---

## 🎯 Curriculum Coverage

✅ **18/18 Modules Complete**

| Module | Status | Coverage |
|--------|--------|----------|
| 1-11 | DevOps Core | 100% |
| 12-18 | AI/ML Stack | 100% |

See **CURRICULUM_MAPPING_SUMMARY.md** for detailed breakdown

---

**Ready to get started?** Run `./init.sh` now! 🚀
