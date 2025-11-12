// ===== ENTERPRISE FORECASTING PLATFORM - MAIN JAVASCRIPT =====
// Professional, Accurate, Corporate-Grade Analytics

const API_BASE = 'http://localhost:5000/api';
let charts = {};
let modelsData = null;
let currentData = null;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    setupSliders();
    await loadInitialData();
    setTimeout(hideLoading, 1200);
});

function hideLoading() {
    const loadingScreen = document.getElementById('loadingScreen');
    loadingScreen.style.opacity = '0';
    setTimeout(() => {
        loadingScreen.style.display = 'none';
    }, 500);
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // CSV Upload
    document.getElementById('uploadCsvBtn').addEventListener('click', openUploadModal);
    document.getElementById('changeSourceBtn').addEventListener('click', openUploadModal);
    document.getElementById('closeModal').addEventListener('click', closeUploadModal);
    document.getElementById('browseBtn').addEventListener('click', () => {
        document.getElementById('csvFileInput').click();
    });
    document.getElementById('csvFileInput').addEventListener('change', handleFileSelect);
    document.getElementById('uploadSubmit').addEventListener('click', uploadFile);
    
    // Export
    document.getElementById('exportBtn').addEventListener('click', exportData);

    // Drag & Drop
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file) {
            document.getElementById('csvFileInput').files = e.dataTransfer.files;
            document.getElementById('selectedFileName').textContent = file.name;
        }
    });

    // Main Actions
    document.getElementById('runAnalysisBtn').addEventListener('click', runComprehensiveAnalysis);
    document.getElementById('resetBtn').addEventListener('click', resetConfiguration);

    // Model Lab
    document.querySelectorAll('.model-select-btn').forEach(btn => {
        btn.addEventListener('click', () => switchModelDashboard(btn.dataset.model));
    });

    document.getElementById('trainNaive')?.addEventListener('click', () => trainSingleModel('Naive'));
    document.getElementById('trainArima')?.addEventListener('click', () => trainSingleModel('ARIMA'));
    document.getElementById('trainRF')?.addEventListener('click', () => trainSingleModel('Random_Forest'));
    document.getElementById('trainXGB')?.addEventListener('click', () => trainSingleModel('XGBoost'));

    // Forecast & Insights
    document.getElementById('generateForecast')?.addEventListener('click', generateForecast);
    document.getElementById('generateInsights')?.addEventListener('click', generateAIInsights);
    document.getElementById('applyThreshold')?.addEventListener('click', applyThreshold);

    // Toast Close
    document.getElementById('toastClose').addEventListener('click', hideToast);
}

function setupSliders() {
    // Test Size Slider
    const testSize = document.getElementById('testSize');
    const testSizeValue = document.getElementById('testSizeValue');
    testSize.addEventListener('input', (e) => {
        testSizeValue.textContent = e.target.value;
    });

    // Forecast Horizon Slider
    const forecastHorizon = document.getElementById('forecastHorizon');
    const forecastHorizonValue = document.getElementById('forecastHorizonValue');
    forecastHorizon.addEventListener('input', (e) => {
        forecastHorizonValue.textContent = e.target.value;
    });

    // MAPE Threshold
    const mapeThreshold = document.getElementById('mapeThreshold');
    const mapeThresholdValue = document.getElementById('mapeThresholdValue');
    mapeThreshold.addEventListener('input', (e) => {
        mapeThresholdValue.textContent = e.target.value + '%';
    });

    // WAPE Threshold
    const wapeThreshold = document.getElementById('wapeThreshold');
    const wapeThresholdValue = document.getElementById('wapeThresholdValue');
    wapeThreshold.addEventListener('input', (e) => {
        wapeThresholdValue.textContent = e.target.value + '%';
    });
}

// ===== TAB SWITCHING =====
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    // Load advanced analytics when switching to that tab
    if (tabName === 'advanced' && modelsData) {
        loadSeasonalDecomposition();
        loadFeatureImportance();
        loadAdvancedAnalytics();
    }
}

