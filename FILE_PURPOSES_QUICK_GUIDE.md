# 📋 QUICK FILE REFERENCE GUIDE
## Simple Explanation of Every File

---

## 🔧 MICROSERVICES (Backend Services)

| File | Purpose |
|------|---------|
| **api-gateway.js** | Entrance point for all API requests. Handles authentication, rate limiting, and routes requests to correct services. |
| **user-service.js** | Manages user registration, login, and profile information. Uses JWT for secure authentication. |
| **movie-service.js** | Stores and serves movie information (title, genre, description). Uses Redis caching for fast lookups. |
| **booking-service.js** | Handles seat reservations. Ensures no double-booking through transactional logic. |
| **payment-service.js** | Processes payment transactions. Integrates with Stripe for secure payment handling. |
| **notification-service.js** | Sends SMS and email notifications to users asynchronously via RabbitMQ. |

---

## 🎨 FRONTEND APPLICATIONS

| File | Purpose |
|------|---------|
| **frontend-app.jsx** | React web application. Provides UI for browsing movies, selecting seats, and booking tickets. |
| **mobile-app.tsx** | React Native mobile app. Same functionality as web app but optimized for mobile devices. |
| **App.css** | Styling file. Dark theme, responsive design, works on all screen sizes. |

---

## 🤖 MACHINE LEARNING MODELS (NEW - Modules 12-13)

| File | Purpose |
|------|---------|
| **recommendation_model.py** | Recommends movies to users based on their viewing history. Uses hybrid approach (collaborative + content-based filtering). |
| **fraud_detection_model.py** | Detects fraudulent transactions using XGBoost. Analyzes transaction patterns and flags suspicious activity. |
| **demand_forecasting_model.py** | Predicts ticket demand for next 7 days using LSTM neural network. Helps with resource planning. |

---

## 🚀 MODEL DEPLOYMENT (Module 14)

| File | Purpose |
|------|---------|
| **model_serving_api.py** | REST API server using FastAPI. Serves all 3 ML models. You make HTTP requests to get predictions in real-time. |

---

## 🔬 MLOPS & MONITORING (Modules 13, 18)

| File | Purpose |
|------|---------|
| **mlflow_setup.py** | Tracks ML experiments and manages model versions. Records which parameters work best for each model. |
| **model_monitoring.py** | Watches models in production. Detects if data changed (drift) or model accuracy dropped. Triggers retraining if needed. |

---

## 📊 DATA PIPELINE (Module 16)

| File | Purpose |
|------|---------|
| **airflow_etl_dag.py** | Apache Airflow workflow that automatically extracts, transforms, and loads data daily. Ingests transaction/user/movie data, cleans it, creates features, validates quality. |

---

## 💬 GENERATIVE AI (Module 17)

| File | Purpose |
|------|---------|
| **llm_chatbot_rag.py** | Customer support chatbot using LLM. Stores FAQ in vector database, retrieves relevant info, and generates responses. |

---

## 📦 DOCKER & CONTAINERIZATION (Module 6)

| File | Purpose |
|------|---------|
| **Dockerfile** | Blueprint for creating container image. Specifies how to package the app into a runnable Docker container. |
| **docker-compose.yml** | Configuration for running 11 services locally. Starts PostgreSQL, Redis, RabbitMQ, all microservices, and frontends with one command. |

---

## ☸️ KUBERNETES CONFIGURATION (Modules 7, 15)

| File | Purpose |
|------|---------|
| **kubernetes-deployment.yaml** | YAML file for deploying microservices on Kubernetes. Defines pods, services, storage, and scaling rules. |
| **kubernetes_ai_workloads.yaml** | YAML file for deploying ML models on Kubernetes. Sets up KServe for model serving, GPU support, and training jobs. |

---

## 📋 CONFIGURATION FILES

| File | Purpose |
|------|---------|
| **package.json** | Lists all Node.js dependencies and their versions. Tells npm what to install for the project. |

---

## 📖 DOCUMENTATION FILES (Main Guides)

