"""
Input Validation Module
"""

from typing import Dict
import numpy as np


class PredictionValidator:
    """Validate prediction inputs"""
    
    @staticmethod
    def validate_features(features: Dict[str, float], required_features: list) -> bool:
        """Validate that all required features are present and valid"""
        missing = set(required_features) - set(features.keys())
        if missing:
            raise ValueError(f"Missing features: {missing}")
        
        for col, val in features.items():
            try:
                numeric_val = float(val)
                if np.isnan(numeric_val) or np.isinf(numeric_val):
                    raise ValueError(f"Feature {col} has invalid value: {val}")
            except (TypeError, ValueError):
                raise ValueError(f"Feature {col} must be a number, got {val}")
        
        return True
    
    @staticmethod
    def validate_batch_features(features_list: list, required_features: list) -> bool:
        """Validate batch of features"""
        for i, features in enumerate(features_list):
            try:
                PredictionValidator.validate_features(features, required_features)
            except ValueError as e:
                raise ValueError(f"Error in sample {i}: {str(e)}")
        return True
