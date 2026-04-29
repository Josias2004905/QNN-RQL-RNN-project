# 🚀 Quick Start Guide - Modern Interface

## ⚡ Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- pip or conda
- ~2GB disk space
- ~4GB RAM
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Setup (2 minutes)

```bash
# Navigate to project
cd QNN_Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Application (1 minute)

```bash
cd app/api
python flask_api.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Step 3: Open the Interface (1 minute)

Open your web browser and go to:
```
http://localhost:5000
```

You should see the beautiful modern interface! ✨

### Step 4: Try a Prediction (1 minute)

1. Click "Charger l'exemple" to load sample data
2. Click "Prédire" to make a prediction
3. View the results in the right panel
4. (Optional) Click "Expliquer" for SHAP explanations

---

## 🎯 Quick Features

| Feature | Time | Result |
|---------|------|--------|
| Load Page | <2s | Beautiful dark interface |
| Load Example | <1s | Sample data in inputs |
| Make Prediction | 1-2s | 3 quantile results + chart |
| Get Explanation | 2-3s | Feature importance shown |
| API Health | <1s | Status indicator updates |

---

## 📚 Next Steps

### API Documentation
Visit **http://localhost:5000/api/v1** for interactive API docs

### Python API Usage
```bash
# Batch predictions
python example_predictions.py

# SHAP explanations
python example_shap_explanation.py
```

### Run Tests
```bash
pytest tests/
```

### Docker Deployment

```bash
# Build Docker image
docker build -t qnn-volatility:latest .

# Run container
docker run -p 5000:5000 qnn-volatility:latest

# Or use Docker Compose
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'tensorflow'`

**Solution:**
```bash
pip install tensorflow==2.13.0
```

### Issue: `Model file not found: model/model_volatility.h5`

**Solution:**
- Ensure you're in the correct directory
- Check that model files exist in `model/` folder

### Issue: Port 5000 already in use

**Solution:**
```bash
# Use different port
cd app/api
python -c "from flask_api import app; app.run(port=5001)"
```

---

## 📖 Documentation

- [README.md](../README.md) - Main documentation
- [docs/API.md](../docs/API.md) - API reference
- [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) - Deployment guide
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - Architecture details

---

## 💡 Common Tasks

### Make a Prediction

```python
from app.core.predictor import VolatilityPredictor

predictor = VolatilityPredictor()
predictor.initialize('model/model_volatility.h5', 'model/scaler.pkl')

result = predictor.predict({
    'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
    'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
    'std5': 2.1, 'std20': 2.3
})

print(result)  # {'q10': 0.125, 'q50': 0.150, 'q90': 0.180}
```

### Batch Predictions from CSV

```python
import pandas as pd
from app.core.predictor import VolatilityPredictor

df = pd.read_csv('data/data_clean.csv')

predictor = VolatilityPredictor()
predictor.initialize('model/model_volatility.h5', 'model/scaler.pkl')

results = predictor.predict_from_dataframe(df)
results.to_csv('predictions_output.csv')
```

### Get Model Explanation

```python
import numpy as np
from app.core.predictor import VolatilityPredictor
from app.explainability.shap_explainer import SHAPExplainer

predictor = VolatilityPredictor()
predictor.initialize('model/model_volatility.h5', 'model/scaler.pkl')

features = {'lag1': 0.5, 'lag2': 0.3, ...}
feature_array = np.array([features[col] for col in predictor.FEATURE_COLUMNS])
scaled = predictor.scaler.transform(feature_array.reshape(1, -1))

explainer = SHAPExplainer(predictor.model, scaled)
explanation = explainer.explain_prediction(scaled, predictor.FEATURE_COLUMNS)

print(explanation['feature_importance'])
```

---

## 🎯 API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API status |
| `/info` | GET | Model information |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch predictions |
| `/explain` | POST | SHAP explanation |

---

## 📞 Need Help?

1. Check logs: `cat logs/api.log`
2. Read documentation in `docs/` folder
3. Run tests: `pytest tests/`
4. Review examples: `example_*.py`

---

## 🚢 Ready to Deploy?

See [DEPLOYMENT.md](../docs/DEPLOYMENT.md) for:
- Docker deployment
- Cloud deployment (AWS, GCP, Azure)
- Production setup (Nginx, Gunicorn)
- Security configuration

---

**Good luck! 🎉**
