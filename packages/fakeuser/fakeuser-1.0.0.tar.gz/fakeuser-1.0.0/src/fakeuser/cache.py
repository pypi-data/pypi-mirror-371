"""
Cache management for fake user generator
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class CacheManager:
    """Manages caching for cities data and user files"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache manager
        
        Args:
            cache_dir: Custom cache directory path. If None, uses default.
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default to .cache in current working directory
            self.cache_dir = Path.cwd() / ".cache"
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Define cache file paths
        self.cities_file = self.cache_dir / "cities15000.txt"
        self.cities_zip_file = self.cache_dir / "cities15000.zip"
    
    def get_users_cache_file(self, count: int) -> Path:
        """Get path for users cache file based on count
        
        Args:
            count: Number of users
            
        Returns:
            Path to users cache file
        """
        return self.cache_dir / f"users_{count}.json"
    
    def cities_cached(self) -> bool:
        """Check if cities data is cached
        
        Returns:
            True if cities15000.txt exists in cache
        """
        return self.cities_file.exists() and self.cities_file.stat().st_size > 0
    
    def users_cached(self, count: int) -> bool:
        """Check if users data is cached for given count
        
        Args:
            count: Number of users to check
            
        Returns:
            True if users file exists for this count
        """
        users_file = self.get_users_cache_file(count)
        return users_file.exists() and users_file.stat().st_size > 0
    
    def save_users(self, users_data: Dict[str, Any], count: int) -> None:
        """Save users data to cache
        
        Args:
            users_data: User data to save
            count: Number of users (for filename)
        """
        users_file = self.get_users_cache_file(count)
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    def load_users(self, count: int) -> Optional[Dict[str, Any]]:
        """Load users data from cache
        
        Args:
            count: Number of users to load
            
        Returns:
            Users data dict or None if not cached
        """
        users_file = self.get_users_cache_file(count)
        if not self.users_cached(count):
            return None
        
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def clear_cache(self) -> None:
        """Clear all cache files"""
        for file_path in self.cache_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
    
    def get_cache_size(self) -> int:
        """Get total size of cache directory in bytes"""
        total_size = 0
        for file_path in self.cache_dir.glob("**/*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def list_cached_files(self) -> Dict[str, Dict[str, Any]]:
        """List all cached files with metadata
        
        Returns:
            Dict mapping filename to metadata (size, modified time, etc.)
        """
        cached_files = {}
        for file_path in self.cache_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                cached_files[file_path.name] = {
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "modified": stat.st_mtime,
                    "path": str(file_path)
                }
        return cached_files
