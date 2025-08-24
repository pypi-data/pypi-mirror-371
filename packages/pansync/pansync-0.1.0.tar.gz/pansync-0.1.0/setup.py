#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies - now managed via pyproject.toml
requirements = [
    "bypy>=1.7.0",
    "PyYAML>=6.0",
    "requests>=2.28.0",
    "psutil>=5.9.0",
    "click>=8.0.0",
    "colorama>=0.4.4",
    "cryptography>=3.4.8",
    "loguru>=0.6.0",
    "pytz>=2022.1",
    "python-dateutil>=2.8.2",
    "watchdog>=2.1.9",
    "tqdm>=4.64.0",
    "toml>=0.10.2",
    "urllib3>=1.26.12",
]

setup(
    name="pansync",
    version="0.1.0",
    author="PanSync Team",
    author_email="pansync@example.com",
    description="百度网盘多客户端同步工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/pansync",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "pansync=pansync.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)