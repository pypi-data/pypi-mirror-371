from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bitepics",
    version="1.0.0",
    author="BitePics",
    author_email="info@bite.pics",
    description="AI-powered restaurant location analysis using Google Maps and LLM insights for marketing optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bite.pics",
    project_urls={
        "Homepage": "https://bite.pics",
        "Bug Tracker": "https://github.com/bitepics/bitepics-python/issues",
        "Repository": "https://github.com/bitepics/bitepics-python",
        "Documentation": "https://bite.pics/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "googlemaps>=4.7.0",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black", "flake8"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    keywords=[
        "restaurant", "location", "analysis", "google-maps", "ai", "marketing", 
        "food-business", "llm", "bitepics", "business-intelligence", "geo-analysis",
        "restaurant-marketing", "food-photography", "ai-enhancement"
    ],
    entry_points={
        "console_scripts": [
            "bitepics=bitepics.cli:main",
        ],
    },
)