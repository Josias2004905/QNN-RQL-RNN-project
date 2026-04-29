"""
Dual Model Demo Server - Supports both QNN and RNN models with mock data
"""

from flask import Flask, request, jsonify, render_template
import random
import os

# Initialize Flask app
app = Flask(__name__, template_folder='../templates')

# Global state
current_model = 'qnn'
available_models = {
    'qnn': {'name': 'Quantile Neural Network', 'ready': True},
    'rnn': {'name': 'Recurrent Neural Network', 'ready': True}
}

# Model specs for display
model_specs = {
    'qnn': {
        'accuracy': '94.7%',
        'latency': '47ms',
        'confidence': '88%',
        'description': 'Quantile Neural Network with SHAP explanations'
    },
    'rnn': {
        'accuracy': '96.3%',
        'latency': '62ms',
        'confidence': '91%',
        'description': 'LSTM-based Recurrent Neural Network'
    }
}

@app.route('/')
def web_interface():
    """Serve the web interface"""
    return render_template('enterprise_dashboard_dual.html')

@app.route('/api/models/select', methods=['POST'])
def select_model():
    """Select the active model"""
    global current_model
    
    data = request.get_json()
    model_type = data.get('model', '').lower()
    
    if model_type not in ['qnn', 'rnn']:
        return {'error': 'Invalid model type. Use qnn or rnn'}, 400
    
    current_model = model_type
    
    return {
        'message': f'Switched to {model_type.upper()} model',
        'current_model': current_model,
        'model_info': model_specs.get(model_type, {})
    }

@app.route('/api/models/current')
def get_current_model():
    """Get current model information"""
    return {
        'current_model': current_model,
        'model_info': model_specs.get(current_model, {}),
        'available_models': available_models
    }

@app.route('/api/models/compare', methods=['POST'])
def compare_models():
    """Get predictions from both models for comparison"""
    data = request.get_json()
    
    # Generate predictions for both models
    qnn_result = generate_prediction(data, 'qnn')
    rnn_result = generate_prediction(data, 'rnn')
    
    return {
        'qnn': qnn_result,
        'rnn': rnn_result
    }

@app.route('/api/v1/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'current_model': current_model,
        'available_models': available_models,
        'model_info': model_specs.get(current_model, {}),
        'version': '2.0.0'
    }, 200

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    """Make prediction using current model"""
    data = request.get_json()
    
    result = generate_prediction(data, current_model)
    result['model_used'] = current_model
    
    return result

@app.route('/api/v1/explain', methods=['POST'])
def explain():
    """Get explanation from current model (QNN only)"""
    data = request.get_json()
    
    if current_model != 'qnn':
        return {'error': 'SHAP explanations only available for QNN model'}, 503
    
    result = generate_prediction(data, current_model)
    result['explanation'] = generate_shap_explanation(data)
    result['model_used'] = current_model
    
    return result

@app.route('/api/v1/info')
def model_info():
    """Model information endpoint"""
    return {
        'current_model': current_model,
        'available_models': available_models,
        'model_info': model_specs.get(current_model, {}),
        'features': ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20'],
        'quantiles': ['q10', 'q50', 'q90'],
        'model_type': 'Dual Model System (QNN + RNN)',
        'description': 'Dual model system supporting both Quantile Neural Networks and Recurrent Neural Networks'
    }, 200

def generate_prediction(data, model_type):
    """Generate mock prediction based on model type and input data"""
    try:
        # Base volatility calculation
        base_volatility = 0.15
        
        # Adjust based on input features
        if data:
            lag_influence = (data.get('lag1', 0) + data.get('lag2', 0)) * 0.1
            vol_influence = (data.get('vol_lag1', 0) + data.get('vol_lag2', 0)) * 0.15
            ret_influence = data.get('ret_abs', 0) * 2.0
            
            base_volatility += lag_influence + vol_influence + ret_influence
            base_volatility = max(0.05, min(0.5, base_volatility))
        
        # Model-specific adjustments
        if model_type == 'qnn':
            # QNN tends to be more conservative
            q10 = base_volatility * 0.82
            q50 = base_volatility * 0.95
            q90 = base_volatility * 1.18
        else:  # RNN
            # RNN tends to be more aggressive
            q10 = base_volatility * 0.78
            q50 = base_volatility * 1.02
            q90 = base_volatility * 1.25
        
        # Add small random variations
        noise = 0.005
        q10 += random.uniform(-noise, noise)
        q50 += random.uniform(-noise, noise)
        q90 += random.uniform(-noise, noise)
        
        return {
            'q10': round(q10, 4),
            'q50': round(q50, 4),
            'q90': round(q90, 4),
            'model_type': model_type.upper()
        }
        
    except Exception as e:
        return {'error': f'Prediction error: {str(e)}'}

def generate_shap_explanation(data):
    """Generate mock SHAP explanation"""
    feature_importance = {}
    
    if data:
        for feature, value in data.items():
            # Higher absolute values get higher importance
            importance = abs(value) * random.uniform(0.5, 1.5)
            # Random sign for positive/negative contribution
            importance *= random.choice([-1, 1])
            feature_importance[feature] = round(importance, 4)
    else:
        # Default importance values
        feature_importance = {
            'lag1': 0.025, 'lag2': 0.018, 'vol_lag1': 0.032, 'vol_lag2': 0.028,
            'ret_abs': 0.015, 'ret_sq': 0.012, 'ma5': 0.022, 'ma20': 0.035,
            'std5': 0.020, 'std20': 0.030
        }
    
    return {
        'feature_importance': feature_importance
    }

if __name__ == '__main__':
    print("🚀 Starting Dual Model Volatility Predictor (Demo Mode)")
    print("📊 Web interface will be available at: http://localhost:5000")
    print("🔄 Dual model system supporting QNN and RNN")
    print("✅ This is a demo version with mock predictions")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
