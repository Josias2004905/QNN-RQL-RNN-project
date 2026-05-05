#!/usr/bin/env python3
import requests
import json

# Test comparison endpoint with 10 features (QNN format)
comparison_data = {
    "data": [0.01, 0.02, 0.015, 0.008, 0.005, 0.0001, 920, 925, 0.006, 0.012]  # 10 features
}

try:
    response = requests.post(
        "http://localhost:5000/models/compare",
        headers={"Content-Type": "application/json"},
        json=comparison_data,
        timeout=30
    )
    print(f"Comparison Status: {response.status_code}")
    print(f"Comparison Response: {response.text}")
except Exception as e:
    print(f"Comparison Exception: {e}")
