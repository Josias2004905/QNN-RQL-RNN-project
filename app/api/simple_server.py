"""
Simple Flask server to serve the web interface without ML dependencies
"""

from flask import Flask, render_template
import os

# Initialize Flask app
app = Flask(__name__, template_folder='../templates')

@app.route('/')
def web_interface():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/api/v1/health')
def health_check():
    """Mock health check endpoint"""
    return {
        'status': 'healthy',
        'model_loaded': False,
        'version': '1.0.0'
    }, 200

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    """Mock prediction endpoint"""
    return {
        'q10': 0.125,
        'q50': 0.150,
        'q90': 0.180
    }, 200

@app.route('/api/v1/explain', methods=['POST'])
def explain():
    """Mock explanation endpoint"""
    return {
        'prediction': {
            'q10': 0.125,
            'q50': 0.150,
            'q90': 0.180
        },
        'explanation': {
            'feature_importance': {
                'lag1': 0.025,
                'lag2': 0.018,
                'vol_lag1': 0.032,
                'vol_lag2': 0.028,
                'ret_abs': 0.015,
                'ret_sq': 0.012,
                'ma5': 0.022,
                'ma20': 0.035,
                'std5': 0.020,
                'std20': 0.030
            }
        }
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
