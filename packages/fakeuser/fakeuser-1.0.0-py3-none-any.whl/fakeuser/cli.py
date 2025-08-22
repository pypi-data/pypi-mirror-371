#!/usr/bin/env python3
"""
Command line interface for fake user generator
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from .core import FakeUserGenerator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate realistic fake users with accurate geographic information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fakeuser 100                          # Generate 100 users
  fakeuser 500 --output users.json     # Save to specific file
  fakeuser 50 --force-users            # Force refetch users
  fakeuser 1000 --cache-dir /tmp/cache # Use custom cache directory
  fakeuser --show-cache                # Show cache information
  fakeuser --clear-cache               # Clear all cached data
        """
    )
    
    # Main arguments
    parser.add_argument(
        'count',
        type=int,
        nargs='?',
        help='Number of users to generate (required unless using --show-cache or --clear-cache)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--force-users',
        action='store_true',
        help='Force refetch users even if cached'
    )
    
    parser.add_argument(
        '--cache-dir',
        type=str,
        help='Custom cache directory path (default: ./.cache)'
    )
    
    # Cache management
    cache_group = parser.add_argument_group('cache management')
    cache_group.add_argument(
        '--show-cache',
        action='store_true',
        help='Show cache information and exit'
    )
    
    cache_group.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear all cached data and exit'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments
    if not args.show_cache and not args.clear_cache and args.count is None:
        parser.error("count is required unless using --show-cache or --clear-cache")
    
    if args.count is not None and args.count <= 0:
        parser.error("count must be a positive integer")
    
    # Initialize generator
    try:
        generator = FakeUserGenerator(cache_dir=args.cache_dir)
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle cache management commands
    if args.show_cache:
        show_cache_info(generator)
        return
    
    if args.clear_cache:
        clear_cache(generator)
        return
    
    # Generate users
    try:
        print(f"Generating {args.count} fake users with realistic locations...", file=sys.stderr)
        
        users_data = generator.generate_users(
            count=args.count,
            force_users=args.force_users
        )
        
        if users_data is None:
            print("❌ Failed to generate users", file=sys.stderr)
            sys.exit(1)
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {args.count} users to {output_path}", file=sys.stderr)
        else:
            # Output to stdout
            json.dump(users_data, sys.stdout, indent=2, ensure_ascii=False)
            print("", file=sys.stderr)  # Add newline for stderr
        
        print("✅ Generation complete!", file=sys.stderr)
        
    except KeyboardInterrupt:
        print("\\n❌ Generation interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def show_cache_info(generator: FakeUserGenerator):
    """Show cache information"""
    cache = generator.cache
    
    print("Cache Information:")
    print("=" * 50)
    print(f"Cache directory: {cache.cache_dir}")
    print(f"Cities data cached: {'✅' if cache.cities_cached() else '❌'}")
    
    # Show cached files
    cached_files = cache.list_cached_files()
    if cached_files:
        print(f"\\nCached files:")
        for filename, metadata in cached_files.items():
            print(f"  {filename}: {metadata['size_mb']} MB")
        
        total_size = cache.get_cache_size()
        print(f"\\nTotal cache size: {total_size / 1024 / 1024:.2f} MB")
    else:
        print("\\nNo cached files found")
    
    # Show user cache files
    user_files = [f for f in cached_files.keys() if f.startswith('users_') and f.endswith('.json')]
    if user_files:
        print(f"\\nCached user datasets:")
        for filename in sorted(user_files):
            # Extract count from filename
            try:
                count = int(filename.replace('users_', '').replace('.json', ''))
                metadata = cached_files[filename]
                print(f"  {count} users: {metadata['size_mb']} MB")
            except ValueError:
                continue


def clear_cache(generator: FakeUserGenerator):
    """Clear cache"""
    cache = generator.cache
    
    try:
        cache.clear_cache()
        print("✅ Cache cleared successfully")
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
