"""
Enhanced Model Loading Module - Handles loading and caching of QNN_modifié, RQN_model, and RNN
"""

import os
import logging
from typing import Dict, Optional, Union, Tuple
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model
import pickle
import sys

# Add model directory to path
sys.path.append('../../model')
sys.path.append('../core')
sys.path.append('../../model')

try:
    from qnn_modified import QNNModified, QuantileLoss
    from rqn_model import RQNModel
    from predictor import RNNPredictor
except ImportError as e:
    logging.warning(f"Could not import model classes: {e}")
    QNNModified = None
    RQNModel = None
    RNNPredictor = None

logger = logging.getLogger(__name__)


class EnhancedModelLoader:
    """Enhanced model loader supporting QNN_modifié, RQN_model, and RNN"""
    
    _instance = None
    _qnn_model = None
    _rqn_model = None
    _rnn_model = None
    _current_model = None
    _model_type = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnhancedModelLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._qnn_model = None
            self._rqn_model = None
            self._rnn_model = None
            self._current_model = None
            self._model_type = None
            self.initialized = True
    
    def load_qnn_modified(self, model_base_path: str = ".", scaler_path: str = "scaler_qnn_modified.pkl"):
        """Load QNN_modifié models"""
        try:
            if QNNModified is None:
                raise ImportError("QNNModified class not available")
            
            # Get project root path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            
            # Update paths to be relative to project root
            model_base_path = project_root  # QNN models are in root directory
            scaler_path = os.path.join(project_root, scaler_path)
            
            self._qnn_model = QNNModified()
            self._qnn_model.load_models(model_base_path, scaler_path)
            
            logger.info("QNN_modifié models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading QNN_modifié: {str(e)}")
            return False
    
    def load_rqn_model(self, model_path: str = "rqn_models.pkl", scaler_path: str = "scaler_rqn.pkl"):
        """Load RQN_model"""
        try:
            if RQNModel is None:
                raise ImportError("RQNModel class not available")
            
            # Get project root path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            
            # Update paths to be relative to project root
            model_path = os.path.join(project_root, model_path)
            scaler_path = os.path.join(project_root, scaler_path)
            
            self._rqn_model = RQNModel()
            self._rqn_model.load_models(model_path, scaler_path)
            
            logger.info("RQN_model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading RQN_model: {str(e)}")
            return False
    
    def load_rnn_model(self, model_path: str = "model/model_volatility.h5", scaler_path: str = "scaler_rqn.pkl"):
        """Load RNN model"""
        try:
            if RNNPredictor is None:
                raise ImportError("RNNPredictor class not available")
            
            # Get project root path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            
            # Update paths to be relative to project root
            model_path = os.path.join(project_root, model_path)
            scaler_path = os.path.join(project_root, scaler_path)
            
            self._rnn_model = RNNPredictor()
            self._rnn_model.load_model(model_path)
            self._rnn_model.load_scaler(scaler_path)
            
            logger.info("RNN model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading RNN model: {str(e)}")
            return False
    
    def set_active_model(self, model_type: str):
        """Set the active model type"""
        if model_type.lower() not in ['qnn_modified', 'rqn', 'rnn']:
            raise ValueError("Model type must be 'qnn_modified', 'rqn', or 'rnn'")
        
        if model_type.lower() == 'qnn_modified' and self._qnn_model is not None:
            self._current_model = self._qnn_model
            self._model_type = 'qnn_modified'
            logger.info("Active model set to QNN_modifié")
        elif model_type.lower() == 'rqn' and self._rqn_model is not None:
            self._current_model = self._rqn_model
            self._model_type = 'rqn'
            logger.info("Active model set to RQN_model")
        elif model_type.lower() == 'rnn' and self._rnn_model is not None:
            self._current_model = self._rnn_model
            self._model_type = 'rnn'
            logger.info("Active model set to RNN")
        else:
            raise RuntimeError(f"Model {model_type} not loaded. Call load method first.")
    
    def get_active_model(self):
        """Get the currently active model"""
        if self._current_model is None:
            raise RuntimeError("No active model set. Call set_active_model first.")
        return self._current_model
    
    def get_model_type(self):
        """Get the current model type"""
        return self._model_type
    
    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> Dict[float, np.ndarray]:
        """Make predictions with the active model"""
        if self._current_model is None:
            raise RuntimeError("No active model set. Call set_active_model first.")
        
        return self._current_model.predict(X)
    
    def get_feature_columns(self) -> list:
        """Get feature columns for the active model"""
        if self._current_model is None:
            raise RuntimeError("No active model set. Call set_active_model first.")
        
        return self._current_model.feature_cols
    
    def is_model_loaded(self, model_type: str) -> bool:
        """Check if a specific model is loaded"""
        if model_type.lower() == 'qnn_modified':
            return self._qnn_model is not None
        elif model_type.lower() == 'rqn':
            return self._rqn_model is not None
        elif model_type.lower() == 'rnn':
            return self._rnn_model is not None
        return False
    
    def get_loaded_models(self) -> Dict[str, bool]:
        """Get status of all loaded models"""
        return {
            'qnn_modified': self._qnn_model is not None,
            'rqn': self._rqn_model is not None,
            'rnn': self._rnn_model is not None
        }
    
    def train_qnn_modified(self, data_path: str = "data/data_clean.csv", save_models: bool = True):
        """Train QNN_modifié model"""
        try:
            if QNNModified is None:
                raise ImportError("QNNModified class not available")
            
            self._qnn_model = QNNModified()
            models, predictions, y_test = self._qnn_model.train(data_path)
            
            if save_models:
                self._qnn_model.save_models()
            
            logger.info("QNN_modifié trained successfully")
            return models, predictions, y_test
            
        except Exception as e:
            logger.error(f"Error training QNN_modifié: {str(e)}")
            raise
    
    def train_rqn_model(self, data_path: str = "data/data_clean.csv", save_models: bool = True):
        """Train RQN_model"""
        try:
            if RQNModel is None:
                raise ImportError("RQNModel class not available")
            
            self._rqn_model = RQNModel()
            models, predictions, y_test, X_test = self._rqn_model.train(data_path)
            
            if save_models:
                self._rqn_model.save_models()
            
            logger.info("RQN_model trained successfully")
            return models, predictions, y_test, X_test
            
        except Exception as e:
            logger.error(f"Error training RQN_model: {str(e)}")
            raise


# Global instance
enhanced_loader = EnhancedModelLoader()


def initialize_enhanced_models():
    """Initialize all models if available"""
    success = True
    
    # Try to load QNN_modifié
    if not enhanced_loader.load_qnn_modified():
        logger.warning("Failed to load QNN_modifié, will train if needed")
        success = False
    
    # Try to load RQN_model
    if not enhanced_loader.load_rqn_model():
        logger.warning("Failed to load RQN_model, will train if needed")
        success = False
    
    # Try to load RNN model
    if not enhanced_loader.load_rnn_model():
        logger.warning("Failed to load RNN model, will train if needed")
        success = False
    
    # Set default active model
    if enhanced_loader.is_model_loaded('qnn_modified'):
        enhanced_loader.set_active_model('qnn_modified')
    elif enhanced_loader.is_model_loaded('rqn'):
        enhanced_loader.set_active_model('rqn')
    elif enhanced_loader.is_model_loaded('rnn'):
        enhanced_loader.set_active_model('rnn')
    
    return success


def get_enhanced_loader():
    """Get the global enhanced loader instance"""
    return enhanced_loader
