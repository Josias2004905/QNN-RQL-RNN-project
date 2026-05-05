#!/usr/bin/env python3
import requests
import json

# Test RQL model (should cause HTTP 400 if there's a mismatch)
rql_data = {
    "data": [0.01, 0.02, 0.015, 0.005, 0.0001, 920, 925, 0.006],  # 8 features for RQL
    "model_type": "rqn"
}

# Test QNN model (should cause HTTP 500 if there's a backend error)
qnn_data = {
    "data": [0.01, 0.02, 0.015, 0.008, 0.005, 0.0001, 920, 925, 0.006, 0.012],  # 10 features for QNN
    "model_type": "qnn_modified"
}

# Test RNN model (should cause HTTP 500 if there's a backend error)
rnn_data = {
    "data": [0.01, 0.02, 0.015, 0.008, 0.005, 0.0001, 920, 925, 0.006, 0.012],  # 10 features for RNN
    "model_type": "rnn"
}

def test_model(data, model_name):
    try:
        response = requests.post(
            "http://localhost:5000/predictions/predict",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=10
        )
        print(f"\n=== {model_name} ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"\n=== {model_name} ===")
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    print("Testing all three models...")
    
    test_model(rql_data, "RQL (rqn)")
    test_model(qnn_data, "QNN (qnn_modified)")
    test_model(rnn_data, "RNN (rnn)")
