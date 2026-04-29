"""
Example: Model Explanation using SHAP
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.predictor import VolatilityPredictor
from app.explainability.shap_explainer import SHAPExplainer
from config.config import get_config

# Get configuration
config = get_config()

# Initialize predictor
predictor = VolatilityPredictor()
predictor.initialize(str(config.MODEL_PATH), str(config.SCALER_PATH))


def explain_prediction():
    """Explain a single prediction using SHAP"""
    
    # Example features
    features = {
        'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
        'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
        'std5': 2.1, 'std20': 2.3
    }
    
    # Make prediction
    prediction = predictor.predict(features)
    print("Prediction:", prediction)
    
    # Prepare features for explanation
    feature_array = np.array([features[col] for col in predictor.FEATURE_COLUMNS]).reshape(1, -1)
    scaled_features = predictor.scaler.transform(feature_array)
    
    # Create SHAP explainer (may take a moment)
    print("\nInitializing SHAP explainer (this may take a moment)...")
    try:
        explainer = SHAPExplainer(predictor.model, scaled_features)
        
        # Get explanation
        explanation = explainer.explain_prediction(scaled_features, predictor.FEATURE_COLUMNS)
        
        print("\nFeature Importance (SHAP):")
        for feature, importance in explanation['feature_importance'].items():
            print(f"  {feature}: {importance:.4f}")
        
        print(f"\nBase Value: {explanation['base_value']:.4f}")
        
        return explanation
    
    except Exception as e:
        print(f"Error in SHAP explanation: {str(e)}")
        print("Note: SHAP requires more computational resources. Try with smaller dataset or GPU.")


def compare_feature_importance_across_samples():
    """Compare feature importance across multiple samples"""
    
    # Create multiple samples
    samples = [
        {
            'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
            'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
            'std5': 2.1, 'std20': 2.3
        },
        {
            'lag1': 0.2, 'lag2': 0.1, 'vol_lag1': 0.15, 'vol_lag2': 0.12,
            'ret_abs': 0.01, 'ret_sq': 0.0001, 'ma5': 101.0, 'ma20': 101.5,
            'std5': 1.8, 'std20': 1.9
        }
    ]
    
    print("Comparing Feature Importance Across Samples\n")
    
    for i, sample in enumerate(samples):
        print(f"Sample {i+1}:")
        
        feature_array = np.array([sample[col] for col in predictor.FEATURE_COLUMNS]).reshape(1, -1)
        scaled_features = predictor.scaler.transform(feature_array)
        
        try:
            explainer = SHAPExplainer(predictor.model, scaled_features)
            explanation = explainer.explain_prediction(scaled_features, predictor.FEATURE_COLUMNS)
            
            print("  Top 5 Important Features:")
            for feature, importance in list(explanation['feature_importance'].items())[:5]:
                print(f"    {feature}: {importance:.4f}")
        
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        print()


if __name__ == '__main__':
    print("QNN Model Explanation Examples\n")
    print("="*50)
    
    # Run explanation example
    explain_prediction()
    
    print("\n" + "="*50)
    print("\nNote: SHAP computation can be intensive.")
    print("For large-scale explanations, consider using GPU or sampling.")
