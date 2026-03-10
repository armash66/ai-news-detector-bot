"""
AI News Intelligence - Misinformation Detection Platform
"""

from setuptools import setup, find_packages

setup(
    name="news-intelligence",
    version="1.0.0",
    description="Production-grade AI-powered misinformation detection platform",
    author="Armash Ansari",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "spacy>=3.6.0",
        "newspaper3k>=0.2.8",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "httpx>=0.25.0",
        ],
        "explainability": [
            "shap>=0.43.0",
            "lime>=0.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "news-train=backend.training.train:main",
            "news-eval=backend.training.evaluate:main",
        ],
    },
)
