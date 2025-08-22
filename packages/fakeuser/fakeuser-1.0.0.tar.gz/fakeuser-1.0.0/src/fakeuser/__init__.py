"""
Fake User Generator with Realistic Locations

A Python package that generates realistic user data with accurate geographic 
information for testing location-based searches and applications.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import FakeUserGenerator
from .cache import CacheManager
from .downloader import DataDownloader

__all__ = ["FakeUserGenerator", "CacheManager", "DataDownloader"]
