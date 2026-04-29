"""
Model Loading Module - Handles loading and caching of trained models
"""

import os
import logging
from typing import Tuple
import numpy as np
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model

logger = logging.getLogger(__name__)


class QuantileLoss:
    """Custom Quantile Loss for QNN models"""
    
    @staticmethod
    def quantile_loss(q):
        def loss(y_true, y_pred):
            error = y_true - y_pred
            return tf.reduce_mean(tf.maximum(q * error, (q - 1) * error))
        return loss


class ModelLoader:
    """Singleton class to load and cache models and scalers"""
    
    _instance = None
    _model = None
    _scaler = None
    _model_path = None
    _scaler_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model_and_scaler(self, model_path: str, scaler_path: str):
        """
        Load the QNN model and scaler
        
        Args:
            model_path: Path to the trained model (.h5)
            scaler_path: Path to the scaler (.pkl)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        
        try:
            # Load scaler
            self._scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded from {scaler_path}")
            
            # Load model with custom loss and error handling for version compatibility
            try:
                custom_objects = {
                    'loss': QuantileLoss.quantile_loss(0.5),
                    'mse': 'mse',
                    'mae': 'mae'
                }
                self._model = load_model(model_path, custom_objects=custom_objects, safe_mode=False)
            except Exception as version_error:
                logger.warning(f"Failed with custom objects, trying with compile=False: {str(version_error)}")
                # Try loading without compile as fallback
                self._model = load_model(model_path, compile=False)
                # Recompile with default settings
                self._model.compile(optimizer='adam', loss='mse')
            
            self._model_path = model_path
            self._scaler_path = scaler_path
            logger.info(f"Model loaded successfully from {model_path}")
            
        except Exception as e:
            logger.error(f"Error loading model or scaler: {str(e)}")
            raise
    
    def get_model(self):
        """Get loaded model"""
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model_and_scaler first.")
        return self._model
    
    def get_scaler(self):
        """Get loaded scaler"""
        if self._scaler is None:
            raise RuntimeError("Scaler not loaded. Call load_model_and_scaler first.")
        return self._scaler
    
    def is_loaded(self) -> bool:
        """Check if model and scaler are loaded"""
        return self._model is not None and self._scaler is not None