// ===== DATA LOADING =====
async function loadInitialData() {
    updateStatus('Loading data...', 'loading');
    try {
        const response = await fetch(`${API_BASE}/load-data`);
        const data = await response.json();
        
        if (data.success) {
            currentData = data;
            updateHeroStats(data);
            renderHistoricalChart(data);
            updateDataExploration(data);
            showToast('Data Loaded', 'Enterprise data loaded successfully', 'success');
            updateStatus('Ready', 'ready');
        } else {
            showToast('Error', 'Failed to load data', 'error');
            updateStatus('Error', 'error');
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showToast('Error', 'Network error loading data', 'error');
        updateStatus('Error', 'error');
    }
}

function updateHeroStats(data) {
    // Average Sales
    const avgSales = data.stats.avg_sales;
    document.getElementById('statAvgSales').textContent = `$${(avgSales / 1000).toFixed(1)}K`;
    
    // Growth Rate
    const growthRate = data.stats.growth_rate;
    document.getElementById('statGrowth').textContent = `${growthRate > 0 ? '+' : ''}${growthRate.toFixed(1)}%`;
    
    // Period
    const startDate = new Date(data.stats.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
    const endDate = new Date(data.stats.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
    document.getElementById('statPeriod').textContent = `${startDate} - ${endDate}`;
    
    // Update data source info
    document.getElementById('dataPoints').textContent = `${data.stats.total_months} months`;
}

function updateDataExploration(data) {
    document.getElementById('dataPointsCount').textContent = data.stats.total_months;
    
    const startDate = new Date(data.stats.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
    const endDate = new Date(data.stats.end_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
    document.getElementById('dateRange').textContent = `${startDate} - ${endDate}`;
    
    document.getElementById('meanSales').textContent = `$${(data.stats.avg_sales / 1000).toFixed(1)}K`;
    document.getElementById('stdSales').textContent = `$${(data.stats.std_sales / 1000).toFixed(1)}K`;
    
    // Features Overview
    if (data.features) {
        const featuresHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                    <h4 style="color: var(--primary-blue); margin-bottom: 0.5rem;">
                        <i class="fas fa-clock"></i> Lag Features
                    </h4>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">
                        ${data.features.lag_features?.join(', ') || 'Not available'}
                    </p>
                </div>
                <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                    <h4 style="color: var(--accent-teal); margin-bottom: 0.5rem;">
                        <i class="fas fa-calendar"></i> Seasonal Features
                    </h4>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">
                        ${data.features.seasonal_features?.join(', ') || 'Month, Quarter indicators'}
                    </p>
                </div>
                <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                    <h4 style="color: var(--accent-emerald); margin-bottom: 0.5rem;">
                        <i class="fas fa-chart-line"></i> Rolling Statistics
                    </h4>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">
                        ${data.features.rolling_features?.join(', ') || '3-month MA, 6-month MA'}
                    </p>
                </div>
            </div>
        `;
        document.getElementById('featuresOverview').innerHTML = featuresHTML;
    }
}

// ===== CHART RENDERING =====
function renderHistoricalChart(data) {
    const ctx = document.getElementById('historicalChart').getContext('2d');
    
    if (charts.historical) {
        charts.historical.destroy();
    }
    
    charts.historical = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.historical_data.dates,
            datasets: [{
                label: 'Sales',
                data: data.historical_data.sales,
                borderColor: '#1E3A8A',
                backgroundColor: 'rgba(30, 58, 138, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#1E3A8A'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#0F172A',
                    bodyColor: '#475569',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Sales: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94A3B8'
                    }
                },
                y: {
                    grid: {
                        color: '#F1F5F9'
                    },
                    ticks: {
                        color: '#94A3B8',
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                }
            }
        }
    });
}

// ===== COMPREHENSIVE ANALYSIS =====
async function runComprehensiveAnalysis() {
    // Get selected models
    const selectedModels = [];
    if (document.getElementById('modelNaive').checked) selectedModels.push('Naive');
    if (document.getElementById('modelArima').checked) selectedModels.push('ARIMA');
    if (document.getElementById('modelRF').checked) selectedModels.push('Random_Forest');
    if (document.getElementById('modelXGB').checked) selectedModels.push('XGBoost');
    
    if (selectedModels.length === 0) {
        showToast('Error', 'Please select at least one model', 'error');
        return;
    }
    
    const testSize = parseInt(document.getElementById('testSize').value);
    
    updateStatus('Training models...', 'loading');
    showToast('Training', `Training ${selectedModels.length} models...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/train-models`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                models: selectedModels,
                test_size: testSize
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            modelsData = data;
            renderOverviewResults(data);
            renderComparisonChart(data);
            
            // Load advanced analytics
            loadSeasonalDecomposition();
            loadFeatureImportance();
            loadAdvancedAnalytics();
            
            updateStatus('Analysis complete', 'ready');
            showToast('Success', `All ${selectedModels.length} models trained successfully!`, 'success');
            
            // Switch to overview tab to show results
            switchTab('overview');
        } else {
            showToast('Error', data.message || 'Training failed', 'error');
            updateStatus('Error', 'error');
        }
    } catch (error) {
        console.error('Error training models:', error);
        showToast('Error', 'Network error during training', 'error');
        updateStatus('Error', 'error');
    }
}

function renderOverviewResults(data) {
    // Update metrics
    const bestModel = data.metrics.reduce((best, current) => 
        current.MAPE < best.MAPE ? current : best
    );
    
    document.getElementById('bestMAPE').textContent = bestModel.MAPE.toFixed(2) + '%';
    
    const avgMAPE = data.metrics.reduce((sum, m) => sum + m.MAPE, 0) / data.metrics.length;
    document.getElementById('avgAccuracy').textContent = (100 - avgMAPE).toFixed(1) + '%';
    
    document.getElementById('topModel').textContent = bestModel.Model;
    document.getElementById('modelsTrained').textContent = `${data.metrics.length}/4`;
    
    // Render overview chart
    renderOverviewChart(data);
    
    // Render metrics table
    renderMetricsTable(data.metrics);
}

function renderOverviewChart(data) {
    const ctx = document.getElementById('overviewChart').getContext('2d');
    
    if (charts.overview) {
        charts.overview.destroy();
    }
    
    const colors = {
        'Naive': '#1E3A8A',
        'ARIMA': '#0891B2',
        'Random_Forest': '#059669',
        'XGBoost': '#D97706'
    };
    
    const datasets = [{
        label: 'Actual Sales',
        data: data.actual,
        borderColor: '#E11D48',
        backgroundColor: 'rgba(225, 29, 72, 0.1)',
        borderWidth: 3,
        fill: false,
        tension: 0.4,
        pointRadius: 5
    }];
    
    Object.keys(data.predictions).forEach(model => {
        datasets.push({
            label: model,
            data: data.predictions[model],
            borderColor: colors[model] || '#94A3B8',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            tension: 0.4,
            pointRadius: 3
        });
    });
    
    charts.overview = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.test_dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#0F172A',
                    bodyColor: '#475569',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94A3B8'
                    }
                },
                y: {
                    grid: {
                        color: '#F1F5F9'
                    },
                    ticks: {
                        color: '#94A3B8',
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                }
            }
        }
    });
}

function renderMetricsTable(metrics) {
    const tbody = document.getElementById('metricsTableBody');
    tbody.innerHTML = '';
    
    const bestModel = metrics.reduce((best, current) => 
        current.MAPE < best.MAPE ? current : best
    );
    
    metrics.forEach(metric => {
        const row = document.createElement('tr');
        if (metric.Model === bestModel.Model) {
            row.classList.add('best-row');
        }
        
        row.innerHTML = `
            <td><strong>${metric.Model}</strong></td>
            <td>${metric.MAPE.toFixed(2)}%</td>
            <td>${metric.WAPE.toFixed(2)}%</td>
            <td>$${metric.MAE.toFixed(0)}</td>
            <td>$${metric.RMSE.toFixed(0)}</td>
            <td>
                ${metric.Model === bestModel.Model ? 
                    '<span class="badge badge-success">Best Model</span>' : 
                    (metric.MAPE < 15 ? 
                        '<span class="badge badge-primary">Good</span>' : 
                        '<span class="badge badge-warning">Fair</span>'
                    )
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderComparisonChart(data) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    if (charts.comparison) {
        charts.comparison.destroy();
    }
    
    charts.comparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.metrics.map(m => m.Model),
            datasets: [{
                label: 'MAPE (%)',
                data: data.metrics.map(m => m.MAPE),
                backgroundColor: '#3B82F6',
                borderRadius: 6
            }, {
                label: 'WAPE (%)',
                data: data.metrics.map(m => m.WAPE),
                backgroundColor: '#0891B2',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#0F172A',
                    bodyColor: '#475569',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#F1F5F9'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// ===== SINGLE MODEL TRAINING =====
async function trainSingleModel(modelName) {
    // Check if data is loaded
    if (!currentData) {
        showToast('Error', 'Please load data first. Click "Run Comprehensive Analysis" or reload the page.', 'error');
        return;
    }
    
    const testSize = parseInt(document.getElementById('testSize').value);
    
    updateStatus(`Training ${modelName}...`, 'loading');
    showToast('Training', `Training ${modelName} model...`, 'info');
    
    console.log('[DEBUG] Training model:', modelName);
    console.log('[DEBUG] Test size:', testSize);
    
    try {
        const response = await fetch(`${API_BASE}/train-single-model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: modelName,
                test_size: testSize,
                parameters: {}
            })
        });
        
        // Check if response is ok
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: `HTTP ${response.status}: ${response.statusText}` }));
            const errorMsg = errorData.message || errorData.error || `Server error: ${response.status}`;
            console.error(`Training error for ${modelName}:`, errorMsg);
            showToast('Error', errorMsg, 'error');
            updateStatus('Ready', 'ready');
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderSingleModelResults(modelName, data);
            updateStatus('Ready', 'ready');
            showToast('Success', `${modelName} trained successfully!`, 'success');
        } else {
            const errorMsg = data.message || data.error || 'Training failed';
            console.error(`Training error for ${modelName}:`, errorMsg);
            showToast('Error', errorMsg, 'error');
            updateStatus('Ready', 'ready');
        }
    } catch (error) {
        console.error(`Network error training ${modelName}:`, error);
        const errorMsg = error.message || 'Network error during training. Please check if the server is running.';
        showToast('Error', errorMsg, 'error');
        updateStatus('Ready', 'ready');
    }
}

function renderSingleModelResults(modelName, data) {
    // Map model names to HTML IDs
    const modelIdMap = {
        'Naive': 'naive',
        'ARIMA': 'arima',
        'Random_Forest': 'rf',
        'XGBoost': 'xgb'
    };
    
    const modelId = modelIdMap[modelName] || modelName.toLowerCase();
    const resultsDiv = document.getElementById(`${modelId}Results`);
    const metric = data.metrics;
    
    resultsDiv.innerHTML = `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">MAPE</div>
                <div class="metric-value">${metric.MAPE.toFixed(2)}%</div>
                <div class="metric-change ${metric.MAPE < 15 ? 'positive' : ''}">
                    <i class="fas fa-${metric.MAPE < 15 ? 'check-circle' : 'info-circle'}"></i>
                    ${metric.MAPE < 15 ? 'Excellent' : 'Good'}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">WAPE</div>
                <div class="metric-value">${metric.WAPE.toFixed(2)}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">MAE</div>
                <div class="metric-value">$${metric.MAE.toFixed(0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">RMSE</div>
                <div class="metric-value">$${metric.RMSE.toFixed(0)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">R² Score</div>
                <div class="metric-value">${metric.R2_Score.toFixed(4)}</div>
            </div>
        </div>
        
        <div class="chart-section mt-4">
            <div class="chart-header">
                <h3 class="chart-title">
                    <i class="fas fa-chart-line"></i>
                    Actual vs Predicted
                </h3>
            </div>
            <div class="chart-container">
                <canvas id="${modelId}SingleChart"></canvas>
            </div>
        </div>
    `;
    
    // Render chart
    setTimeout(() => {
        const ctx = document.getElementById(`${modelId}SingleChart`).getContext('2d');
        const chartKey = `${modelId}Single`;
        
        if (charts[chartKey]) {
            charts[chartKey].destroy();
        }
        
        charts[chartKey] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.test_dates,
                datasets: [{
                    label: 'Actual',
                    data: data.actual,
                    borderColor: '#E11D48',
                    backgroundColor: 'rgba(225, 29, 72, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 5
                }, {
                    label: 'Predicted',
                    data: data.predictions,
                    borderColor: '#1E3A8A',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        titleColor: '#0F172A',
                        bodyColor: '#475569',
                        borderColor: '#E2E8F0',
                        borderWidth: 1,
                        padding: 12
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        grid: {
                            color: '#F1F5F9'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }, 100);
}

// ===== FORECAST GENERATION =====
async function generateForecast() {
    if (!modelsData) {
        showToast('Error', 'Please run analysis first', 'error');
        return;
    }
    
    const selectedModel = document.getElementById('forecastModel').value;
    const months = parseInt(document.getElementById('forecastMonths').value);
    
    updateStatus('Generating forecast...', 'loading');
    showToast('Forecasting', 'Generating future predictions...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/generate-forecast`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                months: months,
                model_name: selectedModel
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderForecastResults(data);
            updateStatus('Ready', 'ready');
            showToast('Success', 'Forecast generated successfully!', 'success');
        } else {
            showToast('Error', data.message || 'Forecast failed', 'error');
            updateStatus('Ready', 'ready');
        }
    } catch (error) {
        console.error('Error generating forecast:', error);
        showToast('Error', 'Network error during forecast', 'error');
        updateStatus('Ready', 'ready');
    }
}

function renderForecastResults(data) {
    // Show forecast chart section
    document.getElementById('forecastChartSection').style.display = 'block';
    document.getElementById('scenariosSection').style.display = 'block';
    
    // Render forecast chart
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    if (charts.forecast) {
        charts.forecast.destroy();
    }
    
    // Combine historical and forecast data
    const allLabels = [...currentData.historical_data.dates, ...data.forecast_dates];
    const historicalData = [...currentData.historical_data.sales, ...Array(data.forecast_values.length).fill(null)];
    const forecastData = [...Array(currentData.historical_data.sales.length).fill(null), ...data.forecast_values];
    
    charts.forecast = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [{
                label: 'Historical Sales',
                data: historicalData,
                borderColor: '#1E3A8A',
                backgroundColor: 'rgba(30, 58, 138, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }, {
                label: 'Forecasted Sales',
                data: forecastData,
                borderColor: '#059669',
                backgroundColor: 'rgba(5, 150, 105, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#059669'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#0F172A',
                    bodyColor: '#475569',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            if (context.parsed.y === null) return null;
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: '#F1F5F9'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                }
            }
        }
    });
    
    // Render scenario analysis
    const avgForecast = data.forecast_values.reduce((a, b) => a + b, 0) / data.forecast_values.length;
    const bestCase = avgForecast * 1.15;
    const worstCase = avgForecast * 0.85;
    
    document.getElementById('scenariosGrid').innerHTML = `
        <div class="scenario-card">
            <div class="scenario-name">Best Case Scenario</div>
            <div class="scenario-value">$${(bestCase / 1000).toFixed(1)}K</div>
            <div class="scenario-description">+15% optimistic projection</div>
        </div>
        <div class="scenario-card">
            <div class="scenario-name">Base Scenario</div>
            <div class="scenario-value">$${(avgForecast / 1000).toFixed(1)}K</div>
            <div class="scenario-description">Model prediction</div>
        </div>
        <div class="scenario-card">
            <div class="scenario-name">Worst Case Scenario</div>
            <div class="scenario-value">$${(worstCase / 1000).toFixed(1)}K</div>
            <div class="scenario-description">-15% conservative projection</div>
        </div>
    `;
}

// ===== AI INSIGHTS =====
async function generateAIInsights() {
    if (!modelsData) {
        showToast('Error', 'Please run analysis first', 'error');
        return;
    }
    
    updateStatus('Generating AI insights...', 'loading');
    showToast('AI Processing', 'Gemini AI analyzing results...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/ai-insights`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                metrics_df: modelsData.metrics,
                best_model: modelsData.best_model,
                actual_data: modelsData.actual,
                predictions_dict: modelsData.predictions
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderAIInsights(data.insights);
            updateStatus('Ready', 'ready');
            showToast('Success', 'AI insights generated!', 'success');
        } else {
            showToast('Error', data.message || 'AI insights failed', 'error');
            updateStatus('Ready', 'ready');
        }
    } catch (error) {
        console.error('Error generating AI insights:', error);
        showToast('Error', 'Network error during AI processing', 'error');
        updateStatus('Ready', 'ready');
    }
}

function renderAIInsights(insights) {
    // Clean up the insights text for better display
    let cleanedInsights = insights;
    
    // Convert markdown-style headers to HTML
    cleanedInsights = cleanedInsights.replace(/^### (.*$)/gim, '<h3 style="color: #3B82F6; margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1.25rem; font-weight: 600;">$1</h3>');
    cleanedInsights = cleanedInsights.replace(/^## (.*$)/gim, '<h2 style="color: #60A5FA; margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700;">$1</h2>');
    cleanedInsights = cleanedInsights.replace(/^# (.*$)/gim, '<h1 style="color: #3B82F6; margin-top: 2rem; margin-bottom: 1rem; font-size: 2rem; font-weight: 800;">$1</h1>');
    
    // Convert bullet points
    cleanedInsights = cleanedInsights.replace(/^[-*] (.*$)/gim, '<li style="margin-left: 1.5rem; margin-bottom: 0.5rem;">$1</li>');
    cleanedInsights = cleanedInsights.replace(/(<li.*<\/li>)/gim, '<ul style="list-style-type: disc; margin-top: 0.5rem; margin-bottom: 1rem;">$1</ul>');
    
    // Convert numbered lists
    cleanedInsights = cleanedInsights.replace(/^\d+\. (.*$)/gim, '<li style="margin-left: 1.5rem; margin-bottom: 0.5rem;">$1</li>');
    
    // Convert line breaks
    cleanedInsights = cleanedInsights.replace(/\n\n/g, '</p><p style="margin-bottom: 1rem; line-height: 1.6;">');
    cleanedInsights = cleanedInsights.replace(/\n/g, '<br>');
    
    // Wrap in paragraph tags
    cleanedInsights = '<p style="margin-bottom: 1rem; line-height: 1.6; color: #E2E8F0;">' + cleanedInsights + '</p>';
    
    document.getElementById('aiInsightsContent').innerHTML = cleanedInsights;
}

// ===== THRESHOLD FILTERING =====
function applyThreshold() {
    if (!modelsData) {
        showToast('Error', 'Please run analysis first', 'error');
        return;
    }
    
    const mapeThreshold = parseFloat(document.getElementById('mapeThreshold').value);
    const wapeThreshold = parseFloat(document.getElementById('wapeThreshold').value);
    
    const passing = modelsData.metrics.filter(m => m.MAPE <= mapeThreshold && m.WAPE <= wapeThreshold);
    const failing = modelsData.metrics.filter(m => m.MAPE > mapeThreshold || m.WAPE > wapeThreshold);
    
    let html = '<div class="model-params-section mt-4"><h3 class="chart-title"><i class="fas fa-check-circle"></i> Threshold Results</h3>';
    
    html += '<h4 style="color: var(--accent-emerald); margin-top: 1.5rem;">✓ Passing Models</h4>';
    if (passing.length > 0) {
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">';
        passing.forEach(m => {
            html += `
                <div style="background: rgba(5, 150, 105, 0.1); padding: 1rem; border-radius: var(--radius-md); border-left: 4px solid var(--accent-emerald);">
                    <div style="font-weight: 700; margin-bottom: 0.5rem;">${m.Model}</div>
                    <div style="font-size: 0.875rem;">MAPE: ${m.MAPE.toFixed(2)}%</div>
                    <div style="font-size: 0.875rem;">WAPE: ${m.WAPE.toFixed(2)}%</div>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += '<p style="color: var(--text-tertiary); margin-top: 1rem;">No models passed the thresholds</p>';
    }
    
    html += '<h4 style="color: var(--accent-rose); margin-top: 1.5rem;">✗ Failing Models</h4>';
    if (failing.length > 0) {
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">';
        failing.forEach(m => {
            html += `
                <div style="background: rgba(225, 29, 72, 0.1); padding: 1rem; border-radius: var(--radius-md); border-left: 4px solid var(--accent-rose);">
                    <div style="font-weight: 700; margin-bottom: 0.5rem;">${m.Model}</div>
                    <div style="font-size: 0.875rem;">MAPE: ${m.MAPE.toFixed(2)}%</div>
                    <div style="font-size: 0.875rem;">WAPE: ${m.WAPE.toFixed(2)}%</div>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += '<p style="color: var(--text-tertiary); margin-top: 1rem;">All models passed the thresholds</p>';
    }
    
    html += '</div>';
    
    document.getElementById('thresholdResults').innerHTML = html;
    showToast('Success', 'Threshold filter applied', 'success');
}

// ===== ADVANCED ANALYTICS =====
async function loadSeasonalDecomposition() {
    try {
        const response = await fetch(`${API_BASE}/seasonality-analysis`);
        const data = await response.json();
        
        if (data.success) {
            renderSeasonalChart(data);
        } else {
            console.error('Seasonality analysis failed:', data.message);
        }
    } catch (error) {
        console.error('Error loading seasonality:', error);
    }
}

async function loadFeatureImportance() {
    try {
        const response = await fetch(`${API_BASE}/feature-importance`);
        const data = await response.json();
        
        if (data.success) {
            renderFeatureImportanceChart(data);
        } else {
            console.error('Feature importance failed:', data.message);
            // Show message in the chart area
            const canvas = document.getElementById('featureImportanceChart');
            const container = canvas.parentElement;
            container.innerHTML = `
                <div style="padding: 3rem; text-align: center; color: var(--text-tertiary);">
                    <i class="fas fa-info-circle" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>${data.message || 'Please train ML models first'}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading feature importance:', error);
    }
}

async function loadAdvancedAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/advanced-analytics`);
        const data = await response.json();
        
        if (data.success) {
            // Update the metric cards
            document.getElementById('trendStrength').textContent = data.trend_strength || '-';
            document.getElementById('seasonalityDetected').textContent = data.seasonality_detected || '-';
            document.getElementById('bestFeature').textContent = data.best_feature || '-';
            document.getElementById('modelConsensus').textContent = data.model_consensus || '-';
        } else {
            console.error('Advanced analytics failed:', data.message);
        }
    } catch (error) {
        console.error('Error loading advanced analytics:', error);
    }
}

function renderSeasonalChart(data) {
    const ctx = document.getElementById('seasonalityChart');
    
    if (charts['seasonal']) {
        charts['seasonal'].destroy();
    }
    
    charts['seasonal'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.seasonal_data.dates,
            datasets: [{
                label: 'Seasonal Component',
                data: data.seasonal_data.seasonal_component,
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: `Seasonality Strength: ${data.seasonality_strength.toFixed(2)}% | Growth Rate: ${data.growth_rate.toFixed(2)}% | Peak: ${data.peak_month}`,
                    color: '#E2E8F0',
                    font: {
                        size: 13,
                        weight: '500'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#E2E8F0',
                    bodyColor: '#CBD5E1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94A3B8',
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    },
                    ticks: {
                        color: '#94A3B8'
                    }
                }
            }
        }
    });
}

function renderFeatureImportanceChart(data) {
    const ctx = document.getElementById('featureImportanceChart');
    
    if (charts['featureImportance']) {
        charts['featureImportance'].destroy();
    }
    
    // Take top 10 features
    const topFeatures = data.features.slice(0, 10);
    const topImportances = data.importances.slice(0, 10);
    
    charts['featureImportance'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topFeatures,
            datasets: [{
                label: 'Importance',
                data: topImportances,
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                borderColor: '#8B5CF6',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: `Feature Importance - ${data.model_name.replace('_', ' ')}`,
                    color: '#FFFFFF',
                    font: {
                        size: 16,
                        weight: '700'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#E2E8F0',
                    bodyColor: '#CBD5E1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return `Importance: ${(context.parsed.x * 100).toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    },
                    ticks: {
                        color: '#94A3B8',
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94A3B8',
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// ===== MODEL LAB =====
function switchModelDashboard(modelName) {
    document.querySelectorAll('.model-select-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-model="${modelName}"]`).classList.add('active');
    
    document.querySelectorAll('.model-dashboard').forEach(dash => {
        dash.classList.remove('active');
    });
    document.querySelector(`.model-dashboard[data-model="${modelName}"]`).classList.add('active');
}

// ===== CSV UPLOAD =====
function openUploadModal() {
    document.getElementById('uploadModal').classList.add('active');
}

function closeUploadModal() {
    document.getElementById('uploadModal').classList.remove('active');
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('selectedFileName').textContent = file.name;
    }
}

async function uploadFile() {
    const fileInput = document.getElementById('csvFileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Error', 'Please select a CSV file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    updateStatus('Uploading...', 'loading');
    showToast('Uploading', 'Processing CSV file...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/upload-csv`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            closeUploadModal();
            await loadInitialData();
            showToast('Success', 'CSV uploaded and loaded successfully!', 'success');
            document.getElementById('currentSource').textContent = 'Uploaded CSV';
            document.getElementById('fileName').textContent = file.name;
        } else {
            showToast('Error', data.message || 'Upload failed', 'error');
            updateStatus('Ready', 'ready');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        showToast('Error', 'Network error during upload', 'error');
        updateStatus('Ready', 'ready');
    }
}

// ===== EXPORT DATA =====
async function exportData() {
    if (!modelsData) {
        showToast('Error', 'Please run analysis first to export results', 'error');
        return;
    }
    
    updateStatus('Exporting...', 'loading');
    showToast('Exporting', 'Preparing export file...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/export-data`, {
            method: 'GET'
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: `HTTP ${response.status}` }));
            throw new Error(errorData.message || 'Export failed');
        }
        
        // Get the filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'forecast_export.csv';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        // Get the CSV content
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        updateStatus('Ready', 'ready');
        showToast('Success', 'Data exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting data:', error);
        showToast('Error', error.message || 'Export failed', 'error');
        updateStatus('Ready', 'ready');
    }
}

// ===== UTILITIES =====
function updateStatus(text, type) {
    const statusText = document.getElementById('statusText');
    const statusDot = document.getElementById('statusDot');
    
    statusText.textContent = text;
    
    statusDot.style.background = 
        type === 'ready' ? '#059669' : 
        type === 'loading' ? '#D97706' : 
        type === 'error' ? '#E11D48' : '#94A3B8';
}

function showToast(title, message, type) {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    // Set icon
    const iconClass = 
        type === 'success' ? 'fa-check-circle' : 
        type === 'error' ? 'fa-exclamation-circle' : 
        type === 'warning' ? 'fa-exclamation-triangle' : 
        'fa-info-circle';
    toastIcon.innerHTML = `<i class="fas ${iconClass}"></i>`;
    
    // Set class
    toast.className = 'toast';
    toast.classList.add(type);
    toast.classList.add('show');
    
    // Auto hide after 4 seconds
    setTimeout(hideToast, 4000);
}

function hideToast() {
    document.getElementById('toast').classList.remove('show');
}

function resetConfiguration() {
    document.getElementById('testSize').value = 3;
    document.getElementById('testSizeValue').textContent = 3;
    document.getElementById('forecastHorizon').value = 3;
    document.getElementById('forecastHorizonValue').textContent = 3;
    document.getElementById('modelNaive').checked = true;
    document.getElementById('modelArima').checked = true;
    document.getElementById('modelRF').checked = true;
    document.getElementById('modelXGB').checked = true;
    showToast('Reset', 'Configuration reset to defaults', 'info');
}
