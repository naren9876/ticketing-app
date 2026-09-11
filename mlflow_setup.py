"""
MLOps Pipeline Setup with MLflow
Module 13: MLOps Fundamentals - Experiment Tracking & Model Registry
Covers: MLflow, experiment tracking, model versioning, artifact storage
"""

import mlflow
from mlflow.models import infer_signature
import numpy as np
import pandas as pd
from datetime import datetime
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLOpsManager:
    """
    MLOps manager for experiment tracking and model registry
    """
    
    def __init__(self, tracking_uri: str = "http://localhost:5000"):
        """
        Initialize MLOps manager
        
        Args:
            tracking_uri: MLflow tracking server URI
        """
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        logger.info(f"MLflow tracking URI: {tracking_uri}")
    
    def start_experiment(self, experiment_name: str):
        """
        Start new experiment
        
        Args:
            experiment_name: Name of the experiment
        """
        # Create experiment if it doesn't exist
        try:
            experiment_id = mlflow.create_experiment(experiment_name)
        except:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            experiment_id = experiment.experiment_id
        
        mlflow.set_experiment(experiment_name)
        logger.info(f"Started experiment: {experiment_name}")
    
    def log_recommendation_experiment(
        self,
        run_name: str,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        model_object: Any,
        test_data: pd.DataFrame
    ):
        """
        Log recommendation model experiment
        
        Args:
            run_name: Name of the run
            params: Model hyperparameters
            metrics: Model performance metrics
            model_object: Trained model object
            test_data: Test data sample for signature
        """
        with mlflow.start_run(run_name=run_name):
            # Log parameters
            for param_name, param_value in params.items():
                mlflow.log_param(param_name, param_value)
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log model
            signature = infer_signature(test_data, metrics)
            mlflow.sklearn.log_model(
                model_object,
                artifact_path="recommendation_model",
                signature=signature,
                registered_model_name="recommendation-model-v1"
            )
            
            # Log additional metadata
            mlflow.log_dict({
                "model_type": "collaborative_filtering",
                "feature_count": test_data.shape[1],
                "training_date": datetime.now().isoformat()
            }, "model_metadata.json")
            
            logger.info(f"Logged recommendation experiment: {run_name}")
    
    def log_fraud_detection_experiment(
        self,
        run_name: str,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        model_object: Any,
        feature_importance: Dict[str, float],
        confusion_matrix: np.ndarray
    ):
        """
        Log fraud detection model experiment
        
        Args:
            run_name: Name of the run
            params: Model hyperparameters
            metrics: Performance metrics
            model_object: Trained XGBoost model
            feature_importance: Feature importance scores
            confusion_matrix: Confusion matrix from test set
        """
        with mlflow.start_run(run_name=run_name):
            # Log parameters
            for param_name, param_value in params.items():
                mlflow.log_param(param_name, param_value)
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log confusion matrix
            mlflow.log_dict({
                "true_negatives": int(confusion_matrix[0, 0]),
                "false_positives": int(confusion_matrix[0, 1]),
                "false_negatives": int(confusion_matrix[1, 0]),
                "true_positives": int(confusion_matrix[1, 1])
            }, "confusion_matrix.json")
            
            # Log feature importance
            mlflow.log_dict(feature_importance, "feature_importance.json")
            
            # Log model
            mlflow.xgboost.log_model(
                model_object,
                artifact_path="fraud_model",
                registered_model_name="fraud-detection-model-v1"
            )
            
            logger.info(f"Logged fraud detection experiment: {run_name}")
    
    def log_demand_forecasting_experiment(
        self,
        run_name: str,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        model_object: Any,
        forecast_sample: Dict[str, Any],
        training_history: Dict[str, Any]
    ):
        """
        Log demand forecasting model experiment
        
        Args:
            run_name: Name of the run
            params: Model hyperparameters
            metrics: Performance metrics
            model_object: Trained LSTM model
            forecast_sample: Sample forecast output
            training_history: Training history (loss, accuracy, etc.)
        """
        with mlflow.start_run(run_name=run_name):
            # Log parameters
            for param_name, param_value in params.items():
                mlflow.log_param(param_name, param_value)
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log training history
            mlflow.log_dict(training_history, "training_history.json")
            
            # Log forecast sample
            mlflow.log_dict(forecast_sample, "forecast_sample.json")
            
            # Log model
            mlflow.keras.log_model(
                model_object,
                artifact_path="demand_model",
                registered_model_name="demand-forecast-model-v1"
            )
            
            logger.info(f"Logged demand forecasting experiment: {run_name}")
    
    def compare_experiments(self, experiment_names: list):
        """
        Compare multiple experiments
        
        Args:
            experiment_names: List of experiment names to compare
        """
        logger.info(f"Comparing experiments: {experiment_names}")
        
        comparison_results = []
        for exp_name in experiment_names:
            experiment = mlflow.get_experiment_by_name(exp_name)
            runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
            
            if len(runs) > 0:
                best_run = runs.sort_values('metrics.rmse').iloc[0]
                comparison_results.append({
                    "experiment": exp_name,
                    "best_run_id": best_run['run_id'],
                    "best_rmse": best_run['metrics.rmse'],
                    "timestamp": best_run['end_time']
                })
        
        return comparison_results
    
    def register_model_version(
        self,
        model_name: str,
        model_uri: str,
        version_description: str,
        metadata: Dict[str, Any]
    ):
        """
        Register model version in model registry
        
        Args:
            model_name: Name of the model
            model_uri: URI of the model artifact
            version_description: Description of the version
            metadata: Additional metadata
        """
        logger.info(f"Registering model version: {model_name}")
        
        # Load model and register
        model_version = mlflow.register_model(
            model_uri=model_uri,
            name=model_name
        )
        
        # Update version description
        mlflow.tracking.MlflowClient().update_model_version(
            name=model_name,
            version=model_version.version,
            description=version_description
        )
        
        # Log metadata
        mlflow.log_dict(metadata, f"{model_name}_metadata.json")
        
        logger.info(f"Registered {model_name} v{model_version.version}")
        return model_version
    
    def transition_model_stage(
        self,
        model_name: str,
        version: int,
        stage: str
    ):
        """
        Transition model to different stage (Staging, Production, Archived)
        
        Args:
            model_name: Model name
            version: Model version
            stage: Target stage
        """
        logger.info(f"Transitioning {model_name} v{version} to {stage}")
        
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        
        logger.info(f"Transitioned {model_name} v{version} to {stage}")


