# Fake User Generator with Realistic Locations

A Python package that generates realistic user data with accurate geographic information for testing location-based searches and applications.

## Purpose

This application automatically fetches random users and enriches them with realistic location information by:

- **Realistic Country Codes**: Uses proper ISO 2-alpha country codes (GB, US, DE, etc.)
- **Accurate Coordinates**: Provides real latitude/longitude coordinates from actual cities
- **Proper Timezones**: Assigns correct timezone offsets for each location (356 timezones supported)
- **Population Data**: Includes city population information for realistic testing
- **Smart Caching**: Automatically downloads and caches data to avoid repeated downloads

Perfect for testing location search functionality, timezone handling, and geographic data processing in applications.

## Quick Start

### Installation

```bash
pip install fakeuser
```

### Generate Users

```bash
# Generate 100 users with realistic locations
fakeuser 100

# Save to a file
fakeuser 500 --output users.json

# Generate users and view cache info
fakeuser 50 --output test.json
fakeuser --show-cache
```

That's it! The tool automatically:
1. Downloads random users from randomuser.me
2. Downloads cities data from GeoNames (no account required!)
3. Caches everything for future use
4. Enriches users with realistic location data

## How It Works

The `fakeuser` command performs these steps automatically:

1. **Fetches Random Users**: Downloads user data from randomuser.me API
2. **Downloads Cities Data**: Gets the latest cities15000.txt from [GeoNames](https://download.geonames.org/export/dump/cities15000.zip) (no account required!)
3. **Caches Everything**: Stores data locally to avoid repeated downloads
4. **Enriches Locations**: Replaces user cities with real cities from their country
5. **Adds Geographic Data**: Includes accurate coordinates, timezones, and population data

### Data Sources

- **Users**: [randomuser.me](https://randomuser.me) - Generates realistic fake user profiles
- **Cities**: [GeoNames.org](https://www.geonames.org) - Geographic database with ~32,000 cities (population > 15,000)

## CLI Usage

```bash
# Basic usage
fakeuser 100                          # Generate 100 users

# Save to file  
fakeuser 500 --output users.json     # Save to specific file

# Force refetch users (cities are always cached)
fakeuser 50 --force-users            # Force refetch users

# Custom cache directory
fakeuser 1000 --cache-dir /tmp/cache # Use custom cache directory

# Cache management
fakeuser --show-cache                 # Show cache information
fakeuser --clear-cache               # Clear all cached data
```

## Output Format

The enriched user data includes:
```json
{
  "location": {
    "street": {"number": 123, "name": "Main St"},
    "city": "San Francisco",
    "country": "United States", 
    "countrycode": "US",
    "coordinates": {
      "latitude": "37.77493",
      "longitude": "-122.41942"
    },
    "timezone": {
      "offset": "-8:00",
      "description": "America/Los_Angeles"
    }
  },
  "_city_replacement": {
    "original_city": "Anytown",
    "new_city": "San Francisco",
    "geonames_id": "5391959",
    "population": 864816,
    "country_code": "US"
  }
}
```

## Features

- **🚀 Zero Setup**: No manual downloads or account creation required
- **📦 Smart Caching**: Downloads data once, uses cached versions thereafter  
- **🌍 356 Timezone Mappings**: Complete coverage of all timezones in cities15000.txt
- **🏴󠁧󠁢󠁥󠁮󠁧󠁿 Country Code Support**: Supports all ISO 2-alpha country codes
- **🎲 Random Selection**: Cities are selected randomly, so larger cities aren't favored
- **📊 Metadata Tracking**: Keeps track of what was changed for debugging
- **⚡ Fast**: Cached data loads instantly on subsequent runs
- **💾 Space Efficient**: Automatic cleanup and cache management

## Cache Management

The tool automatically creates a `.cache` directory in your current folder:

```
.cache/
├── cities15000.txt      # ~7MB - GeoNames cities data
└── users_500.json      # User data cached by count
```

- **Cities data**: Downloaded once and cached permanently (never force-refreshed)
- **User data**: Cached by count (e.g., `users_100.json`, `users_500.json`)
- **Smart invalidation**: Different user counts create separate cache files
- **Force refresh**: Use `--force-users` to refetch user data

## Requirements

- Python 3.8+
- Internet connection (for initial downloads)
- ~10MB disk space for cache
- `requests` library (auto-installed)

## License

This project uses GeoNames data which is available under Creative Commons Attribution 4.0 License.
