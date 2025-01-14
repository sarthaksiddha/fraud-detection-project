from setuptools import setup, find_packages

setup(
    name="fraud-detection",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if not line.startswith("#")
    ],
    author="Sarthak Siddha",
    author_email="your.email@example.com",
    description="Real-time fraud detection system using ML and streaming data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sarthaksiddha/fraud-detection-project",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "fraud-detection-api=src.api.api_server:start_api_server",
            "fraud-detection-dashboard=src.dashboard.app:main",
        ]
    }
)