"""
Data downloading functionality for fake user generator
"""

import os
import sys
import zipfile
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from .cache import CacheManager


class DataDownloader:
    """Downloads and manages external data sources"""
    
    # URLs for data sources
    GEONAMES_CITIES_URL = "https://download.geonames.org/export/dump/cities15000.zip"
    RANDOM_USER_API_URL = "https://randomuser.me/api/"
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize downloader
        
        Args:
            cache_manager: CacheManager instance
        """
        self.cache = cache_manager
    
    def download_cities_data(self, force: bool = False) -> bool:
        """Download and extract cities15000.txt
        
        Args:
            force: Force download even if cached
            
        Returns:
            True if successful, False otherwise
        """
        if self.cache.cities_cached() and not force:
            print("Cities data already cached, skipping download", file=sys.stderr)
            return True
        
        print("Downloading cities15000.zip from GeoNames...", file=sys.stderr)
        
        try:
            # Download the zip file
            response = requests.get(self.GEONAMES_CITIES_URL, stream=True)
            response.raise_for_status()
            
            # Save zip file to cache
            with open(self.cache.cities_zip_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("Extracting cities15000.txt...", file=sys.stderr)
            
            # Extract the txt file
            with zipfile.ZipFile(self.cache.cities_zip_file, 'r') as zip_ref:
                # Extract only the cities15000.txt file
                zip_ref.extract("cities15000.txt", self.cache.cache_dir)
            
            # Remove the zip file to save space
            self.cache.cities_zip_file.unlink()
            
            print(f"✅ Cities data downloaded and cached at {self.cache.cities_file}", file=sys.stderr)
            return True
            
        except requests.RequestException as e:
            print(f"❌ Failed to download cities data: {e}", file=sys.stderr)
            return False
        except zipfile.BadZipFile as e:
            print(f"❌ Failed to extract cities data: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"❌ Unexpected error downloading cities data: {e}", file=sys.stderr)
            return False
    
    def fetch_random_users(self, count: int, force: bool = False) -> Optional[Dict[str, Any]]:
        """Fetch random users from randomuser.me API
        
        Args:
            count: Number of users to fetch
            force: Force fetch even if cached
            
        Returns:
            Users data dict or None if failed
        """
        # Check cache first
        if not force and self.cache.users_cached(count):
            print(f"Users data for {count} users already cached, loading from cache", file=sys.stderr)
            return self.cache.load_users(count)
        
        print(f"Fetching {count} random users from randomuser.me...", file=sys.stderr)
        
        try:
            # Fetch users from API
            params = {
                'results': count,
                'inc': 'gender,name,location,email,registered,id,picture,nat',
                'format': 'json'
            }
            
            response = requests.get(self.RANDOM_USER_API_URL, params=params)
            response.raise_for_status()
            
            users_data = response.json()
            
            # Validate response
            if 'results' not in users_data or not users_data['results']:
                print("❌ Invalid response from randomuser.me API", file=sys.stderr)
                return None
            
            # Cache the users data
            self.cache.save_users(users_data, count)
            
            print(f"✅ Fetched and cached {len(users_data['results'])} users", file=sys.stderr)
            return users_data
            
        except requests.RequestException as e:
            print(f"❌ Failed to fetch users: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching users: {e}", file=sys.stderr)
            return None
    
    def ensure_data_available(self, user_count: int, force_users: bool = False) -> bool:
        """Ensure both cities and users data are available
        
        Args:
            user_count: Number of users needed
            force_users: Force refetch users even if cached
            
        Returns:
            True if all data is available, False otherwise
        """
        success = True
        
        # Download cities data if needed (never force for cities)
        if not self.cache.cities_cached():
            success &= self.download_cities_data()
        
        # Fetch users data if needed
        users_data = self.fetch_random_users(user_count, force=force_users)
        success &= (users_data is not None)
        
        return success
