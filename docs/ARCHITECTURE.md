# QNN Quantile Neural Networks - Project Documentation

## 📚 Complete Project Guide

### Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Components](#components)
5. [Usage Examples](#usage-examples)
6. [Deployment](#deployment)

---

## Project Overview

### Objective

The **Quantile Neural Networks (QNN) for Financial Volatility Prediction** project aims to:

1. **Develop and Compare Models:**
   - Quantile Neural Networks (QNN)
   - Linear Quantile Regression
   - Compare predictive performance

2. **Predict Multiple Quantiles:**
   - 10th percentile (lower volatility bound)
   - 50th percentile (median volatility)
   - 90th percentile (upper volatility bound)

3. **Implement Explainability (XAI):**
   - Use SHAP for feature importance
   - Understand model decisions

4. **Evaluate Performance:**
   - RMSE (Root Mean Square Error)
   - MAE (Mean Absolute Error)
   - MAPE (Mean Absolute Percentage Error)
   - Quantile-specific metrics

### Key Technologies

- **Machine Learning:** TensorFlow/Keras
- **Feature Processing:** scikit-learn
- **Explainability:** SHAP, LIME
- **API Framework:** Flask
- **Deployment:** Docker
- **Data Processing:** Pandas, NumPy

---

## Project Structure

```
QNN_Project/
│
├── 📂 app/                          # Main application
│   ├── 📂 core/                     # Core prediction logic
│   │   ├── model_loader.py          # Load trained models
│   │   ├── predictor.py             # Prediction pipeline
│   │   └── __init__.py
│   │
│   ├── 📂 api/                      # REST API
│   │   ├── flask_api.py             # Flask application
│   │   └── __init__.py
│   │
│   ├── 📂 explainability/           # XAI Module
│   │   ├── shap_explainer.py        # SHAP explanations
│   │   └── __init__.py
│   │
│   ├── 📂 utils/                    # Utilities
│   │   ├── validators.py            # Input validation
│   │   ├── logger.py                # Logging setup
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── 📂 config/                       # Configuration
│   └── config.py                    # Settings & paths
│
├── 📂 data/                         # Data files
│   ├── data_clean.csv               # Cleaned dataset
│   ├── Masi20.csv                   # Original data
│   └── nettoyage.ipynb              # Data cleaning notebook
│
├── 📂 model/                        # Trained models
│   ├── model_volatility.h5          # Trained QNN
│   ├── scaler.pkl                   # Feature scaler
│   ├── qnn.ipynb                    # QNN training
│   └── RNN MODEL.ipynb              # RNN experiments
│
├── 📂 prediction/                   # Predictions output
│   └── predictions_qnn.xlsx         # Generated predictions
│
├── 📂 resultats/                    # Results & metrics
│   └── resultats_qnn.xlsx           # Evaluation metrics
│
├── 📂 tests/                        # Unit tests
│   ├── test_predictor.py            # Predictor tests
│   └── test_api.py                  # API tests
│
├── 📂 docs/                         # Documentation
│   ├── API.md                       # API reference
│   └── DEPLOYMENT.md                # Deployment guide
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 Dockerfile                    # Docker image
├── 📄 docker-compose.yml            # Docker Compose
├── 📄 example_predictions.py        # Usage examples
├── 📄 example_shap_explanation.py   # SHAP examples
├── 📄 README.md                     # Main README
└── 📄 ARCHITECTURE.md               # This file

```

---

## Quick Start

### 1. Installation

```bash
# Navigate to project
cd QNN_Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run API Locally

```bash
cd app/api
python flask_api.py
```

Visit: http://localhost:5000/api/v1

### 3. Make a Prediction

```bash
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "lag1": 0.5, "lag2": 0.3, "vol_lag1": 0.4, "vol_lag2": 0.35,
    "ret_abs": 0.02, "ret_sq": 0.0004, "ma5": 100.5, "ma20": 101.2,
    "std5": 2.1, "std20": 2.3
  }'
```

---

## Components

### Core Module (`app/core/`)

#### `model_loader.py`
- **Purpose:** Load and cache trained model and scaler
- **Key Classes:**
  - `ModelLoader` - Singleton for model management
  - `QuantileLoss` - Custom TensorFlow loss function

```python
from app.core.model_loader import ModelLoader

loader = ModelLoader()
loader.load_model_and_scaler('model.h5', 'scaler.pkl')
model = loader.get_model()
scaler = loader.get_scaler()
```

#### `predictor.py`
- **Purpose:** Main prediction logic
- **Key Classes:**
  - `VolatilityPredictor` - Handles predictions

```python
from app.core.predictor import VolatilityPredictor

predictor = VolatilityPredictor()
predictor.initialize('model.h5', 'scaler.pkl')

# Single prediction
result = predictor.predict(features_dict)

# Batch prediction
results = predictor.predict_batch(features_list)

# From DataFrame
df_with_predictions = predictor.predict_from_dataframe(df)
```

### API Module (`app/api/`)

#### `flask_api.py`
- **Purpose:** REST API endpoints
- **Endpoints:**
  - `GET /health` - Health check
  - `GET /info` - Model info
  - `POST /predict` - Single prediction
  - `POST /predict/batch` - Batch predictions
  - `POST /explain` - SHAP explanation

### Explainability Module (`app/explainability/`)

#### `shap_explainer.py`
- **Purpose:** Model interpretation
- **Key Classes:**
  - `SHAPExplainer` - SHAP-based explanations
  - `LIMEExplainer` - LIME-based explanations

```python
from app.explainability.shap_explainer import SHAPExplainer

explainer = SHAPExplainer(model, background_data)
explanation = explainer.explain_prediction(features, feature_names)
```

### Utilities Module (`app/utils/`)

#### `validators.py`
- Input validation for predictions
- Feature presence and type checking

#### `logger.py`
- Centralized logging configuration
- Console and file output

---

## Usage Examples

### Example 1: Single Prediction

```python
from app.core.predictor import VolatilityPredictor

# Initialize
predictor = VolatilityPredictor()
predictor.initialize('model/model_volatility.h5', 'model/scaler.pkl')

# Define features
features = {
    'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
    'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
    'std5': 2.1, 'std20': 2.3
}

# Predict
result = predictor.predict(features)
print(f"Q10 (10th percentile): {result['q10']:.4f}")
print(f"Q50 (median): {result['q50']:.4f}")
print(f"Q90 (90th percentile): {result['q90']:.4f}")
```

### Example 2: Batch Predictions

```python
from app.core.predictor import VolatilityPredictor

predictor = VolatilityPredictor()
predictor.initialize('model/model_volatility.h5', 'model/scaler.pkl')

# Batch of features
batch = [
    {'lag1': 0.5, ..., 'std20': 2.3},
    {'lag1': 0.4, ..., 'std20': 2.2},
]

# Predict batch
results = predictor.predict_batch(batch)
for i, result in enumerate(results):
    print(f"Sample {i+1}: {result}")
```

### Example 3: DataFrame Predictions

```python
import pandas as pd
from app.core.predictor import VolatilityPredictor

# Load data
df = pd.read_csv('data/data_clean.csv')

# Initialize predictor
predictor = VolatilityPredictor()
predictor.initialize('model/model_volatility.h5', 'model/scaler.pkl')

# Make predictions
predictions_df = predictor.predict_from_dataframe(df)

# Display results
print(predictions_df[['lag1', 'volatility_q10', 'volatility_q50', 'volatility_q90']])

# Save
predictions_df.to_csv('predictions_output.csv', index=False)
```

### Example 4: SHAP Explanations

```python
import numpy as np
from app.core.predictor import VolatilityPredictor
from app.explainability.shap_explainer import SHAPExplainer

# Initialize
predictor = VolatilityPredictor()
predictor.initialize('model/model_volatility.h5', 'model/scaler.pkl')

# Features to explain
features = {
    'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
    'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
    'std5': 2.1, 'std20': 2.3
}

# Prepare features
feature_array = np.array([features[col] for col in predictor.FEATURE_COLUMNS])
scaled_features = predictor.scaler.transform(feature_array.reshape(1, -1))

# Get explanation
explainer = SHAPExplainer(predictor.model, scaled_features)
explanation = explainer.explain_prediction(scaled_features, predictor.FEATURE_COLUMNS)

# Print feature importance
print("Feature Importance (SHAP):")
for feature, importance in explanation['feature_importance'].items():
    print(f"  {feature}: {importance:.4f}")
```

### Example 5: API Usage (Python Requests)

```python
import requests

url = "http://localhost:5000/api/v1/predict"
features = {
    'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
    'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
    'std5': 2.1, 'std20': 2.3
}

response = requests.post(url, json=features)
result = response.json()

print(f"Volatility Q50: {result['q50']:.4f}")
```

---

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t qnn-volatility:latest .

# Run container
docker run -p 5000:5000 qnn-volatility:latest

# Using Docker Compose
docker-compose up -d
```

### Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed cloud deployment instructions:
- AWS (ECS, Lambda, EC2)
- Google Cloud (Cloud Run)
- Azure (Container Instances, App Service)

### Production Setup

1. Use Gunicorn for production WSGI server
2. Configure Nginx as reverse proxy
3. Set up HTTPS/TLS
4. Implement rate limiting
5. Add monitoring and logging
6. Set up database for audit logs

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Model Size | ~50 MB |
| Inference Time (Single) | ~50 ms |
| Inference Time (Batch/100) | ~200 ms |
| Memory Usage | ~2 GB |
| Supported Quantiles | 3 (0.1, 0.5, 0.9) |
| Number of Features | 10 |

---

## Data Features Description

The model uses 10 financial features:

1. **lag1** - Volatility at previous time step
2. **lag2** - Volatility at 2 previous time steps
3. **vol_lag1** - Recent volatility measurement (lag 1)
4. **vol_lag2** - Recent volatility measurement (lag 2)
5. **ret_abs** - Absolute returns
6. **ret_sq** - Squared returns
7. **ma5** - 5-day moving average
8. **ma20** - 20-day moving average
9. **std5** - 5-day standard deviation
10. **std20** - 20-day standard deviation

---

## Evaluation Metrics

The project evaluates model performance using:

- **RMSE** - Root Mean Square Error
- **MAE** - Mean Absolute Error
- **MAPE** - Mean Absolute Percentage Error
- **Quantile Loss** - Specific to quantile regression

---

## Troubleshooting

### Issue: Model Not Loading

**Solution:**
```bash
# Check file exists
ls -la model/model_volatility.h5
ls -la model/scaler.pkl

# Test loading
python -c "import tensorflow as tf; tf.keras.models.load_model('model/model_volatility.h5')"
```

### Issue: Memory Issues

**Solution:**
- Use GPU if available
- Reduce batch size
- Use model quantization

### Issue: Slow Predictions

**Solution:**
- Use batch predictions
- Reduce model size
- Use GPU acceleration

---

## Support & Contact

For issues, questions, or contributions:
1. Check documentation in `docs/` folder
2. Review logs in `logs/` folder
3. Run tests with `pytest`
4. Contact development team

---

## Version History

- **v1.0.0** (2024) - Initial release
  - QNN model
  - REST API
  - Docker support
  - SHAP explanations

---

## License

[Your License Here]

---

## Authors

QNN Project Team

---

Last Updated: 2024
