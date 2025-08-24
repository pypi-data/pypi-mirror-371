from setuptools import setup, find_packages

setup(
    name="ml_model_handler",
    version="0.1.0",
    author="Rucha Ambaliya",
    author_email="ruchaambaliya@example.com",
    description="A simple library to train, manage, and use multiple ML models easily.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rucha-ambaliya/ml_model_handler",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
        "xgboost"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
