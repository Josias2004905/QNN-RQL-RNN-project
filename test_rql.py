#!/usr/bin/env python3
import requests
import json

# Test RQL model specifically
rql_data = {
    "data": [0.01, 0.02, 0.015, 0.005, 0.0001, 920, 925, 0.006],  # 8 features for RQL
    "model_type": "rqn"
}

try:
    response = requests.post(
        "http://localhost:5000/predictions/predict",
        headers={"Content-Type": "application/json"},
        json=rql_data,
        timeout=30
    )
    print(f"RQL Status: {response.status_code}")
    print(f"RQL Response: {response.text}")
except Exception as e:
    print(f"RQL Exception: {e}")
