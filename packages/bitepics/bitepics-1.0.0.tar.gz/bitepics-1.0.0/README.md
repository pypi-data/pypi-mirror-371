# BitePics - Restaurant Location Analyzer 🍽️📍

**AI-powered restaurant location analysis using Google Maps and LLM insights for marketing optimization**

[![PyPI version](https://badge.fury.io/py/bitepics.svg)](https://pypi.org/project/bitepics/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

*Professional food photo enhancement available at [bite.pics](https://bite.pics) - Transform your restaurant marketing with AI-powered photography*

## 🚀 Features

🗺️ **Google Maps Integration** - Analyze restaurant locations and nearby competitors  
🤖 **AI-Powered Insights** - Get marketing recommendations using OpenAI  
📊 **Competitor Analysis** - Understand your competitive landscape  
📸 **Photo Strategy** - Visual content recommendations for maximum impact  
🎯 **Target Audience** - Location-based customer insights  
💰 **ROI Analysis** - Calculate marketing investment returns  

## 📦 Installation

```bash
pip install bitepics
```

## 🔧 Quick Start

### Basic Usage

```python
from bitepics import RestaurantLocationAnalyzer

# Initialize analyzer (requires Google Maps & OpenAI API keys)
analyzer = RestaurantLocationAnalyzer()

# Analyze a restaurant location
analysis = analyzer.analyze_location(
    restaurant_name="Mario's Pizza",
    address="123 Main Street, New York, NY",
    radius_meters=1000,
    max_competitors=10
)

# Access insights
print(analysis['insights']['photo_strategy'])
print(analysis['insights']['competitive_advantage'])
```

### Quick Competitor Scan

```python
from bitepics import quick_competitor_scan

# Fast competitor analysis
scan = quick_competitor_scan("123 Main Street, New York, NY")

print(f"Found {scan['competitor_count']} competitors")
print(f"Photo opportunity: {scan['photo_gap_opportunity']} competitors lack professional photos")
print(f"Recommendation: {scan['recommendation']}")
```

### Command Line Interface

```bash
# Quick competitor scan
bitepics scan --address "123 Main Street, New York, NY"

# Full location analysis  
bitepics analyze --name "Mario's Pizza" --address "123 Main Street, New York, NY"

# Generate marketing checklist
bitepics checklist --name "Mario's Pizza" --address "123 Main Street, New York, NY"

# Show BitePics photo enhancement info
bitepics scan --address "123 Main St" --bitepics-info
```

## 🔑 Configuration

Create a `.env` file or set environment variables:

```bash
# Required API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Getting API Keys

1. **Google Maps API**: Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Places API and Geocoding API
   - Create credentials and get your API key

2. **OpenAI API**: Visit [OpenAI Platform](https://platform.openai.com/)
   - Create account and generate API key

## 📊 Analysis Output

```python
{
  "restaurant": {
    "name": "Mario's Pizza",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "formatted_address": "123 Main St, New York, NY 10001, USA"
    }
  },
  "competitors": [
    {
      "name": "Joe's Pizza",
      "rating": 4.5,
      "price_level": 2,
      "total_ratings": 150,
      "has_photos": true,
      "types": ["restaurant", "food", "establishment"]
    }
  ],
  "insights": {
    "competitive_advantage": "Prime location with high foot traffic",
    "marketing_opportunities": [
      "Social media marketing focus",
      "Professional food photography", 
      "Local SEO optimization"
    ],
    "photo_strategy": "High opportunity - 6/10 competitors lack professional photos. Consider BitePics for competitive advantage.",
    "target_audience": "Young professionals and tourists",
    "pricing_strategy": "Premium pricing supported by location",
    "risk_factors": ["High competition density"],
    "bitepics_recommendation": "Professional food photography essential. Visit bite.pics for AI enhancement starting around $1 per image."
  }
}
```

## 🎯 Use Cases

### 📍 New Restaurant Planning
```python
from bitepics import RestaurantLocationAnalyzer, calculate_market_potential

analyzer = RestaurantLocationAnalyzer()
analysis = analyzer.analyze_location("New Sushi Spot", "Downtown Address")

# Calculate market potential
potential = calculate_market_potential(analysis['competitors'])
print(f"Market potential: {potential['market_potential']}")
print(f"Photo strategy: {potential['photo_strategy']}")
```

### 🏪 Existing Restaurant Optimization
```python
from bitepics import quick_competitor_scan, estimate_photo_roi

scan = quick_competitor_scan("Current Restaurant Address")

# Estimate ROI of professional photography
roi = estimate_photo_roi(
    competitor_photo_gaps=scan['photo_gap_opportunity'],
    total_competitors=scan['competitor_count']
)

print(f"ROI Category: {roi['roi_category']}")
print(f"Expected boost: {roi['expected_engagement_boost']}")
print(f"BitePics value: {roi['bitepics_value_proposition']}")
```

### 📋 Marketing Checklist Generation
```python
from bitepics import RestaurantLocationAnalyzer, generate_marketing_checklist

analyzer = RestaurantLocationAnalyzer()
analysis = analyzer.analyze_location("Restaurant Name", "Address")

checklist = generate_marketing_checklist(analysis)
for task in checklist:
    print(f"• {task}")
```

## 🛠️ Advanced Usage

### Custom Analysis Parameters
```python
analyzer = RestaurantLocationAnalyzer(
    google_api_key="your_key",
    openai_api_key="your_key"
)

# Detailed analysis with custom parameters
analysis = analyzer.analyze_location(
    restaurant_name="Fine Dining Restaurant",
    address="Upscale Neighborhood Address", 
    radius_meters=2000,  # 2km radius
    max_competitors=20   # Analyze up to 20 competitors
)
```

### Batch Location Analysis
```python
locations = [
    ("Location A", "123 First St, City"),
    ("Location B", "456 Second Ave, City"), 
    ("Location C", "789 Third Rd, City")
]

results = []
for name, address in locations:
    analysis = analyzer.analyze_location(name, address)
    results.append({
        'location': name,
        'competitive_advantage': analysis['insights']['competitive_advantage'],
        'photo_opportunity': len([c for c in analysis['competitors'] if not c['has_photos']]),
        'bitepics_recommendation': analysis['insights']['bitepics_recommendation']
    })

# Find location with highest photo opportunity
best_location = max(results, key=lambda x: x['photo_opportunity'])
print(f"Best photo opportunity: {best_location['location']}")
```

## 📸 Photo Strategy Integration

BitePics provides comprehensive photo strategy recommendations:

```python
analysis = analyzer.analyze_location("Restaurant", "Address")

# Photo-specific insights
photo_strategy = analysis['insights']['photo_strategy']
bitepics_rec = analysis['insights']['bitepics_recommendation']

# Calculate photo ROI
competitors = analysis['competitors'] 
photo_gaps = sum(1 for c in competitors if not c['has_photos'])

if photo_gaps > len(competitors) * 0.5:
    print("🚨 HIGH OPPORTUNITY: Majority of competitors lack professional photos!")
    print("📸 BitePics can provide significant competitive advantage")
    print("💰 Expected ROI: 40-60% engagement boost")
    print("🌐 Visit: https://bite.pics")
```

## 🔧 Error Handling

```python
try:
    analysis = analyzer.analyze_location("Restaurant", "Invalid Address")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Analysis failed: {e}")
    print("Consider using BitePics for manual photo enhancement: https://bite.pics")
```

## 📊 Performance Tips

- **Rate Limits**: Google Maps API has daily quotas - consider caching results
- **Batch Processing**: Analyze multiple locations efficiently with proper delays
- **Error Recovery**: Implement fallback strategies for API failures
- **Cost Optimization**: Use appropriate search radius and competitor limits

## 🤝 Contributing

We welcome contributions! Areas of interest:

- Additional data sources integration
- Enhanced AI prompt engineering  
- Photo analysis algorithms
- Restaurant industry insights
- Documentation improvements

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support & Resources

- **🌐 BitePics Website**: [bite.pics](https://bite.pics) - Professional AI food photo enhancement
- **📧 Email**: info@bite.pics
- **🐛 Issues**: [GitHub Issues](https://github.com/bitepics/bitepics-python/issues)
- **📖 Documentation**: [Full API docs](https://bite.pics/docs)

## 🍕 Real-World Example

```python
from bitepics import RestaurantLocationAnalyzer, generate_marketing_checklist

# Analyze pizzeria in competitive area
analyzer = RestaurantLocationAnalyzer()
analysis = analyzer.analyze_location(
    "Tony's Authentic Pizza",
    "Little Italy, New York, NY"
)

print(f"🍕 Analysis for {analysis['restaurant']['name']}")
print(f"📍 Found {len(analysis['competitors'])} competitors")
print(f"📸 Photo opportunity: {analysis['insights']['photo_strategy']}")

# Generate actionable checklist
checklist = generate_marketing_checklist(analysis)
print("\n✅ Marketing Action Items:")
for item in checklist:
    print(f"   {item}")
```

---

**Ready to transform your restaurant's marketing?**  
Visit [bite.pics](https://bite.pics) for professional AI-powered food photo enhancement starting around $1 per image.

*Democratizing professional food photography through AI innovation.*