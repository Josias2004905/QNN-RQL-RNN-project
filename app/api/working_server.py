"""
Working Flask server with mock predictions for testing the interface
"""

from flask import Flask, request, jsonify, render_template
import random
import os

# Initialize Flask app
app = Flask(__name__, template_folder='../templates')

@app.route('/')
def web_interface():
    """Serve the web interface"""
    return render_template('enterprise_dashboard_v2.html')

@app.route('/api/v1/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'model_loaded': True,
        'version': '1.0.0'
    }, 200

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    """Mock prediction with realistic values based on input"""
    try:
        data = request.get_json()
        
        # Generate realistic predictions based on input values
        base_volatility = 0.15
        
        # Adjust based on input features
        if data:
            # Use input values to influence predictions
            lag_influence = (data.get('lag1', 0) + data.get('lag2', 0)) * 0.1
            vol_influence = (data.get('vol_lag1', 0) + data.get('vol_lag2', 0)) * 0.15
            ret_influence = data.get('ret_abs', 0) * 2.0
            
            base_volatility += lag_influence + vol_influence + ret_influence
            base_volatility = max(0.05, min(0.5, base_volatility))  # Clamp between 0.05 and 0.5
        
        # Generate quantiles with some variance
        q10 = base_volatility * 0.8
        q50 = base_volatility
        q90 = base_volatility * 1.2
        
        # Add small random variations
        q10 += random.uniform(-0.01, 0.01)
        q50 += random.uniform(-0.01, 0.01)
        q90 += random.uniform(-0.01, 0.01)
        
        return {
            'q10': round(q10, 4),
            'q50': round(q50, 4),
            'q90': round(q90, 4)
        }, 200
        
    except Exception as e:
        return {'error': f'Prediction error: {str(e)}'}, 500

@app.route('/api/v1/explain', methods=['POST'])
def explain():
    """Mock explanation with realistic SHAP values"""
    try:
        data = request.get_json()
        
        # Generate base prediction
        prediction_response = predict()[0]
        
        # Generate realistic SHAP values based on input
        feature_importance = {}
        if data:
            for feature, value in data.items():
                # Higher absolute values get higher importance
                importance = abs(value) * random.uniform(0.5, 1.5)
                feature_importance[feature] = round(importance, 4)
        else:
            # Default importance values
            feature_importance = {
                'lag1': 0.025, 'lag2': 0.018, 'vol_lag1': 0.032, 'vol_lag2': 0.028,
                'ret_abs': 0.015, 'ret_sq': 0.012, 'ma5': 0.022, 'ma20': 0.035,
                'std5': 0.020, 'std20': 0.030
            }
        
        return {
            'prediction': prediction_response,
            'explanation': {
                'feature_importance': feature_importance
            }
        }, 200
        
    except Exception as e:
        return {'error': f'Explanation error: {str(e)}'}, 500

@app.route('/api/v1/info')
def model_info():
    """Model information endpoint"""
    return {
        'version': '1.0.0',
        'features': ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20'],
        'quantiles': ['q10', 'q50', 'q90'],
        'model_type': 'Quantile Neural Network (Demo)',
        'description': 'QNN for Financial Volatility Prediction (Demo Mode)'
    }, 200

if __name__ == '__main__':
    print("🚀 Starting QNN Volatility Predictor (Demo Mode)")
    print("📊 Web interface will be available at: http://localhost:5000")
    print("🔧 API endpoints available at: http://localhost:5000/api/v1")
    print("✅ This is a demo version with mock predictions")
    app.run(host='0.0.0.0', port=5000, debug=True)
