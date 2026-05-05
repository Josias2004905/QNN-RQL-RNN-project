#!/usr/bin/env python3
import requests
import json

# Test SHAP endpoint with all models
models = [
    {
        "name": "QNN",
        "data": [0.01, 0.02, 0.015, 0.008, 0.005, 0.0001, 920, 925, 0.006, 0.012],  # 10 features
        "model_type": "qnn_modified"
    },
    {
        "name": "RQL", 
        "data": [0.01, 0.02, 0.015, 0.005, 0.0001, 920, 925, 0.006],  # 8 features
        "model_type": "rqn"
    },
    {
        "name": "RNN",
        "data": [0.01, 0.02, 0.015, 0.008, 0.005, 0.0001, 920, 925, 0.006, 0.012],  # 10 features
        "model_type": "rnn"
    }
]

for model in models:
    try:
        response = requests.post(
            "http://localhost:5000/predictions/explain",
            headers={"Content-Type": "application/json"},
            json={
                "data": model["data"],
                "model_type": model["model_type"]
            },
            timeout=30
        )
        print(f"\n=== {model['name']} SHAP ===")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Features: {len(result['explanation']['feature_names'])}")
            print(f"SHAP values: {len(result['explanation']['shap_values'])}")
            print(f"Prediction: {result['explanation']['prediction']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"\n=== {model['name']} SHAP ===")
        print(f"Exception: {e}")
