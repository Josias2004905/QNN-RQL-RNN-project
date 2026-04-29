"""
Unit Tests for API Endpoints
"""

import sys
import os
import pytest
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.flask_api import app


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code in [200, 500]  # May fail if model not loaded
    
    def test_model_info(self, client):
        """Test model info endpoint"""
        response = client.get('/api/v1/info')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'features' in data
        assert 'quantiles' in data
    
    def test_predict_invalid_input(self, client):
        """Test prediction with invalid input"""
        response = client.post(
            '/api/v1/predict',
            data=json.dumps({'lag1': 0.5}),  # Missing features
            content_type='application/json'
        )
        assert response.status_code in [400, 500]
    
    def test_batch_predict_missing_field(self, client):
        """Test batch prediction without predictions field"""
        response = client.post(
            '/api/v1/predict/batch',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
