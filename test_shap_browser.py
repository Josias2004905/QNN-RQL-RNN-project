#!/usr/bin/env python3
import requests
import json

def test_full_workflow():
    """Test the complete workflow: prediction first, then SHAP analysis"""
    
    # Step 1: Make a prediction (required for SHAP to work)
    prediction_data = {
        "data": [0.01, 0.02, 0.015, 0.008, 0.005, 0.0001, 920, 925, 0.006, 0.012],
        "model_type": "qnn_modified"
    }
    
    print("=== Step 1: Making Prediction ===")
    try:
        pred_response = requests.post(
            "http://localhost:5000/predictions/predict",
            headers={"Content-Type": "application/json"},
            json=prediction_data,
            timeout=30
        )
        print(f"Prediction Status: {pred_response.status_code}")
        if pred_response.status_code == 200:
            pred_result = pred_response.json()
            print(f"Prediction successful: {pred_result['model_type']}")
            print(f"Quantiles: Q10={pred_result['predictions']['quantile_0_1'][0]}, Q50={pred_result['predictions']['quantile_0_5'][0]}, Q90={pred_result['predictions']['quantile_0_9'][0]}")
        else:
            print(f"Prediction failed: {pred_response.text}")
            return
    except Exception as e:
        print(f"Prediction Exception: {e}")
        return
    
    # Step 2: Get SHAP explanation
    print("\n=== Step 2: Getting SHAP Explanation ===")
    try:
        shap_response = requests.post(
            "http://localhost:5000/predictions/explain",
            headers={"Content-Type": "application/json"},
            json=prediction_data,
            timeout=30
        )
        print(f"SHAP Status: {shap_response.status_code}")
        if shap_response.status_code == 200:
            shap_result = shap_response.json()
            print(f"SHAP successful!")
            print(f"Features: {len(shap_result['explanation']['feature_names'])}")
            print(f"SHAP values: {len(shap_result['explanation']['shap_values'])}")
            print(f"Feature importance keys: {list(shap_result['explanation']['feature_importance'].keys())[:3]}...")
            print(f"Positive contributions: {len(shap_result['explanation']['contribution_breakdown']['positive'])}")
            print(f"Negative contributions: {len(shap_result['explanation']['contribution_breakdown']['negative'])}")
            print(f"Base value: {shap_result['explanation']['base_value']}")
            print(f"Prediction: {shap_result['explanation']['prediction']}")
            
            # Show top 3 features
            feature_importance = shap_result['explanation']['feature_importance']
            sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
            print(f"\nTop 3 features:")
            for i, (feature, importance) in enumerate(sorted_features[:3]):
                direction = "increases" if importance > 0 else "decreases"
                print(f"  {i+1}. {feature}: {importance:.4f} ({direction} volatility)")
        else:
            print(f"SHAP failed: {shap_response.text}")
    except Exception as e:
        print(f"SHAP Exception: {e}")

if __name__ == "__main__":
    test_full_workflow()
