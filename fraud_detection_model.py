"""
Fraud Detection System
Module 12: Machine Learning - Fraud Detection Model
Covers: Classification, feature engineering, model evaluation, real-time scoring
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    precision_recall_curve, f1_score
)
import xgboost as xgb
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDetectionModel:
    """
    Real-time fraud detection system using XGBoost
    Features:
    - Transaction amount anomaly detection
    - Time-based patterns
    - User behavior analysis
    - Device fingerprinting
    """
    
    def __init__(self, threshold: float = 0.5):
        """
        Initialize fraud detection model
        
        Args:
            threshold: Prediction threshold for fraud classification (default: 0.5)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.threshold = threshold
        self.feature_names = None
        self.feature_importance = None
        
    def create_features(self, transaction_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create fraud detection features from transaction data
        
        Args:
            transaction_df: DataFrame with raw transaction data
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Creating fraud detection features...")
        
        df = transaction_df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 1. Transaction amount features
        df['amount'] = df['amount'].astype(float)
        df['amount_log'] = np.log1p(df['amount'])
        df['amount_zscore'] = np.abs(
            (df['amount'] - df['amount'].mean()) / df['amount'].std()
        )
        
        # 2. Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = df['hour'].isin([0, 1, 2, 3, 4, 5]).astype(int)
        
        # 3. User behavior features
        user_stats = df.groupby('user_id').agg({
            'amount': ['mean', 'std', 'min', 'max', 'count'],
            'timestamp': 'count'
        }).flatten()
        
        user_stats_dict = {}
        for idx, (user_id, row) in enumerate(df.groupby('user_id')):
            user_amount_mean = df[df['user_id'] == user_id]['amount'].mean()
            user_amount_std = df[df['user_id'] == user_id]['amount'].std()
            user_amount_max = df[df['user_id'] == user_id]['amount'].max()
            
            user_stats_dict[user_id] = {
                'avg_amount': user_amount_mean,
                'std_amount': user_amount_std,
                'max_amount': user_amount_max,
                'num_transactions': len(df[df['user_id'] == user_id])
            }
        
        df['user_avg_amount'] = df['user_id'].map(
            lambda x: user_stats_dict[x]['avg_amount']
        )
        df['user_std_amount'] = df['user_id'].map(
            lambda x: user_stats_dict[x]['std_amount']
        )
        df['user_max_amount'] = df['user_id'].map(
            lambda x: user_stats_dict[x]['max_amount']
        )
        df['amount_vs_user_avg'] = df['amount'] / (df['user_avg_amount'] + 1)
        
        # 4. Velocity features (transactions per hour/day)
        df['transactions_per_hour'] = df.groupby(
            [df['user_id'], df['timestamp'].dt.floor('H')]
        ).size().reset_index(drop=True).groupby(df['user_id']).transform('mean')
        
        # 5. Device/Location features (simulate)
        df['device_type_code'] = pd.factorize(df.get('device_type', 'unknown'))[0]
        df['location_code'] = pd.factorize(df.get('location', 'unknown'))[0]
        df['device_location_change'] = df.groupby('user_id')[
            ['device_type_code', 'location_code']
        ].apply(lambda x: (x.iloc[:, 0] != x.iloc[:, 0].shift()).sum()).values
        
        # 6. Historical fraud probability
        if 'is_fraud' in df.columns:
            fraud_by_user = df.groupby('user_id')['is_fraud'].mean()
            df['user_fraud_rate'] = df['user_id'].map(fraud_by_user).fillna(0)
        
        # Select feature columns
        feature_cols = [
            'amount', 'amount_log', 'amount_zscore',
            'hour', 'day_of_week', 'is_weekend', 'is_night',
            'user_avg_amount', 'user_std_amount', 'user_max_amount',
            'amount_vs_user_avg', 'transactions_per_hour',
            'device_type_code', 'location_code', 'device_location_change'
        ]
        
        # Add user fraud rate if available
        if 'user_fraud_rate' in df.columns:
            feature_cols.append('user_fraud_rate')
        
        self.feature_names = feature_cols
        
        logger.info(f"Created {len(feature_cols)} features")
        return df
    
    def train(self, transaction_df: pd.DataFrame, test_size: float = 0.2):
        """
        Train fraud detection model
        
        Args:
            transaction_df: DataFrame with transaction data and 'is_fraud' label
            test_size: Proportion of data to use for testing
        """
        logger.info("Training fraud detection model...")
        
        # Create features
        df = self.create_features(transaction_df)
        
        # Prepare data
        X = df[self.feature_names].fillna(0)
        y = df['is_fraud']
        
        # Handle class imbalance
        fraud_count = y.sum()
        normal_count = len(y) - fraud_count
        scale_pos_weight = normal_count / fraud_count if fraud_count > 0 else 1
        
        logger.info(f"Class balance: {fraud_count} fraud, {normal_count} normal "
                   f"(ratio: {scale_pos_weight:.2f})")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        logger.info("Training XGBoost classifier...")
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            eval_metric='logloss'
        )
        
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Store feature importance
        self.feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Evaluate
        logger.info("Evaluating model...")
        self._evaluate(X_test_scaled, y_test)
        
        logger.info("Training complete!")
    
    def _evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Classification metrics
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        # ROC-AUC score
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        logger.info(f"ROC-AUC Score: {roc_auc:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        logger.info(f"Confusion Matrix:\n{cm}")
        
        # Feature importance
        logger.info("\nTop 10 Important Features:")
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for feature, importance in sorted_features[:10]:
            logger.info(f"  {feature}: {importance:.4f}")
    
    def predict(self, transaction_df: pd.DataFrame) -> List[Dict]:
        """
        Predict fraud probability for transactions
        
        Args:
            transaction_df: DataFrame with transaction data
            
        Returns:
            List of predictions with fraud scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create features
        df = self.create_features(transaction_df)
        X = df[self.feature_names].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict_proba(X_scaled)[:, 1]
        
        # Prepare results
        results = []
        for idx, (_, row) in enumerate(transaction_df.iterrows()):
            fraud_prob = float(predictions[idx])
            is_fraud = fraud_prob > self.threshold
            
            results.append({
                'transaction_id': row.get('transaction_id', idx),
                'user_id': row['user_id'],
                'amount': row['amount'],
                'timestamp': row['timestamp'],
                'fraud_probability': fraud_prob,
                'is_fraud': is_fraud,
                'risk_level': self._get_risk_level(fraud_prob),
                'recommended_action': self._get_action(is_fraud, fraud_prob)
            })
        
        return results
    
    def _get_risk_level(self, fraud_prob: float) -> str:
        """Determine risk level based on fraud probability"""
        if fraud_prob > 0.8:
            return 'CRITICAL'
        elif fraud_prob > 0.6:
            return 'HIGH'
        elif fraud_prob > 0.4:
            return 'MEDIUM'
        elif fraud_prob > 0.2:
            return 'LOW'
        else:
            return 'NORMAL'
    
    def _get_action(self, is_fraud: bool, fraud_prob: float) -> str:
        """Recommend action based on fraud prediction"""
        if is_fraud:
            if fraud_prob > 0.9:
                return 'BLOCK_IMMEDIATELY'
            elif fraud_prob > 0.7:
                return 'REQUIRE_VERIFICATION'
            else:
                return 'MONITOR_CLOSELY'
        else:
            return 'APPROVE'
    
    def save(self, model_path: str, scaler_path: str):
        """Save model and scaler"""
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Scaler saved to {scaler_path}")
    
    @classmethod
    def load(cls, model_path: str, scaler_path: str):
        """Load model and scaler"""
        instance = cls()
        instance.model = joblib.load(model_path)
        instance.scaler = joblib.load(scaler_path)
        logger.info(f"Model loaded from {model_path}")
        logger.info(f"Scaler loaded from {scaler_path}")
        return instance


# Example usage
if __name__ == "__main__":
    # Create synthetic fraud data
    np.random.seed(42)
    n_transactions = 10000
    
    normal_transactions = pd.DataFrame({
        'transaction_id': range(1, n_transactions + 1),
        'user_id': np.random.randint(1, 1001, n_transactions),
        'amount': np.random.lognormal(4, 1.5, n_transactions),
        'timestamp': pd.date_range('2024-01-01', periods=n_transactions, freq='min'),
        'device_type': np.random.choice(['mobile', 'web', 'app'], n_transactions),
        'location': np.random.choice(['US', 'EU', 'Asia'], n_transactions),
        'is_fraud': 0
    })
    
    # Add some fraudulent transactions
    fraud_amount = int(n_transactions * 0.05)  # 5% fraud rate
    fraud_transactions = pd.DataFrame({
        'transaction_id': range(n_transactions + 1, n_transactions + fraud_amount + 1),
        'user_id': np.random.randint(1, 1001, fraud_amount),
        'amount': np.random.lognormal(6, 1.5, fraud_amount),  # Larger amounts
        'timestamp': pd.date_range('2024-01-01', periods=fraud_amount, freq='5min'),
        'device_type': np.random.choice(['mobile', 'web'], fraud_amount),
        'location': np.random.choice(['Unknown', 'VPN'], fraud_amount),
        'is_fraud': 1
    })
    
    transactions_df = pd.concat([normal_transactions, fraud_transactions], ignore_index=True)
    transactions_df = transactions_df.sample(frac=1).reset_index(drop=True)
    
    # Train model
    fraud_model = FraudDetectionModel(threshold=0.5)
    fraud_model.train(transactions_df)
    
    # Make predictions
    test_transactions = transactions_df.head(100)
    predictions = fraud_model.predict(test_transactions)
    
    print("\nSample Predictions:")
    for pred in predictions[:5]:
        print(f"Transaction {pred['transaction_id']}: "
              f"Fraud Prob={pred['fraud_probability']:.2%}, "
              f"Risk={pred['risk_level']}, "
              f"Action={pred['recommended_action']}")
    
    # Save model
    fraud_model.save(
        '/mnt/user-data/outputs/fraud_model.pkl',
        '/mnt/user-data/outputs/fraud_scaler.pkl'
    )
