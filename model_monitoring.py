"""
Production AI System Monitoring
Module 18: Production AI Systems - Model Drift Detection & Performance Monitoring
Covers: Data drift, model drift, performance degradation, retraining triggers
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging
from scipy import stats
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Drift Detection ====================

class DriftDetector(ABC):
    """Abstract base class for drift detection"""
    
    @abstractmethod
    def calculate_drift(self, current: np.ndarray, reference: np.ndarray) -> float:
        pass


class KolmogorovSmirnovDriftDetector(DriftDetector):
    """
    Kolmogorov-Smirnov test for data drift
    Detects distribution changes
    """
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def calculate_drift(self, current: np.ndarray, reference: np.ndarray) -> float:
        """
        Calculate KS statistic
        Returns: KS statistic (0-1, higher = more drift)
        """
        statistic, p_value = stats.ks_2samp(reference, current)
        return float(statistic)


class JensenShannonDriftDetector(DriftDetector):
    """
    Jensen-Shannon divergence for distribution comparison
    More stable than KS test for histograms
    """
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def calculate_drift(self, current: np.ndarray, reference: np.ndarray) -> float:
        """
        Calculate Jensen-Shannon divergence
        Returns: JS divergence (0-1, higher = more drift)
        """
        # Create histograms
        min_val = min(reference.min(), current.min())
        max_val = max(reference.max(), current.max())
        
        hist_ref, _ = np.histogram(reference, bins=20, range=(min_val, max_val))
        hist_curr, _ = np.histogram(current, bins=20, range=(min_val, max_val))
        
        # Normalize
        hist_ref = hist_ref / hist_ref.sum()
        hist_curr = hist_curr / hist_curr.sum()
        
        # Jensen-Shannon divergence
        js_div = stats.entropy(hist_ref, hist_curr)
        return float(js_div)


class HellingerDriftDetector(DriftDetector):
    """
    Hellinger distance for probability distributions
    """
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def calculate_drift(self, current: np.ndarray, reference: np.ndarray) -> float:
        """Calculate Hellinger distance"""
        min_val = min(reference.min(), current.min())
        max_val = max(reference.max(), current.max())
        
        hist_ref, _ = np.histogram(reference, bins=20, range=(min_val, max_val))
        hist_curr, _ = np.histogram(current, bins=20, range=(min_val, max_val))
        
        # Normalize
        hist_ref = hist_ref / hist_ref.sum()
        hist_curr = hist_curr / hist_curr.sum()
        
        # Hellinger distance
        hellinger = np.sqrt(np.sum((np.sqrt(hist_ref) - np.sqrt(hist_curr)) ** 2) / 2)
        return float(hellinger)


# ==================== Data Drift Monitor ====================

class DataDriftMonitor:
    """
    Monitor for data drift (distribution changes in input features)
    """
    
    def __init__(self, reference_data: pd.DataFrame, drift_detector: DriftDetector = None):
        """
        Initialize drift monitor
        
        Args:
            reference_data: Baseline/reference data distribution
            drift_detector: Drift detection algorithm
        """
        self.reference_data = reference_data
        self.drift_detector = drift_detector or KolmogorovSmirnovDriftDetector()
        self.drift_history = []
    
    def check_drift(self, current_data: pd.DataFrame, alert_threshold: float = 0.3) -> Dict[str, Any]:
        """
        Check for data drift across all features
        
        Args:
            current_data: Current data sample
            alert_threshold: Threshold for drift alert
            
        Returns:
            Dictionary with drift scores for each feature
        """
        logger.info("Checking for data drift...")
        
        drift_results = {
            'timestamp': datetime.now(),
            'features': {},
            'max_drift': 0,
            'drift_features': [],
            'status': 'HEALTHY'
        }
        
        for column in self.reference_data.columns:
            if column not in current_data.columns:
                continue
            
            # Skip categorical columns for now
            if not pd.api.types.is_numeric_dtype(self.reference_data[column]):
                continue
            
            # Calculate drift
            ref_data = self.reference_data[column].values
            curr_data = current_data[column].values
            
            drift_score = self.drift_detector.calculate_drift(curr_data, ref_data)
            
            drift_results['features'][column] = {
                'drift_score': drift_score,
                'reference_mean': float(ref_data.mean()),
                'reference_std': float(ref_data.std()),
                'current_mean': float(curr_data.mean()),
                'current_std': float(curr_data.std()),
                'alert': drift_score > alert_threshold
            }
            
            if drift_score > drift_results['max_drift']:
                drift_results['max_drift'] = drift_score
            
            if drift_score > alert_threshold:
                drift_results['drift_features'].append(column)
                logger.warning(f"Data drift detected in {column}: {drift_score:.4f}")
        
        # Determine status
        if len(drift_results['drift_features']) > 0:
            drift_results['status'] = 'DRIFT_DETECTED'
        
        self.drift_history.append(drift_results)
        
        return drift_results


# ==================== Model Performance Monitor ====================

class ModelPerformanceMonitor:
    """
    Monitor model performance over time
    Detects performance degradation
    """
    
    def __init__(self, baseline_metrics: Dict[str, float]):
        """
        Initialize performance monitor
        
        Args:
            baseline_metrics: Baseline model metrics (e.g., accuracy, precision)
        """
        self.baseline_metrics = baseline_metrics
        self.performance_history = []
        self.alerts = []
    
    def log_metrics(
        self,
        current_metrics: Dict[str, float],
        predictions: np.ndarray,
        actuals: np.ndarray,
        degradation_threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Log current metrics and check for degradation
        
        Args:
            current_metrics: Current model metrics
            predictions: Model predictions
            actuals: Ground truth labels
            degradation_threshold: Performance degradation threshold
            
        Returns:
            Performance report with alerts
        """
        logger.info("Checking model performance...")
        
        report = {
            'timestamp': datetime.now(),
            'current_metrics': current_metrics,
            'degradation_detected': False,
            'degraded_metrics': [],
            'alerts': []
        }
        
        # Check for degradation
        for metric_name, baseline_value in self.baseline_metrics.items():
            if metric_name not in current_metrics:
                continue
            
            current_value = current_metrics[metric_name]
            
            # Calculate degradation
            if baseline_value > 0:
                degradation = abs(current_value - baseline_value) / baseline_value
            else:
                degradation = abs(current_value - baseline_value)
            
            if degradation > degradation_threshold:
                logger.warning(
                    f"Performance degradation detected in {metric_name}: "
                    f"{baseline_value:.4f} → {current_value:.4f} ({degradation:.2%})"
                )
                report['degradation_detected'] = True
                report['degraded_metrics'].append({
                    'metric': metric_name,
                    'baseline': baseline_value,
                    'current': current_value,
                    'degradation': degradation
                })
                
                alert = {
                    'type': 'PERFORMANCE_DEGRADATION',
                    'metric': metric_name,
                    'severity': 'HIGH' if degradation > 0.1 else 'MEDIUM',
                    'timestamp': datetime.now()
                }
                report['alerts'].append(alert)
                self.alerts.append(alert)
        
        # Calculate prediction statistics
        if len(predictions) > 0 and len(actuals) > 0:
            report['prediction_stats'] = {
                'mean_confidence': float(np.mean(predictions)),
                'std_confidence': float(np.std(predictions)),
                'min_confidence': float(np.min(predictions)),
                'max_confidence': float(np.max(predictions))
            }
        
        self.performance_history.append(report)
        
        return report
    
    def should_retrain(self) -> bool:
        """Determine if model should be retrained"""
        if not self.alerts:
            return False
        
        # Check recent alerts
        recent_alerts = [a for a in self.alerts 
                        if (datetime.now() - a['timestamp']).days < 7]
        
        return len(recent_alerts) > 3  # Retrain if 3+ alerts in 7 days


