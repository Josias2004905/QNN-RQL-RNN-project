"""
Unit Tests for Prediction Module
"""

import sys
import os
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.predictor import VolatilityPredictor
from app.utils.validators import PredictionValidator


class TestVolatilityPredictor:
    """Test VolatilityPredictor class"""
    
    @pytest.fixture
    def predictor(self):
        """Fixture for predictor instance"""
        pred = VolatilityPredictor()
        return pred
    
    @pytest.fixture
    def valid_features(self):
        """Fixture for valid features"""
        return {
            'lag1': 0.5, 'lag2': 0.3, 'vol_lag1': 0.4, 'vol_lag2': 0.35,
            'ret_abs': 0.02, 'ret_sq': 0.0004, 'ma5': 100.5, 'ma20': 101.2,
            'std5': 2.1, 'std20': 2.3
        }
    
    def test_feature_columns(self, predictor):
        """Test that feature columns are correctly defined"""
        cols = predictor.get_feature_columns()
        assert len(cols) == 10
        assert 'lag1' in cols
        assert 'std20' in cols
    
    def test_quantiles(self, predictor):
        """Test that quantiles are correctly defined"""
        quants = predictor.get_quantiles()
        assert quants == [0.1, 0.5, 0.9]
    
    def test_validate_features_valid(self, predictor, valid_features):
        """Test feature validation with valid features"""
        # Should not raise
        predictor._validate_features(valid_features)
    
    def test_validate_features_missing(self, predictor):
        """Test feature validation with missing features"""
        incomplete_features = {'lag1': 0.5, 'lag2': 0.3}
        with pytest.raises(ValueError, match="Missing features"):
            predictor._validate_features(incomplete_features)
    
    def test_validate_features_nan(self, predictor, valid_features):
        """Test feature validation with NaN values"""
        invalid_features = valid_features.copy()
        invalid_features['lag1'] = np.nan
        with pytest.raises(ValueError, match="NaN"):
            predictor._validate_features(invalid_features)


class TestPredictionValidator:
    """Test PredictionValidator class"""
    
    def test_validate_features_valid(self):
        """Test validation with valid features"""
        features = {
            'feature1': 1.0,
            'feature2': 2.0,
            'feature3': 3.0
        }
        assert PredictionValidator.validate_features(features, ['feature1', 'feature2', 'feature3'])
    
    def test_validate_features_missing(self):
        """Test validation with missing features"""
        features = {'feature1': 1.0}
        with pytest.raises(ValueError, match="Missing features"):
            PredictionValidator.validate_features(features, ['feature1', 'feature2'])
    
    def test_validate_features_invalid_type(self):
        """Test validation with invalid types"""
        features = {'feature1': 'string_value', 'feature2': 2.0}
        with pytest.raises(ValueError):
            PredictionValidator.validate_features(features, ['feature1', 'feature2'])
    
    def test_validate_batch_features_valid(self):
        """Test batch validation with valid features"""
        batch = [
            {'f1': 1.0, 'f2': 2.0},
            {'f1': 3.0, 'f2': 4.0}
        ]
        assert PredictionValidator.validate_batch_features(batch, ['f1', 'f2'])
    
    def test_validate_batch_features_invalid(self):
        """Test batch validation with invalid features"""
        batch = [
            {'f1': 1.0, 'f2': 2.0},
            {'f1': 3.0}  # Missing f2
        ]
        with pytest.raises(ValueError):
            PredictionValidator.validate_batch_features(batch, ['f1', 'f2'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
