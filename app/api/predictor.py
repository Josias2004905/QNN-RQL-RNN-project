"""
Prediction Pipeline Module - Core prediction logic
"""

import logging
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from core.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class VolatilityPredictor:
    """Main prediction class for volatility forecasting"""
    
    # Expected feature columns
    FEATURE_COLUMNS = [
        "lag1", "lag2", "vol_lag1", "vol_lag2",
        "ret_abs", "ret_sq", "ma5", "ma20", "std5", "std20"
    ]
    
    QUANTILES = [0.1, 0.5, 0.9]
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.scaler = None
        self.model = None
    
    def initialize(self, model_path: str, scaler_path: str):
        """
        Initialize the predictor with model and scaler paths
        
        Args:
            model_path: Path to the trained model
            scaler_path: Path to the scaler
        """
        self.model_loader.load_model_and_scaler(model_path, scaler_path)
        self.scaler = self.model_loader.get_scaler()
        self.model = self.model_loader.get_model()
        logger.info("Predictor initialized successfully")
    
    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Make a single prediction for volatility quantiles
        
        Args:
            features: Dictionary with feature names and values
        
        Returns:
            Dictionary with predictions for different quantiles
        """
        # Validate input
        self._validate_features(features)
        
        # Create feature array
        feature_array = np.array([features[col] for col in self.FEATURE_COLUMNS]).reshape(1, -1)
        
        # Scale features
        scaled_features = self.scaler.transform(feature_array)
        
        # Make predictions for each quantile
        predictions = {}
        try:
            raw_prediction = self.model.predict(scaled_features, verbose=0)
            predictions['q10'] = float(raw_prediction[0][0])
            predictions['q50'] = float(raw_prediction[0][1]) if raw_prediction.shape[1] > 1 else predictions['q10']
            predictions['q90'] = float(raw_prediction[0][2]) if raw_prediction.shape[1] > 2 else predictions['q10']
            
            logger.info(f"Prediction made successfully: {predictions}")
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
        
        return predictions
    
    def predict_batch(self, features_list: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Make predictions for multiple samples
        
        Args:
            features_list: List of feature dictionaries
        
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        for features in features_list:
            pred = self.predict(features)
            predictions.append(pred)
        return predictions
    
    def predict_from_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions from a DataFrame
        
        Args:
            df: DataFrame with feature columns
        
        Returns:
            DataFrame with original features and predictions
        """
        # Validate columns
        if not all(col in df.columns for col in self.FEATURE_COLUMNS):
            missing = set(self.FEATURE_COLUMNS) - set(df.columns)
            raise ValueError(f"Missing columns: {missing}")
        
        # Extract features
        X = df[self.FEATURE_COLUMNS].values
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        raw_predictions = self.model.predict(X_scaled, verbose=0)
        
        # Create result dataframe
        result_df = df.copy()
        result_df['volatility_q10'] = raw_predictions[:, 0] if raw_predictions.shape[1] > 0 else raw_predictions.flatten()
        result_df['volatility_q50'] = raw_predictions[:, 1] if raw_predictions.shape[1] > 1 else raw_predictions[:, 0]
        result_df['volatility_q90'] = raw_predictions[:, 2] if raw_predictions.shape[1] > 2 else raw_predictions[:, 0]
        
        logger.info(f"Batch prediction completed for {len(df)} samples")
        
        return result_df
    
    def _validate_features(self, features: Dict[str, float]):
        """Validate that all required features are present"""
        missing = set(self.FEATURE_COLUMNS) - set(features.keys())
        if missing:
            raise ValueError(f"Missing features: {missing}")
        
        # Check for NaN values
        for col, val in features.items():
            if np.isnan(float(val)):
                raise ValueError(f"Feature {col} has NaN value")
    
    def get_feature_columns(self) -> List[str]:
        """Get list of required feature columns"""
        return self.FEATURE_COLUMNS.copy()
    
    def get_quantiles(self) -> List[float]:
        """Get list of quantiles"""
        return self.QUANTILES.copy()