# ==================== Automated Retraining Pipeline ====================

class RetrainingPipeline:
    """
    Automated retraining pipeline triggered by data drift or performance degradation
    """
    
    def __init__(self, mlops_manager: MLOpsManager):
        self.mlops_manager = mlops_manager
    
    def check_data_drift(
        self,
        current_data: pd.DataFrame,
        reference_data: pd.DataFrame,
        threshold: float = 0.3
    ) -> bool:
        """
        Check if data drift exceeds threshold
        
        Args:
            current_data: Current data distribution
            reference_data: Reference/baseline data
            threshold: Drift threshold (Kolmogorov-Smirnov test)
            
        Returns:
            True if drift detected
        """
        from scipy.stats import ks_2samp
        
        logger.info("Checking for data drift...")
        
        drift_detected = False
        for column in current_data.columns:
            if pd.api.types.is_numeric_dtype(current_data[column]):
                statistic, p_value = ks_2samp(
                    reference_data[column],
                    current_data[column]
                )
                
                if statistic > threshold:
                    logger.warning(f"Data drift detected in {column}: {statistic:.4f}")
                    drift_detected = True
        
        return drift_detected
    
    def check_model_performance_degradation(
        self,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float],
        threshold: float = 0.05
    ) -> bool:
        """
        Check if model performance degraded
        
        Args:
            current_metrics: Current model metrics
            baseline_metrics: Baseline/reference metrics
            threshold: Performance degradation threshold
            
        Returns:
            True if degradation detected
        """
        logger.info("Checking for model performance degradation...")
        
        degradation_detected = False
        for metric_name in baseline_metrics:
            if metric_name in current_metrics:
                degradation = (
                    abs(current_metrics[metric_name] - baseline_metrics[metric_name]) /
                    abs(baseline_metrics[metric_name])
                )
                
                if degradation > threshold:
                    logger.warning(
                        f"Performance degradation in {metric_name}: {degradation:.2%}"
                    )
                    degradation_detected = True
        
        return degradation_detected
    
    def trigger_retraining(self, model_name: str, reason: str):
        """
        Trigger model retraining
        
        Args:
            model_name: Model to retrain
            reason: Reason for retraining
        """
        logger.info(f"Triggering retraining for {model_name}: {reason}")
        
        # In production, this would:
        # 1. Fetch new training data
        # 2. Create new training job
        # 3. Log experiment with MLflow
        # 4. Compare with baseline
        # 5. If better, promote to staging/production
        
        mlflow.log_param("retraining_reason", reason)
        mlflow.log_param("retraining_timestamp", datetime.now().isoformat())


# ==================== Example Usage ====================

if __name__ == "__main__":
    # Initialize MLOps manager
    mlops = MLOpsManager(tracking_uri="http://localhost:5000")
    
    # Example: Log recommendation experiment
    mlops.start_experiment("recommendation_model_experiments")
    
    mlops.log_recommendation_experiment(
        run_name="collaborative_filtering_v1",
        params={
            "alpha": 0.6,
            "similarity_metric": "cosine",
            "n_recommendations": 5
        },
        metrics={
            "rmse": 0.85,
            "mae": 0.68,
            "precision@5": 0.72,
            "recall@5": 0.65
        },
        model_object=None,  # In production, pass actual model
        test_data=pd.DataFrame()
    )
    
    # Example: Log fraud detection experiment
    mlops.start_experiment("fraud_detection_experiments")
    
    mlops.log_fraud_detection_experiment(
        run_name="xgboost_v2",
        params={
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1
        },
        metrics={
            "roc_auc": 0.95,
            "precision": 0.88,
            "recall": 0.82,
            "f1_score": 0.85
        },
        model_object=None,
        feature_importance={
            "amount_zscore": 0.25,
            "hour": 0.18,
            "user_avg_amount": 0.15
        },
        confusion_matrix=np.array([[950, 30], [50, 150]])
    )
    
    # Example: Check data drift
    pipeline = RetrainingPipeline(mlops)
    
    # Simulate data
    reference_data = pd.DataFrame({'feature': np.random.normal(0, 1, 1000)})
    current_data = pd.DataFrame({'feature': np.random.normal(0.5, 1, 1000)})  # Shifted distribution
    
    drift_detected = pipeline.check_data_drift(current_data, reference_data)
    if drift_detected:
        pipeline.trigger_retraining("recommendation_model", "data_drift_detected")
    
    logger.info("MLOps setup complete!")
