"""
Example: Batch Prediction Script
"""

import sys
import os
import pandas as pd
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.predictor import VolatilityPredictor
from config.config import get_config

# Get configuration
config = get_config()

# Initialize predictor
predictor = VolatilityPredictor()
predictor.initialize(str(config.MODEL_PATH), str(config.SCALER_PATH))

def predict_from_csv(csv_path: str, output_path: str = 'predictions.csv'):
    """
    Make predictions from a CSV file
    
    Args:
        csv_path: Path to input CSV with features
        output_path: Path to save predictions
    """
    # Read data
    df = pd.read_csv(csv_path)
    
    # Make predictions
    result_df = predictor.predict_from_dataframe(df)
    
    # Save results
    result_df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}")
    
    return result_df


def predict_single_example():
    """Example: Single prediction"""
    
    # Example features
    features = {
        'lag1': 0.5,
        'lag2': 0.3,
        'vol_lag1': 0.4,
        'vol_lag2': 0.35,
        'ret_abs': 0.02,
        'ret_sq': 0.0004,
        'ma5': 100.5,
        'ma20': 101.2,
        'std5': 2.1,
        'std20': 2.3
    }
    
    # Make prediction
    prediction = predictor.predict(features)
    
    print("Single Prediction:")
    print(json.dumps(prediction, indent=2))
    
    return prediction


def predict_batch_example():
    """Example: Batch prediction"""
    
    # Example batch of features
    batch = [
        {
            'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
            'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
            'std5': 2.1, 'std20': 2.3
        },
        {
            'lag1': 0.4, 'lag2': 0.2, 'vol_lag1': 0.35, 'vol_lag2': 0.3,
            'ret_abs': 0.015, 'ret_sq': 0.000225, 'ma5': 100.2, 'ma20': 101.0,
            'std5': 2.0, 'std20': 2.2
        }
    ]
    
    # Make batch predictions
    predictions = predictor.predict_batch(batch)
    
    print("\nBatch Predictions:")
    print(json.dumps(predictions, indent=2))
    
    return predictions


if __name__ == '__main__':
    print("QNN Volatility Prediction - Examples\n")
    
    # Run examples
    predict_single_example()
    predict_batch_example()
    
    