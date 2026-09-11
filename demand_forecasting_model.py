"""
Demand Forecasting System
Module 12: Machine Learning - Time Series Forecasting
Covers: LSTM, time series data, feature engineering, seasonality handling
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
import logging
from typing import Tuple, Dict, List
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemandForecastingModel:
    """
    LSTM-based demand forecasting system for movie ticket sales
    Features:
    - Time series prediction with LSTM
    - Seasonality detection and handling
    - Multi-step ahead forecasting
    - Uncertainty quantification
    """
    
    def __init__(self, lookback_period: int = 30, forecast_horizon: int = 7):
        """
        Initialize demand forecasting model
        
        Args:
            lookback_period: Number of historical days to use for prediction
            forecast_horizon: Number of days ahead to forecast
        """
        self.lookback_period = lookback_period
        self.forecast_horizon = forecast_horizon
        self.model = None
        self.scaler = MinMaxScaler()
        self.history = None
        
    def create_features(self, demand_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time series features from demand data
        
        Args:
            demand_df: DataFrame with columns [date, demand, movie_id]
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Creating time series features...")
        
        df = demand_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # 1. Moving averages
        df['ma_7'] = df['demand'].rolling(window=7, min_periods=1).mean()
        df['ma_30'] = df['demand'].rolling(window=30, min_periods=1).mean()
        
        # 2. Seasonal decomposition features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        
        # 3. Lag features
        for lag in [1, 7, 14, 30]:
            df[f'lag_{lag}'] = df['demand'].shift(lag)
        
        # 4. Rolling statistics
        df['rolling_std_7'] = df['demand'].rolling(window=7, min_periods=1).std()
        df['rolling_min_7'] = df['demand'].rolling(window=7, min_periods=1).min()
        df['rolling_max_7'] = df['demand'].rolling(window=7, min_periods=1).max()
        
        # 5. Trend
        df['trend'] = range(len(df))
        
        # 6. Weekend indicator
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Fill NaN values from lag features
        df = df.fillna(method='bfill')
        
        logger.info(f"Created {len(df.columns) - 2} features")
        return df
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training sequences for LSTM
        
        Args:
            data: Normalized demand data
            
        Returns:
            X, y arrays for training
        """
        X, y = [], []
        
        for i in range(len(data) - self.lookback_period - self.forecast_horizon + 1):
            X.append(data[i:i + self.lookback_period])
            y.append(data[i + self.lookback_period:i + self.lookback_period + self.forecast_horizon])
        
        return np.array(X), np.array(y)
    
    def build_model(self, n_features: int) -> models.Sequential:
        """
        Build LSTM model for demand forecasting
        
        Args:
            n_features: Number of input features
            
        Returns:
            Compiled Keras model
        """
        logger.info("Building LSTM model...")
        
        model = models.Sequential([
            # First LSTM layer
            layers.LSTM(
                units=64,
                return_sequences=True,
                activation='relu',
                input_shape=(self.lookback_period, n_features)
            ),
            layers.Dropout(0.2),
            
            # Second LSTM layer
            layers.LSTM(
                units=32,
                return_sequences=False,
                activation='relu'
            ),
            layers.Dropout(0.2),
            
            # Dense layers
            layers.Dense(units=16, activation='relu'),
            layers.Dropout(0.1),
            layers.Dense(units=self.forecast_horizon)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info(model.summary())
        return model
    
    def train(self, demand_df: pd.DataFrame, epochs: int = 50, batch_size: int = 32):
        """
        Train demand forecasting model
        
        Args:
            demand_df: DataFrame with demand data
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        logger.info("Training demand forecasting model...")
        
        # Create features
        df = self.create_features(demand_df)
        
        # Prepare data
        demand_data = df['demand'].values.reshape(-1, 1)
        
        # Normalize data
        demand_scaled = self.scaler.fit_transform(demand_data)
        
        # Prepare sequences
        X, y = self.prepare_sequences(demand_scaled)
        
        logger.info(f"Training set shape: X={X.shape}, y={y.shape}")
        
        # Split into train/validation
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Build and train model
        self.model = self.build_model(X_train.shape[2])
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                )
            ]
        )
        
        # Evaluate
        logger.info("Evaluating model...")
        self._evaluate(X_val, y_val)
        
        logger.info("Training complete!")
    
    def _evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate model performance"""
        y_pred = self.model.predict(X_test)
        
        # Inverse transform to original scale
        y_test_rescaled = self.scaler.inverse_transform(y_test.reshape(-1, 1)).reshape(y_test.shape)
        y_pred_rescaled = self.scaler.inverse_transform(y_pred.reshape(-1, 1)).reshape(y_pred.shape)
        
        # Calculate metrics
        mse = mean_squared_error(y_test_rescaled, y_pred_rescaled)
        mae = mean_absolute_error(y_test_rescaled, y_pred_rescaled)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test_rescaled, y_pred_rescaled)
        mape = np.mean(np.abs((y_test_rescaled - y_pred_rescaled) / y_test_rescaled)) * 100
        
        logger.info(f"Evaluation Metrics:")
        logger.info(f"  RMSE: {rmse:.4f}")
        logger.info(f"  MAE: {mae:.4f}")
        logger.info(f"  R²: {r2:.4f}")
        logger.info(f"  MAPE: {mape:.2f}%")
    
    def forecast(self, historical_data: np.ndarray, steps: int = None) -> Dict:
        """
        Forecast future demand
        
        Args:
            historical_data: Recent historical demand data
            steps: Number of days to forecast (default: forecast_horizon)
            
        Returns:
            Dictionary with forecast and statistics
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if steps is None:
            steps = self.forecast_horizon
        
        # Prepare input
        historical_normalized = self.scaler.transform(
            historical_data[-self.lookback_period:].reshape(-1, 1)
        )
        
        # Make prediction
        forecast_normalized = self.model.predict(
            historical_normalized.reshape(1, self.lookback_period, 1),
            verbose=0
        )
        
        # Inverse transform
        forecast = self.scaler.inverse_transform(
            forecast_normalized.reshape(-1, 1)
        ).flatten()
        
        # Calculate uncertainty bounds
        std_error = np.std(forecast_normalized)
        lower_bound = self.scaler.inverse_transform(
            (forecast_normalized - 1.96 * std_error).reshape(-1, 1)
        ).flatten()
        upper_bound = self.scaler.inverse_transform(
            (forecast_normalized + 1.96 * std_error).reshape(-1, 1)
        ).flatten()
        
        # Ensure non-negative values
        forecast = np.maximum(forecast, 0)
        lower_bound = np.maximum(lower_bound, 0)
        upper_bound = np.maximum(upper_bound, 0)
        
        result = {
            'forecast': forecast[:steps].tolist(),
            'lower_bound': lower_bound[:steps].tolist(),
            'upper_bound': upper_bound[:steps].tolist(),
            'mean_forecast': float(np.mean(forecast[:steps])),
            'confidence_interval': 0.95
        }
        
        return result
    
    def predict_with_features(self, demand_df: pd.DataFrame) -> List[Dict]:
        """
        Predict demand with engineered features
        
        Args:
            demand_df: DataFrame with demand data
            
        Returns:
            List of predictions
        """
        df = self.create_features(demand_df)
        
        predictions = []
        for idx in range(len(df) - self.lookback_period - self.forecast_horizon + 1):
            window = df.iloc[idx:idx + self.lookback_period]
            actual = df.iloc[idx + self.lookback_period:idx + self.lookback_period + self.forecast_horizon]
            
            # Get forecast
            historical_data = window['demand'].values
            forecast_result = self.forecast(historical_data)
            
            predictions.append({
                'period': window.iloc[-1]['date'],
                'forecast': forecast_result['forecast'],
                'lower_bound': forecast_result['lower_bound'],
                'upper_bound': forecast_result['upper_bound'],
                'mean_forecast': forecast_result['mean_forecast'],
                'actual_next_7': actual['demand'].tolist() if len(actual) > 0 else None
            })
        
        return predictions
    
    def save(self, model_path: str, scaler_path: str):
        """Save model and scaler"""
        if self.model:
            self.model.save(model_path)
            logger.info(f"Model saved to {model_path}")
        
        import joblib
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Scaler saved to {scaler_path}")
    
    @classmethod
    def load(cls, model_path: str, scaler_path: str, lookback: int = 30, horizon: int = 7):
        """Load model and scaler"""
        instance = cls(lookback_period=lookback, forecast_horizon=horizon)
        instance.model = keras.models.load_model(model_path)
        
        import joblib
        instance.scaler = joblib.load(scaler_path)
        logger.info(f"Model loaded from {model_path}")
        return instance


# Example usage
if __name__ == "__main__":
    # Create synthetic demand data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=365, freq='D')
    
    # Generate demand with trend and seasonality
    trend = np.linspace(100, 150, 365)
    seasonality = 30 * np.sin(np.arange(365) * 2 * np.pi / 365)
    noise = np.random.normal(0, 10, 365)
    demand = trend + seasonality + noise
    demand = np.maximum(demand, 0)  # Ensure non-negative
    
    demand_df = pd.DataFrame({
        'date': dates,
        'demand': demand,
        'movie_id': np.random.randint(1, 50, 365)
    })
    
    # Train model
    logger.info("Starting demand forecasting...")
    model = DemandForecastingModel(lookback_period=30, forecast_horizon=7)
    model.train(demand_df, epochs=20, batch_size=32)
    
    # Make forecast
    recent_demand = demand_df.tail(30)['demand'].values
    forecast = model.forecast(recent_demand)
    
    print("\n7-Day Demand Forecast:")
    print(f"Forecast: {[f'{val:.1f}' for val in forecast['forecast']]}")
    print(f"Mean: {forecast['mean_forecast']:.1f}")
    print(f"Lower Bound (95% CI): {[f'{val:.1f}' for val in forecast['lower_bound']]}")
    print(f"Upper Bound (95% CI): {[f'{val:.1f}' for val in forecast['upper_bound']]}")
    
    # Save model
    model.save(
        '/mnt/user-data/outputs/demand_forecasting_model.h5',
        '/mnt/user-data/outputs/demand_scaler.pkl'
    )
