"""
Dual Model API - Supports both QNN and RNN models
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
import os
import sys
import logging
from typing import Dict, Optional

# Add parent directories to path for imports
sys.path.append('../..')
sys.path.append('../core')

# Import predictors
try:
    from app.core.predictor import QNNPredictor, initialize_qnn_predictor, get_qnn_predictor
    from app.core.rnn_predictor import RNNPredictor, initialize_rnn_predictor, get_rnn_predictor
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for development
    QNNPredictor = None
    RNNPredictor = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with static folder
app = Flask(__name__, template_folder='../templates', static_folder='../static', static_url_path='/static')
CORS(app)

# Add web interface route before Flask-RESTX
@app.route('/')
def web_interface():
    """Serve the web interface"""
    return render_template('enterprise_dashboard_v2.html')

# Initialize Flask-RESTX
api = Api(app, version='2.0', title='Dual Model Volatility Prediction API',
          description='API supporting both QNN and RNN models for volatility prediction')

# Global model instances
qnn_predictor: Optional[QNNPredictor] = None
rnn_predictor: Optional[RNNPredictor] = None
current_model = 'qnn'  # Default to QNN

# Model selection namespace
model_ns = Namespace('models', description='Model selection and information')
api.add_namespace(model_ns)

# Prediction namespaces
qnn_ns = Namespace('qnn', description='QNN Model Predictions')
rnn_ns = Namespace('rnn', description='RNN Model Predictions')
dual_ns = Namespace('dual', description='Dual Model Operations')
api.add_namespace(qnn_ns)
api.add_namespace(rnn_ns)
api.add_namespace(dual_ns)

# Data models for API documentation
input_model = api.model('PredictionInput', {
    'lag1': fields.Float(required=True, description='Lag 1 volatility'),
    'lag2': fields.Float(required=True, description='Lag 2 volatility'),
    'vol_lag1': fields.Float(required=True, description='Volume lag 1'),
    'vol_lag2': fields.Float(required=True, description='Volume lag 2'),
    'ret_abs': fields.Float(required=True, description='Absolute return'),
    'ret_sq': fields.Float(required=True, description='Squared return'),
    'ma5': fields.Float(required=True, description='5-day moving average'),
    'ma20': fields.Float(required=True, description='20-day moving average'),
    'std5': fields.Float(required=True, description='5-day standard deviation'),
    'std20': fields.Float(required=True, description='20-day standard deviation')
})

def initialize_models():
    """Initialize both QNN and RNN models"""
    global qnn_predictor, rnn_predictor
    
    try:
        # Initialize QNN predictor
        if QNNPredictor:
            qnn_predictor = initialize_qnn_predictor()
            logger.info("QNN predictor initialized")
        
        # Initialize RNN predictor  
        if RNNPredictor:
            rnn_predictor = initialize_rnn_predictor()
            logger.info("RNN predictor initialized")
            
    except Exception as e:
        logger.error(f"Error initializing models: {e}")

# Model selection endpoints
@model_ns.route('/select')
class ModelSelection(Resource):
    @model_ns.doc('select_model')
    @model_ns.expect(api.model('ModelSelection', {
        'model': fields.String(required=True, description='Model type: qnn or rnn')
    }))
    def post(self):
        """Select the active model for predictions"""
        global current_model
        
        data = request.get_json()
        model_type = data.get('model', '').lower()
        
        if model_type not in ['qnn', 'rnn']:
            return {'error': 'Invalid model type. Use qnn or rnn'}, 400
        
        # Check if selected model is available
        if model_type == 'qnn' and not qnn_predictor:
            return {'error': 'QNN model not available'}, 503
        if model_type == 'rnn' and not rnn_predictor:
            return {'error': 'RNN model not available'}, 503
        
        current_model = model_type
        logger.info(f"Switched to {model_type.upper()} model")
        
        return {
            'message': f'Switched to {model_type.upper()} model',
            'current_model': current_model,
            'model_info': get_current_model_info()
        }

@model_ns.route('/current')
class CurrentModel(Resource):
    @model_ns.doc('get_current_model')
    def get(self):
        """Get information about the currently selected model"""
        return {
            'current_model': current_model,
            'model_info': get_current_model_info(),
            'available_models': get_available_models()
        }

@model_ns.route('/compare')
class ModelComparison(Resource):
    @model_ns.doc('compare_models')
    @model_ns.expect(input_model)
    def post(self):
        """Get predictions from both models for comparison"""
        data = request.get_json()
        
        results = {}
        
        # Get QNN prediction if available
        if qnn_predictor:
            try:
                qnn_result = qnn_predictor.predict(data)
                results['qnn'] = qnn_result
            except Exception as e:
                logger.error(f"QNN prediction error: {e}")
                results['qnn'] = {'error': str(e)}
        
        # Get RNN prediction if available
        if rnn_predictor:
            try:
                rnn_result = rnn_predictor.predict(data)
                results['rnn'] = rnn_result
            except Exception as e:
                logger.error(f"RNN prediction error: {e}")
                results['rnn'] = {'error': str(e)}
        
        if not results:
            return {'error': 'No models available'}, 503
            
        return results

# QNN prediction endpoints
@qnn_ns.route('/predict')
class QNNPrediction(Resource):
    @qnn_ns.doc('qnn_predict')
    @qnn_ns.expect(input_model)
    def post(self):
        """Make prediction using QNN model"""
        if not qnn_predictor:
            return {'error': 'QNN model not available'}, 503
        
        try:
            data = request.get_json()
            result = qnn_predictor.predict(data)
            return result
        except Exception as e:
            logger.error(f"QNN prediction error: {e}")
            return {'error': str(e)}, 500

@qnn_ns.route('/explain')
class QNNExplanation(Resource):
    @qnn_ns.doc('qnn_explain')
    @qnn_ns.expect(input_model)
    def post(self):
        """Get SHAP explanation from QNN model"""
        if not qnn_predictor:
            return {'error': 'QNN model not available'}, 503
        
        try:
            data = request.get_json()
            result = qnn_predictor.predict_with_explanation(data)
            return result
        except Exception as e:
            logger.error(f"QNN explanation error: {e}")
            return {'error': str(e)}, 500

# RNN prediction endpoints
@rnn_ns.route('/predict')
class RNNPrediction(Resource):
    @rnn_ns.doc('rnn_predict')
    @rnn_ns.expect(input_model)
    def post(self):
        """Make prediction using RNN model"""
        if not rnn_predictor:
            return {'error': 'RNN model not available'}, 503
        
        try:
            data = request.get_json()
            result = rnn_predictor.predict(data)
            return result
        except Exception as e:
            logger.error(f"RNN prediction error: {e}")
            return {'error': str(e)}, 500

# Dual model endpoints (uses current selection)
@dual_ns.route('/predict')
class DualPrediction(Resource):
    @dual_ns.doc('dual_predict')
    @dual_ns.expect(input_model)
    def post(self):
        """Make prediction using currently selected model"""
        if current_model == 'qnn':
            if not qnn_predictor:
                return {'error': 'QNN model not available'}, 503
            try:
                data = request.get_json()
                result = qnn_predictor.predict(data)
                result['model_used'] = 'qnn'
                return result
            except Exception as e:
                logger.error(f"QNN prediction error: {e}")
                return {'error': str(e)}, 500
                
        elif current_model == 'rnn':
            if not rnn_predictor:
                return {'error': 'RNN model not available'}, 503
            try:
                data = request.get_json()
                result = rnn_predictor.predict(data)
                result['model_used'] = 'rnn'
                return result
            except Exception as e:
                logger.error(f"RNN prediction error: {e}")
                return {'error': str(e)}, 500
        
        else:
            return {'error': f'Unknown model: {current_model}'}, 400

@dual_ns.route('/explain')
class DualExplanation(Resource):
    @dual_ns.doc('dual_explain')
    @dual_ns.expect(input_model)
    def post(self):
        """Get explanation from currently selected model"""
        if current_model == 'qnn':
            if not qnn_predictor:
                return {'error': 'QNN model not available'}, 503
            try:
                data = request.get_json()
                result = qnn_predictor.predict_with_explanation(data)
                result['model_used'] = 'qnn'
                return result
            except Exception as e:
                logger.error(f"QNN explanation error: {e}")
                return {'error': str(e)}, 500
                
        elif current_model == 'rnn':
            # RNN doesn't have SHAP explanations yet
            return {'error': 'RNN model does not support SHAP explanations yet'}, 503
        
        else:
            return {'error': f'Unknown model: {current_model}'}, 400

# Legacy endpoints for backward compatibility
@api.route('/api/v1/health')
class HealthCheck(Resource):
    def get(self):
        """Health check endpoint"""
        available_models = get_available_models()
        return {
            'status': 'healthy',
            'current_model': current_model,
            'available_models': available_models,
            'model_info': get_current_model_info(),
            'version': '2.0.0'
        }, 200

@api.route('/api/v1/predict', methods=['POST'])
class LegacyPredict(Resource):
    def post(self):
        """Legacy prediction endpoint - uses current model"""
        if current_model == 'qnn' and qnn_predictor:
            try:
                data = request.get_json()
                result = qnn_predictor.predict(data)
                return result
            except Exception as e:
                return {'error': str(e)}, 500
        elif current_model == 'rnn' and rnn_predictor:
            try:
                data = request.get_json()
                result = rnn_predictor.predict(data)
                return result
            except Exception as e:
                return {'error': str(e)}, 500
        else:
            return {'error': 'No model available'}, 503

@api.route('/api/v1/explain', methods=['POST'])
class LegacyExplain(Resource):
    def post(self):
        """Legacy explanation endpoint - uses current model"""
        if current_model == 'qnn' and qnn_predictor:
            try:
                data = request.get_json()
                result = qnn_predictor.predict_with_explanation(data)
                return result
            except Exception as e:
                return {'error': str(e)}, 500
        else:
            return {'error': 'Explanation not available for current model'}, 503

@api.route('/api/v1/info')
class ModelInfo(Resource):
    def get(self):
        """Model information endpoint"""
        return {
            'current_model': current_model,
            'available_models': get_available_models(),
            'model_info': get_current_model_info(),
            'features': ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20'],
            'quantiles': ['q10', 'q50', 'q90'],
            'model_type': 'Dual Model System (QNN + RNN)',
            'description': 'Dual model system supporting both Quantile Neural Networks and Recurrent Neural Networks'
        }, 200

# Helper functions
def get_current_model_info() -> Dict:
    """Get information about the current model"""
    if current_model == 'qnn' and qnn_predictor:
        return qnn_predictor.get_model_info()
    elif current_model == 'rnn' and rnn_predictor:
        return rnn_predictor.get_model_info()
    else:
        return {'error': f'Model {current_model} not available'}

def get_available_models() -> Dict:
    """Get information about available models"""
    available = {}
    
    if qnn_predictor:
        available['qnn'] = {
            'name': 'Quantile Neural Network',
            'ready': qnn_predictor.is_ready(),
            'info': qnn_predictor.get_model_info()
        }
    
    if rnn_predictor:
        available['rnn'] = {
            'name': 'Recurrent Neural Network (LSTM)',
            'ready': rnn_predictor.is_ready(),
            'info': rnn_predictor.get_model_info()
        }
    
    return available

# Initialize models on startup
def initialize_app():
    """Initialize the application"""
    try:
        initialize_models()
        logger.info("Dual model API initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize app: {e}")

if __name__ == '__main__':
    print("🚀 Starting Dual Model Volatility Predictor API")
    print("📊 Web interface will be available at: http://localhost:5000")
    print("🔧 API endpoints available at: http://localhost:5000/api/v1")
    print("🔄 Dual model system supporting QNN and RNN")
    
    initialize_app()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
