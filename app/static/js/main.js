/**
 * QNN Volatility Predictor - Main JavaScript
 * Handles form submissions, API calls, and chart rendering
 */

const API_BASE = '/api/v1';
let predictionChart = null;
let shapChart = null;

// ============================================
// Document Ready
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkHealth();
    loadExampleData();
});

// ============================================
// Event Listeners
// ============================================

function initializeEventListeners() {
    const form = document.getElementById('predictionForm');
    const explainBtn = document.getElementById('explainBtn');
    const loadExampleBtn = document.getElementById('loadExampleBtn');

    if (form) {
        form.addEventListener('submit', handlePredictionSubmit);
    }

    if (explainBtn) {
        explainBtn.addEventListener('click', handleExplainClick);
    }

    if (loadExampleBtn) {
        loadExampleBtn.addEventListener('click', loadExampleData);
    }
}

// ============================================
// Form Handlers
// ============================================

async function handlePredictionSubmit(e) {
    e.preventDefault();
    await makePrediction(false);
}

async function handleExplainClick(e) {
    e.preventDefault();
    await makePrediction(true);
}

// ============================================
// API Functions
// ============================================

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        const statusLabel = document.getElementById('statusLabel');
        if (statusLabel && data.status === 'healthy') {
            statusLabel.textContent = 'En ligne';
            statusLabel.classList.add('text-emerald-400');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        const statusLabel = document.getElementById('statusLabel');
        if (statusLabel) {
            statusLabel.textContent = 'Erreur';
            statusLabel.classList.add('text-red-400');
        }
    }
}

async function makePrediction(getExplanation = false) {
    const formData = {};
    const fields = ['lag1', 'lag2', 'vol_lag1', 'vol_lag2', 'ret_abs', 'ret_sq', 'ma5', 'ma20', 'std5', 'std20'];
    
    // Collect form data
    fields.forEach(field => {
        const element = document.getElementById(field);
        if (element) {
            formData[field] = parseFloat(element.value);
        }
    });

    // Validate data
    if (!validateFormData(formData, fields)) {
        alert('Veuillez remplir tous les champs correctement');
        return;
    }

    try {
        // Show loading state
        showLoadingState();

        const endpoint = getExplanation ? `${API_BASE}/explain` : `${API_BASE}/predict`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        displayResults(data.prediction || data);
        
        if (data.explanation && getExplanation) {
            displaySHAPExplanation(data.explanation);
        }

    } catch (error) {
        console.error('Prediction error:', error);
        alert('Erreur: ' + error.message);
    } finally {
        hideLoadingState();
    }
}

// ============================================
// Display Functions
// ============================================

function displayResults(prediction) {
    // Update result values
    document.getElementById('q10Result').textContent = prediction.q10.toFixed(4);
    document.getElementById('q50Result').textContent = prediction.q50.toFixed(4);
    document.getElementById('q90Result').textContent = prediction.q90.toFixed(4);

    // Show results container
    const resultsContainer = document.getElementById('resultsContainer');
    const emptyState = document.getElementById('emptyState');
    
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
        resultsContainer.classList.add('fade-in');
    }
    
    if (emptyState) {
        emptyState.style.display = 'none';
    }

    // Update chart
    updatePredictionChart(prediction);
}

function updatePredictionChart(prediction) {
    const ctx = document.getElementById('predictionChart');
    if (!ctx) return;

    const canvasCtx = ctx.getContext('2d');
    
    if (predictionChart) {
        predictionChart.destroy();
    }

    predictionChart = new Chart(canvasCtx, {
        type: 'bar',
        data: {
            labels: ['Q10 (Pessimiste)', 'Q50 (Médiane)', 'Q90 (Optimiste)'],
            datasets: [{
                label: 'Prédictions de volatilité',
                data: [prediction.q10, prediction.q50, prediction.q90],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(34, 197, 228, 0.7)',
                    'rgba(16, 185, 129, 0.7)'
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(34, 197, 228, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(203, 213, 225, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(203, 213, 225, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#cbd5e1'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.8)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    padding: 12,
                    borderRadius: 8
                }
            }
        }
    });
}

function displaySHAPExplanation(explanation) {
    const explanationContainer = document.getElementById('explanationContainer');
    if (!explanationContainer) return;

    explanationContainer.style.display = 'block';
    explanationContainer.classList.add('fade-in');

    // You can extend this to display more detailed SHAP explanations
    const content = document.getElementById('explanationContent');
    if (content && explanation.feature_importance) {
        content.innerHTML = renderFeatureImportance(explanation.feature_importance);
    }
}

function renderFeatureImportance(featureImportance) {
    const features = Object.entries(featureImportance)
        .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a));

    let html = '<div class="space-y-3">';
    
    features.forEach(([feature, importance]) => {
        const percentage = Math.abs(importance) * 100;
        const color = importance > 0 ? 'from-emerald-600' : 'from-red-600';
        
        html += `
            <div class="space-y-1">
                <div class="flex justify-between items-center text-sm">
                    <span class="font-medium">${feature}</span>
                    <span class="${importance > 0 ? 'text-emerald-400' : 'text-red-400'}">
                        ${importance > 0 ? '+' : ''}${importance.toFixed(4)}
                    </span>
                </div>
                <div class="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div class="bg-gradient-to-r ${color} to-transparent h-full" style="width: ${Math.min(percentage, 100)}%"></div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    return html;
}

// ============================================
// Utility Functions
// ============================================

function loadExampleData() {
    const exampleValues = {
        lag1: 0.05,
        lag2: 0.04,
        vol_lag1: 0.02,
        vol_lag2: 0.018,
        ret_abs: 0.001,
        ret_sq: 0.0001,
        ma5: 0.045,
        ma20: 0.042,
        std5: 0.003,
        std20: 0.0032
    };

    Object.entries(exampleValues).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.value = value;
        }
    });
}

function validateFormData(formData, fields) {
    for (let field of fields) {
        if (!(field in formData) || isNaN(formData[field])) {
            return false;
        }
    }
    return true;
}

function showLoadingState() {
    const buttons = document.querySelectorAll('#predictionForm button[type="submit"], #explainBtn');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.6';
    });
}

function hideLoadingState() {
    const buttons = document.querySelectorAll('#predictionForm button[type="submit"], #explainBtn');
    buttons.forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = '1';
    });
}

// ============================================
// Scroll Functions
// ============================================

function scrollToPredictor() {
    const predictor = document.getElementById('predictor');
    if (predictor) {
        predictor.scrollIntoView({ behavior: 'smooth' });
    }
}
