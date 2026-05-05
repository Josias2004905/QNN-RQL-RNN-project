"""
SHAP Explainability Module - Feature importance analysis
"""

import logging
from typing import Dict, Tuple
import numpy as np
import pandas as pd
import shap
from core.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class SHAPExplainer:
    """SHAP-based explainability for QNN model"""
    
    def __init__(self, model, background_data: np.ndarray):
        """
        Initialize SHAP explainer
        
        Args:
            model: Keras/TensorFlow model
            background_data: Background data for SHAP (scaled features)
        """
        self.model = model
        self.background_data = background_data
        self.explainer = None
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer"""
        try:
            # Use KernelExplainer for model-agnostic approach
            self.explainer = shap.KernelExplainer(
                model=self.model.predict,
                data=shap.sample(self.background_data, 100)
            )
            logger.info("SHAP explainer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SHAP explainer: {str(e)}")
            raise
    
    def explain_prediction(self, features: np.ndarray, feature_names: list) -> Dict:
        """
        Explain a single prediction using SHAP
        
        Args:
            features: Input features (scaled)
            feature_names: Names of features
        
        Returns:
            Dictionary with SHAP values and explanations
        """
        try:
            # Get SHAP values
            shap_values = self.explainer.shap_values(features)
            
            # Create explanation dictionary
            explanation = {
                'shap_values': shap_values.tolist() if isinstance(shap_values, np.ndarray) else shap_values,
                'base_value': float(self.explainer.expected_value),
                'feature_importance': self._calculate_importance(shap_values, feature_names),
                'feature_names': feature_names
            }
            
            logger.info("Prediction explained successfully")
            return explanation
        
        except Exception as e:
            logger.error(f"Error explaining prediction: {str(e)}")
            raise
    
    def explain_batch(self, features: np.ndarray, feature_names: list) -> list:
        """
        Explain multiple predictions
        
        Args:
            features: Input features (scaled)
            feature_names: Names of features
        
        Returns:
            List of explanation dictionaries
        """
        explanations = []
        for i in range(len(features)):
            exp = self.explain_prediction(features[i:i+1], feature_names)
            explanations.append(exp)
        return explanations
    
    @staticmethod
    def _calculate_importance(shap_values: np.ndarray, feature_names: list) -> Dict[str, float]:
        """
        Calculate feature importance from SHAP values
        
        Args:
            shap_values: SHAP values array
            feature_names: Names of features
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        # Handle multi-output case
        if isinstance(shap_values, list):
            # Average across outputs
            mean_abs_shap = np.mean([np.abs(sv) for sv in shap_values], axis=0).flatten()
        else:
            mean_abs_shap = np.abs(shap_values).flatten()
        
        # Create importance dictionary
        importance = {
            name: float(value)
            for name, value in zip(feature_names, mean_abs_shap)
        }
        
        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        return importance


class LIMEExplainer:
    """LIME-based explainability for QNN model"""
    
    def __init__(self, model, feature_names: list, scaler):
        """
        Initialize LIME explainer
        
        Args:
            model: Keras/TensorFlow model
            feature_names: Names of features
            scaler: Scaler object for feature transformation
        """
        try:
            import lime
            import lime.lime_tabular
            self.model = model
            self.feature_names = feature_names
            self.scaler = scaler
            
            # Create LIME explainer
            self.explainer = lime.lime_tabular.LimeTabularExplainer(
                training_data=scaler.data_mean_.reshape(1, -1),  # Use mean as reference
                feature_names=feature_names,
                mode='regression'
            )
            logger.info("LIME explainer initialized successfully")
        except ImportError:
            logger.warning("LIME not installed. Skipping LIME explainer.")
            self.explainer = None
    
    def explain_prediction(self, features: np.ndarray) -> Dict:
        """
        Explain a single prediction using LIME
        
        Args:
            features: Input features (scaled)
        
        Returns:
            Dictionary with LIME explanation
        """
        if self.explainer is None:
            logger.warning("LIME explainer not available")
            return {}
        
        try:
            # Get prediction
            prediction = self.model.predict(features, verbose=0)
            
            # Get LIME explanation
            exp = self.explainer.explain_instance(
                features.flatten(),
                predict_fn=self.model.predict,
                num_features=len(self.feature_names)
            )
            
            # Extract feature weights
            feature_weights = dict(exp.as_list())
            
            explanation = {
                'prediction': float(prediction[0][0]),
                'feature_weights': feature_weights,
                'feature_names': self.feature_names
            }
            
            logger.info("LIME explanation generated successfully")
            return explanation
        
        except Exception as e:
            logger.error(f"Error in LIME explanation: {str(e)}")
            return {}
