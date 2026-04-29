# API Documentation

## Overview

This is the REST API for the Quantile Neural Networks (QNN) Volatility Prediction system. The API provides endpoints for:

- Single and batch predictions
- Model information and health checks
- Feature importance analysis using SHAP
- Comprehensive error handling

## Base URL

```
http://localhost:5000/api/v1
```

For production, replace with your deployment URL.

## Authentication

Currently, the API does not require authentication. For production, add API key authentication:

```bash
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Health Check

Check if the API is running and the model is loaded.

**Request:**
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

**Status Codes:**
- `200` - API is healthy
- `500` - Model not loaded or error

---

### 2. Model Information

Get information about the model, features, and quantiles.

**Request:**
```
GET /info
```

**Response:**
```json
{
  "version": "1.0.0",
  "features": [
    "lag1", "lag2", "vol_lag1", "vol_lag2",
    "ret_abs", "ret_sq", "ma5", "ma20", "std5", "std20"
  ],
  "quantiles": [0.1, 0.5, 0.9],
  "model_type": "Quantile Neural Network",
  "description": "QNN for Financial Volatility Prediction"
}
```

---

### 3. Single Prediction

Make a volatility prediction for a single observation.

**Request:**
```
POST /predict
Content-Type: application/json

{
  "lag1": 0.5,
  "lag2": 0.3,
  "vol_lag1": 0.4,
  "vol_lag2": 0.35,
  "ret_abs": 0.02,
  "ret_sq": 0.0004,
  "ma5": 100.5,
  "ma20": 101.2,
  "std5": 2.1,
  "std20": 2.3
}
```

**Response:**
```json
{
  "q10": 0.125,
  "q50": 0.150,
  "q90": 0.180
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid input (missing or invalid features)
- `500` - Server error

**Example using cURL:**
```bash
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "lag1": 0.5,
    "lag2": 0.3,
    "vol_lag1": 0.4,
    "vol_lag2": 0.35,
    "ret_abs": 0.02,
    "ret_sq": 0.0004,
    "ma5": 100.5,
    "ma20": 101.2,
    "std5": 2.1,
    "std20": 2.3
  }'
```

**Example using Python:**
```python
import requests

url = "http://localhost:5000/api/v1/predict"
data = {
    "lag1": 0.5,
    "lag2": 0.3,
    "vol_lag1": 0.4,
    "vol_lag2": 0.35,
    "ret_abs": 0.02,
    "ret_sq": 0.0004,
    "ma5": 100.5,
    "ma20": 101.2,
    "std5": 2.1,
    "std20": 2.3
}

response = requests.post(url, json=data)
print(response.json())
```

---

### 4. Batch Predictions

Make predictions for multiple observations.

**Request:**
```
POST /predict/batch
Content-Type: application/json

{
  "predictions": [
    {
      "lag1": 0.5,
      "lag2": 0.3,
      "vol_lag1": 0.4,
      "vol_lag2": 0.35,
      "ret_abs": 0.02,
      "ret_sq": 0.0004,
      "ma5": 100.5,
      "ma20": 101.2,
      "std5": 2.1,
      "std20": 2.3
    },
    {
      "lag1": 0.4,
      "lag2": 0.2,
      "vol_lag1": 0.35,
      "vol_lag2": 0.3,
      "ret_abs": 0.015,
      "ret_sq": 0.000225,
      "ma5": 100.2,
      "ma20": 101.0,
      "std5": 2.0,
      "std20": 2.2
    }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    {"q10": 0.125, "q50": 0.150, "q90": 0.180},
    {"q10": 0.120, "q50": 0.145, "q90": 0.175}
  ]
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid input
- `500` - Server error

**Example using Python:**
```python
import requests

url = "http://localhost:5000/api/v1/predict/batch"
batch_data = {
    "predictions": [
        {
            "lag1": 0.5, "lag2": 0.3, "vol_lag1": 0.4, "vol_lag2": 0.35,
            "ret_abs": 0.02, "ret_sq": 0.0004, "ma5": 100.5, "ma20": 101.2,
            "std5": 2.1, "std20": 2.3
        },
        {
            "lag1": 0.4, "lag2": 0.2, "vol_lag1": 0.35, "vol_lag2": 0.3,
            "ret_abs": 0.015, "ret_sq": 0.000225, "ma5": 100.2, "ma20": 101.0,
            "std5": 2.0, "std20": 2.2
        }
    ]
}

response = requests.post(url, json=batch_data)
for i, pred in enumerate(response.json()["predictions"]):
    print(f"Sample {i+1}: {pred}")
```

---

### 5. Model Explanation (SHAP)

Get SHAP-based explanation for a prediction.

**Request:**
```
POST /explain
Content-Type: application/json

{
  "lag1": 0.5,
  "lag2": 0.3,
  ...
}
```

**Response:**
```json
{
  "prediction": {
    "q10": 0.125,
    "q50": 0.150,
    "q90": 0.180
  },
  "explanation": {
    "shap_values": [...],
    "base_value": 0.15,
    "feature_importance": {
      "lag1": 0.045,
      "vol_lag1": 0.042,
      "lag2": 0.038,
      ...
    },
    "feature_names": [...]
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid input
- `500` - Server error

**Note:** SHAP explanations may take longer to compute due to computational requirements.

---

## Feature Descriptions

| Feature | Type | Description |
|---------|------|-------------|
| `lag1` | float | Volatility at lag 1 |
| `lag2` | float | Volatility at lag 2 |
| `vol_lag1` | float | Volatility measurement lag 1 |
| `vol_lag2` | float | Volatility measurement lag 2 |
| `ret_abs` | float | Absolute returns |
| `ret_sq` | float | Squared returns |
| `ma5` | float | 5-day moving average |
| `ma20` | float | 20-day moving average |
| `std5` | float | 5-day standard deviation |
| `std20` | float | 20-day standard deviation |

## Output Quantiles

The model returns predictions for three volatility quantiles:

| Quantile | Description |
|----------|-------------|
| `q10` | 10th percentile (lower bound) |
| `q50` | 50th percentile (median prediction) |
| `q90` | 90th percentile (upper bound) |

These quantiles provide a range of volatility predictions, useful for risk assessment.

## Error Responses

### Missing Required Field

**Status:** `400`
```json
{
  "error": "Missing features: ['lag1', 'lag2']"
}
```

### Invalid Feature Value

**Status:** `400`
```json
{
  "error": "Feature lag1 must be a number, got string_value"
}
```

### Server Error

**Status:** `500`
```json
{
  "error": "An unexpected error occurred"
}
```

## Rate Limiting (Production)

For production deployments, rate limiting is recommended:

- **Requests per minute:** 60 (per IP)
- **Burst limit:** 10 requests
- **Timeout:** 5 seconds per request

## Performance Metrics

| Metric | Value |
|--------|-------|
| Inference time (single) | ~50ms |
| Inference time (batch/100) | ~200ms |
| Memory usage | ~2GB |
| Model size | ~50MB |

## Integration Examples

### Python Integration

```python
import requests
import pandas as pd

class QNNPredictor:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def predict(self, features):
        response = requests.post(
            f"{self.base_url}/api/v1/predict",
            json=features
        )
        return response.json()
    
    def predict_batch(self, df):
        batch = df.to_dict('records')
        response = requests.post(
            f"{self.base_url}/api/v1/predict/batch",
            json={"predictions": batch}
        )
        return response.json()['predictions']

# Usage
predictor = QNNPredictor()
result = predictor.predict({
    "lag1": 0.5, "lag2": 0.3, "vol_lag1": 0.4, "vol_lag2": 0.35,
    "ret_abs": 0.02, "ret_sq": 0.0004, "ma5": 100.5, "ma20": 101.2,
    "std5": 2.1, "std20": 2.3
})
print(result)
```

### JavaScript/Node.js Integration

```javascript
async function predictVolatility(features) {
    const response = await fetch('http://localhost:5000/api/v1/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(features)
    });
    return response.json();
}

// Usage
const features = {
    lag1: 0.5, lag2: 0.3, vol_lag1: 0.4, vol_lag2: 0.35,
    ret_abs: 0.02, ret_sq: 0.0004, ma5: 100.5, ma20: 101.2,
    std5: 2.1, std20: 2.3
};

predictVolatility(features).then(result => console.log(result));
```

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review the README.md
3. Contact the development team

## Version History

- **v1.0.0** - Initial API release
