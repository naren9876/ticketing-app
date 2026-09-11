"""
Model Serving API using FastAPI
Module 14: AI Model Deployment
Covers: REST API for ML models, async inference, batch predictions, monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime
import logging
import json
from enum import Enum
import time
import asyncio
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import ML models (in production, these would be loaded once)
# from recommendation_model import RecommendationSystem
# from fraud_detection_model import FraudDetectionModel
# from demand_forecasting_model import DemandForecastingModel

# Models storage
models_cache = {}

# ==================== Request/Response Models ====================

class RecommendationRequest(BaseModel):
    """Request model for movie recommendations"""
    user_id: int
    n_recommendations: int = Field(default=5, ge=1, le=20)
    recommendation_type: str = Field(default="hybrid", regex="^(collaborative|content|hybrid)$")

class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    user_id: int
    recommendations: List[Dict[str, Any]]
    generated_at: datetime
    model_version: str

class FraudTransaction(BaseModel):
    """Single transaction for fraud detection"""
    transaction_id: Optional[str] = None
    user_id: int
    amount: float
    timestamp: datetime
    device_type: str = "unknown"
    location: str = "unknown"

class FraudDetectionRequest(BaseModel):
    """Request model for fraud detection"""
    transactions: List[FraudTransaction]

class FraudDetectionResponse(BaseModel):
    """Response model for fraud predictions"""
    predictions: List[Dict[str, Any]]
    processed_at: datetime
    fraud_detection_score: float

class DemandForecastRequest(BaseModel):
    """Request model for demand forecasting"""
    movie_id: int
    forecast_days: int = Field(default=7, ge=1, le=30)
    include_confidence_interval: bool = True

class DemandForecastResponse(BaseModel):
    """Response model for demand forecast"""
    movie_id: int
    forecast: List[float]
    lower_bound: Optional[List[float]] = None
    upper_bound: Optional[List[float]] = None
    mean_forecast: float
    forecast_generated_at: datetime

# ==================== Batch Processing Models ====================

class BatchPredictionRequest(BaseModel):
    """Request for batch predictions"""
    batch_id: str
    predictions_type: str = Field(regex="^(recommendation|fraud|demand)$")
    data: List[Dict[str, Any]]

class BatchPredictionResponse(BaseModel):
    """Response for batch predictions"""
    batch_id: str
    status: str = Field(regex="^(processing|completed|failed)$")
    total_records: int
    processed_records: int
    results_url: Optional[str] = None
    created_at: datetime

# ==================== Monitoring Models ====================

class ModelMetrics(BaseModel):
    """Model performance metrics"""
    model_name: str
    predictions_total: int
    predictions_successful: int
    predictions_failed: int
    avg_latency_ms: float
    last_updated: datetime

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    models_loaded: List[str]
    timestamp: datetime
    uptime_seconds: float

# ==================== Lifespan Context ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load models on startup, cleanup on shutdown
    """
    logger.info("Starting Model Serving API...")
    
    # Load models (in production, use proper model registry)
    models_cache['recommendation_model'] = {
        'status': 'loaded',
        'version': '1.0.0',
        'predictions_total': 0,
        'predictions_successful': 0,
        'avg_latency': 0
    }
    models_cache['fraud_model'] = {
        'status': 'loaded',
        'version': '1.0.0',
        'predictions_total': 0,
        'predictions_successful': 0,
        'avg_latency': 0
    }
    models_cache['demand_model'] = {
        'status': 'loaded',
        'version': '1.0.0',
        'predictions_total': 0,
        'predictions_successful': 0,
        'avg_latency': 0
    }
    
    logger.info(f"Loaded {len(models_cache)} models")
    
    yield
    
    logger.info("Shutting down Model Serving API...")
    # Cleanup resources

# ==================== Initialize FastAPI ====================

app = FastAPI(
    title="Movie Ticketing ML Model Serving API",
    description="REST API for serving recommendation, fraud detection, and demand forecasting models",
    version="1.0.0",
    lifespan=lifespan
)

