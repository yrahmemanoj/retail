"""
Recommendation System Module
Generates business recommendations based on EDA insights.
"""

import json
import os
from datetime import datetime
import numpy as np

class RecommendationEngine:
    """
    Generates actionable business recommendations from EDA results.
    """
    
    def __init__(self):
        self.recommendations = {
            'strategic': [],
            'operational': [],
            'marketing': [],
            'inventory': [],
            'customer_experience': []
        }
        self.priority_weights = {
            'revenue_impact': 0.3,
            'implementation_ease': 0.2,
            'customer_satisfaction': 0.25,
            'market_opportunity': 0.25
        }
    
    def analyze_revenue_opportunities(self, stats_data, ts_data):
        """Identify revenue enhancement opportunities."""
        recommendations = []
        
        # Revenue volatility analysis
        if ts_data and 'daily_analysis' in ts_data:
            daily_stats = ts_data['daily_analysis']['statistics']
            volatility = daily_stats.get('revenue_volatility', 0)
            avg_revenue = daily_stats.get('avg_daily_revenue', 0)
            
            if avg_revenue > 0:
                cv = (volatility / avg_revenue) * 100
                if cv > 30:
                    recommendations.append({
                        'category': 'strategic',
                        'title': 'Revenue Stabilization Program',
                        'description': f'Daily revenue shows high volatility (CV: {cv:.1f}%)',
                        'recommendation': 'Implement demand forecasting and dynamic pricing strategies',
                        'impact': 'High',
                        'timeline': '3-6 months',
                        'priority': 90
                    })
        
        # Seasonal revenue optimization
        if ts_data and 'seasonal_analysis' in ts_data:
            seasonal_data = ts_data['seasonal_analysis']['chart_data']
            if seasonal_data:
                revenues = [item['revenue'] for item in seasonal_data]
                max_revenue = max(revenues)
                min_revenue = min(revenues)
                seasonal_gap = ((max_revenue - min_revenue) / max_revenue) * 100
                
                if seasonal_gap > 25:
                    best_season = max(seasonal_data, key=lambda x: x['revenue'])['season']
                    worst_season = min(seasonal_data, key=lambda x: x['revenue'])['season']
                    
                    recommendations.append({
                        'category': 'marketing',
                        'title': 'Seasonal Campaign Optimization',
                        'description': f'Large seasonal revenue gap: {seasonal_gap:.1f}% between {best_season} and {worst_season}',
                        'recommendation': f'Develop targeted promotions for {worst_season} and maximize {best_season} performance',
                        'impact': 'Medium',
                        'timeline': '1-2 months',
                        'priority': 75
                    })
        
        return recommendations
    
    def analyze_customer_opportunities(self, cp_data):
        """Identify customer-focused opportunities."""
        recommendations = []
        
        # Customer retention analysis
        if 'customer_behavior' in cp_data:
            behavior_stats = cp_data['customer_behavior']['statistics']
            retention_rate = behavior_stats.get('customer_retention_rate', 0)
            
            if retention_rate < 60:
                recommendations.append({
                    'category': 'customer_experience',
                    'title': 'Customer Retention Enhancement',
                    'description': f'Customer retention rate is {retention_rate:.1f}% (below industry standard)',
                    'recommendation': 'Launch loyalty program with personalized rewards and targeted re-engagement campaigns',
                    'impact': 'High',
                    'timeline': '2-4 months',
                    'priority': 95
                })
            
            # High-value customer focus
            clv_segments = cp_data['customer_behavior'].get('clv_segments', {})
            if 'High Value' in clv_segments:
                high_value_pct = clv_segments['High Value']['percentage']
                if high_value_pct < 20:
                    recommendations.append({
                        'category': 'strategic',
                        'title': 'High-Value Customer Expansion',
                        'description': f'High-value customers represent only {high_value_pct:.1f}% of customer base',
                        'recommendation': 'Develop VIP program and premium service tiers to convert medium-value customers',
                        'impact': 'High',
                        'timeline': '3-6 months',
                        'priority': 85
                    })
        
        # Cross-selling opportunities
        if 'customer_product_matrix' in cp_data:
            cross_sell = cp_data['customer_product_matrix']['cross_selling_opportunities']
            if cross_sell:
                best_opportunity = list(cross_sell.keys())[0]
                rate = cross_sell[best_opportunity]['cross_sell_rate']
                
                recommendations.append({
                    'category': 'marketing',
                    'title': 'Cross-Selling Campaign',
                    'description': f'Best cross-selling opportunity: {best_opportunity} ({rate:.1f}% success rate)',
                    'recommendation': 'Create bundled product offerings and targeted email campaigns',
                    'impact': 'Medium',
                    'timeline': '1-2 months',
                    'priority': 70
                })
        
        return recommendations
    
    def analyze_product_opportunities(self, cp_data):
        """Identify product and inventory opportunities."""
        recommendations = []
        
        if 'product_performance' in cp_data:
            performance_stats = cp_data['product_performance']['statistics']
            chart_data = cp_data['product_performance']['chart_data']
            
            # Market concentration risk
            concentration = performance_stats.get('revenue_concentration', 0)
            if concentration > 40:
                best_category = performance_stats.get('best_performing_category', '')
                recommendations.append({
                    'category': 'strategic',
                    'title': 'Product Portfolio Diversification',
                    'description': f'{best_category} dominates with {concentration:.1f}% market share',
                    'recommendation': 'Invest in expanding underperforming categories and reduce dependency risk',
                    'impact': 'Medium',
                    'timeline': '6-12 months',
                    'priority': 65
                })
            
            # Underperforming categories
            if chart_data:
                sorted_categories = sorted(chart_data, key=lambda x: x['revenue'])
                if len(sorted_categories) >= 2:
                    worst_category = sorted_categories[0]
                    avg_revenue = np.mean([cat['revenue'] for cat in chart_data])
                    
                    if worst_category['revenue'] < avg_revenue * 0.5:
                        recommendations.append({
                            'category': 'inventory',
                            'title': f'{worst_category["category"]} Category Optimization',
                            'description': f'{worst_category["category"]} significantly underperforms (50% below average)',
                            'recommendation': 'Conduct market research and consider category refresh or discontinuation',
                            'impact': 'Medium',
                            'timeline': '2-3 months',
                            'priority': 60
                        })
        
        return recommendations
    
    def analyze_operational_opportunities(self, ts_data):
        """Identify operational efficiency opportunities."""
        recommendations = []
        
        # Weekly pattern optimization
        if 'weekly_patterns' in ts_data:
            weekly_stats = ts_data['weekly_patterns']['statistics']
            dow_data = ts_data['weekly_patterns']['day_of_week_data']
            
            if dow_data:
                revenues = [day['revenue'] for day in dow_data]
                max_revenue = max(revenues)
                min_revenue = min(revenues)
                weekly_variance = ((max_revenue - min_revenue) / max_revenue) * 100
                
                if weekly_variance > 50:
                    best_day = max(dow_data, key=lambda x: x['revenue'])['day']
                    worst_day = min(dow_data, key=lambda x: x['revenue'])['day']
                    
                    recommendations.append({
                        'category': 'operational',
                        'title': 'Staffing and Inventory Optimization',
                        'description': f'Large weekly variance: {best_day} vs {worst_day} ({weekly_variance:.1f}% difference)',
                        'recommendation': 'Adjust staffing levels and inventory distribution based on weekly patterns',
                        'impact': 'Medium',
                        'timeline': '1 month',
                        'priority': 55
                    })
        
        # Trend-based recommendations
        if 'trend_analysis' in ts_data:
            trend_stats = ts_data['trend_analysis']['statistics']
            trend_direction = trend_stats.get('trend_direction', '')
            r_squared = trend_stats.get('r_squared', 0)
            
            if r_squared > 0.7:  # Strong trend
                if trend_direction == 'Increasing':
                    recommendations.append({
                        'category': 'strategic',
                        'title': 'Growth Acceleration Program',
                        'description': f'Strong positive trend identified (R²: {r_squared:.2f})',
                        'recommendation': 'Invest in capacity expansion and market penetration strategies',
                        'impact': 'High',
                        'timeline': '6-12 months',
                        'priority': 80
                    })
                elif trend_direction == 'Decreasing':
                    recommendations.append({
                        'category': 'strategic',
                        'title': 'Revenue Decline Mitigation',
                        'description': f'Strong negative trend identified (R²: {r_squared:.2f})',
                        'recommendation': 'Implement immediate corrective measures and market analysis',
                        'impact': 'Critical',
                        'timeline': '1 month',
                        'priority': 100
                    })
        
        return recommendations
    
    def analyze_demographic_opportunities(self, cp_data):
        """Identify demographic-based opportunities."""
        recommendations = []
        
        if 'demographics' in cp_data:
            demographics = cp_data['demographics']
            
            # Gender-based opportunities
            if 'gender' in demographics:
                gender_data = demographics['gender']
                if len(gender_data) == 2:
                    revenues = [item['total_spent'] for item in gender_data]
                    max_revenue = max(revenues)
                    min_revenue = min(revenues)
                    gender_gap = ((max_revenue - min_revenue) / max_revenue) * 100
                    
                    if gender_gap > 20:
                        high_spender = max(gender_data, key=lambda x: x['total_spent'])
                        low_spender = min(gender_data, key=lambda x: x['total_spent'])
                        
                        recommendations.append({
                            'category': 'marketing',
                            'title': f'{low_spender["gender"]} Market Expansion',
                            'description': f'{gender_gap:.1f}% revenue gap between genders',
                            'recommendation': f'Develop targeted marketing campaigns and product lines for {low_spender["gender"]} customers',
                            'impact': 'Medium',
                            'timeline': '3-4 months',
                            'priority': 65
                        })
            
            # Age group opportunities
            if 'age_groups' in demographics:
                age_data = demographics['age_groups']
                if age_data:
                    sorted_ages = sorted(age_data, key=lambda x: x['total_spent'], reverse=True)
                    if len(sorted_ages) >= 2:
                        top_age_group = sorted_ages[0]
                        recommendations.append({
                            'category': 'marketing',
                            'title': f'{top_age_group["age_group"]} Segment Focus',
                            'description': f'{top_age_group["age_group"]} age group shows highest spending',
                            'recommendation': 'Develop age-specific marketing strategies and product recommendations',
                            'impact': 'Medium',
                            'timeline': '2-3 months',
                            'priority': 60
                        })
        
        return recommendations
    
    def prioritize_recommendations(self):
        """Prioritize recommendations based on impact and feasibility."""
        all_recommendations = []
        
        for category, recs in self.recommendations.items():
            for rec in recs:
                rec['category_type'] = category
                all_recommendations.append(rec)
        
        # Sort by priority score
        prioritized = sorted(all_recommendations, key=lambda x: x['priority'], reverse=True)
        
        return prioritized
    
    def generate_action_plan(self, recommendations):
        """Generate actionable implementation plan."""
        action_plan = {
            'immediate_actions': [],
            'short_term_goals': [],
            'long_term_strategy': []
        }
        
        for rec in recommendations:
            timeline = rec.get('timeline', '')
            action_item = {
                'title': rec['title'],
                'description': rec['recommendation'],
                'impact': rec['impact'],
                'category': rec['category_type']
            }
            
            if 'month' in timeline and '1' in timeline:
                action_plan['immediate_actions'].append(action_item)
            elif 'months' in timeline and any(x in timeline for x in ['2', '3', '4', '5', '6']):
                action_plan['short_term_goals'].append(action_item)
            else:
                action_plan['long_term_strategy'].append(action_item)
        
        return action_plan
    
    def run_complete_analysis(self, stats_data=None, ts_data=None, cp_data=None):
        """Run complete recommendation analysis."""
        print("Generating Business Recommendations...")
        
        # Analyze different opportunity areas
        if stats_data and ts_data:
            revenue_recs = self.analyze_revenue_opportunities(stats_data, ts_data)
            self.recommendations['strategic'].extend(revenue_recs)
        
        if cp_data:
            customer_recs = self.analyze_customer_opportunities(cp_data)
            self.recommendations['customer_experience'].extend(customer_recs)
            
            product_recs = self.analyze_product_opportunities(cp_data)
            self.recommendations['inventory'].extend(product_recs)
            
            demo_recs = self.analyze_demographic_opportunities(cp_data)
            self.recommendations['marketing'].extend(demo_recs)
        
        if ts_data:
            operational_recs = self.analyze_operational_opportunities(ts_data)
            self.recommendations['operational'].extend(operational_recs)
        
        print("✓ Revenue opportunities analyzed")
        print("✓ Customer opportunities analyzed")
        print("✓ Product opportunities analyzed")
        print("✓ Operational opportunities analyzed")
        print("✓ Demographic opportunities analyzed")
        
        # Prioritize and create action plan
        prioritized_recs = self.prioritize_recommendations()
        action_plan = self.generate_action_plan(prioritized_recs[:15])  # Top 15 recommendations
        
        return {
            'recommendations': prioritized_recs,
            'action_plan': action_plan,
            'summary': {
                'total_recommendations': len(prioritized_recs),
                'high_impact_count': len([r for r in prioritized_recs if r['impact'] == 'High']),
                'critical_count': len([r for r in prioritized_recs if r['impact'] == 'Critical']),
                'categories_covered': list(set([r['category_type'] for r in prioritized_recs]))
            }
        }
    
    def save_recommendations(self, results, output_path='recommendations/recommendations.json'):
        """Save recommendations to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Recommendations saved to {output_path}")
    
    def generate_markdown_report(self, results, output_path='recommendations/recommendations.md'):
        """Generate markdown report of recommendations."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding="utf-8") as f:
            f.write("# Retail Sales Analysis - Business Recommendations\n\n")
            f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            summary = results['summary']
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Recommendations:** {summary['total_recommendations']}\n")
            f.write(f"- **High Impact Opportunities:** {summary['high_impact_count']}\n")
            f.write(f"- **Critical Issues:** {summary['critical_count']}\n")
            f.write(f"- **Categories Covered:** {', '.join(summary['categories_covered'])}\n\n")
            
            # Action Plan
            action_plan = results['action_plan']
            f.write("## Action Plan\n\n")
            
            f.write("### 🚨 Immediate Actions (1 Month)\n\n")
            for i, action in enumerate(action_plan['immediate_actions'], 1):
                f.write(f"{i}. **{action['title']}** ({action['impact']} Impact)\n")
                f.write(f"   - {action['description']}\n")
                f.write(f"   - Category: {action['category'].title()}\n\n")
            
            f.write("### 📈 Short-term Goals (2-6 Months)\n\n")
            for i, action in enumerate(action_plan['short_term_goals'], 1):
                f.write(f"{i}. **{action['title']}** ({action['impact']} Impact)\n")
                f.write(f"   - {action['description']}\n")
                f.write(f"   - Category: {action['category'].title()}\n\n")
            
            f.write("### 🎯 Long-term Strategy (6+ Months)\n\n")
            for i, action in enumerate(action_plan['long_term_strategy'], 1):
                f.write(f"{i}. **{action['title']}** ({action['impact']} Impact)\n")
                f.write(f"   - {action['description']}\n")
                f.write(f"   - Category: {action['category'].title()}\n\n")
            
            # Detailed Recommendations
            f.write("## Detailed Recommendations\n\n")
            
            categories = {}
            for rec in results['recommendations']:
                cat = rec['category_type']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(rec)
            
            for category, recs in categories.items():
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                
                for rec in recs:
                    f.write(f"#### {rec['title']}\n\n")
                    f.write(f"**Priority Score:** {rec['priority']}/100\n\n")
                    f.write(f"**Impact:** {rec['impact']}\n\n")
                    f.write(f"**Timeline:** {rec['timeline']}\n\n")
                    f.write(f"**Analysis:** {rec['description']}\n\n")
                    f.write(f"**Recommended Action:** {rec['recommendation']}\n\n")
                    f.write("---\n\n")
        
        print(f"✓ Markdown report saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    engine = RecommendationEngine()
    
    # Load analysis results
    stats_data = None
    ts_data = None
    cp_data = None
    
    try:
        with open('visuals/statistical_analysis.json', 'r') as f:
            stats_data = json.load(f)
    except FileNotFoundError:
        pass
    
    try:
        with open('visuals/time_series_analysis.json', 'r') as f:
            ts_data = json.load(f)
    except FileNotFoundError:
        pass
    
    try:
        with open('visuals/customer_product_analysis.json', 'r') as f:
            cp_data = json.load(f)
    except FileNotFoundError:
        pass
    
    # Generate recommendations
    results = engine.run_complete_analysis(stats_data, ts_data, cp_data)
    
    # Save results
    engine.save_recommendations(results)
    engine.generate_markdown_report(results)
    
    print("\n" + "="*50)
    print("BUSINESS RECOMMENDATIONS COMPLETED")
    print("="*50)