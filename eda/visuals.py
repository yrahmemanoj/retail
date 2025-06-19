"""
Visualization Module
Generates and exports visualizations for the EDA analysis.
"""

import json
import os
from datetime import datetime

class VisualizationGenerator:
    """
    Generates visualization configurations for the web dashboard.
    """
    
    def __init__(self):
        self.viz_configs = {}
    
    def create_revenue_charts(self, data):
        """Create revenue-focused chart configurations."""
        charts = {}
        
        # Daily revenue trend
        if 'daily_analysis' in data:
            daily_data = data['daily_analysis']['chart_data']
            charts['daily_revenue'] = {
                'type': 'line',
                'title': 'Daily Revenue Trend',
                'data': {
                    'labels': [item['date'] for item in daily_data],
                    'datasets': [{
                        'label': 'Daily Revenue',
                        'data': [item['revenue'] for item in daily_data],
                        'borderColor': '#2563eb',
                        'backgroundColor': 'rgba(37, 99, 235, 0.1)',
                        'tension': 0.4,
                        'fill': True
                    }]
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return "$" + value.toLocaleString(); }'
                            }
                        }
                    }
                }
            }
        
        # Monthly revenue with growth
        if 'monthly_trends' in data:
            monthly_data = data['monthly_trends']['chart_data']
            charts['monthly_revenue'] = {
                'type': 'bar',
                'title': 'Monthly Revenue Trend',
                'data': {
                    'labels': [item['month_name'] for item in monthly_data],
                    'datasets': [{
                        'label': 'Monthly Revenue',
                        'data': [item['revenue'] for item in monthly_data],
                        'backgroundColor': 'rgba(37, 99, 235, 0.8)',
                        'borderColor': '#2563eb',
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {
                            'display': True
                        }
                    }
                }
            }
        
        return charts
    
    def create_customer_charts(self, data):
        """Create customer-focused chart configurations."""
        charts = {}
        
        # Customer value segments
        if 'customer_behavior' in data and 'clv_segments' in data['customer_behavior']:
            segments = data['customer_behavior']['clv_segments']
            charts['customer_segments'] = {
                'type': 'doughnut',
                'title': 'Customer Value Segments',
                'data': {
                    'labels': list(segments.keys()),
                    'datasets': [{
                        'data': [segment['customer_count'] for segment in segments.values()],
                        'backgroundColor': [
                            '#ef4444',  # Low Value - Red
                            '#f97316',  # Medium Value - Orange
                            '#10b981'   # High Value - Green
                        ],
                        'borderWidth': 2,
                        'borderColor': '#ffffff'
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {
                            'position': 'bottom'
                        }
                    }
                }
            }
        
        # Demographics - Gender
        if 'demographics' in data and 'gender' in data['demographics']:
            gender_data = data['demographics']['gender']
            charts['gender_analysis'] = {
                'type': 'bar',
                'title': 'Revenue by Gender',
                'data': {
                    'labels': [item['gender'] for item in gender_data],
                    'datasets': [{
                        'label': 'Total Revenue',
                        'data': [item['total_spent'] for item in gender_data],
                        'backgroundColor': ['#8b5cf6', '#ec4899'],
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'indexAxis': 'y'
                }
            }
        
        return charts
    
    def create_product_charts(self, data):
        """Create product-focused chart configurations."""
        charts = {}
        
        # Product category performance
        if 'product_performance' in data:
            product_data = data['product_performance']['chart_data']
            charts['category_performance'] = {
                'type': 'bar',
                'title': 'Product Category Performance',
                'data': {
                    'labels': [item['category'] for item in product_data],
                    'datasets': [{
                        'label': 'Revenue',
                        'data': [item['revenue'] for item in product_data],
                        'backgroundColor': [
                            '#2563eb', '#10b981', '#f97316', 
                            '#8b5cf6', '#ef4444', '#06b6d4'
                        ],
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'beginAtZero': True
                        }
                    }
                }
            }
            
            # Market share pie chart
            charts['market_share'] = {
                'type': 'pie',
                'title': 'Market Share by Category',
                'data': {
                    'labels': [item['category'] for item in product_data],
                    'datasets': [{
                        'data': [item['market_share'] for item in product_data],
                        'backgroundColor': [
                            '#2563eb', '#10b981', '#f97316', 
                            '#8b5cf6', '#ef4444', '#06b6d4'
                        ],
                        'borderWidth': 2,
                        'borderColor': '#ffffff'
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {
                            'position': 'right'
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.label + ": " + context.parsed + "%"; }'
                            }
                        }
                    }
                }
            }
        
        return charts
    
    def create_time_series_charts(self, data):
        """Create time series chart configurations."""
        charts = {}
        
        # Weekly patterns
        if 'weekly_patterns' in data:
            dow_data = data['weekly_patterns']['day_of_week_data']
            charts['weekly_patterns'] = {
                'type': 'radar',
                'title': 'Weekly Sales Pattern',
                'data': {
                    'labels': [item['day'] for item in dow_data],
                    'datasets': [{
                        'label': 'Average Daily Revenue',
                        'data': [item['revenue'] / item['transactions'] if item['transactions'] > 0 else 0 for item in dow_data],
                        'borderColor': '#2563eb',
                        'backgroundColor': 'rgba(37, 99, 235, 0.2)',
                        'pointBackgroundColor': '#2563eb',
                        'pointRadius': 5
                    }]
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'r': {
                            'beginAtZero': True
                        }
                    }
                }
            }
        
        # Seasonal analysis
        if 'seasonal_analysis' in data:
            seasonal_data = data['seasonal_analysis']['chart_data']
            charts['seasonal_analysis'] = {
                'type': 'polarArea',
                'title': 'Seasonal Revenue Distribution',
                'data': {
                    'labels': [item['season'] for item in seasonal_data],
                    'datasets': [{
                        'data': [item['revenue'] for item in seasonal_data],
                        'backgroundColor': [
                            'rgba(34, 197, 94, 0.7)',   # Spring - Green
                            'rgba(249, 115, 22, 0.7)',  # Summer - Orange
                            'rgba(239, 68, 68, 0.7)',   # Fall - Red
                            'rgba(59, 130, 246, 0.7)'   # Winter - Blue
                        ],
                        'borderWidth': 2,
                        'borderColor': '#ffffff'
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {
                            'position': 'bottom'
                        }
                    }
                }
            }
        
        return charts
    
    def create_kpi_cards(self, stats_data, ts_data, cp_data):
        """Create KPI card configurations."""
        kpis = []
        
        # Revenue KPIs
        if stats_data and 'descriptive' in stats_data:
            total_amount_stats = stats_data['descriptive'].get('Total_Amount', {})
            if total_amount_stats:
                kpis.extend([
                    {
                        'title': 'Total Revenue',
                        'value': f"${total_amount_stats.get('mean', 0) * total_amount_stats.get('count', 0):,.2f}",
                        'subtitle': f"From {total_amount_stats.get('count', 0)} transactions",
                        'icon': 'dollar-sign',
                        'color': 'success'
                    },
                    {
                        'title': 'Average Transaction',
                        'value': f"${total_amount_stats.get('mean', 0):,.2f}",
                        'subtitle': f"Median: ${total_amount_stats.get('median', 0):,.2f}",
                        'icon': 'trending-up',
                        'color': 'primary'
                    }
                ])
        
        # Customer KPIs
        if cp_data and 'customer_behavior' in cp_data:
            customer_stats = cp_data['customer_behavior']['statistics']
            kpis.extend([
                {
                    'title': 'Total Customers',
                    'value': f"{customer_stats.get('total_customers', 0):,}",
                    'subtitle': f"{customer_stats.get('customer_retention_rate', 0):.1f}% retention rate",
                    'icon': 'users',
                    'color': 'info'
                },
                {
                    'title': 'Customer Lifetime Value',
                    'value': f"${customer_stats.get('avg_customer_value', 0):,.2f}",
                    'subtitle': f"Avg {customer_stats.get('avg_transactions_per_customer', 0):.1f} transactions",
                    'icon': 'heart',
                    'color': 'warning'
                }
            ])
        
        # Time-based KPIs
        if ts_data and 'daily_analysis' in ts_data:
            daily_stats = ts_data['daily_analysis']['statistics']
            kpis.extend([
                {
                    'title': 'Daily Revenue',
                    'value': f"${daily_stats.get('avg_daily_revenue', 0):,.2f}",
                    'subtitle': f"Peak: ${daily_stats.get('max_daily_revenue', 0):,.2f}",
                    'icon': 'calendar',
                    'color': 'secondary'
                }
            ])
        
        return kpis
    
    def create_insights_summary(self, stats_data, ts_data, cp_data):
        """Create insights summary for dashboard."""
        all_insights = []
        
        # Collect insights from all analyses
        if stats_data and 'business_insights' in stats_data:
            all_insights.extend(stats_data['business_insights'])
        
        if ts_data and 'time_insights' in ts_data:
            all_insights.extend(ts_data['time_insights'])
        
        if cp_data and 'cp_insights' in cp_data:
            all_insights.extend(cp_data['cp_insights'])
        
        # Format insights for dashboard
        formatted_insights = []
        for insight in all_insights[:8]:  # Limit to top 8 insights
            formatted_insights.append({
                'category': insight.get('category', 'General'),
                'insight': insight.get('insight', ''),
                'recommendation': insight.get('recommendation', ''),
                'priority': 'high' if 'significant' in insight.get('insight', '').lower() else 'medium'
            })
        
        return formatted_insights
    
    def generate_dashboard_config(self, stats_data=None, ts_data=None, cp_data=None):
        """Generate complete dashboard configuration."""
        config = {
            'timestamp': datetime.now().isoformat(),
            'charts': {},
            'kpis': [],
            'insights': []
        }
        
        # Generate all chart types
        if ts_data:
            config['charts'].update(self.create_revenue_charts(ts_data))
            config['charts'].update(self.create_time_series_charts(ts_data))
        
        if cp_data:
            config['charts'].update(self.create_customer_charts(cp_data))
            config['charts'].update(self.create_product_charts(cp_data))
        
        # Generate KPIs
        config['kpis'] = self.create_kpi_cards(stats_data, ts_data, cp_data)
        
        # Generate insights
        config['insights'] = self.create_insights_summary(stats_data, ts_data, cp_data)
        
        return config
    
    def save_dashboard_config(self, config, output_path='visuals/dashboard_config.json'):
        """Save dashboard configuration to file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Dashboard configuration saved to {output_path}")
    
    def generate_complete_visualization_suite(self):
        """Generate complete visualization suite from analysis results."""
        # Load analysis results
        stats_data = self.load_json_file('visuals/statistical_analysis.json')
        ts_data = self.load_json_file('visuals/time_series_analysis.json')
        cp_data = self.load_json_file('visuals/customer_product_analysis.json')
        
        # Generate dashboard configuration
        config = self.generate_dashboard_config(stats_data, ts_data, cp_data)
        
        # Save configuration
        self.save_dashboard_config(config)
        
        return config
    
    def load_json_file(self, filepath):
        """Load JSON file if it exists."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    generator = VisualizationGenerator()
    config = generator.generate_complete_visualization_suite()
    
    print("\n" + "="*50)
    print("VISUALIZATION CONFIGURATION COMPLETED")
    print("="*50)