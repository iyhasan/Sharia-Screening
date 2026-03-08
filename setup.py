"""Setup script for Sharia Compliance Screener Package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sharia-screener",
    version="1.0.0",
    author="OpenClaw",
    description="Islamic Sharia-Compliant Stock Screener (AAOIFI Methodology)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/sharia-screener",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yfinance>=0.2.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.0.0",
    ],
    extras_require={
        "dev": [
            "graphviz>=0.20.0",
            "matplotlib>=3.7.0",
        ],
    },
)
