"""
Customer and Product Analysis Module
Analyzes customer behavior and product performance patterns.
"""

import pandas as pd
import numpy as np
import json
import os
from collections import defaultdict

class CustomerProductAnalyzer:
    """
    Performs customer behavior and product performance analysis.
    """
    
    def __init__(self, df):
        self.df = df
        self.cp_results = {}
    
    def customer_behavior_analysis(self):
        """Analyze customer purchasing behavior patterns."""
        # Customer-level aggregations
        customer_metrics = self.df.groupby('Customer_ID').agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Quantity': 'sum',
            'Date': ['min', 'max'],
            'Product_Category': lambda x: x.nunique()
        }).round(2)
        
        customer_metrics.columns = ['total_spent', 'avg_transaction', 'transaction_count', 
                                   'total_quantity', 'first_purchase', 'last_purchase', 
                                   'categories_purchased']
        
        # Calculate customer lifetime (days)
        customer_metrics['customer_lifetime_days'] = (
            customer_metrics['last_purchase'] - customer_metrics['first_purchase']
        ).dt.days
        
        # Customer value segmentation
        customer_metrics['clv_segment'] = pd.qcut(
            customer_metrics['total_spent'], 
            q=3, 
            labels=['Low Value', 'Medium Value', 'High Value']
        )
        
        # Purchase frequency segmentation
        # Calculate the number of quantiles that can be formed
        n_bins = 4
        if customer_metrics['transaction_count'].nunique() >= n_bins:
            try:
                customer_metrics['frequency_segment'] = pd.qcut(
                    customer_metrics['transaction_count'],
                    q=n_bins,
                    labels=["Low", "Medium", "High", "Very High"],
                    duplicates='drop'
                )
            except ValueError:
                customer_metrics['frequency_segment'] = 'Undefined'
        else:
            customer_metrics['frequency_segment'] = 'Undefined'
        
        # Customer behavior statistics
        behavior_stats = {
            'total_customers': int(len(customer_metrics)),
            'avg_customer_value': float(customer_metrics['total_spent'].mean()),
            'avg_transactions_per_customer': float(customer_metrics['transaction_count'].mean()),
            'avg_customer_lifetime': float(customer_metrics['customer_lifetime_days'].mean()),
            'customer_retention_rate': float(
                (customer_metrics['transaction_count'] > 1).sum() / len(customer_metrics) * 100
            ),
            'avg_categories_per_customer': float(customer_metrics['categories_purchased'].mean())
        }
        
        # CLV segment analysis
        clv_segments = {}
        for segment in customer_metrics['clv_segment'].unique():
            if pd.notna(segment):
                segment_data = customer_metrics[customer_metrics['clv_segment'] == segment]
                clv_segments[str(segment)] = {
                    'customer_count': int(len(segment_data)),
                    'percentage': float(len(segment_data) / len(customer_metrics) * 100),
                    'avg_total_spent': float(segment_data['total_spent'].mean()),
                    'avg_transaction_count': float(segment_data['transaction_count'].mean()),
                    'total_revenue_contribution': float(segment_data['total_spent'].sum())
                }
        
        # Top customers
        top_customers = customer_metrics.nlargest(10, 'total_spent')[
            ['total_spent', 'transaction_count', 'avg_transaction']
        ].round(2)
        
        top_customers_list = []
        for customer_id, row in top_customers.iterrows():
            top_customers_list.append({
                'customer_id': str(customer_id),
                'total_spent': float(row['total_spent']),
                'transaction_count': int(row['transaction_count']),
                'avg_transaction': float(row['avg_transaction'])
            })
        
        self.cp_results['customer_behavior'] = {
            'statistics': behavior_stats,
            'clv_segments': clv_segments,
            'top_customers': top_customers_list
        }
        
        return self.cp_results['customer_behavior']
    
    def product_performance_analysis(self):
        """Analyze product category performance."""
        # Product category analysis
        category_metrics = self.df.groupby('Product_Category').agg({
            'Total_Amount': ['sum', 'mean', 'count'],
            'Quantity': 'sum',
            'Price_per_Unit': 'mean',
            'Customer_ID': 'nunique'
        }).round(2)
        
        category_metrics.columns = ['total_revenue', 'avg_transaction', 'transaction_count', 
                                   'total_quantity', 'avg_price', 'unique_customers']
        
        # Calculate market share
        total_revenue = category_metrics['total_revenue'].sum()
        category_metrics['market_share'] = (category_metrics['total_revenue'] / total_revenue * 100).round(2)
        
        # Category performance ranking
        category_metrics['revenue_rank'] = category_metrics['total_revenue'].rank(ascending=False, method='dense')
        category_metrics['quantity_rank'] = category_metrics['total_quantity'].rank(ascending=False, method='dense')
        category_metrics['customer_rank'] = category_metrics['unique_customers'].rank(ascending=False, method='dense')
        
        # Convert to chart data
        category_chart_data = []
        for category, row in category_metrics.iterrows():
            category_chart_data.append({
                'category': str(category),
                'revenue': float(row['total_revenue']),
                'transactions': int(row['transaction_count']),
                'customers': int(row['unique_customers']),
                'avg_price': float(row['avg_price']),
                'market_share': float(row['market_share']),
                'avg_transaction': float(row['avg_transaction'])
            })
        
        # Category performance statistics
        performance_stats = {
            'total_categories': int(len(category_metrics)),
            'best_performing_category': category_metrics['total_revenue'].idxmax(),
            'highest_avg_transaction': category_metrics['avg_transaction'].idxmax(),
            'most_popular_category': category_metrics['transaction_count'].idxmax(),
            'premium_category': category_metrics['avg_price'].idxmax(),
            'revenue_concentration': float(category_metrics['market_share'].max())  # Highest market share
        }
        
        self.cp_results['product_performance'] = {
            'chart_data': category_chart_data,
            'statistics': performance_stats
        }
        
        return self.cp_results['product_performance']
    
    def customer_product_matrix(self):
        """Analyze customer-product relationships."""
        # Create customer-product matrix
        cp_matrix = self.df.pivot_table(
            index='Customer_ID', 
            columns='Product_Category', 
            values='Total_Amount', 
            aggfunc='sum', 
            fill_value=0
        )
        
        # Cross-selling analysis
        cross_sell_matrix = (cp_matrix > 0).astype(int)  # Binary matrix
        
        # Calculate category co-occurrence
        category_pairs = {}
        categories = list(cp_matrix.columns)
        
        for i, cat1 in enumerate(categories):
            for j, cat2 in enumerate(categories):
                if i < j:  # Avoid duplicates
                    # Count customers who bought both categories
                    both_count = ((cross_sell_matrix[cat1] == 1) & (cross_sell_matrix[cat2] == 1)).sum()
                    cat1_count = (cross_sell_matrix[cat1] == 1).sum()
                    
                    if cat1_count > 0:
                        cross_sell_rate = (both_count / cat1_count) * 100
                        category_pairs[f"{cat1} → {cat2}"] = {
                            'customers_bought_both': int(both_count),
                            'cross_sell_rate': float(cross_sell_rate),
                            'base_category_customers': int(cat1_count)
                        }
        
        # Sort by cross-sell rate
        sorted_pairs = sorted(category_pairs.items(), key=lambda x: x[1]['cross_sell_rate'], reverse=True)
        top_cross_sell = dict(sorted_pairs[:5])  # Top 5 cross-selling opportunities
        
        # Customer diversity analysis
        customer_diversity = cross_sell_matrix.sum(axis=1)  # Number of categories per customer
        diversity_stats = {
            'avg_categories_per_customer': float(customer_diversity.mean()),
            'max_categories_per_customer': int(customer_diversity.max()),
            'customers_single_category': int((customer_diversity == 1).sum()),
            'customers_multi_category': int((customer_diversity > 1).sum()),
            'multi_category_rate': float((customer_diversity > 1).sum() / len(customer_diversity) * 100)
        }
        
        self.cp_results['customer_product_matrix'] = {
            'cross_selling_opportunities': top_cross_sell,
            'customer_diversity': diversity_stats
        }
        
        return self.cp_results['customer_product_matrix']
    
    def demographic_analysis(self):
        """Analyze customer demographics and purchasing patterns."""
        demographic_results = {}
        
        # Gender analysis
        if 'Gender' in self.df.columns:
            gender_analysis = self.df.groupby('Gender').agg({
                'Total_Amount': ['sum', 'mean', 'count'],
                'Customer_ID': 'nunique',
                'Product_Category': lambda x: x.value_counts().index[0]  # Most popular category
            }).round(2)
            
            gender_analysis.columns = ['total_spent', 'avg_transaction', 'transaction_count', 
                                     'unique_customers', 'top_category']
            
            gender_chart_data = []
            for gender, row in gender_analysis.iterrows():
                gender_chart_data.append({
                    'gender': str(gender),
                    'total_spent': float(row['total_spent']),
                    'avg_transaction': float(row['avg_transaction']),
                    'customers': int(row['unique_customers']),
                    'top_category': str(row['top_category'])
                })
            
            demographic_results['gender'] = gender_chart_data
        
        # Age group analysis
        if 'Age_Group' in self.df.columns:
            age_analysis = self.df.groupby('Age_Group').agg({
                'Total_Amount': ['sum', 'mean', 'count'],
                'Customer_ID': 'nunique'
            }).round(2)
            
            age_analysis.columns = ['total_spent', 'avg_transaction', 'transaction_count', 'unique_customers']
            
            age_chart_data = []
            for age_group, row in age_analysis.iterrows():
                if pd.notna(age_group):
                    age_chart_data.append({
                        'age_group': str(age_group),
                        'total_spent': float(row['total_spent']),
                        'avg_transaction': float(row['avg_transaction']),
                        'customers': int(row['unique_customers'])
                    })
            
            demographic_results['age_groups'] = age_chart_data
        
        # Product preferences by demographics
        if 'Gender' in self.df.columns:
            gender_product_pref = self.df.groupby(['Gender', 'Product_Category']).agg({
                'Total_Amount': 'sum'
            }).unstack(fill_value=0)
            
            # Normalize to percentages
            gender_product_pref_pct = gender_product_pref.div(gender_product_pref.sum(axis=1), axis=0) * 100
            
            product_preferences = {}
            for gender in gender_product_pref_pct.index:
                preferences = gender_product_pref_pct.loc[gender].round(2)
                product_preferences[str(gender)] = {
                    str(category): float(pct) for category, pct in preferences.items()
                }
            
            demographic_results['product_preferences'] = product_preferences
        
        self.cp_results['demographics'] = demographic_results
        return demographic_results
    
    def purchase_patterns(self):
        """Analyze purchase patterns and customer journey."""
        patterns = {}
        
        # Transaction timing patterns
        if 'Date' in self.df.columns:
            # Calculate days between purchases for each customer
            customer_intervals = []
            for customer in self.df['Customer_ID'].unique():
                customer_data = self.df[self.df['Customer_ID'] == customer].sort_values('Date')
                if len(customer_data) > 1:
                    dates = customer_data['Date'].tolist()
                    intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                    customer_intervals.extend(intervals)
            
            if customer_intervals:
                interval_stats = {
                    'avg_days_between_purchases': float(np.mean(customer_intervals)),
                    'median_days_between_purchases': float(np.median(customer_intervals)),
                    'min_days_between_purchases': int(min(customer_intervals)),
                    'max_days_between_purchases': int(max(customer_intervals))
                }
                patterns['purchase_intervals'] = interval_stats
        
        # Quantity patterns
        quantity_patterns = self.df['Quantity'].value_counts().sort_index()
        quantity_distribution = []
        for qty, count in quantity_patterns.items():
            quantity_distribution.append({
                'quantity': int(qty),
                'transactions': int(count),
                'percentage': float(count / len(self.df) * 100)
            })
        
        patterns['quantity_distribution'] = quantity_distribution
        
        # Price range preferences
        if 'Price_Category' in self.df.columns:
            price_preferences = self.df['Price_Category'].value_counts()
            price_distribution = []
            for price_cat, count in price_preferences.items():
                if pd.notna(price_cat):
                    price_distribution.append({
                        'price_category': str(price_cat),
                        'transactions': int(count),
                        'percentage': float(count / len(self.df) * 100)
                    })
            
            patterns['price_preferences'] = price_distribution
        
        self.cp_results['purchase_patterns'] = patterns
        return patterns
    
    def generate_customer_product_insights(self):
        """Generate business insights from customer and product analysis."""
        insights = []
        
        # Customer value insights
        if 'customer_behavior' in self.cp_results:
            behavior_stats = self.cp_results['customer_behavior']['statistics']
            retention_rate = behavior_stats.get('customer_retention_rate', 0)
            
            if retention_rate < 50:
                insights.append({
                    'category': 'Customer Retention',
                    'insight': f'Customer retention rate is low at {retention_rate:.1f}%',
                    'recommendation': 'Implement loyalty programs and personalized marketing to improve retention'
                })
            
            clv_segments = self.cp_results['customer_behavior'].get('clv_segments', {})
            if 'High Value' in clv_segments:
                high_value_pct = clv_segments['High Value']['percentage']
                insights.append({
                    'category': 'Customer Segmentation',
                    'insight': f'High-value customers represent {high_value_pct:.1f}% of customer base',
                    'recommendation': 'Focus on retaining and expanding high-value customer relationships'
                })
        
        # Product performance insights
        if 'product_performance' in self.cp_results:
            perf_stats = self.cp_results['product_performance']['statistics']
            concentration = perf_stats.get('revenue_concentration', 0)
            
            if concentration > 40:
                best_category = perf_stats.get('best_performing_category', '')
                insights.append({
                    'category': 'Product Portfolio',
                    'insight': f'{best_category} dominates with {concentration:.1f}% market share',
                    'recommendation': 'Diversify product portfolio to reduce dependency on single category'
                })
        
        # Cross-selling insights
        if 'customer_product_matrix' in self.cp_results:
            cross_sell = self.cp_results['customer_product_matrix']['cross_selling_opportunities']
            if cross_sell:
                best_opportunity = list(cross_sell.keys())[0]
                rate = cross_sell[best_opportunity]['cross_sell_rate']
                insights.append({
                    'category': 'Cross-selling',
                    'insight': f'Best cross-selling opportunity: {best_opportunity} ({rate:.1f}% rate)',
                    'recommendation': 'Develop targeted cross-selling campaigns for identified product pairs'
                })
        
        self.cp_results['cp_insights'] = insights
        return insights
    
    def run_complete_analysis(self):
        """Run all customer and product analyses."""
        print("Running Customer & Product Analysis...")
        
        self.customer_behavior_analysis()
        print("✓ Customer behavior analysis completed")
        
        self.product_performance_analysis()
        print("✓ Product performance analysis completed")
        
        self.customer_product_matrix()
        print("✓ Customer-product matrix analysis completed")
        
        self.demographic_analysis()
        print("✓ Demographic analysis completed")
        
        self.purchase_patterns()
        print("✓ Purchase patterns analysis completed")
        
        self.generate_customer_product_insights()
        print("✓ Customer & product insights generated")
        
        return self.cp_results
    
    def save_results(self, output_path='visuals/customer_product_analysis.json'):
        """Save all customer and product analysis results."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.cp_results, f, indent=2)
        
        print(f"✓ Customer & product analysis results saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    from load_clean import DataLoader
    
    loader = DataLoader()
    data = loader.load_data()
    cleaned_data = loader.clean_data()
    
    if cleaned_data is not None:
        analyzer = CustomerProductAnalyzer(cleaned_data)
        results = analyzer.run_complete_analysis()
        analyzer.save_results()
        
        print("\n" + "="*50)
        print("CUSTOMER & PRODUCT ANALYSIS COMPLETED")
        print("="*50)