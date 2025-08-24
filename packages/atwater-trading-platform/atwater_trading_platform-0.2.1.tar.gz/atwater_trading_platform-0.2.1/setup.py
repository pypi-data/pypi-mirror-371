from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="atwater-trading-platform",
    version="0.2.1",
    author="Atwater Financial",
    author_email="dev@atwater.financial",
    description="Python SDK for the AtwaterFinancial HFT Trading Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AtwaterFinancial/AtwaterFinancial",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "websockets>=10.0",
        "pydantic>=1.8.0",
        "python-dateutil>=2.8.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-mock>=3.6.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "examples": [
            "pandas>=1.3.0",
            "numpy>=1.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "atwater-trading-platform=trading_platform.cli:main",
        ],
    },
)