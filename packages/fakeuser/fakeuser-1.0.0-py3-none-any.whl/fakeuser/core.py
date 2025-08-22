"""
Core functionality for fake user generator
"""

import json
import sys
import random
from collections import defaultdict
from typing import Dict, List, Optional, Any
from .cache import CacheManager
from .downloader import DataDownloader
from .timezone_mappings import get_comprehensive_timezone_offsets


class FakeUserGenerator:
    """Main class for generating fake users with realistic locations"""
    
    # Mapping from user 'nat' codes to GeoNames country codes (ISO 2-alpha)
    COUNTRY_CODE_MAP = {
        "AU": "AU", "BR": "BR", "CA": "CA", "CH": "CH", "DE": "DE", "DK": "DK",
        "ES": "ES", "FI": "FI", "FR": "FR", "GB": "GB", "IE": "IE", "IN": "IN",
        "MX": "MX", "NL": "NL", "NO": "NO", "NZ": "NZ", "RS": "RS", "TR": "TR",
        "UA": "UA", "US": "US", "AD": "AD", "AE": "AE", "AF": "AF", "AG": "AG",
        "AI": "AI", "AL": "AL", "AM": "AM", "AO": "AO", "AQ": "AQ", "AR": "AR",
        "AS": "AS", "AT": "AT", "AW": "AW", "AX": "AX", "AZ": "AZ", "BA": "BA",
        "BB": "BB", "BD": "BD", "BE": "BE", "BF": "BF", "BG": "BG", "BH": "BH",
        "BI": "BI", "BJ": "BJ", "BL": "BL", "BM": "BM", "BN": "BN", "BO": "BO",
        "BQ": "BQ", "BS": "BS", "BT": "BT", "BV": "BV", "BW": "BW", "BY": "BY",
        "BZ": "BZ", "CC": "CC", "CD": "CD", "CF": "CF", "CG": "CG", "CI": "CI",
        "CK": "CK", "CL": "CL", "CM": "CM", "CN": "CN", "CO": "CO", "CR": "CR",
        "CU": "CU", "CV": "CV", "CW": "CW", "CX": "CX", "CY": "CY", "CZ": "CZ",
        "DJ": "DJ", "DM": "DM", "DO": "DO", "DZ": "DZ", "EC": "EC", "EE": "EE",
        "EG": "EG", "EH": "EH", "ER": "ER", "ET": "ET", "FJ": "FJ", "FK": "FK",
        "FM": "FM", "FO": "FO", "GA": "GA", "GD": "GD", "GE": "GE", "GF": "GF",
        "GG": "GG", "GH": "GH", "GI": "GI", "GL": "GL", "GM": "GM", "GN": "GN",
        "GP": "GP", "GQ": "GQ", "GR": "GR", "GS": "GS", "GT": "GT", "GU": "GU",
        "GW": "GW", "GY": "GY", "HK": "HK", "HM": "HM", "HN": "HN", "HR": "HR",
        "HT": "HT", "HU": "HU", "ID": "ID", "IL": "IL", "IM": "IM", "IO": "IO",
        "IQ": "IQ", "IR": "IR", "IS": "IS", "IT": "IT", "JE": "JE", "JM": "JM",
        "JO": "JO", "JP": "JP", "KE": "KE", "KG": "KG", "KH": "KH", "KI": "KI",
        "KM": "KM", "KN": "KN", "KP": "KP", "KR": "KR", "KW": "KW", "KY": "KY",
        "KZ": "KZ", "LA": "LA", "LB": "LB", "LC": "LC", "LI": "LI", "LK": "LK",
        "LR": "LR", "LS": "LS", "LT": "LT", "LU": "LU", "LV": "LV", "LY": "LY",
        "MA": "MA", "MC": "MC", "MD": "MD", "ME": "ME", "MF": "MF", "MG": "MG",
        "MH": "MH", "MK": "MK", "ML": "ML", "MM": "MM", "MN": "MN", "MO": "MO",
        "MP": "MP", "MQ": "MQ", "MR": "MR", "MS": "MS", "MT": "MT", "MU": "MU",
        "MV": "MV", "MW": "MW", "MY": "MY", "MZ": "MZ", "NA": "NA", "NC": "NC",
        "NE": "NE", "NF": "NF", "NG": "NG", "NI": "NI", "NP": "NP", "NR": "NR",
        "NU": "NU", "OM": "OM", "PA": "PA", "PE": "PE", "PF": "PF", "PG": "PG",
        "PH": "PH", "PK": "PK", "PL": "PL", "PM": "PM", "PN": "PN", "PR": "PR",
        "PS": "PS", "PT": "PT", "PW": "PW", "PY": "PY", "QA": "QA", "RE": "RE",
        "RO": "RO", "RU": "RU", "RW": "RW", "SA": "SA", "SB": "SB", "SC": "SC",
        "SD": "SD", "SE": "SE", "SG": "SG", "SH": "SH", "SI": "SI", "SJ": "SJ",
        "SK": "SK", "SL": "SL", "SM": "SM", "SN": "SN", "SO": "SO", "SR": "SR",
        "SS": "SS", "ST": "ST", "SV": "SV", "SX": "SX", "SY": "SY", "SZ": "SZ",
        "TC": "TC", "TD": "TD", "TF": "TF", "TG": "TG", "TH": "TH", "TJ": "TJ",
        "TK": "TK", "TL": "TL", "TM": "TM", "TN": "TN", "TO": "TO", "TT": "TT",
        "TV": "TV", "TW": "TW", "TZ": "TZ", "UG": "UG", "UM": "UM", "UY": "UY",
        "UZ": "UZ", "VA": "VA", "VC": "VC", "VE": "VE", "VG": "VG", "VI": "VI",
        "VN": "VN", "VU": "VU", "WF": "WF", "WS": "WS", "YE": "YE", "YT": "YT",
        "ZA": "ZA", "ZM": "ZM", "ZW": "ZW"
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the fake user generator
        
        Args:
            cache_dir: Custom cache directory path
        """
        self.cache = CacheManager(cache_dir)
        self.downloader = DataDownloader(self.cache)
        self.cities_by_country = {}
        self.timezone_offsets = get_comprehensive_timezone_offsets()
    
    def _load_cities_data(self) -> bool:
        """Load cities data from cache
        
        Returns:
            True if successful, False otherwise
        """
        if not self.cache.cities_cached():
            print("❌ Cities data not found in cache", file=sys.stderr)
            return False
        
        print("Loading cities data from cache...", file=sys.stderr)
        
        try:
            self.cities_by_country = defaultdict(list)
            line_count = 0
            
            with open(self.cache.cities_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 5000 == 0:
                        print(f"  Processed {line_num} cities...", file=sys.stderr)
                    
                    parts = line.strip().split('\t')
                    if len(parts) < 19:
                        continue
                    
                    # Parse GeoNames format
                    city_data = {
                        'geonameid': parts[0],
                        'name': parts[1],
                        'asciiname': parts[2],
                        'alternatenames': parts[3].split(',') if parts[3] else [],
                        'latitude': float(parts[4]),
                        'longitude': float(parts[5]),
                        'country_code': parts[8],
                        'admin1_code': parts[10],
                        'population': int(parts[14]) if parts[14] else 0,
                        'timezone': parts[17]
                    }
                    
                    self.cities_by_country[parts[8]].append(city_data)
                    line_count += 1
            
            # Convert defaultdict to regular dict
            self.cities_by_country = dict(self.cities_by_country)
            
            print(f"✅ Loaded {line_count} cities from {len(self.cities_by_country)} countries", file=sys.stderr)
            
            # Show top countries by city count
            sorted_countries = sorted(self.cities_by_country.items(), 
                                    key=lambda x: len(x[1]), reverse=True)
            for country_code, cities in sorted_countries[:5]:
                print(f"    {country_code}: {len(cities)} cities", file=sys.stderr)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load cities data: {e}", file=sys.stderr)
            return False
    
    def _get_random_city_for_country(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get a random city for the given country code
        
        Args:
            country_code: ISO 2-alpha country code
            
        Returns:
            City data dict or None if not found
        """
        if country_code not in self.cities_by_country:
            return None
        
        cities = self.cities_by_country[country_code]
        if not cities:
            return None
        
        return random.choice(cities)
    
    def _calculate_timezone_offset(self, timezone_name: str) -> str:
        """Calculate timezone offset from timezone name
        
        Args:
            timezone_name: Timezone identifier (e.g., 'America/New_York')
            
        Returns:
            Timezone offset string (e.g., '-5:00')
        """
        return self.timezone_offsets.get(timezone_name, '+0:00')
    
    def _replace_user_location(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Replace a user's location with a random city from their country
        
        Args:
            user: User data dict
            
        Returns:
            Updated user data dict
        """
        user_nat = user['nat']
        original_street = user['location']['street']
        original_city = user['location']['city']
        original_country = user['location']['country']
        
        # Map nationality to country code
        country_code = self.COUNTRY_CODE_MAP.get(user_nat)
        if not country_code:
            print(f"  ⚠️  No country mapping for nat: {user_nat}", file=sys.stderr)
            return user
        
        # Get random city for the country
        city = self._get_random_city_for_country(country_code)
        if not city:
            print(f"  ⚠️  No cities found for country: {country_code}", file=sys.stderr)
            return user
        
        # Calculate timezone offset
        timezone_offset = self._calculate_timezone_offset(city['timezone'])
        
        # Update the user's location
        user['location'] = {
            'street': original_street,  # Keep original street
            'city': city['name'],
            'country': original_country,  # Keep original country name
            'countrycode': country_code,  # Add country code
            'postcode': user['location'].get('postcode', ''),  # Keep original postcode if it exists
            'coordinates': {
                'latitude': str(city['latitude']),
                'longitude': str(city['longitude'])
            },
            'timezone': {
                'offset': timezone_offset,
                'description': city['timezone']
            }
        }
        
        # Add metadata about the replacement
        user['_city_replacement'] = {
            'original_city': original_city,
            'new_city': city['name'],
            'geonames_id': city['geonameid'],
            'population': city['population'],
            'country_code': country_code
        }
        
        return user
    
    def generate_users(self, count: int, force_users: bool = False) -> Optional[Dict[str, Any]]:
        """Generate users with realistic locations
        
        Args:
            count: Number of users to generate
            force_users: Force refetch users even if cached
            
        Returns:
            Users data dict with enriched locations or None if failed
        """
        # Ensure data is available
        if not self.downloader.ensure_data_available(count, force_users):
            print("❌ Failed to ensure required data is available", file=sys.stderr)
            return None
        
        # Load cities data
        if not self.cities_by_country and not self._load_cities_data():
            print("❌ Failed to load cities data", file=sys.stderr)
            return None
        
        # Load users data
        users_data = self.cache.load_users(count)
        if not users_data:
            print("❌ Failed to load users data from cache", file=sys.stderr)
            return None
        
        users = users_data.get('results', users_data) if isinstance(users_data, dict) else users_data
        
        print(f"Enriching {len(users)} users with realistic locations...", file=sys.stderr)
        
        # Replace each user's location
        enriched_users = []
        stats = {'success': 0, 'failed': 0}
        
        for i, user in enumerate(users):
            if i % 100 == 0 and i > 0:
                print(f"  Processed {i}/{len(users)} users...", file=sys.stderr)
            
            original_city = user['location']['city']
            enriched_user = self._replace_user_location(user)
            
            if '_city_replacement' in enriched_user:
                stats['success'] += 1
            else:
                stats['failed'] += 1
            
            enriched_users.append(enriched_user)
        
        # Update the data structure
        if isinstance(users_data, dict):
            users_data['results'] = enriched_users
            output_data = users_data
        else:
            output_data = enriched_users
        
        print(f"✅ Successfully enriched {stats['success']} users", file=sys.stderr)
        if stats['failed'] > 0:
            print(f"⚠️  Failed to enrich {stats['failed']} users", file=sys.stderr)
        
        return output_data