# ==================== Model Drift Detector ====================

class ModelDriftDetector:
    """
    Detect model drift (prediction distribution changes)
    """
    
    def __init__(self, reference_predictions: np.ndarray):
        self.reference_predictions = reference_predictions
        self.prediction_history = []
    
    def check_prediction_drift(
        self,
        current_predictions: np.ndarray,
        threshold: float = 0.2
    ) -> Dict[str, Any]:
        """
        Check if prediction distribution has changed
        
        Args:
            current_predictions: Current model predictions
            threshold: Drift threshold
            
        Returns:
            Drift report
        """
        logger.info("Checking for model prediction drift...")
        
        # Calculate statistics
        ref_mean = np.mean(self.reference_predictions)
        ref_std = np.std(self.reference_predictions)
        curr_mean = np.mean(current_predictions)
        curr_std = np.std(current_predictions)
        
        # Z-score based drift
        mean_drift = abs(curr_mean - ref_mean) / (ref_std + 1e-8)
        std_drift = abs(curr_std - ref_std) / (ref_std + 1e-8)
        
        report = {
            'timestamp': datetime.now(),
            'reference_mean': float(ref_mean),
            'reference_std': float(ref_std),
            'current_mean': float(curr_mean),
            'current_std': float(curr_std),
            'mean_drift_zscore': float(mean_drift),
            'std_drift_zscore': float(std_drift),
            'drift_detected': max(mean_drift, std_drift) > threshold
        }
        
        if report['drift_detected']:
            logger.warning(f"Model drift detected! Mean Z-score: {mean_drift:.2f}, Std Z-score: {std_drift:.2f}")
        
        self.prediction_history.append(report)
        
        return report


# ==================== Comprehensive Monitoring System ====================

