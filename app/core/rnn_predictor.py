"""
RNN Volatility Predictor Service
Handles RNN model loading, preprocessing, and predictions
"""

import logging
import numpy as np
import joblib
import tensorflow as tf
from typing import Dict, List, Tuple, Optional

# Setup logging
logger = logging.getLogger(__name__)

class RNNPredictor:
    """RNN-based volatility prediction service"""
    
    def __init__(self, model_path: str = None, scaler_x_path: str = None, scaler_y_path: str = None):
        """
        Initialize RNN predictor
        
        Args:
            model_path: Path to the RNN model file
            scaler_x_path: Path to the X scaler file  
            scaler_y_path: Path to the y scaler file
        """
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        self.sequence_length = 20
        self.feature_order = ['return', 'lag1', 'lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20']
        
        # Load model and scalers
        self._load_model(model_path, scaler_x_path, scaler_y_path)
    
    def _load_model(self, model_path: str, scaler_x_path: str, scaler_y_path: str) -> None:
        """Load the RNN model and scalers"""
        try:
            # Load model
            if model_path:
                self.model = tf.keras.models.load_model(model_path)
                logger.info(f"RNN model loaded from {model_path}")
            
            # Load scalers
            if scaler_x_path:
                self.scaler_X = joblib.load(scaler_x_path)
                logger.info(f"X scaler loaded from {scaler_x_path}")
            
            if scaler_y_path:
                self.scaler_y = joblib.load(scaler_y_path)
                logger.info(f"Y scaler loaded from {scaler_y_path}")
                
        except Exception as e:
            logger.error(f"Error loading RNN model/scalers: {e}")
            raise
    
    def _prepare_input_data(self, input_data: Dict) -> np.ndarray:
        """
        Prepare input data for RNN prediction
        
        Args:
            input_data: Dictionary with input features
            
        Returns:
            Prepared input array with shape (1, 20, 9)
        """
        try:
            # Extract features in correct order
            features = []
            for feature in self.feature_order:
                if feature in input_data:
                    features.append(input_data[feature])
                else:
                    logger.warning(f"Feature {feature} not found in input, using 0")
                    features.append(0.0)
            
            # Convert to numpy array and reshape
            input_array = np.array(features).reshape(1, -1)
            
            # Scale the input
            if self.scaler_X:
                input_scaled = self.scaler_X.transform(input_array)
            else:
                input_scaled = input_array
            
            # Create sequence - repeat the input 20 times for demo
            # In production, you'd need the actual historical sequence
            sequence = np.tile(input_scaled, (1, self.sequence_length, 1))
            
            return sequence
            
        except Exception as e:
            logger.error(f"Error preparing input data: {e}")
            raise
    
    def predict(self, input_data: Dict) -> Dict:
        """
        Make volatility prediction using RNN model
        
        Args:
            input_data: Dictionary with input features
            
        Returns:
            Dictionary with prediction results
        """
        try:
            if not self.model:
                raise ValueError("RNN model not loaded")
            
            # Prepare input
            sequence = self._prepare_input_data(input_data)
            
            # Scale input features before prediction
            if self.scaler_X:
                sequence_scaled = self.scaler_X.transform(sequence)
            else:
                sequence_scaled = sequence
            
            logger.info(f"RNN input shape: {sequence_scaled.shape}")
            logger.info(f"RNN input range: [{sequence_scaled.min():.6f}, {sequence_scaled.max():.6f}]")
            
            # Make prediction
            prediction_scaled = self.model.predict(sequence_scaled, verbose=0)
            
            logger.info(f"RNN prediction (scaled): {prediction_scaled}")
            
            # Inverse transform to get actual values
            if self.scaler_y:
                prediction = self.scaler_y.inverse_transform(prediction_scaled)
            else:
                prediction = prediction_scaled
            
            # Extract single value
            volatility_prediction = float(prediction[0][0])
            
            # Generate quantiles (RNN gives point prediction, we simulate quantiles)
            q10 = volatility_prediction * 0.85  # Lower bound
            q50 = volatility_prediction          # Median (point prediction)  
            q90 = volatility_prediction * 1.15  # Upper bound
            
            return {
                'q10': round(q10, 4),
                'q50': round(q50, 4), 
                'q90': round(q90, 4),
                'point_prediction': round(volatility_prediction, 4),
                'model_type': 'RNN'
            }
            
        except Exception as e:
            logger.error(f"Error making RNN prediction: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """Get RNN model information"""
        return {
            'model_type': 'Recurrent Neural Network (LSTM)',
            'architecture': 'LSTM(128) -> Dropout -> LSTM(64) -> Dropout -> LSTM(32) -> Dropout -> Dense(1)',
            'sequence_length': self.sequence_length,
            'features': self.feature_order,
            'input_shape': f'(1, {self.sequence_length}, {len(self.feature_order)})',
            'scalers': {
                'X_scaler': 'MinMaxScaler' if self.scaler_X else None,
                'y_scaler': 'MinMaxScaler' if self.scaler_y else None
            }
        }
    
    def is_ready(self) -> bool:
        """Check if RNN predictor is ready for predictions"""
        return self.model is not None and self.scaler_X is not None and self.scaler_y is not None

# Global RNN predictor instance
rnn_predictor = None

def initialize_rnn_predictor(model_path: str = None, scaler_x_path: str = None, scaler_y_path: str = None) -> RNNPredictor:
    """
    Initialize global RNN predictor instance
    
    Args:
        model_path: Path to RNN model file
        scaler_x_path: Path to X scaler file
        scaler_y_path: Path to y scaler file
        
    Returns:
        Initialized RNN predictor instance
    """
    global rnn_predictor
    
    # Default paths if not provided
    if not model_path:
        model_path = '../../model/model_volatility.h5'
    if not scaler_x_path:
        scaler_x_path = '../../model/scaler_X.save'
    if not scaler_y_path:
        scaler_y_path = '../../model/scaler_y.save'
    
    try:
        rnn_predictor = RNNPredictor(model_path, scaler_x_path, scaler_y_path)
        logger.info("RNN predictor initialized successfully")
        return rnn_predictor
    except Exception as e:
        logger.error(f"Failed to initialize RNN predictor: {e}")
        raise

def get_rnn_predictor() -> Optional[RNNPredictor]:
    """Get the global RNN predictor instance"""
    return rnn_predictor
