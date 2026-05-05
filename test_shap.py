#!/usr/bin/env python3
import requests
import json

# Test SHAP endpoint with QNN model
shap_data = {
    "data": [0.01, 0.02, 0.015, 0.008, 0.005, 0.0001, 920, 925, 0.006, 0.012],  # 10 features for QNN
    "model_type": "qnn_modified"
}

try:
    response = requests.post(
        "http://localhost:5000/predictions/explain",
        headers={"Content-Type": "application/json"},
        json=shap_data,
        timeout=30
    )
    print(f"SHAP Status: {response.status_code}")
    print(f"SHAP Response: {response.text}")
except Exception as e:
    print(f"SHAP Exception: {e}")
