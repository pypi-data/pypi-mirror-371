from setuptools import setup, find_packages

setup(
    name="stockpredictor",
    version="0.2.3",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "yfinance",
        "matplotlib",
        "scikit-learn"
    ],
    author="BLILLP",
    author_email="deviprasadgurrana@gmail.com",
    description="A Python library for predicting stock index trends using historical data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BLILLP/stocks-nn",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
