"""
BitePics - AI-powered restaurant location analysis and marketing optimization.

Professional food photo enhancement available at https://bite.pics
"""

__version__ = "1.0.0"
__author__ = "BitePics"
__email__ = "info@bite.pics"
__url__ = "https://bite.pics"

from .analyzer import RestaurantLocationAnalyzer
from .utils import quick_competitor_scan, calculate_market_potential

__all__ = [
    "RestaurantLocationAnalyzer",
    "quick_competitor_scan", 
    "calculate_market_potential",
]