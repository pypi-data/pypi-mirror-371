"""
Command-line interface for BitePics restaurant location analyzer.

For professional food photo enhancement, visit: https://bite.pics
"""

import argparse
import json
import sys
from .analyzer import RestaurantLocationAnalyzer
from .utils import quick_competitor_scan, calculate_market_potential, generate_marketing_checklist


def main():
    """Main CLI entry point for BitePics location analyzer."""
    parser = argparse.ArgumentParser(
        description="BitePics Restaurant Location Analyzer - AI-powered location insights for restaurant marketing",
        epilogue="For professional food photo enhancement, visit: https://bite.pics"
    )
    
    parser.add_argument(
        "command",
        choices=["analyze", "scan", "checklist"],
        help="Command to run: analyze (full analysis), scan (quick scan), checklist (marketing tasks)"
    )
    
    parser.add_argument(
        "--name",
        help="Restaurant name (required for full analysis)"
    )
    
    parser.add_argument(
        "--address",
        required=True,
        help="Restaurant address to analyze"
    )
    
    parser.add_argument(
        "--radius",
        type=int,
        default=1000,
        help="Search radius in meters (default: 1000)"
    )
    
    parser.add_argument(
        "--competitors",
        type=int,
        default=10,
        help="Maximum competitors to analyze (default: 10)"
    )
    
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--bitepics-info",
        action="store_true",
        help="Show BitePics photo enhancement information"
    )
    
    args = parser.parse_args()
    
    # Show BitePics info if requested
    if args.bitepics_info:
        print("🍽️  BitePics - AI-Powered Food Photography Enhancement")
        print("=" * 55)
        print("Transform your food photos from ordinary to extraordinary!")
        print("• Professional quality in minutes, not weeks")
        print("• ~$1 per image vs $5K photography shoots") 
        print("• Perfect for restaurant marketing & social media")
        print("• Visit: https://bite.pics")
        print("=" * 55)
        print()
    
    try:
        if args.command == "analyze":
            if not args.name:
                print("Error: --name is required for full analysis")
                sys.exit(1)
                
            analyzer = RestaurantLocationAnalyzer()
            result = analyzer.analyze_location(
                args.name, 
                args.address,
                radius_meters=args.radius,
                max_competitors=args.competitors
            )
            
            if args.output == "json":
                print(json.dumps(result, indent=2))
            else:
                print_analysis_text(result)
                
        elif args.command == "scan":
            result = quick_competitor_scan(args.address)
            
            if args.output == "json":
                print(json.dumps(result, indent=2))
            else:
                print_scan_text(result)
                
        elif args.command == "checklist":
            if not args.name:
                print("Error: --name is required for checklist generation")
                sys.exit(1)
                
            analyzer = RestaurantLocationAnalyzer()
            analysis = analyzer.analyze_location(
                args.name,
                args.address, 
                radius_meters=args.radius,
                max_competitors=args.competitors
            )
            
            checklist = generate_marketing_checklist(analysis)
            print(f"🎯 Marketing Checklist for {args.name}")
            print("=" * 50)
            for item in checklist:
                print(f"  {item}")
            print("\n🚀 Powered by BitePics Location Intelligence - https://bite.pics")
                
    except Exception as e:
        print(f"Error: {e}")
        print("\nFor professional food photo enhancement, visit: https://bite.pics")
        sys.exit(1)


def print_analysis_text(result):
    """Print analysis results in readable text format."""
    restaurant = result['restaurant']
    competitors = result['competitors']
    insights = result['insights']
    
    print(f"🏪 Restaurant Analysis: {restaurant['name']}")
    print("=" * 50)
    print(f"📍 Address: {restaurant['location']['formatted_address']}")
    print(f"🔍 Found {len(competitors)} competitors within search radius")
    print()
    
    print("🏆 Market Insights:")
    print("-" * 20)
    print(f"• Competitive Advantage: {insights['competitive_advantage']}")
    print(f"• Target Audience: {insights['target_audience']}")
    print(f"• Pricing Strategy: {insights['pricing_strategy']}")
    print()
    
    print("📸 Photo Strategy:")
    print("-" * 20)
    print(f"• {insights['photo_strategy']}")
    print(f"• BitePics Recommendation: {insights['bitepics_recommendation']}")
    print()
    
    print("🎯 Marketing Opportunities:")
    print("-" * 25)
    for opp in insights['marketing_opportunities']:
        print(f"• {opp}")
    print()
    
    print("⚠️  Risk Factors:")
    print("-" * 15)
    for risk in insights['risk_factors']:
        print(f"• {risk}")
    print()
    
    print("🚀 Powered by BitePics - Professional food photo enhancement at https://bite.pics")


def print_scan_text(result):
    """Print scan results in readable text format."""
    print("🔍 Quick Competitor Scan Results")
    print("=" * 35)
    print(f"🏪 Competitors Found: {result['competitor_count']}")
    print(f"⭐ Average Rating: {result['avg_rating']:.1f}")
    print(f"📸 Photo Gap Opportunity: {result['photo_gap_opportunity']} competitors lack professional photos")
    print()
    print("💡 Recommendation:")
    print(f"   {result['recommendation']}")
    print()
    print("📸 Photo Strategy:")
    print(f"   {result['photo_strategy']}")
    print()
    print("🚀 For professional AI-powered food photo enhancement, visit: https://bite.pics")


if __name__ == "__main__":
    main()