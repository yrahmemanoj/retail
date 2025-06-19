/**
 * Retail Sales EDA Dashboard
 * Interactive dashboard for exploring retail sales data insights
 */

class RetailDashboard {
    constructor() {
        this.data = null;
        this.charts = {};
        this.currentTheme = 'light';
        this.currentSection = 'overview';
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        this.showLoading();
        
        try {
            await this.loadData();
            this.hideLoading();
            this.renderDashboard();
        } catch (error) {
            this.hideLoading();
            this.showError(error.message);
        }
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });
        
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Refresh data
        document.getElementById('refreshData').addEventListener('click', () => {
            this.refreshData();
        });
        
        // Modal controls
        document.getElementById('closeErrorModal').addEventListener('click', () => {
            this.hideError();
        });
        
        document.getElementById('runAnalysisBtn').addEventListener('click', () => {
            this.runAnalysis();
        });
        
        document.getElementById('retryLoadBtn').addEventListener('click', () => {
            this.init();
        });
        
        // Insight category filters
        document.querySelectorAll('.insight-category').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.currentTarget.dataset.category;
                this.filterInsights(category);
            });
        });
    }
    
    async loadData() {
        try {
            // Load dashboard configuration
            const response = await fetch('../visuals/dashboard_config.json');
            if (!response.ok) {
                throw new Error('Dashboard configuration not found. Please run the EDA analysis first.');
            }
            
            this.data = await response.json();
            
            // Load additional analysis files if needed
            await this.loadAdditionalData();
            
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }
    
    async loadAdditionalData() {
        try {
            // Load statistical analysis
            const statsResponse = await fetch('../visuals/statistical_analysis.json');
            if (statsResponse.ok) {
                this.data.statistical_analysis = await statsResponse.json();
            }
            
            // Load time series analysis
            const tsResponse = await fetch('../visuals/time_series_analysis.json');
            if (tsResponse.ok) {
                this.data.time_series_analysis = await tsResponse.json();
            }
            
            // Load customer product analysis
            const cpResponse = await fetch('../visuals/customer_product_analysis.json');
            if (cpResponse.ok) {
                this.data.customer_product_analysis = await cpResponse.json();
            }
            
            // Load recommendations
            const recResponse = await fetch('../recommendations/recommendations.json');
            if (recResponse.ok) {
                this.data.recommendations = await recResponse.json();
            }
            
        } catch (error) {
            console.warn('Some additional data files could not be loaded:', error);
        }
    }
    
    renderDashboard() {
        this.renderKPIs();
        this.renderCharts();
        this.renderInsights();
        this.renderActionPlan();
        this.renderTopCustomers();
    }
    
    renderKPIs() {
        const kpiGrid = document.getElementById('kpiGrid');
        if (!kpiGrid || !this.data.kpis) return;
        
        kpiGrid.innerHTML = '';
        
        this.data.kpis.forEach(kpi => {
            const kpiCard = document.createElement('div');
            kpiCard.className = 'kpi-card fade-in';
            
            kpiCard.innerHTML = `
                <div class="kpi-icon ${kpi.color}">
                    <i class="fas fa-${kpi.icon}"></i>
                </div>
                <div class="kpi-title">${kpi.title}</div>
                <div class="kpi-value">${kpi.value}</div>
                <div class="kpi-subtitle">${kpi.subtitle}</div>
            `;
            
            kpiGrid.appendChild(kpiCard);
        });
    }
    
    renderCharts() {
        // Overview charts
        this.renderOverviewCharts();
        
        // Revenue charts
        this.renderRevenueCharts();
        
        // Customer charts
        this.renderCustomerCharts();
        
        // Product charts
        this.renderProductCharts();
    }
    
    renderOverviewCharts() {
        // Daily Revenue Chart
        if (this.data.charts?.daily_revenue) {
            this.createChart('overviewRevenueChart', this.data.charts.daily_revenue);
        }
        
        // Customer Segments Chart
        if (this.data.charts?.customer_segments) {
            this.createChart('overviewCustomerChart', this.data.charts.customer_segments);
        }
        
        // Product Performance Chart
        if (this.data.charts?.category_performance) {
            this.createChart('overviewProductChart', this.data.charts.category_performance);
        }
        
        // Weekly Patterns Chart
        if (this.data.charts?.weekly_patterns) {
            this.createChart('overviewWeeklyChart', this.data.charts.weekly_patterns);
        }
    }
    
    renderRevenueCharts() {
        // Revenue Timeline
        if (this.data.charts?.monthly_revenue) {
            this.createChart('revenueTimelineChart', this.data.charts.monthly_revenue);
        }
        
        // Seasonal Revenue
        if (this.data.charts?.seasonal_analysis) {
            this.createChart('seasonalRevenueChart', this.data.charts.seasonal_analysis);
        }
        
        // Revenue Distribution (create from statistical data)
        this.createRevenueDistributionChart();
    }
    
    renderCustomerCharts() {
        // Customer Segments
        if (this.data.charts?.customer_segments) {
            this.createChart('customerSegmentsChart', this.data.charts.customer_segments);
        }
        
        // Demographics
        if (this.data.charts?.gender_analysis) {
            this.createChart('customerDemographicsChart', this.data.charts.gender_analysis);
        }
        
        // Purchase Behavior (create from customer data)
        this.createPurchaseBehaviorChart();
        
        // CLV Chart (create from customer data)
        this.createCLVChart();
    }
    
    renderProductCharts() {
        // Category Performance
        if (this.data.charts?.category_performance) {
            this.createChart('categoryPerformanceChart', this.data.charts.category_performance);
        }
        
        // Market Share
        if (this.data.charts?.market_share) {
            this.createChart('marketShareChart', this.data.charts.market_share);
        }
        
        // Price Analysis (create from product data)
        this.createPriceAnalysisChart();
        
        // Cross-selling (create from customer-product data)
        this.createCrossSellingChart();
    }
    
    createChart(canvasId, chartConfig) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }
        
        const ctx = canvas.getContext('2d');
        
        // Apply theme-appropriate colors
        const themedConfig = this.applyThemeToChart(chartConfig);
        
        this.charts[canvasId] = new Chart(ctx, themedConfig);
    }
    
    applyThemeToChart(config) {
        const isDark = this.currentTheme === 'dark';
        const themedConfig = JSON.parse(JSON.stringify(config));
        
        // Apply theme colors
        if (themedConfig.options) {
            themedConfig.options.plugins = themedConfig.options.plugins || {};
            themedConfig.options.plugins.legend = themedConfig.options.plugins.legend || {};
            themedConfig.options.plugins.legend.labels = themedConfig.options.plugins.legend.labels || {};
            themedConfig.options.plugins.legend.labels.color = isDark ? '#f8fafc' : '#1f2937';
            
            if (themedConfig.options.scales) {
                Object.keys(themedConfig.options.scales).forEach(scaleKey => {
                    themedConfig.options.scales[scaleKey].ticks = themedConfig.options.scales[scaleKey].ticks || {};
                    themedConfig.options.scales[scaleKey].ticks.color = isDark ? '#cbd5e1' : '#6b7280';
                    themedConfig.options.scales[scaleKey].grid = themedConfig.options.scales[scaleKey].grid || {};
                    themedConfig.options.scales[scaleKey].grid.color = isDark ? '#374151' : '#e5e7eb';
                });
            }
        }
        
        return themedConfig;
    }
    
    createRevenueDistributionChart() {
        if (!this.data.statistical_analysis?.descriptive?.Total_Amount) return;
        
        const stats = this.data.statistical_analysis.descriptive.Total_Amount;
        
        const config = {
            type: 'bar',
            data: {
                labels: ['Min', 'Q1', 'Median', 'Q3', 'Max'],
                datasets: [{
                    label: 'Revenue Distribution',
                    data: [stats.min, stats.q1, stats.median, stats.q3, stats.max],
                    backgroundColor: 'rgba(37, 99, 235, 0.8)',
                    borderColor: '#2563eb',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Transaction Value Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        };
        
        this.createChart('revenueDistributionChart', config);
    }
    
    createPurchaseBehaviorChart() {
        if (!this.data.customer_product_analysis?.purchase_patterns?.quantity_distribution) return;
        
        const quantityData = this.data.customer_product_analysis.purchase_patterns.quantity_distribution;
        
        const config = {
            type: 'doughnut',
            data: {
                labels: quantityData.map(item => `${item.quantity} items`),
                datasets: [{
                    data: quantityData.map(item => item.percentage),
                    backgroundColor: [
                        '#2563eb', '#10b981', '#f97316', '#8b5cf6', '#ef4444'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        };
        
        this.createChart('purchaseBehaviorChart', config);
    }
    
    createCLVChart() {
        if (!this.data.customer_product_analysis?.customer_behavior?.clv_segments) return;
        
        const segments = this.data.customer_product_analysis.customer_behavior.clv_segments;
        
        const config = {
            type: 'bar',
            data: {
                labels: Object.keys(segments),
                datasets: [{
                    label: 'Average Customer Value',
                    data: Object.values(segments).map(seg => seg.avg_total_spent),
                    backgroundColor: ['#ef4444', '#f97316', '#10b981'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        };
        
        this.createChart('clvChart', config);
    }
    
    createPriceAnalysisChart() {
        if (!this.data.customer_product_analysis?.purchase_patterns?.price_preferences) return;
        
        const priceData = this.data.customer_product_analysis.purchase_patterns.price_preferences;
        
        const config = {
            type: 'polarArea',
            data: {
                labels: priceData.map(item => item.price_category),
                datasets: [{
                    data: priceData.map(item => item.percentage),
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.7)',
                        'rgba(249, 115, 22, 0.7)',
                        'rgba(37, 99, 235, 0.7)',
                        'rgba(139, 92, 246, 0.7)',
                        'rgba(239, 68, 68, 0.7)'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        };
        
        this.createChart('priceAnalysisChart', config);
    }
    
    createCrossSellingChart() {
        if (!this.data.customer_product_analysis?.customer_product_matrix?.cross_selling_opportunities) return;
        
        const crossSell = this.data.customer_product_analysis.customer_product_matrix.cross_selling_opportunities;
        const opportunities = Object.entries(crossSell).slice(0, 5); // Top 5
        
        const config = {
            type: 'horizontalBar',
            data: {
                labels: opportunities.map(([pair]) => pair),
                datasets: [{
                    label: 'Cross-sell Rate (%)',
                    data: opportunities.map(([, data]) => data.cross_sell_rate),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10b981',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        };
        
        this.createChart('crossSellingChart', config);
    }
    
    renderInsights() {
        const insightsGrid = document.getElementById('insightsMainGrid');
        if (!insightsGrid || !this.data.insights) return;
        
        insightsGrid.innerHTML = '';
        
        this.data.insights.forEach(insight => {
            const insightCard = document.createElement('div');
            insightCard.className = `insight-card ${insight.priority}-priority fade-in`;
            insightCard.dataset.category = insight.category.toLowerCase();
            
            insightCard.innerHTML = `
                <div class="insight-card-header">
                    <div>
                        <div class="insight-card-title">${this.getInsightTitle(insight)}</div>
                        <div class="insight-card-category">${insight.category}</div>
                    </div>
                </div>
                <div class="insight-card-content">
                    ${insight.insight}
                </div>
                <div class="insight-card-recommendation">
                    <strong>Recommendation:</strong> ${insight.recommendation}
                </div>
            `;
            
            insightsGrid.appendChild(insightCard);
        });
    }
    
    getInsightTitle(insight) {
        // Generate a title from the insight text
        const words = insight.insight.split(' ').slice(0, 4);
        return words.join(' ') + (insight.insight.split(' ').length > 4 ? '...' : '');
    }
    
    renderActionPlan() {
        if (!this.data.recommendations?.action_plan) return;
        
        const actionPlan = this.data.recommendations.action_plan;
        
        // Immediate Actions
        this.renderTimelineItems('immediateActions', actionPlan.immediate_actions);
        
        // Short-term Goals
        this.renderTimelineItems('shortTermGoals', actionPlan.short_term_goals);
        
        // Long-term Strategy
        this.renderTimelineItems('longTermStrategy', actionPlan.long_term_strategy);
    }
    
    renderTimelineItems(containerId, items) {
        const container = document.getElementById(containerId);
        if (!container || !items) return;
        
        container.innerHTML = '';
        
        items.forEach(item => {
            const timelineItem = document.createElement('div');
            timelineItem.className = 'timeline-item slide-in';
            
            timelineItem.innerHTML = `
                <div class="timeline-item-title">${item.title}</div>
                <div class="timeline-item-description">${item.description}</div>
            `;
            
            container.appendChild(timelineItem);
        });
    }
    
    renderTopCustomers() {
        if (!this.data.customer_product_analysis?.customer_behavior?.top_customers) return;
        
        const topCustomers = this.data.customer_product_analysis.customer_behavior.top_customers;
        const tableBody = document.querySelector('#topCustomersTable tbody');
        
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        topCustomers.forEach(customer => {
            const row = document.createElement('tr');
            
            // Determine segment based on total spent
            let segment = 'Low Value';
            if (customer.total_spent > 1000) segment = 'High Value';
            else if (customer.total_spent > 500) segment = 'Medium Value';
            
            row.innerHTML = `
                <td>${customer.customer_id}</td>
                <td>$${customer.total_spent.toLocaleString()}</td>
                <td>${customer.transaction_count}</td>
                <td>$${customer.avg_transaction.toLocaleString()}</td>
                <td><span class="badge ${segment.toLowerCase().replace(' ', '-')}">${segment}</span></td>
            `;
            
            tableBody.appendChild(row);
        });
    }
    
    switchSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        
        // Update sections
        document.querySelectorAll('.dashboard-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');
        
        this.currentSection = sectionName;
        
        // Trigger chart resize for proper rendering
        setTimeout(() => {
            Object.values(this.charts).forEach(chart => {
                if (chart && typeof chart.resize === 'function') {
                    chart.resize();
                }
            });
        }, 100);
    }
    
    filterInsights(category) {
        // Update category buttons
        document.querySelectorAll('.insight-category').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-category="${category}"]`).classList.add('active');
        
        // Filter insight cards
        document.querySelectorAll('.insight-card').forEach(card => {
            if (category === 'all' || card.dataset.category === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        
        // Update theme toggle icon
        const themeIcon = document.querySelector('#themeToggle i');
        themeIcon.className = this.currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        
        // Re-render charts with new theme
        setTimeout(() => {
            Object.keys(this.charts).forEach(chartId => {
                if (this.charts[chartId]) {
                    const canvas = document.getElementById(chartId);
                    if (canvas) {
                        // Find the original chart config and re-create
                        this.recreateChart(chartId);
                    }
                }
            });
        }, 100);
    }
    
    recreateChart(chartId) {
        // This would need to store original configs to properly recreate
        // For now, just trigger a resize
        if (this.charts[chartId] && typeof this.charts[chartId].resize === 'function') {
            this.charts[chartId].resize();
        }
    }
    
    async refreshData() {
        const refreshBtn = document.getElementById('refreshData');
        const icon = refreshBtn.querySelector('i');
        
        // Add spinning animation
        icon.classList.add('fa-spin');
        refreshBtn.disabled = true;
        
        try {
            await this.loadData();
            this.renderDashboard();
            
            // Show success message
            this.showNotification('Data refreshed successfully!', 'success');
            
        } catch (error) {
            this.showNotification('Failed to refresh data', 'error');
        } finally {
            // Remove spinning animation
            icon.classList.remove('fa-spin');
            refreshBtn.disabled = false;
        }
    }
    
    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }
    
    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
    
    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('errorModal').classList.add('active');
    }
    
    hideError() {
        document.getElementById('errorModal').classList.remove('active');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    async runAnalysis() {
        this.hideError();
        this.showLoading();
        
        try {
            // This would trigger the Python EDA pipeline
            // For now, just show a message
            alert('Please run the EDA analysis using: python eda/run_eda.py');
            
        } catch (error) {
            this.showError('Failed to run analysis: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RetailDashboard();
});

// Add notification styles dynamically
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 24px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 1001;
    animation: slideInRight 0.3s ease-out;
}

.notification-success {
    background-color: #10b981;
}

.notification-error {
    background-color: #ef4444;
}

.notification-info {
    background-color: #06b6d4;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.badge.high-value {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.badge.medium-value {
    background-color: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

.badge.low-value {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);