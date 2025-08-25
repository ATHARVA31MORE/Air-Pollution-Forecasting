# backend/real_data_fetcher.py
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

class RealAirQualityFetcher:
    def __init__(self):
        # Get API Keys from environment variables
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        
        
        # City coordinates
        self.city_coords = {
            'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
            'Delhi': {'lat': 28.7041, 'lon': 77.1025},
            'Bangalore': {'lat': 12.9716, 'lon': 77.5946},
            'Chennai': {'lat': 13.0827, 'lon': 80.2707},
            'Kolkata': {'lat': 22.5726, 'lon': 88.3639},
            'Hyderabad': {'lat': 17.3850, 'lon': 78.4867}
        }
    
    def fetch_openweather_pollution(self, city):
        """Fetch real air pollution data from OpenWeatherMap"""
        try:
            coords = self.city_coords.get(city)
            if not coords:
                raise ValueError(f"Coordinates not found for {city}")
            
            # Current air pollution
            url = "http://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'appid': self.openweather_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract pollution data
            pollution = data['list'][0]
            components = pollution['components']
            
            return {
                'timestamp': datetime.fromtimestamp(pollution['dt']),
                'aqi': pollution['main']['aqi'],  # 1-5 scale
                'co': components.get('co', 0),
                'no': components.get('no', 0),
                'no2': components.get('no2', 0),
                'o3': components.get('o3', 0),
                'so2': components.get('so2', 0),
                'pm2_5': components.get('pm2_5', 0),
                'pm10': components.get('pm10', 0),
                'nh3': components.get('nh3', 0),
                'source': 'OpenWeatherMap'
            }
            
        except Exception as e:
            logger.error(f"Error fetching OpenWeather data for {city}: {str(e)}")
            return None
    
    def fetch_airvisual_data(self, city):
        """Fetch data from AirVisual (IQAir)"""
        try:
            # City mapping for AirVisual
            city_mapping = {
                'Mumbai': {'city': 'Mumbai', 'state': 'Maharashtra', 'country': 'India'},
                'Delhi': {'city': 'Delhi', 'state': 'Delhi', 'country': 'India'},
                'Bangalore': {'city': 'Bangalore', 'state': 'Karnataka', 'country': 'India'},
                'Chennai': {'city': 'Chennai', 'state': 'Tamil Nadu', 'country': 'India'},
                'Kolkata': {'city': 'Kolkata', 'state': 'West Bengal', 'country': 'India'},
                'Hyderabad': {'city': 'Hyderabad', 'state': 'Telangana', 'country': 'India'}
            }
            
            city_info = city_mapping.get(city)
            if not city_info:
                raise ValueError(f"City mapping not found for {city}")
            
            url = "http://api.airvisual.com/v2/city"
            params = {
                'city': city_info['city'],
                'state': city_info['state'],
                'country': city_info['country'],
                'key': self.airvisual_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'success':
                pollution = data['data']['current']['pollution']
                weather = data['data']['current']['weather']
                
                return {
                    'timestamp': datetime.fromisoformat(pollution['ts'].replace('Z', '+00:00')),
                    'aqi_us': pollution['aqius'],  # US AQI
                    'aqi_cn': pollution['aqicn'],  # China AQI
                    'main_pollutant_us': pollution['mainus'],
                    'main_pollutant_cn': pollution['maincn'],
                    'temperature': weather['tp'],
                    'humidity': weather['hu'],
                    'pressure': weather['pr'],
                    'wind_speed': weather['ws'],
                    'source': 'AirVisual'
                }
            else:
                logger.error(f"AirVisual API error: {data.get('data', {}).get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching AirVisual data for {city}: {str(e)}")
            return None
    
    def fetch_waqi_data(self, city):
        """Fetch data from World Air Quality Index"""
        try:
            url = f"https://api.waqi.info/feed/{city}/"
            params = {'token': self.waqi_token}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'ok':
                aqi_data = data['data']
                
                # Extract individual pollutant data
                iaqi = aqi_data.get('iaqi', {})
                
                return {
                    'timestamp': datetime.fromisoformat(aqi_data['time']['iso']),
                    'aqi': aqi_data['aqi'],
                    'pm25': iaqi.get('pm25', {}).get('v'),
                    'pm10': iaqi.get('pm10', {}).get('v'),
                    'o3': iaqi.get('o3', {}).get('v'),
                    'no2': iaqi.get('no2', {}).get('v'),
                    'so2': iaqi.get('so2', {}).get('v'),
                    'co': iaqi.get('co', {}).get('v'),
                    'dominant_pollutant': aqi_data.get('dominentpol'),
                    'city_name': aqi_data.get('city', {}).get('name'),
                    'source': 'WAQI'
                }
            else:
                logger.error(f"WAQI API error for {city}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching WAQI data for {city}: {str(e)}")
            return None
    
    def fetch_combined_data(self, city):
        """Fetch data from multiple sources and combine"""
        results = {}
        
        # Try each API
        openweather_data = self.fetch_openweather_pollution(city)
        if openweather_data:
            results['openweather'] = openweather_data
        
        airvisual_data = self.fetch_airvisual_data(city)
        if airvisual_data:
            results['airvisual'] = airvisual_data
        
        waqi_data = self.fetch_waqi_data(city)
        if waqi_data:
            results['waqi'] = waqi_data
        
        # Combine the best data from all sources
        if results:
            combined = self.combine_data_sources(results)
            return combined
        else:
            logger.warning(f"No real data available for {city}, using fallback")
            return None
    
    def combine_data_sources(self, data_sources):
        """Combine data from multiple sources intelligently"""
        combined = {
            'timestamp': datetime.now(),
            'sources_used': list(data_sources.keys())
        }
        
        # Priority: OpenWeather > AirVisual > WAQI for pollutants
        # Priority: AirVisual > OpenWeather > WAQI for weather
        
        for source_name, source_data in data_sources.items():
            if source_name == 'openweather':
                combined.update({
                    'PM2.5': source_data.get('pm2_5'),
                    'PM10': source_data.get('pm10'),
                    'NO2': source_data.get('no2'),
                    'SO2': source_data.get('so2'),
                    'CO': source_data.get('co'),
                    'O3': source_data.get('o3'),
                })
            
            elif source_name == 'airvisual':
                combined.update({
                    'AQI': source_data.get('aqi_us'),
                    'temperature': source_data.get('temperature'),
                    'humidity': source_data.get('humidity'),
                    'pressure': source_data.get('pressure'),
                    'wind_speed': source_data.get('wind_speed'),
                })
            
            elif source_name == 'waqi':
                # Fill in missing data from WAQI
                if 'PM2.5' not in combined:
                    combined['PM2.5'] = source_data.get('pm25')
                if 'PM10' not in combined:
                    combined['PM10'] = source_data.get('pm10')
                if 'AQI' not in combined:
                    combined['AQI'] = source_data.get('aqi')
        
        # Calculate missing AQI if not available
        if 'AQI' not in combined and combined.get('PM2.5'):
            combined['AQI'] = self.calculate_aqi_from_pm25(combined['PM2.5'])
        
        # Determine air quality category
        aqi = combined.get('AQI', 0)
        if aqi <= 50:
            combined['category'] = "Good"
            combined['color'] = "#00e400"
        elif aqi <= 100:
            combined['category'] = "Satisfactory"
            combined['color'] = "#ffff00"
        elif aqi <= 200:
            combined['category'] = "Moderate"
            combined['color'] = "#ff7e00"
        elif aqi <= 300:
            combined['category'] = "Poor"
            combined['color'] = "#ff0000"
        else:
            combined['category'] = "Very Poor"
            combined['color'] = "#8f3f97"
        
        return combined
    
    def calculate_aqi_from_pm25(self, pm25):
        """Calculate AQI from PM2.5 using US EPA standard"""
        if pm25 <= 12.0:
            return pm25 * 50 / 12.0
        elif pm25 <= 35.4:
            return 50 + (pm25 - 12.0) * 50 / (35.4 - 12.0)
        elif pm25 <= 55.4:
            return 100 + (pm25 - 35.4) * 50 / (55.4 - 35.4)
        elif pm25 <= 150.4:
            return 150 + (pm25 - 55.4) * 50 / (150.4 - 55.4)
        elif pm25 <= 250.4:
            return 200 + (pm25 - 150.4) * 100 / (250.4 - 150.4)
        else:
            return 300 + (pm25 - 250.4) * 100 / (350.4 - 250.4)

# Usage example
def get_real_air_quality(city):
    """Get real air quality data for a city"""
    fetcher = RealAirQualityFetcher()
    
    # Try to get real data
    real_data = fetcher.fetch_combined_data(city)
    
    if real_data:
        print(f"✅ Real data fetched for {city}")
        return real_data
    else:
        print(f"⚠️ Real data not available for {city}, using mock data")
        # Fallback to mock data
        from app import generate_current_conditions
        return generate_current_conditions(city)

# Integration with Flask app
def update_flask_app_for_real_data():
    """Update your Flask app to use real data"""
    
    # In your app.py, replace the generate_current_conditions call with:
    """
    @app.route('/api/current', methods=['POST'])
    def get_current_conditions():
        try:
            data = request.get_json()
            city = data['city']
            
            # Try to get real data first
            fetcher = RealAirQualityFetcher()
            real_data = fetcher.fetch_combined_data(city)
            
            if real_data:
                current_conditions = real_data
            else:
                # Fallback to mock data
                current_conditions = generate_current_conditions(city)
            
            return jsonify({
                'success': True,
                'city': city,
                'conditions': current_conditions,
                'data_type': 'real' if real_data else 'synthetic'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    """

if __name__ == "__main__":
    # Test the real data fetcher
    fetcher = RealAirQualityFetcher()
    
    # Test with Mumbai
    print("Testing real data fetch for Mumbai...")
    data = fetcher.fetch_combined_data("Mumbai")
    
    if data:
        print("✅ Success! Real data:")
        print(json.dumps(data, indent=2, default=str))
    else:
        print("❌ Failed to fetch real data")