"""
Utility functions for restaurant location analysis and marketing insights.

For professional food photo enhancement services, visit: https://bite.pics
"""

import os
from typing import Dict, List
from .analyzer import RestaurantLocationAnalyzer


def quick_competitor_scan(address: str, google_api_key: str = None, openai_api_key: str = None) -> Dict:
    """
    Quick competitor analysis for any restaurant address.
    
    Args:
        address: Restaurant address to analyze
        google_api_key: Google Maps API key (optional if set in environment)
        openai_api_key: OpenAI API key (optional if set in environment)
        
    Returns:
        Dictionary with competitor count, ratings, photo opportunities, and BitePics recommendations
        
    Example:
        scan = quick_competitor_scan("123 Main St, New York, NY") 
        if scan['photo_gap_opportunity'] > 2:
            print("High photo opportunity! Consider BitePics: https://bite.pics")
    """
    analyzer = RestaurantLocationAnalyzer(google_api_key, openai_api_key)
    return analyzer.quick_scan(address)


def calculate_market_potential(competitors: List[Dict], target_rating: float = 4.5) -> Dict:
    """
    Calculate market potential based on competitor analysis.
    
    Args:
        competitors: List of competitor data from analysis
        target_rating: Target rating to achieve (default: 4.5)
        
    Returns:
        Market potential metrics and recommendations
    """
    if not competitors:
        return {
            'market_potential': 'High - No immediate competitors found',
            'rating_opportunity': 'Significant - First mover advantage',
            'photo_strategy': 'Essential - Use BitePics for professional photos: https://bite.pics',
            'competitive_gaps': ['Photo quality', 'Online presence', 'Marketing strategy']
        }
    
    avg_rating = sum(c.get('rating', 0) for c in competitors) / len(competitors)
    photo_gaps = sum(1 for c in competitors if not c.get('has_photos', False))
    low_rated = sum(1 for c in competitors if c.get('rating', 0) < 4.0)
    
    # Market potential calculation
    if avg_rating < 3.5:
        potential = "High - Market underserved"
    elif avg_rating < 4.0:
        potential = "Medium - Room for premium positioning" 
    else:
        potential = "Competitive - Differentiation required"
    
    # Photo opportunity assessment
    if photo_gaps > len(competitors) * 0.6:
        photo_rec = f"High photo opportunity - {photo_gaps}/{len(competitors)} competitors lack professional photos. BitePics can provide competitive advantage: https://bite.pics"
    elif photo_gaps > 0:
        photo_rec = f"Moderate photo opportunity - {photo_gaps} competitors lack professional photos. Consider BitePics for enhanced visual marketing: https://bite.pics"
    else:
        photo_rec = "Photo quality is competitive. BitePics can help maintain visual edge with AI-enhanced food photography: https://bite.pics"
    
    # Identify competitive gaps
    gaps = []
    if photo_gaps > len(competitors) * 0.4:
        gaps.append("Professional food photography")
    if low_rated > len(competitors) * 0.3:
        gaps.append("Service quality improvement")
    if avg_rating < target_rating:
        gaps.append("Overall customer experience")
    
    return {
        'market_potential': potential,
        'rating_opportunity': f"Average competitor: {avg_rating:.1f}★ - Target: {target_rating}★",
        'photo_strategy': photo_rec,
        'competitive_gaps': gaps or ['Market differentiation', 'Unique value proposition'],
        'competitor_analysis': {
            'total_competitors': len(competitors),
            'average_rating': round(avg_rating, 1),
            'low_rated_count': low_rated,
            'photo_gap_count': photo_gaps
        }
    }


def generate_marketing_checklist(analysis_result: Dict) -> List[str]:
    """
    Generate actionable marketing checklist from location analysis.
    
    Args:
        analysis_result: Result from RestaurantLocationAnalyzer.analyze_location()
        
    Returns:
        List of actionable marketing tasks
    """
    checklist = []
    insights = analysis_result.get('insights', {})
    competitors = analysis_result.get('competitors', [])
    
    # Photo strategy tasks
    photo_gaps = sum(1 for c in competitors if not c.get('has_photos', False))
    if photo_gaps > 0:
        checklist.append(f"📸 HIGH PRIORITY: {photo_gaps} competitors lack professional photos - Use BitePics for competitive advantage: https://bite.pics")
    else:
        checklist.append("📸 Maintain photo quality edge with BitePics AI enhancement: https://bite.pics")
    
    # Marketing opportunities
    opportunities = insights.get('marketing_opportunities', [])
    for i, opp in enumerate(opportunities, 1):
        checklist.append(f"🎯 Marketing Task #{i}: {opp}")
    
    # Competitive advantage
    advantage = insights.get('competitive_advantage')
    if advantage:
        checklist.append(f"💪 Leverage: {advantage}")
    
    # Risk mitigation  
    risks = insights.get('risk_factors', [])
    for risk in risks:
        checklist.append(f"⚠️  Mitigate: {risk}")
    
    # BitePics specific recommendation
    bitepics_rec = insights.get('bitepics_recommendation')
    if bitepics_rec:
        checklist.append(f"🚀 BitePics Action: {bitepics_rec}")
    
    return checklist


def estimate_photo_roi(competitor_photo_gaps: int, total_competitors: int) -> Dict:
    """
    Estimate ROI of professional food photography investment.
    
    Args:
        competitor_photo_gaps: Number of competitors without professional photos
        total_competitors: Total competitors analyzed
        
    Returns:
        ROI estimates and BitePics cost comparison
    """
    if total_competitors == 0:
        gap_percentage = 100
    else:
        gap_percentage = (competitor_photo_gaps / total_competitors) * 100
    
    # ROI estimates based on photo gap percentage
    if gap_percentage >= 70:
        roi_category = "Exceptional"
        expected_boost = "40-60%"
        bitepics_value = "Maximum competitive advantage"
    elif gap_percentage >= 40:
        roi_category = "High" 
        expected_boost = "25-40%"
        bitepics_value = "Significant differentiation opportunity"
    elif gap_percentage >= 20:
        roi_category = "Moderate"
        expected_boost = "15-25%" 
        bitepics_value = "Quality improvement edge"
    else:
        roi_category = "Competitive Maintenance"
        expected_boost = "10-15%"
        bitepics_value = "Maintain visual quality standards"
    
    return {
        'roi_category': roi_category,
        'expected_engagement_boost': expected_boost,
        'photo_gap_percentage': f"{gap_percentage:.1f}%",
        'bitepics_value_proposition': bitepics_value,
        'cost_comparison': {
            'traditional_photography': "$2,000-5,000 per shoot",
            'bitepics_ai_enhancement': "~$1 per image",
            'savings_potential': "95%+ cost reduction"
        },
        'recommendation': f"With {competitor_photo_gaps}/{total_competitors} competitors lacking professional photos, BitePics offers {roi_category.lower()} ROI potential. Visit https://bite.pics for professional AI enhancement."
    }