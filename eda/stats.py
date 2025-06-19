"""
Statistical Analysis Module
Provides comprehensive statistical analysis of retail sales data.
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
import os

class StatisticalAnalyzer:
    """
    Performs statistical analysis on retail sales data.
    """
    
    def __init__(self, df):
        self.df = df
        self.stats_results = {}
    
    def descriptive_statistics(self):
        """Generate comprehensive descriptive statistics."""
        numeric_cols = ['Age', 'Quantity', 'Price_per_Unit', 'Total_Amount']
        
        stats_summary = {}
        
        for col in numeric_cols:
            if col in self.df.columns:
                stats_summary[col] = {
                    'count': int(self.df[col].count()),
                    'mean': float(self.df[col].mean()),
                    'median': float(self.df[col].median()),
                    'mode': float(self.df[col].mode().iloc[0]) if not self.df[col].mode().empty else None,
                    'std': float(self.df[col].std()),
                    'variance': float(self.df[col].var()),
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'q1': float(self.df[col].quantile(0.25)),
                    'q3': float(self.df[col].quantile(0.75)),
                    'iqr': float(self.df[col].quantile(0.75) - self.df[col].quantile(0.25)),
                    'skewness': float(self.df[col].skew()),
                    'kurtosis': float(self.df[col].kurtosis())
                }
        
        self.stats_results['descriptive'] = stats_summary
        return stats_summary
    
    def correlation_analysis(self):
        """Perform correlation analysis between numerical variables."""
        numeric_cols = ['Age', 'Quantity', 'Price_per_Unit', 'Total_Amount']
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        if len(available_cols) > 1:
            correlation_matrix = self.df[available_cols].corr()
            
            # Convert to serializable format
            corr_dict = {}
            for i, col1 in enumerate(available_cols):
                corr_dict[col1] = {}
                for j, col2 in enumerate(available_cols):
                    corr_dict[col1][col2] = float(correlation_matrix.iloc[i, j])
            
            self.stats_results['correlation'] = corr_dict
            return corr_dict
        
        return {}
    
    def hypothesis_testing(self):
        """Perform various hypothesis tests."""
        tests_results = {}
        
        # Test 1: Gender difference in spending
        if 'Gender' in self.df.columns and 'Total_Amount' in self.df.columns:
            male_spending = self.df[self.df['Gender'] == 'Male']['Total_Amount']
            female_spending = self.df[self.df['Gender'] == 'Female']['Total_Amount']
            
            # Independent t-test
            t_stat, p_value = stats.ttest_ind(male_spending, female_spending)
            
            tests_results['gender_spending_difference'] = {
                'test': 'Independent t-test',
                'null_hypothesis': 'No difference in spending between genders',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': bool(p_value < 0.05),
                'male_mean': float(male_spending.mean()),
                'female_mean': float(female_spending.mean())
            }
        
        # Test 2: Age and spending correlation
        if 'Age' in self.df.columns and 'Total_Amount' in self.df.columns:
            correlation, p_value = stats.pearsonr(self.df['Age'], self.df['Total_Amount'])
            
            tests_results['age_spending_correlation'] = {
                'test': 'Pearson correlation',
                'null_hypothesis': 'No correlation between age and spending',
                'correlation_coefficient': float(correlation),
                'p_value': float(p_value),
                'significant': bool(p_value < 0.05)
            }
        
        # Test 3: Product category spending differences (ANOVA)
        if 'Product_Category' in self.df.columns and 'Total_Amount' in self.df.columns:
            categories = self.df['Product_Category'].unique()
            category_spending = [self.df[self.df['Product_Category'] == cat]['Total_Amount'] 
                               for cat in categories]
            
            f_stat, p_value = stats.f_oneway(*category_spending)
            
            tests_results['category_spending_anova'] = {
                'test': 'One-way ANOVA',
                'null_hypothesis': 'No difference in spending across product categories',
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significant': bool(p_value < 0.05),
                'categories_tested': list(categories)
            }
        
        self.stats_results['hypothesis_tests'] = tests_results
        return tests_results
    
    def outlier_detection(self):
        """Detect outliers using various methods."""
        numeric_cols = ['Age', 'Quantity', 'Price_per_Unit', 'Total_Amount']
        outliers_summary = {}
        
        for col in numeric_cols:
            if col in self.df.columns:
                data = self.df[col]
                
                # IQR method
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                iqr_outliers = data[(data < lower_bound) | (data > upper_bound)]
                
                # Z-score method
                z_scores = np.abs(stats.zscore(data))
                z_outliers = data[z_scores > 3]
                
                outliers_summary[col] = {
                    'iqr_method': {
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound),
                        'outlier_count': int(len(iqr_outliers)),
                        'outlier_percentage': float(len(iqr_outliers) / len(data) * 100)
                    },
                    'zscore_method': {
                        'outlier_count': int(len(z_outliers)),
                        'outlier_percentage': float(len(z_outliers) / len(data) * 100)
                    }
                }
        
        self.stats_results['outliers'] = outliers_summary
        return outliers_summary
    
    def categorical_Analysis(self):
        """Analyze categorical variables."""
        categorical_cols = ['Gender', 'Product_Category', 'Age_Group']
        categorical_summary = {}
        
        for col in categorical_cols:
            if col in self.df.columns:
                value_counts = self.df[col].value_counts()
                proportions = self.df[col].value_counts(normalize=True)
                
                categorical_summary[col] = {
                    'unique_values': int(self.df[col].nunique()),
                    'value_counts': value_counts.to_dict(),
                    'proportions': {k: float(v) for k, v in proportions.to_dict().items()},
                    'mode': str(value_counts.index[0]),
                    'entropy': float(-sum(proportions * np.log2(proportions + 1e-10)))
                }
        
        self.stats_results['categorical'] = categorical_summary
        return categorical_summary
    
    def customer_segments_analysis(self):
        """Analyze customer segments based on spending behavior."""
        if 'Customer_ID' in self.df.columns and 'Total_Amount' in self.df.columns:
            customer_stats = self.df.groupby('Customer_ID').agg({
                'Total_Amount': ['sum', 'mean', 'count'],
                'Quantity': 'sum',
                'Date': ['min', 'max']
            }).round(2)
            
            customer_stats.columns = ['total_spent', 'avg_transaction', 'transaction_count', 
                                    'total_quantity', 'first_purchase', 'last_purchase']
            
            # Customer lifetime value segments
            customer_stats['customer_segment'] = pd.cut(
                customer_stats['total_spent'],
                bins=[0, customer_stats['total_spent'].quantile(0.33), 
                      customer_stats['total_spent'].quantile(0.67), 
                      customer_stats['total_spent'].max()],
                labels=['Low Value', 'Medium Value', 'High Value']
            )
            
            segment_summary = customer_stats.groupby('customer_segment').agg({
                'total_spent': ['count', 'mean', 'sum'],
                'avg_transaction': 'mean',
                'transaction_count': 'mean'
            }).round(2)
            
            # Convert to serializable format
            segments = {}
            for segment in customer_stats['customer_segment'].unique():
                if pd.notna(segment):
                    segment_data = customer_stats[customer_stats['customer_segment'] == segment]
                    segments[str(segment)] = {
                        'customer_count': int(len(segment_data)),
                        'avg_total_spent': float(segment_data['total_spent'].mean()),
                        'avg_transaction_value': float(segment_data['avg_transaction'].mean()),
                        'avg_transaction_count': float(segment_data['transaction_count'].mean()),
                        'total_revenue': float(segment_data['total_spent'].sum())
                    }
            
            self.stats_results['customer_segments'] = segments
            return segments
        
        return {}
    
    def generate_insights(self):
        """Generate business insights from statistical analysis."""
        insights = []
        
        # Revenue insights
        if 'descriptive' in self.stats_results:
            total_amount_stats = self.stats_results['descriptive'].get('Total_Amount', {})
            if total_amount_stats:
                insights.append({
                    'category': 'Revenue',
                    'insight': f"Average transaction value is ${total_amount_stats['mean']:.2f} with high variability (std: ${total_amount_stats['std']:.2f})",
                    'recommendation': 'Focus on increasing transaction consistency and targeting high-value customers'
                })
        
        # Gender insights
        if 'hypothesis_tests' in self.stats_results:
            gender_test = self.stats_results['hypothesis_tests'].get('gender_spending_difference', {})
            if gender_test and gender_test.get('significant'):
                higher_spender = 'Male' if gender_test['male_mean'] > gender_test['female_mean'] else 'Female'
                insights.append({
                    'category': 'Demographics',
                    'insight': f"{higher_spender} customers spend significantly more on average",
                    'recommendation': f'Develop targeted marketing strategies for {higher_spender} customer segment'
                })
        
        # Product category insights
        if 'categorical' in self.stats_results:
            categories = self.stats_results['categorical'].get('Product_Category', {})
            if categories and 'value_counts' in categories:
                top_category = max(categories['value_counts'], key=categories['value_counts'].get)
                insights.append({
                    'category': 'Products',
                    'insight': f"{top_category} is the most popular product category",
                    'recommendation': f'Invest in expanding {top_category} product lines and inventory'
                })
        
        # Customer segment insights
        if 'customer_segments' in self.stats_results:
            segments = self.stats_results['customer_segments']
            if 'High Value' in segments:
                high_value_count = segments['High Value']['customer_count']
                total_customers = sum(seg['customer_count'] for seg in segments.values())
                high_value_percentage = (high_value_count / total_customers) * 100
                
                insights.append({
                    'category': 'Customer Loyalty',
                    'insight': f"High-value customers represent {high_value_percentage:.1f}% of customer base but drive significant revenue",
                    'recommendation': 'Implement VIP loyalty programs to retain high-value customers'
                })
        
        self.stats_results['business_insights'] = insights
        return insights
    
    def run_complete_analysis(self):
        """Run all statistical analyses."""
        print("Running Statistical Analysis...")
        
        self.descriptive_statistics()
        print("✓ Descriptive statistics completed")
        
        self.correlation_analysis()
        print("✓ Correlation analysis completed")
        
        self.hypothesis_testing()
        print("✓ Hypothesis testing completed")
        
        self.outlier_detection()
        print("✓ Outlier detection completed")
        
        self.categorical_Analysis()
        print("✓ Categorical analysis completed")
        
        self.customer_segments_analysis()
        print("✓ Customer segmentation completed")
        
        self.generate_insights()
        print("✓ Business insights generated")
        
        return self.stats_results
    
    def save_results(self, output_path='visuals/statistical_analysis.json'):
        """Save all statistical analysis results."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.stats_results, f, indent=2)
        
        print(f"✓ Statistical analysis results saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    from load_clean import DataLoader
    
    loader = DataLoader()
    data = loader.load_data()
    cleaned_data = loader.clean_data()
    
    if cleaned_data is not None:
        analyzer = StatisticalAnalyzer(cleaned_data)
        results = analyzer.run_complete_analysis()
        analyzer.save_results()
        
        print("\n" + "="*50)
        print("STATISTICAL ANALYSIS COMPLETED")
        print("="*50)