class ProductionAIMonitor:
    """
    Complete monitoring system for production AI models
    """
    
    def __init__(
        self,
        reference_data: pd.DataFrame,
        baseline_metrics: Dict[str, float],
        baseline_predictions: np.ndarray
    ):
        self.data_drift_monitor = DataDriftMonitor(reference_data)
        self.performance_monitor = ModelPerformanceMonitor(baseline_metrics)
        self.prediction_drift_monitor = ModelDriftDetector(baseline_predictions)
        
        self.monitoring_reports = []
    
    def monitor_batch(
        self,
        current_data: pd.DataFrame,
        current_metrics: Dict[str, float],
        predictions: np.ndarray,
        actuals: np.ndarray
    ) -> Dict[str, Any]:
        """
        Run complete monitoring on batch of data
        
        Args:
            current_data: Current feature data
            current_metrics: Model performance metrics
            predictions: Model predictions
            actuals: Ground truth labels
            
        Returns:
            Comprehensive monitoring report
        """
        logger.info("=" * 80)
        logger.info("PRODUCTION AI MONITORING - COMPREHENSIVE CHECK")
        logger.info("=" * 80)
        
        report = {
            'timestamp': datetime.now(),
            'data_drift': self.data_drift_monitor.check_drift(current_data),
            'performance': self.performance_monitor.log_metrics(
                current_metrics, predictions, actuals
            ),
            'prediction_drift': self.prediction_drift_monitor.check_prediction_drift(predictions),
            'actions_required': []
        }
        
        # Determine actions
        if report['data_drift']['status'] == 'DRIFT_DETECTED':
            report['actions_required'].append({
                'action': 'INVESTIGATE_DATA_QUALITY',
                'severity': 'HIGH',
                'description': 'Data distribution has shifted significantly'
            })
        
        if report['performance']['degradation_detected']:
            report['actions_required'].append({
                'action': 'CHECK_MODEL_PERFORMANCE',
                'severity': 'HIGH',
                'description': 'Model performance has degraded'
            })
        
        if report['prediction_drift']['drift_detected']:
            report['actions_required'].append({
                'action': 'RETRAIN_MODEL',
                'severity': 'MEDIUM',
                'description': 'Prediction distribution has changed'
            })
        
        # Should retrain?
        if self.performance_monitor.should_retrain():
            report['actions_required'].append({
                'action': 'TRIGGER_RETRAINING',
                'severity': 'HIGH',
                'description': 'Multiple performance issues detected'
            })
        
        # Overall status
        if len(report['actions_required']) > 0:
            report['overall_status'] = 'REQUIRES_ATTENTION'
        else:
            report['overall_status'] = 'HEALTHY'
        
        logger.info(f"Overall Status: {report['overall_status']}")
        logger.info(f"Actions Required: {len(report['actions_required'])}")
        
        self.monitoring_reports.append(report)
        
        return report
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        if not self.monitoring_reports:
            return {'status': 'No reports yet'}
        
        latest_report = self.monitoring_reports[-1]
        
        return {
            'latest_timestamp': latest_report['timestamp'],
            'overall_status': latest_report['overall_status'],
            'data_drift_status': latest_report['data_drift']['status'],
            'max_data_drift': latest_report['data_drift']['max_drift'],
            'performance_degradation': latest_report['performance']['degradation_detected'],
            'prediction_drift': latest_report['prediction_drift']['drift_detected'],
            'actions_count': len(latest_report['actions_required']),
            'total_reports': len(self.monitoring_reports)
        }


# ==================== Example Usage ====================

if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    
    # Reference data (training/baseline)
    ref_features = pd.DataFrame({
        'amount': np.random.normal(100, 30, 1000),
        'latency': np.random.normal(50, 10, 1000),
        'success_rate': np.random.normal(0.95, 0.05, 1000)
    })
    
    baseline_metrics = {
        'accuracy': 0.95,
        'precision': 0.92,
        'recall': 0.90,
        'f1_score': 0.91
    }
    
    baseline_predictions = np.random.uniform(0.8, 1.0, 1000)
    
    # Initialize monitor
    monitor = ProductionAIMonitor(ref_features, baseline_metrics, baseline_predictions)
    
    # Simulate production data with drift
    prod_features = pd.DataFrame({
        'amount': np.random.normal(110, 35, 100),  # Shifted mean
        'latency': np.random.normal(45, 15, 100),  # Changed variance
        'success_rate': np.random.normal(0.92, 0.08, 100)  # Degraded
    })
    
    current_metrics = {
        'accuracy': 0.88,  # Degraded
        'precision': 0.85,  # Degraded
        'recall': 0.87,
        'f1_score': 0.86  # Degraded
    }
    
    predictions = np.random.uniform(0.7, 0.95, 100)
    actuals = np.random.randint(0, 2, 100)
    
    # Run monitoring
    report = monitor.monitor_batch(prod_features, current_metrics, predictions, actuals)
    
    # Print summary
    print("\n" + "="*80)
    print("MONITORING SUMMARY")
    print("="*80)
    
    summary = monitor.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
