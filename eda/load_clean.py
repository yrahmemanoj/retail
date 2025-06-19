"""
Data Loading and Cleaning Module
Handles data import, validation, and preprocessing for retail sales analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

class DataLoader:
    """
    Handles loading and cleaning of retail sales data.
    """
    
    def __init__(self, data_path='data/retail_sales_dataset.csv'):
        self.data_path = data_path
        self.df = None
        self.cleaned_df = None
        self.data_quality_report = {}
    
    def load_data(self):
        """Load raw data from CSV file."""
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"✓ Data loaded successfully: {len(self.df)} records")
            return self.df
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            return None
    
    def validate_data(self):
        """Perform data quality validation."""
        if self.df is None:
            return False
        
        # Basic validation checks
        validations = {
            'total_records': len(self.df),
            'missing_values': self.df.isnull().sum().to_dict(),
            'duplicate_records': self.df.duplicated().sum(),
            'date_format_errors': 0,
            'negative_values': 0,
            'data_types': self.df.dtypes.to_dict()
        }
        
        # Check for negative values in numeric columns
        numeric_cols = ['Age', 'Quantity', 'Price_per_Unit', 'Total_Amount']
        for col in numeric_cols:
            if col in self.df.columns:
                validations['negative_values'] += (self.df[col] < 0).sum()
        
        # Validate date format
        try:
            pd.to_datetime(self.df['Date'])
        except:
            validations['date_format_errors'] = len(self.df)
        
        self.data_quality_report = validations
        return True
    
    def clean_data(self):
        """Clean and preprocess the data."""
        if self.df is None:
            return None
        
        # Create a copy for cleaning
        self.cleaned_df = self.df.copy()
        
        # Convert Date column to datetime
        self.cleaned_df['Date'] = pd.to_datetime(self.cleaned_df['Date'])
        
        # Remove duplicates
        initial_count = len(self.cleaned_df)
        self.cleaned_df = self.cleaned_df.drop_duplicates()
        removed_duplicates = initial_count - len(self.cleaned_df)
        
        # Handle missing values
        # For numeric columns, fill with median
        numeric_columns = ['Age', 'Quantity', 'Price_per_Unit', 'Total_Amount']
        for col in numeric_columns:
            if col in self.cleaned_df.columns:
                self.cleaned_df[col] = self.cleaned_df[col].fillna(self.cleaned_df[col].median())
        
        # For categorical columns, fill with mode
        categorical_columns = ['Gender', 'Product_Category']
        for col in categorical_columns:
            if col in self.cleaned_df.columns:
                mode_value = self.cleaned_df[col].mode()[0] if not self.cleaned_df[col].mode().empty else 'Unknown'
                self.cleaned_df[col] = self.cleaned_df[col].fillna(mode_value)
        
        # Add derived columns
        self.cleaned_df['Year'] = self.cleaned_df['Date'].dt.year
        self.cleaned_df['Month'] = self.cleaned_df['Date'].dt.month
        self.cleaned_df['Day_of_Week'] = self.cleaned_df['Date'].dt.dayofweek
        self.cleaned_df['Week_of_Year'] = self.cleaned_df['Date'].dt.isocalendar().week
        
        # Create age groups
        self.cleaned_df['Age_Group'] = pd.cut(
            self.cleaned_df['Age'], 
            bins=[0, 25, 35, 45, 55, 100], 
            labels=['18-25', '26-35', '36-45', '46-55', '55+']
        )
        
        # Create price categories
        self.cleaned_df['Price_Category'] = pd.cut(
            self.cleaned_df['Price_per_Unit'],
            bins=[0, 50, 100, 300, 1000, float('inf')],
            labels=['Budget', 'Economy', 'Mid-range', 'Premium', 'Luxury']
        )
        
        print(f"✓ Data cleaned successfully")
        print(f"  - Removed {removed_duplicates} duplicate records")
        print(f"  - Final dataset: {len(self.cleaned_df)} records")
        
        return self.cleaned_df
    
    def get_data_summary(self):
        """Generate comprehensive data summary."""
        if self.cleaned_df is None:
            return None
        
        summary = {
            'basic_info': {
                'total_records': len(self.cleaned_df),
                'total_customers': self.cleaned_df['Customer_ID'].nunique(),
                'date_range': {
                    'start': self.cleaned_df['Date'].min().strftime('%Y-%m-%d'),
                    'end': self.cleaned_df['Date'].max().strftime('%Y-%m-%d')
                },
                'product_categories': self.cleaned_df['Product_Category'].nunique(),
                'total_revenue': float(self.cleaned_df['Total_Amount'].sum())
            },
            'categorical_distributions': {
                'gender': self.cleaned_df['Gender'].value_counts().to_dict(),
                'product_category': self.cleaned_df['Product_Category'].value_counts().to_dict(),
                'age_group': self.cleaned_df['Age_Group'].value_counts().to_dict()
            },
            'numerical_statistics': {
                'age': {
                    'mean': float(self.cleaned_df['Age'].mean()),
                    'median': float(self.cleaned_df['Age'].median()),
                    'std': float(self.cleaned_df['Age'].std())
                },
                'quantity': {
                    'mean': float(self.cleaned_df['Quantity'].mean()),
                    'median': float(self.cleaned_df['Quantity'].median()),
                    'std': float(self.cleaned_df['Quantity'].std())
                },
                'total_amount': {
                    'mean': float(self.cleaned_df['Total_Amount'].mean()),
                    'median': float(self.cleaned_df['Total_Amount'].median()),
                    'std': float(self.cleaned_df['Total_Amount'].std())
                }
            }
        }
        
        return summary
    
    def export_cleaned_data(self, output_path='data/cleaned_retail_data.csv'):
        """Export cleaned data to CSV."""
        if self.cleaned_df is not None:
            self.cleaned_df.to_csv(output_path, index=False)
            print(f"✓ Cleaned data exported to {output_path}")
            return True
        return False
    
    def save_data_quality_report(self, output_path='visuals/data_quality_report.json'):
        """Save data quality report as JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert numpy types to Python types for JSON serialization
        report = {}
        for key, value in self.data_quality_report.items():
            if isinstance(value, dict):
                report[key] = {k: int(v) if isinstance(v, (np.integer, np.int64)) else str(v) 
                              for k, v in value.items()}
            else:
                report[key] = int(value) if isinstance(value, (np.integer, np.int64)) else value
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Data quality report saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    loader = DataLoader()
    data = loader.load_data()
    
    if data is not None:
        loader.validate_data()
        cleaned_data = loader.clean_data()
        summary = loader.get_data_summary()
        
        # Export results
        loader.export_cleaned_data()
        loader.save_data_quality_report()
        
        print("\n" + "="*50)
        print("DATA LOADING AND CLEANING COMPLETED")
        print("="*50)