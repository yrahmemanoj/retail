"""
Time Series Analysis Module
Analyzes temporal patterns in retail sales data.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

class TimeSeriesAnalyzer:
    """
    Performs time series analysis on retail sales data.
    """
    
    def __init__(self, df):
        self.df = df
        self.ts_results = {}
        
        # Ensure Date column is datetime
        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'])
    
    def daily_sales_analysis(self):
        """Analyze daily sales patterns."""
        daily_sales = self.df.groupby('Date').agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Quantity': 'sum',
            'Customer_ID': 'nunique'
        }).round(2)
        
        daily_sales.columns = ['total_revenue', 'avg_transaction', 'transaction_count', 
                              'total_quantity', 'unique_customers']
        
        # Calculate daily statistics
        daily_stats = {
            'total_days': int(len(daily_sales)),
            'avg_daily_revenue': float(daily_sales['total_revenue'].mean()),
            'max_daily_revenue': float(daily_sales['total_revenue'].max()),
            'min_daily_revenue': float(daily_sales['total_revenue'].min()),
            'avg_daily_transactions': float(daily_sales['transaction_count'].mean()),
            'avg_daily_customers': float(daily_sales['unique_customers'].mean()),
            'revenue_volatility': float(daily_sales['total_revenue'].std())
        }
        
        # Identify best and worst performing days
        best_day = daily_sales['total_revenue'].idxmax()
        worst_day = daily_sales['total_revenue'].idxmin()
        
        daily_stats['best_day'] = {
            'date': best_day.strftime('%Y-%m-%d'),
            'revenue': float(daily_sales.loc[best_day, 'total_revenue']),
            'transactions': int(daily_sales.loc[best_day, 'transaction_count'])
        }
        
        daily_stats['worst_day'] = {
            'date': worst_day.strftime('%Y-%m-%d'),
            'revenue': float(daily_sales.loc[worst_day, 'total_revenue']),
            'transactions': int(daily_sales.loc[worst_day, 'transaction_count'])
        }
        
        # Convert daily sales for visualization
        daily_chart_data = []
        for date, row in daily_sales.iterrows():
            daily_chart_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(row['total_revenue']),
                'transactions': int(row['transaction_count']),
                'customers': int(row['unique_customers'])
            })
        
        self.ts_results['daily_analysis'] = {
            'statistics': daily_stats,
            'chart_data': daily_chart_data
        }
        
        return self.ts_results['daily_analysis']
    
    def weekly_patterns(self):
        """Analyze weekly patterns and day-of-week effects."""
        # Add day names
        self.df['day_name'] = self.df['Date'].dt.day_name()
        self.df['week_number'] = self.df['Date'].dt.isocalendar().week
        
        # Day of week analysis
        dow_analysis = self.df.groupby('day_name').agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Quantity': 'sum',
            'Customer_ID': 'nunique'
        }).round(2)
        
        dow_analysis.columns = ['total_revenue', 'avg_transaction', 'transaction_count', 
                               'total_quantity', 'unique_customers']
        
        # Reorder by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_analysis = dow_analysis.reindex([day for day in day_order if day in dow_analysis.index])
        
        # Convert to chart data
        dow_chart_data = []
        for day, row in dow_analysis.iterrows():
            dow_chart_data.append({
                'day': day,
                'revenue': float(row['total_revenue']),
                'transactions': int(row['transaction_count']),
                'avg_transaction': float(row['avg_transaction'])
            })
        
        # Weekly analysis
        weekly_analysis = self.df.groupby('week_number').agg({
            'Total_Amount': ['sum', 'mean'],
            'Transaction_ID': 'count'
        }).round(2)
        
        weekly_analysis.columns = ['total_revenue', 'avg_transaction', 'transaction_count']
        
        weekly_chart_data = []
        for week, row in weekly_analysis.iterrows():
            weekly_chart_data.append({
                'week': int(week),
                'revenue': float(row['total_revenue']),
                'transactions': int(row['transaction_count'])
            })
        
        # Calculate weekly statistics
        weekly_stats = {
            'best_day_of_week': dow_analysis['total_revenue'].idxmax(),
            'worst_day_of_week': dow_analysis['total_revenue'].idxmin(),
            'weekend_vs_weekday': {
                'weekend_avg': float(dow_analysis.loc[['Saturday', 'Sunday']]['avg_transaction'].mean()) 
                              if all(day in dow_analysis.index for day in ['Saturday', 'Sunday']) else 0,
                'weekday_avg': float(dow_analysis.loc[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']]['avg_transaction'].mean())
                              if all(day in dow_analysis.index for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']) else 0
            }
        }
        
        self.ts_results['weekly_patterns'] = {
            'day_of_week_data': dow_chart_data,
            'weekly_data': weekly_chart_data,
            'statistics': weekly_stats
        }
        
        return self.ts_results['weekly_patterns']
    
    def monthly_trends(self):
        """Analyze monthly trends and seasonality."""
        # Monthly analysis
        monthly_analysis = self.df.groupby(['Year', 'Month']).agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Quantity': 'sum',
            'Customer_ID': 'nunique'
        }).round(2)
        
        monthly_analysis.columns = ['total_revenue', 'avg_transaction', 'transaction_count', 
                                   'total_quantity', 'unique_customers']
        
        # Convert to chart data
        monthly_chart_data = []
        for (year, month), row in monthly_analysis.iterrows():
            month_name = pd.to_datetime(f'{year}-{month}-01').strftime('%B %Y')
            monthly_chart_data.append({
                'year': int(year),
                'month': int(month),
                'month_name': month_name,
                'revenue': float(row['total_revenue']),
                'transactions': int(row['transaction_count']),
                'customers': int(row['unique_customers'])
            })
        
        # Calculate growth rates
        monthly_revenues = [data['revenue'] for data in monthly_chart_data]
        growth_rates = []
        for i in range(1, len(monthly_revenues)):
            growth_rate = ((monthly_revenues[i] - monthly_revenues[i-1]) / monthly_revenues[i-1]) * 100
            growth_rates.append(growth_rate)
        
        # Monthly statistics
        monthly_stats = {
            'total_months': len(monthly_chart_data),
            'avg_monthly_revenue': float(np.mean(monthly_revenues)),
            'revenue_growth_rate': float(np.mean(growth_rates)) if growth_rates else 0,
            'best_month': max(monthly_chart_data, key=lambda x: x['revenue']),
            'worst_month': min(monthly_chart_data, key=lambda x: x['revenue'])
        }
        
        self.ts_results['monthly_trends'] = {
            'chart_data': monthly_chart_data,
            'statistics': monthly_stats,
            'growth_rates': growth_rates
        }
        
        return self.ts_results['monthly_trends']
    
    def seasonal_analysis(self):
        """Analyze seasonal patterns in sales."""
        # Define seasons
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        self.df['Season'] = self.df['Month'].apply(get_season)
        
        # Seasonal analysis
        seasonal_analysis = self.df.groupby('Season').agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Quantity': 'sum',
            'Customer_ID': 'nunique'
        }).round(2)
        
        seasonal_analysis.columns = ['total_revenue', 'avg_transaction', 'transaction_count', 
                                    'total_quantity', 'unique_customers']
        
        # Convert to chart data
        seasonal_chart_data = []
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        for season in season_order:
            if season in seasonal_analysis.index:
                row = seasonal_analysis.loc[season]
                seasonal_chart_data.append({
                    'season': season,
                    'revenue': float(row['total_revenue']),
                    'transactions': int(row['transaction_count']),
                    'avg_transaction': float(row['avg_transaction'])
                })
        
        # Seasonal statistics
        seasonal_stats = {
            'best_season': max(seasonal_chart_data, key=lambda x: x['revenue'])['season'],
            'worst_season': min(seasonal_chart_data, key=lambda x: x['revenue'])['season'],
            'seasonal_variance': float(np.var([data['revenue'] for data in seasonal_chart_data]))
        }
        
        self.ts_results['seasonal_analysis'] = {
            'chart_data': seasonal_chart_data,
            'statistics': seasonal_stats
        }
        
        return self.ts_results['seasonal_analysis']
    
    def trend_analysis(self):
        """Analyze overall trends and forecast."""
        # Create time series
        daily_sales = self.df.groupby('Date')['Total_Amount'].sum().reset_index()
        daily_sales = daily_sales.sort_values('Date')
        
        # Calculate moving averages
        daily_sales['MA_7'] = daily_sales['Total_Amount'].rolling(window=7, min_periods=1).mean()
        daily_sales['MA_30'] = daily_sales['Total_Amount'].rolling(window=30, min_periods=1).mean()
        
        # Simple linear trend
        x = np.arange(len(daily_sales))
        y = daily_sales['Total_Amount'].values
        
        # Linear regression
        z = np.polyfit(x, y, 1)
        trend_line = np.poly1d(z)
        
        # Convert to chart data
        trend_chart_data = []
        for idx, row in daily_sales.iterrows():
            trend_chart_data.append({
                'date': row['Date'].strftime('%Y-%m-%d'),
                'actual': float(row['Total_Amount']),
                'ma_7': float(row['MA_7']),
                'ma_30': float(row['MA_30']),
                'trend': float(trend_line(idx))
            })
        
        # Trend statistics
        trend_stats = {
            'trend_slope': float(z[0]),
            'trend_direction': 'Increasing' if z[0] > 0 else 'Decreasing',
            'trend_strength': float(abs(z[0])),
            'r_squared': float(np.corrcoef(y, trend_line(x))[0, 1] ** 2)
        }
        
        self.ts_results['trend_analysis'] = {
            'chart_data': trend_chart_data,
            'statistics': trend_stats
        }
        
        return self.ts_results['trend_analysis']
    
    def generate_time_insights(self):
        """Generate time-based business insights."""
        insights = []
        
        # Daily insights
        if 'daily_analysis' in self.ts_results:
            daily_stats = self.ts_results['daily_analysis']['statistics']
            volatility = daily_stats.get('revenue_volatility', 0)
            avg_revenue = daily_stats.get('avg_daily_revenue', 0)
            
            if avg_revenue > 0:
                cv = (volatility / avg_revenue) * 100  # Coefficient of variation
                if cv > 30:
                    insights.append({
                        'category': 'Revenue Stability',
                        'insight': f'Daily revenue shows high volatility (CV: {cv:.1f}%)',
                        'recommendation': 'Implement strategies to stabilize daily sales through promotions and inventory management'
                    })
        
        # Weekly insights
        if 'weekly_patterns' in self.ts_results:
            weekly_stats = self.ts_results['weekly_patterns']['statistics']
            best_day = weekly_stats.get('best_day_of_week')
            if best_day:
                insights.append({
                    'category': 'Weekly Patterns',
                    'insight': f'{best_day} is the best performing day of the week',
                    'recommendation': f'Schedule major promotions and new product launches on {best_day}s'
                })
        
        # Seasonal insights
        if 'seasonal_analysis' in self.ts_results:
            seasonal_stats = self.ts_results['seasonal_analysis']['statistics']
            best_season = seasonal_stats.get('best_season')
            if best_season:
                insights.append({
                    'category': 'Seasonality',
                    'insight': f'{best_season} shows the highest sales performance',
                    'recommendation': f'Increase inventory and marketing budget during {best_season} season'
                })
        
        # Trend insights
        if 'trend_analysis' in self.ts_results:
            trend_stats = self.ts_results['trend_analysis']['statistics']
            trend_direction = trend_stats.get('trend_direction')
            r_squared = trend_stats.get('r_squared', 0)
            
            if r_squared > 0.7:  # Strong trend
                insights.append({
                    'category': 'Business Trend',
                    'insight': f'Sales show a strong {trend_direction.lower()} trend (R²: {r_squared:.2f})',
                    'recommendation': 'Leverage current trend momentum for strategic planning and investment decisions'
                })
        
        self.ts_results['time_insights'] = insights
        return insights
    
    def run_complete_analysis(self):
        """Run all time series analyses."""
        print("Running Time Series Analysis...")
        
        self.daily_sales_analysis()
        print("✓ Daily sales analysis completed")
        
        self.weekly_patterns()
        print("✓ Weekly patterns analysis completed")
        
        self.monthly_trends()
        print("✓ Monthly trends analysis completed")
        
        self.seasonal_analysis()
        print("✓ Seasonal analysis completed")
        
        self.trend_analysis()
        print("✓ Trend analysis completed")
        
        self.generate_time_insights()
        print("✓ Time-based insights generated")
        
        return self.ts_results
    
    def save_results(self, output_path='visuals/time_series_analysis.json'):
        """Save all time series analysis results."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.ts_results, f, indent=2)
        
        print(f"✓ Time series analysis results saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    from load_clean import DataLoader
    
    loader = DataLoader()
    data = loader.load_data()
    cleaned_data = loader.clean_data()
    
    if cleaned_data is not None:
        analyzer = TimeSeriesAnalyzer(cleaned_data)
        results = analyzer.run_complete_analysis()
        analyzer.save_results()
        
        print("\n" + "="*50)
        print("TIME SERIES ANALYSIS COMPLETED")
        print("="*50)