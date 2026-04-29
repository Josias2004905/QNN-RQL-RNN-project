#  Application Structure Overview
##  Module Guide

### 1. **Core Module** (`app/core/`)
**Purpose:** Prediction engine

**Key Files:**
- `model_loader.py` - Singleton model management
- `predictor.py` - VolatilityPredictor class

**Usage:**
```python
from app.core.predictor import VolatilityPredictor

predictor = VolatilityPredictor()
predictor.initialize('model.h5', 'scaler.pkl')
result = predictor.predict(features)
```

### 2. **API Module** (`app/api/`)
**Purpose:** REST API with Flask

**Key Files:**
- `flask_api.py` - 5 Flask-RESTX endpoints

**Endpoints:**
- `GET /health` - Health check
- `GET /info` - Model info
- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch predictions
- `POST /explain` - SHAP explanation

### 3. **Explainability Module** (`app/explainability/`)
**Purpose:** Model interpretation

**Key Files:**
- `shap_explainer.py` - SHAP & LIME explanations

**Usage:**
```python
from app.explainability.shap_explainer import SHAPExplainer

explainer = SHAPExplainer(model, background_data)
explanation = explainer.explain_prediction(features, feature_names)
```

### 4. **Utils Module** (`app/utils/`)
**Purpose:** Helper utilities

**Key Files:**
- `validators.py` - Input validation
- `logger.py` - Logging setup

### 5. **Config Module** (`config/`)
**Purpose:** Configuration management

**Key Files:**
- `config.py` - Dev/prod/test configs

---