| File | Purpose |
|------|---------|
| **README.md** | Quick overview of the project. What it does and how to start it. |
| **ARCHITECTURE.md** | System design explanation. Shows how microservices communicate with each other. |
| **DEPLOYMENT_GUIDE.md** | Step-by-step instructions for deploying to AWS, Azure, and GCP. |
| **ENTERPRISE_DEPLOYMENT_PATTERNS.md** | Explains 4 deployment strategies: Blue-Green, Canary, Rolling, Shadow. When to use each. |
| **ENTERPRISE_DEPLOYMENT_IMPLEMENTATION.md** | Actual bash scripts and code for implementing deployment strategies. |
| **DEPLOYMENT_STRATEGIES_VISUAL_GUIDE.md** | Diagrams and decision trees for choosing deployment strategy. |
| **CURRICULUM_COVERAGE_ANALYSIS.md** | Detailed breakdown of all 18 curriculum modules and what's covered. |
| **QUICK_MODULE_REFERENCE.txt** | One-page lookup table showing all modules and files. |
| **CURRICULUM_MAPPING_SUMMARY.md** | Executive summary connecting curriculum to implementation. |
| **COMPLETE_18_MODULES_DOCUMENTATION.md** | Comprehensive 50+ page guide explaining all 18 modules in detail. |
| **README_18_MODULES.md** | Quick start guide for complete 18-module extended version. |

---

## 📊 SUMMARY BY CATEGORY

### **Microservices** (6 files)
- Handle core business logic (users, movies, bookings, payments, notifications)

### **Frontend** (3 files)
- Web and mobile UI for customers to book tickets

### **Machine Learning** (3 files)
- Train ML models for recommendations, fraud, and forecasting

### **Model Serving** (1 file)
- API server to make predictions from trained models

### **MLOps & Monitoring** (2 files)
- Track experiments and monitor model performance

### **Data Pipeline** (1 file)
- Automate data ingestion and feature engineering

### **Chatbot** (1 file)
- AI-powered customer support

### **Docker & Kubernetes** (4 files)
- Package and deploy everything on cloud

### **Documentation** (11 files)
- Guides and references for every aspect

---

## 🚀 HOW THEY WORK TOGETHER

```
REQUEST FLOW:
User → Frontend (React/Mobile) 
   ↓
API Gateway (Rate limiting, Auth)
   ↓
Microservices (User/Movie/Booking/Payment/Notification)
   ↓
Database & Cache (PostgreSQL, Redis)

ML FLOW:
Raw Data → Airflow (Extract, Transform, Load)
   ↓
Feature Engineering
   ↓
Train Models (Recommendation, Fraud, Demand)
   ↓
MLflow (Track experiments)
   ↓
FastAPI Server (Serve predictions)
   ↓
Model Monitoring (Detect drift)
   ↓
Auto-retrain if needed

CHATBOT FLOW:
User Question → LLM Chatbot
   ↓
Search Vector DB (FAQ)
   ↓
Retrieve Relevant Docs
   ↓
Generate Response
   ↓
Monitor Quality
```

---

## 📁 WHERE TO START?

**For Understanding:**
1. Start: `README_18_MODULES.md`
2. Learn: `CURRICULUM_MAPPING_SUMMARY.md`
3. Deep Dive: `COMPLETE_18_MODULES_DOCUMENTATION.md`

**For Development:**
1. Setup: `docker-compose.yml` (local) or `kubernetes-deployment.yaml` (production)
2. Code: The microservices files (*.js) and ML files (*.py)
3. Deploy: `kubernetes_ai_workloads.yaml` for ML models

**For Deployment:**
1. Strategy: `ENTERPRISE_DEPLOYMENT_PATTERNS.md` (which approach?)
2. Implementation: `ENTERPRISE_DEPLOYMENT_IMPLEMENTATION.md` (how to deploy)
3. Visual: `DEPLOYMENT_STRATEGIES_VISUAL_GUIDE.md` (see decision trees)

---

## ✅ WHAT EACH FILE DOES (One Sentence Each)

**Services:**
- `api-gateway.js` → Routes requests and handles security
- `user-service.js` → Manages login and profiles
- `movie-service.js` → Provides movie information
- `booking-service.js` → Reserves seats
- `payment-service.js` → Processes payments
- `notification-service.js` → Sends messages

**Frontend:**
- `frontend-app.jsx` → Web app UI
- `mobile-app.tsx` → Mobile app UI
- `App.css` → Styling

**ML Models:**
- `recommendation_model.py` → Suggests movies
- `fraud_detection_model.py` → Catches fraud
- `demand_forecasting_model.py` → Predicts ticket demand

**ML Operations:**
- `model_serving_api.py` → Serves ML predictions via API
- `mlflow_setup.py` → Tracks ML experiments
- `model_monitoring.py` → Checks if models are still accurate

**Data:**
- `airflow_etl_dag.py` → Processes data daily

**AI:**
- `llm_chatbot_rag.py` → Customer support chatbot

**Deployment:**
- `Dockerfile` → Container blueprint
- `docker-compose.yml` → Run locally
- `kubernetes-deployment.yaml` → Deploy microservices
- `kubernetes_ai_workloads.yaml` → Deploy ML models
- `package.json` → List dependencies

**Documentation:**
- All `*.md` and `*.txt` files → Guides and references
