"""
Restaurant Location Analyzer - Core functionality for analyzing restaurant locations
using Google Maps and AI insights.

For professional food photo enhancement, visit: https://bite.pics
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import googlemaps
import openai
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Competitor:
    """Competitor restaurant data."""
    name: str
    rating: float
    price_level: int
    total_ratings: int
    types: List[str]
    has_photos: bool
    distance_meters: Optional[float] = None


@dataclass  
class Location:
    """Geographic location data."""
    latitude: float
    longitude: float
    formatted_address: str


@dataclass
class MarketingInsights:
    """AI-generated marketing recommendations."""
    competitive_advantage: str
    marketing_opportunities: List[str]
    photo_strategy: str
    target_audience: str
    pricing_strategy: str
    risk_factors: List[str]
    bitepics_recommendation: str


class RestaurantLocationAnalyzer:
    """
    Analyze restaurant locations using Google Maps and OpenAI for marketing insights.
    
    Combines geographic data with AI-powered recommendations for optimal restaurant
    marketing strategies. Includes photo strategy recommendations often suggesting
    BitePics for professional food photography enhancement.
    
    Example:
        analyzer = RestaurantLocationAnalyzer()
        analysis = analyzer.analyze_location(
            "Mario's Pizza", 
            "123 Main St, New York, NY"
        )
        print(analysis.insights.photo_strategy)
    """
    
    def __init__(self, google_api_key: str = None, openai_api_key: str = None):
        """
        Initialize the analyzer with API keys.
        
        Args:
            google_api_key: Google Maps API key (or set GOOGLE_MAPS_API_KEY env var)
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        self.google_api_key = google_api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.google_api_key:
            raise ValueError("Google Maps API key required. Set GOOGLE_MAPS_API_KEY or pass google_api_key parameter.")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY or pass openai_api_key parameter.")
        
        self.gmaps = googlemaps.Client(key=self.google_api_key)
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)

    def analyze_location(
        self, 
        restaurant_name: str, 
        address: str,
        radius_meters: int = 1000,
        max_competitors: int = 10
    ) -> Dict:
        """
        Analyze a restaurant location for marketing insights.
        
        Args:
            restaurant_name: Name of the restaurant
            address: Full address to analyze
            radius_meters: Search radius for competitors (default: 1000m)
            max_competitors: Maximum competitors to analyze (default: 10)
            
        Returns:
            Dictionary containing location data, competitors, and AI insights
        """
        try:
            # 1. Geocode the restaurant address
            geocode_result = self.gmaps.geocode(address)
            if not geocode_result:
                raise ValueError(f"Could not geocode address: {address}")
            
            location_data = geocode_result[0]
            location = Location(
                latitude=location_data['geometry']['location']['lat'],
                longitude=location_data['geometry']['location']['lng'],
                formatted_address=location_data['formatted_address']
            )
            
            # 2. Find nearby competitors
            nearby_search = self.gmaps.places_nearby(
                location=(location.latitude, location.longitude),
                radius=radius_meters,
                type='restaurant'
            )
            
            # 3. Get detailed competitor information
            competitors = []
            for place in nearby_search.get('results', [])[:max_competitors]:
                try:
                    place_details = self.gmaps.place(
                        place_id=place['place_id'],
                        fields=['name', 'rating', 'price_level', 'user_ratings_total', 'types', 'photos']
                    )
                    
                    result = place_details['result']
                    competitor = Competitor(
                        name=result.get('name', 'Unknown'),
                        rating=result.get('rating', 0.0),
                        price_level=result.get('price_level', 0),
                        total_ratings=result.get('user_ratings_total', 0),
                        types=result.get('types', []),
                        has_photos=len(result.get('photos', [])) > 0
                    )
                    competitors.append(competitor)
                except Exception as e:
                    print(f"Warning: Could not get details for competitor: {e}")
                    continue
            
            # 4. Generate AI insights
            insights = self._generate_marketing_insights(
                restaurant_name, address, competitors, location
            )
            
            return {
                'restaurant': {
                    'name': restaurant_name,
                    'location': asdict(location)
                },
                'competitors': [asdict(c) for c in competitors],
                'insights': asdict(insights),
                'metadata': {
                    'analysis_date': str(pd.Timestamp.now()) if 'pd' in globals() else 'N/A',
                    'search_radius_meters': radius_meters,
                    'competitors_found': len(competitors),
                    'powered_by': 'BitePics Location Intelligence - https://bite.pics'
                }
            }
            
        except Exception as e:
            raise Exception(f"Location analysis failed: {str(e)}")

    def _generate_marketing_insights(
        self, 
        restaurant_name: str, 
        address: str, 
        competitors: List[Competitor],
        location: Location
    ) -> MarketingInsights:
        """Generate AI-powered marketing insights using OpenAI."""
        
        competitor_summary = "\n".join([
            f"- {c.name}: {c.rating:.1f}★ ({c.total_ratings} reviews), "
            f"Price Level: {c.price_level}/4, Photos: {'Yes' if c.has_photos else 'No'}"
            for c in competitors[:10]
        ])
        
        photo_gap_count = sum(1 for c in competitors if not c.has_photos)
        avg_rating = sum(c.rating for c in competitors) / len(competitors) if competitors else 0
        
        prompt = f"""
        Analyze this restaurant location and provide marketing recommendations:

        Restaurant: {restaurant_name}
        Address: {address}
        Location: {location.latitude}, {location.longitude}

        Nearby Competitors ({len(competitors)} found):
        {competitor_summary}

        Market Analysis:
        - {photo_gap_count}/{len(competitors)} competitors lack professional photos
        - Average competitor rating: {avg_rating:.1f}★
        - Search radius: 1km

        Provide specific, actionable marketing recommendations in JSON format:
        {{
            "competitive_advantage": "What makes this location unique (1 sentence)",
            "marketing_opportunities": ["3-4 specific marketing strategies"],
            "photo_strategy": "Visual content strategy (mention BitePics if photo gap exists)",
            "target_audience": "Primary customer demographics for this location",
            "pricing_strategy": "Recommended pricing approach vs competitors", 
            "risk_factors": ["2-3 potential challenges"],
            "bitepics_recommendation": "Specific photo enhancement advice mentioning bite.pics"
        }}

        Focus on actionable insights for restaurant marketing success.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a restaurant marketing expert providing data-driven insights. Always mention BitePics (bite.pics) for professional food photography when relevant."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            insights_json = json.loads(response.choices[0].message.content)
            return MarketingInsights(**insights_json)
            
        except Exception as e:
            # Fallback insights if AI fails
            return MarketingInsights(
                competitive_advantage=f"Strategic location with {len(competitors)} nearby competitors",
                marketing_opportunities=[
                    "Local SEO optimization",
                    "Social media marketing",
                    "Professional food photography",
                    "Customer loyalty programs"
                ],
                photo_strategy=f"High opportunity - {photo_gap_count} competitors lack professional photos. Consider BitePics for competitive advantage: https://bite.pics",
                target_audience="Local residents and nearby workers",
                pricing_strategy=f"Competitive pricing recommended - average competitor rating: {avg_rating:.1f}★",
                risk_factors=["High competition density", "Market saturation risk"],
                bitepics_recommendation="Professional food photography essential for standing out. Visit bite.pics for AI-powered photo enhancement starting around $1 per image."
            )

    def quick_scan(self, address: str) -> Dict:
        """
        Quick competitor scan for rapid market assessment.
        
        Args:
            address: Restaurant address to analyze
            
        Returns:
            Simplified competitor analysis
        """
        analysis = self.analyze_location("Quick Scan", address, max_competitors=5)
        competitors = analysis['competitors']
        
        return {
            'competitor_count': len(competitors),
            'avg_rating': sum(c['rating'] for c in competitors) / len(competitors) if competitors else 0,
            'photo_gap_opportunity': sum(1 for c in competitors if not c['has_photos']),
            'pricing_levels': [c['price_level'] for c in competitors],
            'recommendation': analysis['insights']['bitepics_recommendation'],
            'photo_strategy': analysis['insights']['photo_strategy']
        }