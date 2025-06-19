"""
Main EDA Runner
Orchestrates the complete exploratory data analysis pipeline.
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_clean import DataLoader
from stats import StatisticalAnalyzer
from time_series import TimeSeriesAnalyzer
from customer_product import CustomerProductAnalyzer
from visuals import VisualizationGenerator
from recommend import RecommendationEngine

class EDARunner:
    """
    Main class to run complete EDA pipeline.
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        
    def print_header(self):
        """Print analysis header."""
        print("="*60)
        print("🔍 RETAIL SALES DATA - EXPLORATORY DATA ANALYSIS")
        print("="*60)
        print(f"Analysis Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
    
    def print_section(self, title):
        """Print section header."""
        print(f"\n{'='*20} {title.upper()} {'='*20}")
    
    def run_data_loading_and_cleaning(self):
        """Run data loading and cleaning phase."""
        self.print_section("Data Loading & Cleaning")
        
        loader = DataLoader()
        
        # Load data
        raw_data = loader.load_data()
        if raw_data is None:
            print("❌ Failed to load data. Exiting.")
            return None
        
        # Validate data
        loader.validate_data()
        
        # Clean data
        cleaned_data = loader.clean_data()
        if cleaned_data is None:
            print("❌ Failed to clean data. Exiting.")
            return None
        
        # Generate summary
        summary = loader.get_data_summary()
        
        # Export results
        loader.export_cleaned_data()
        loader.save_data_quality_report()
        
        self.results['data_summary'] = summary
        return cleaned_data
    
    def run_statistical_analysis(self, df):
        """Run statistical analysis phase."""
        self.print_section("Statistical Analysis")
        
        analyzer = StatisticalAnalyzer(df)
        stats_results = analyzer.run_complete_analysis()
        analyzer.save_results()
        
        self.results['statistical_analysis'] = stats_results
        return stats_results
    
    def run_time_series_analysis(self, df):
        """Run time series analysis phase."""
        self.print_section("Time Series Analysis")
        
        analyzer = TimeSeriesAnalyzer(df)
        ts_results = analyzer.run_complete_analysis()
        analyzer.save_results()
        
        self.results['time_series_analysis'] = ts_results
        return ts_results
    
    def run_customer_product_analysis(self, df):
        """Run customer and product analysis phase."""
        self.print_section("Customer & Product Analysis")
        
        analyzer = CustomerProductAnalyzer(df)
        cp_results = analyzer.run_complete_analysis()
        analyzer.save_results()
        
        self.results['customer_product_analysis'] = cp_results
        return cp_results
    
    def run_visualization_generation(self):
        """Run visualization generation phase."""
        self.print_section("Visualization Generation")
        
        generator = VisualizationGenerator()
        viz_config = generator.generate_complete_visualization_suite()
        
        self.results['visualization_config'] = viz_config
        return viz_config
    
    def run_recommendation_generation(self):
        """Run recommendation generation phase."""
        self.print_section("Business Recommendations")
        
        engine = RecommendationEngine()
        
        # Get analysis results
        stats_data = self.results.get('statistical_analysis')
        ts_data = self.results.get('time_series_analysis')
        cp_data = self.results.get('customer_product_analysis')
        
        # Generate recommendations
        recommendations = engine.run_complete_analysis(stats_data, ts_data, cp_data)
        
        # Save results
        engine.save_recommendations(recommendations)
        engine.generate_markdown_report(recommendations)
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def generate_summary_report(self):
        """Generate final summary report."""
        self.print_section("Analysis Summary")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Collect key metrics
        summary_data = {}
        
        if 'data_summary' in self.results:
            basic_info = self.results['data_summary']['basic_info']
            summary_data.update({
                'total_records': basic_info.get('total_records', 0),
                'total_customers': basic_info.get('total_customers', 0),
                'total_revenue': basic_info.get('total_revenue', 0),
                'product_categories': basic_info.get('product_categories', 0)
            })
        
        if 'recommendations' in self.results:
            rec_summary = self.results['recommendations']['summary']
            summary_data.update({
                'total_recommendations': rec_summary.get('total_recommendations', 0),
                'high_impact_recommendations': rec_summary.get('high_impact_count', 0),
                'critical_issues': rec_summary.get('critical_count', 0)
            })
        
        # Print summary
        print(f"✅ Analysis completed successfully!")
        print(f"⏱️  Total duration: {duration.total_seconds():.1f} seconds")
        print(f"📊 Records analyzed: {summary_data.get('total_records', 0):,}")
        print(f"👥 Customers analyzed: {summary_data.get('total_customers', 0):,}")
        print(f"💰 Total revenue: ${summary_data.get('total_revenue', 0):,.2f}")
        print(f"📦 Product categories: {summary_data.get('product_categories', 0)}")
        print(f"💡 Recommendations generated: {summary_data.get('total_recommendations', 0)}")
        print(f"🔥 High-impact opportunities: {summary_data.get('high_impact_recommendations', 0)}")
        
        # Save complete results
        complete_results = {
            'analysis_metadata': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'version': '1.0.0'
            },
            'summary_metrics': summary_data,
            'results': self.results
        }
        
        os.makedirs('visuals', exist_ok=True)
        with open('visuals/complete_eda_results.json', 'w') as f:
            json.dump(complete_results, f, indent=2)
        
        print(f"💾 Complete results saved to visuals/complete_eda_results.json")
        
        return complete_results
    
    def run_complete_pipeline(self):
        """Run the complete EDA pipeline."""
        try:
            self.print_header()
            
            # 1. Data Loading and Cleaning
            cleaned_data = self.run_data_loading_and_cleaning()
            if cleaned_data is None:
                return False
            
            # 2. Statistical Analysis
            stats_results = self.run_statistical_analysis(cleaned_data)
            
            # 3. Time Series Analysis
            ts_results = self.run_time_series_analysis(cleaned_data)
            
            # 4. Customer & Product Analysis
            cp_results = self.run_customer_product_analysis(cleaned_data)
            
            # 5. Visualization Generation
            viz_config = self.run_visualization_generation()
            
            # 6. Business Recommendations
            recommendations = self.run_recommendation_generation()
            
            # 7. Summary Report
            summary_report = self.generate_summary_report()
            
            print("\n" + "="*60)
            print("🎉 COMPLETE EDA PIPELINE FINISHED SUCCESSFULLY!")
            print("="*60)
            print("\n📁 Output Files Generated:")
            print("   - data/cleaned_retail_data.csv")
            print("   - visuals/data_quality_report.json")
            print("   - visuals/statistical_analysis.json")
            print("   - visuals/time_series_analysis.json")
            print("   - visuals/customer_product_analysis.json")
            print("   - visuals/dashboard_config.json")
            print("   - visuals/complete_eda_results.json")
            print("   - recommendations/recommendations.json")
            print("   - recommendations/recommendations.md")
            
            print("\n🌐 Next Steps:")
            print("   1. Open dashboard/index.html in your browser")
            print("   2. Review recommendations/recommendations.md")
            print("   3. Run the development server for interactive dashboard")
            print("Open your dashboard at: http://localhost:8000/dashboard/")
            
            with open("your_report.md", "w", encoding="utf-8") as f:
                f.write("### 🚨 Immediate Actions (1 Month)\n\n")
                f.write("- Review high-impact recommendations\n")
                f.write("- Implement quick wins for immediate revenue boost\n")
                f.write("- Monitor key metrics for changes\n")
                f.write("- Schedule follow-up analysis in 1 month\n")
            
            print("📄 Action report generated: your_report.md")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during EDA pipeline: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    runner = EDARunner()
    success = runner.run_complete_pipeline()
    
    if success:
        print("\n🚀 Ready to explore your data insights!")
    else:
        print("\n💥 EDA pipeline failed. Please check the error messages above.")

