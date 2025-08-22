#!/usr/bin/env python3
"""
Setup script for fakeuser package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fakeuser",
    version="1.0.0",
    author="Julian Man",
    author_email="julian.mann@gmail.com",
    description="Generate realistic user data with accurate geographic information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hoolymama/fakeuser",
    project_urls={
        "Bug Reports": "https://github.com/hoolymama/fakeuser/issues",
        "Source": "https://github.com/hoolymama/fakeuser",
        "Documentation": "https://github.com/hoolymama/fakeuser#readme",
    },
    keywords="fake users location testing geonames randomuser geographic data",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "fakeuser=fakeuser.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