# ==================== Health & Status Endpoints ====================

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Check API and model health
    """
    return {
        "status": "healthy",
        "models_loaded": list(models_cache.keys()),
        "timestamp": datetime.now(),
        "uptime_seconds": time.time()
    }

@app.get("/models/status", response_model=List[ModelMetrics])
async def get_model_status():
    """
    Get status and metrics for all loaded models
    """
    metrics = []
    for model_name, model_info in models_cache.items():
        metrics.append({
            "model_name": model_name,
            "predictions_total": model_info['predictions_total'],
            "predictions_successful": model_info['predictions_successful'],
            "predictions_failed": model_info.get('predictions_total', 0) - model_info['predictions_successful'],
            "avg_latency_ms": model_info.get('avg_latency', 0),
            "last_updated": datetime.now()
        })
    return metrics

# ==================== Recommendation Endpoints ====================

@app.post("/recommendations/predict", response_model=RecommendationResponse)
async def recommend_movies(request: RecommendationRequest):
    """
    Get movie recommendations for a user
    
    Args:
        request: RecommendationRequest with user_id and preferences
        
    Returns:
        List of recommended movies with scores
    """
    try:
        start_time = time.time()
        
        # Simulate model prediction
        # In production: rec_model = load_model('recommendation_model')
        logger.info(f"Getting {request.recommendation_type} recommendations for user {request.user_id}")
        
        # Mock recommendations
        mock_recommendations = [
            {
                'movie_id': i,
                'title': f'Movie {i}',
                'genre': 'Action',
                'predicted_rating': 4.5 - (i * 0.1),
                'confidence': 0.9 - (i * 0.05)
            }
            for i in range(1, request.n_recommendations + 1)
        ]
        
        # Update metrics
        latency = (time.time() - start_time) * 1000
        models_cache['recommendation_model']['predictions_total'] += 1
        models_cache['recommendation_model']['predictions_successful'] += 1
        models_cache['recommendation_model']['avg_latency'] = latency
        
        return {
            "user_id": request.user_id,
            "recommendations": mock_recommendations,
            "generated_at": datetime.now(),
            "model_version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Recommendation prediction failed: {str(e)}")
        models_cache['recommendation_model']['predictions_total'] += 1
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations/batch")
async def batch_recommendations(request: List[RecommendationRequest], background_tasks: BackgroundTasks):
    """
    Get batch recommendations for multiple users
    
    Args:
        request: List of recommendation requests
        
    Returns:
        Batch job status and results URL
    """
    batch_id = f"rec_batch_{int(time.time())}"
    logger.info(f"Starting batch recommendation job {batch_id} for {len(request)} users")
    
    # Add background task to process batch
    background_tasks.add_task(process_recommendation_batch, batch_id, request)
    
    return {
        "batch_id": batch_id,
        "status": "processing",
        "total_records": len(request),
        "processed_records": 0,
        "created_at": datetime.now()
    }

async def process_recommendation_batch(batch_id: str, requests: List[RecommendationRequest]):
    """Process recommendation batch in background"""
    logger.info(f"Processing batch {batch_id}...")
    results = []
    
    for req in requests:
        # Process each request
        rec = await recommend_movies(req)
        results.append(rec.dict())
    
    # Save results
    logger.info(f"Batch {batch_id} completed: {len(results)} records processed")

# ==================== Fraud Detection Endpoints ====================

@app.post("/fraud/predict", response_model=FraudDetectionResponse)
async def detect_fraud(request: FraudDetectionRequest):
    """
    Detect fraudulent transactions
    
    Args:
        request: FraudDetectionRequest with transaction data
        
    Returns:
        Fraud predictions with risk scores
    """
    try:
        start_time = time.time()
        
        logger.info(f"Detecting fraud in {len(request.transactions)} transactions")
        
        # Mock fraud predictions
        predictions = []
        fraud_count = 0
        
        for i, tx in enumerate(request.transactions):
            fraud_prob = np.random.uniform(0, 1)
            is_fraud = fraud_prob > 0.95
            if is_fraud:
                fraud_count += 1
            
            predictions.append({
                'transaction_id': tx.transaction_id or f"tx_{i}",
                'user_id': tx.user_id,
                'amount': tx.amount,
                'fraud_probability': float(fraud_prob),
                'is_fraud': is_fraud,
                'risk_level': get_risk_level(fraud_prob),
                'recommended_action': get_action(is_fraud, fraud_prob)
            })
        
        # Update metrics
        latency = (time.time() - start_time) * 1000
        models_cache['fraud_model']['predictions_total'] += len(request.transactions)
        models_cache['fraud_model']['predictions_successful'] += len(request.transactions)
        models_cache['fraud_model']['avg_latency'] = latency
        
        fraud_score = fraud_count / len(request.transactions) if request.transactions else 0
        
        return {
            "predictions": predictions,
            "processed_at": datetime.now(),
            "fraud_detection_score": float(fraud_score)
        }
        
    except Exception as e:
        logger.error(f"Fraud detection failed: {str(e)}")
        models_cache['fraud_model']['predictions_total'] += len(request.transactions)
        raise HTTPException(status_code=500, detail=str(e))

def get_risk_level(fraud_prob: float) -> str:
    """Determine risk level"""
    if fraud_prob > 0.8:
        return 'CRITICAL'
    elif fraud_prob > 0.6:
        return 'HIGH'
    elif fraud_prob > 0.4:
        return 'MEDIUM'
    else:
        return 'LOW'

def get_action(is_fraud: bool, fraud_prob: float) -> str:
    """Recommend action"""
    if is_fraud:
        return 'BLOCK_IMMEDIATELY' if fraud_prob > 0.9 else 'REQUIRE_VERIFICATION'
    return 'APPROVE'

# ==================== Demand Forecasting Endpoints ====================

@app.post("/demand/forecast", response_model=DemandForecastResponse)
async def forecast_demand(request: DemandForecastRequest):
    """
    Forecast movie ticket demand
    
    Args:
        request: DemandForecastRequest with movie_id and forecast days
        
    Returns:
        Demand forecast with confidence intervals
    """
    try:
        start_time = time.time()
        
        logger.info(f"Forecasting demand for movie {request.movie_id} ({request.forecast_days} days)")
        
        # Mock forecast
        base_demand = np.random.uniform(100, 500)
        forecast = [
            base_demand + np.random.normal(0, base_demand * 0.1)
            for _ in range(request.forecast_days)
        ]
        forecast = [max(f, 0) for f in forecast]
        
        lower_bound = [f * 0.85 for f in forecast] if request.include_confidence_interval else None
        upper_bound = [f * 1.15 for f in forecast] if request.include_confidence_interval else None
        
        # Update metrics
        latency = (time.time() - start_time) * 1000
        models_cache['demand_model']['predictions_total'] += 1
        models_cache['demand_model']['predictions_successful'] += 1
        models_cache['demand_model']['avg_latency'] = latency
        
        return {
            "movie_id": request.movie_id,
            "forecast": forecast,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "mean_forecast": float(np.mean(forecast)),
            "forecast_generated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Demand forecast failed: {str(e)}")
        models_cache['demand_model']['predictions_total'] += 1
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Batch Prediction Endpoint ====================

@app.post("/batch/predict", response_model=BatchPredictionResponse)
async def batch_predict(request: BatchPredictionRequest, background_tasks: BackgroundTasks):
    """
    Submit batch prediction job
    
    Args:
        request: Batch prediction request with data
        
    Returns:
        Batch job status
    """
    logger.info(f"Submitting batch job {request.batch_id} ({request.predictions_type}): {len(request.data)} records")
    
    # Add background task
    background_tasks.add_task(process_batch_predictions, request)
    
    return {
        "batch_id": request.batch_id,
        "status": "processing",
        "total_records": len(request.data),
        "processed_records": 0,
        "created_at": datetime.now()
    }

async def process_batch_predictions(request: BatchPredictionRequest):
    """Process batch predictions in background"""
    logger.info(f"Processing batch {request.batch_id}...")
    # Simulate batch processing
    await asyncio.sleep(5)
    logger.info(f"Batch {request.batch_id} completed!")

# ==================== Model Management Endpoints ====================

@app.get("/models/info")
async def get_models_info():
    """Get information about loaded models"""
    return {
        "models": list(models_cache.keys()),
        "count": len(models_cache),
        "timestamp": datetime.now()
    }

@app.post("/models/{model_name}/reload")
async def reload_model(model_name: str):
    """Reload a specific model"""
    if model_name not in models_cache:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    logger.info(f"Reloading model {model_name}...")
    # Simulate model reload
    models_cache[model_name]['status'] = 'reloading'
    await asyncio.sleep(2)
    models_cache[model_name]['status'] = 'loaded'
    
    return {
        "model_name": model_name,
        "status": "reloaded",
        "timestamp": datetime.now()
    }

# ==================== Monitoring & Logging ====================

@app.get("/metrics")
async def get_metrics():
    """Get overall API metrics"""
    total_predictions = sum(m['predictions_total'] for m in models_cache.values())
    total_successful = sum(m['predictions_successful'] for m in models_cache.values())
    
    return {
        "total_predictions": total_predictions,
        "total_successful": total_successful,
        "models_count": len(models_cache),
        "avg_latency_ms": np.mean([m['avg_latency'] for m in models_cache.values()]) if models_cache else 0,
        "timestamp": datetime.now()
    }

# ==================== Root Endpoint ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Movie Ticketing ML Model Serving API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "models": "/models/status",
            "recommendations": "/recommendations/predict",
            "fraud_detection": "/fraud/predict",
            "demand_forecast": "/demand/forecast",
            "batch_predict": "/batch/predict",
            "metrics": "/metrics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Model Serving API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
