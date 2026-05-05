"""
Simple Model Loader - Demo version for testing interface
Returns mock predictions for all models
"""

import logging
import numpy as np
from typing import Dict, List

logger = logging.getLogger(__name__)

class SimpleModelLoader:
    """Simple model loader that returns mock predictions"""
    
    def __init__(self):
        self.current_model_type = 'qnn_modified'
        # Set active model on initialization
        self.set_active_model('qnn_modified')
        self.feature_cols = {
            'qnn_modified': ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20'],
            'rqn': ['return', 'lag1', 'lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5'],
            'rnn': ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20']
        }
    
    def is_model_loaded(self, model_type: str) -> bool:
        """All models are 'loaded' in this demo version"""
        return True
    
    def get_loaded_models(self) -> Dict[str, bool]:
        """Return status of all models"""
        return {
            'qnn_modified': True,
            'rqn': True,
            'rnn': True
        }
    
    def set_active_model(self, model_type: str):
        """Set the active model type"""
        if model_type.lower() in ['qnn_modified', 'rqn', 'rnn']:
            self.current_model_type = model_type.lower()
            logger.info(f"Active model set to {model_type}")
        else:
            raise ValueError(f"Model type must be 'qnn_modified', 'rqn', or 'rnn'")
    
    def get_model_type(self):
        """Get the current model type"""
        return self.current_model_type
    
    def get_feature_columns(self):
        """Get feature columns for current model"""
        return self.feature_cols.get(self.current_model_type, self.feature_cols['qnn_modified'])
    
    def predict(self, X):
        """Return mock predictions"""
        if isinstance(X, np.ndarray):
            n_samples = X.shape[0]
        else:
            n_samples = len(X)
        
        # Generate realistic-looking mock predictions based on model type
        if self.current_model_type == 'qnn_modified':
            # QNN predictions - more conservative
            base_value = 0.015
            q10 = np.full(n_samples, base_value * 0.3)  # 0.0045
            q50 = np.full(n_samples, base_value)        # 0.015
            q90 = np.full(n_samples, base_value * 2.5)  # 0.0375
        elif self.current_model_type == 'rqn':
            # RQL predictions - slightly different pattern
            base_value = 0.018
            q10 = np.full(n_samples, base_value * 0.25) # 0.0045
            q50 = np.full(n_samples, base_value)        # 0.018
            q90 = np.full(n_samples, base_value * 2.2)  # 0.0396
        else:  # RNN
            # RNN predictions - more volatile
            base_value = 0.012
            q10 = np.full(n_samples, base_value * 0.4)  # 0.0048
            q50 = np.full(n_samples, base_value)        # 0.012
            q90 = np.full(n_samples, base_value * 3.0)  # 0.036
        
        return {
            'quantile_0_1': q10.tolist(),
            'quantile_0_5': q50.tolist(),
            'quantile_0_9': q90.tolist()
        }

# Global instance
simple_loader = SimpleModelLoader()

def get_simple_loader():
    """Get the global simple loader instance"""
    return simple_loader
