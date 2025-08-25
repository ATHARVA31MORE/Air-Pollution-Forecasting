import math
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random
from forecaster import AirPollutionForecaster
import logging
import os
import secrets
from real_data_fetcher import RealAirQualityFetcher

SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

real_data_fetcher = RealAirQualityFetcher()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])  # Enable CORS for React

# Initialize forecaster
forecaster = AirPollutionForecaster()

# Global variable to store if models are loaded
models_loaded = False

def init_models():
    """Initialize and load ML models"""
    global models_loaded
    try:
        # Try to load existing models
        if not forecaster.load_models():
            logger.info("No existing models found. Training new models...")
            # Generate data and train models
            df = forecaster.generate_synthetic_data(num_records=10000)
            df_processed, encoders = forecaster.preprocess_data(df)
            forecaster.train_models(df_processed)
            logger.info("Models trained successfully!")
        
        models_loaded = True
        logger.info("Air Pollution Forecaster initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        models_loaded = False

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'message': 'Air Pollution Forecasting API',
        'version': '1.0.0',
        'status': 'running',
        'models_loaded': models_loaded
    })

@app.route('/api/current', methods=['POST'])
def get_current_conditions():
    """Get current air quality conditions for a city"""
    try:
        data = request.get_json()
        if not data or 'city' not in data:
            return jsonify({
                'success': False,
                'error': 'City parameter is required'
            }), 400
        
        city = data['city']
        logger.info(f"Fetching current conditions for {city}")
        
        # Try to get real data first
        try:
            real_data = real_data_fetcher.fetch_combined_data(city)
            if real_data:
                logger.info(f"✅ Real data fetched for {city}")
                data_type = 'real'
                current_conditions = real_data
            else:
                raise Exception("No real data available")
        except Exception as e:
            logger.warning(f"Real data fetch failed for {city}: {str(e)}")
            logger.info(f"Using synthetic data for {city}")
            data_type = 'synthetic'
            current_conditions = generate_current_conditions(city)
        
        return jsonify({
            'success': True,
            'city': city,
            'conditions': current_conditions,
            'data_type': data_type  # This tells frontend if data is real or mock
        })
    
    except Exception as e:
        logger.error(f"Error in get_current_conditions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/api/data-sources', methods=['GET'])
def get_data_sources():
    """Get status of different data sources"""
    try:
        # Test each API
        test_city = 'Mumbai'
        sources_status = {}
        
        # Test OpenWeather
        try:
            ow_data = real_data_fetcher.fetch_openweather_pollution(test_city)
            sources_status['openweather'] = {
                'status': 'active' if ow_data else 'inactive',
                'last_updated': ow_data.get('timestamp') if ow_data else None
            }
        except:
            sources_status['openweather'] = {'status': 'error', 'last_updated': None}
        
        # Test AirVisual
        try:
            av_data = real_data_fetcher.fetch_airvisual_data(test_city)
            sources_status['airvisual'] = {
                'status': 'active' if av_data else 'inactive',
                'last_updated': av_data.get('timestamp') if av_data else None
            }
        except:
            sources_status['airvisual'] = {'status': 'error', 'last_updated': None}
        
        # Test WAQI
        try:
            waqi_data = real_data_fetcher.fetch_waqi_data(test_city)
            sources_status['waqi'] = {
                'status': 'active' if waqi_data else 'inactive',
                'last_updated': waqi_data.get('timestamp') if waqi_data else None
            }
        except:
            sources_status['waqi'] = {'status': 'error', 'last_updated': None}
        
        return jsonify({
            'success': True,
            'sources': sources_status,
            'total_active': sum(1 for s in sources_status.values() if s['status'] == 'active')
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/forecast', methods=['POST'])
def get_forecast():
    """Generate pollution forecast for a city"""
    try:
        data = request.get_json()
        print(f"Received forecast request: {data}")
        
        if not data or 'city' not in data:
            return jsonify({
                'success': False,
                'error': 'City parameter is required'
            }), 400
        
        city = data['city']
        hours = int(data.get('hours', 24))
        
        print(f"Generating forecast for {city}, {hours} hours")
        
        if hours < 1 or hours > 168:
            return jsonify({
                'success': False,
                'error': 'Hours must be between 1 and 168'
            }), 400
        
        logger.info(f"Generating {hours}-hour forecast for {city}")
        
        # Generate mock forecast data
        print("Generating mock forecast data...")
        formatted_predictions = generate_mock_forecast(city, hours)
        
        print(f"Generated {len(formatted_predictions)} predictions")
        
        response_data = {
            'success': True,
            'city': city,
            'predictions': formatted_predictions,
            'hours': hours,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("Returning forecast response...")
        return jsonify(response_data)
        
    except ValueError as e:
        error_msg = f"Invalid input: {str(e)}"
        print(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400
        
    except Exception as e:
        error_msg = f"Error in get_forecast: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error occurred'
        }), 500

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get list of supported cities"""
    cities = [
        {'value': 'Mumbai', 'label': 'Mumbai', 'icon': '🏙️', 'coordinates': [19.0760, 72.8777]},
        {'value': 'Delhi', 'label': 'Delhi', 'icon': '🏛️', 'coordinates': [28.7041, 77.1025]},
        {'value': 'Bangalore', 'label': 'Bangalore', 'icon': '🌆', 'coordinates': [12.9716, 77.5946]},
        {'value': 'Chennai', 'label': 'Chennai', 'icon': '🏖️', 'coordinates': [13.0827, 80.2707]},
        {'value': 'Kolkata', 'label': 'Kolkata', 'icon': '🌉', 'coordinates': [22.5726, 88.3639]},
        {'value': 'Hyderabad', 'label': 'Hyderabad', 'icon': '🏰', 'coordinates': [17.3850, 78.4867]},
    ]
    
    return jsonify({
        'success': True,
        'cities': cities
    })

@app.route('/api/historical', methods=['POST'])
def get_historical_data():
    """Get historical air quality data"""
    try:
        data = request.get_json()
        city = data.get('city', 'Mumbai')
        days = int(data.get('days', 7))
        
        # Generate mock historical data
        historical_data = generate_historical_data(city, days)
        
        return jsonify({
            'success': True,
            'city': city,
            'data': historical_data,
            'days': days
        })
    
    except Exception as e:
        logger.error(f"Error in get_historical_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health-recommendations', methods=['POST'])
def get_health_recommendations():
    """Get health recommendations based on AQI"""
    try:
        data = request.get_json()
        aqi = int(data.get('aqi', 50))
        
        recommendations = generate_health_recommendations(aqi)
        
        return jsonify({
            'success': True,
            'aqi': aqi,
            'recommendations': recommendations
        })
    
    except Exception as e:
        logger.error(f"Error in get_health_recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions
def generate_current_conditions(city):
    """Generate realistic current air quality conditions"""
    base_pollution = {
        'Mumbai': 80, 'Delhi': 150, 'Bangalore': 60,
        'Chennai': 70, 'Kolkata': 100, 'Hyderabad': 75
    }
    
    base = base_pollution.get(city, 75)
    current_hour = datetime.now().hour
    
    # Rush hour effect
    rush_hour_effect = 1.3 if current_hour in [7, 8, 9, 18, 19, 20] else 1.0
    
    # Random variations
    pm25 = max(10, base * rush_hour_effect + random.uniform(-20, 25))
    pm10 = pm25 * random.uniform(1.6, 2.0) + random.uniform(-15, 20)
    no2 = base * 0.4 * rush_hour_effect + random.uniform(-12, 15)
    so2 = base * 0.2 + random.uniform(-8, 10)
    co = base * 0.08 + random.uniform(-2, 4)
    o3 = 60 + random.uniform(-25, 35)
    
    # Calculate AQI (simplified)
    aqi = max(pm25 * 2.2, pm10 * 1.1, no2 * 1.8)
    
    if aqi <= 50:
        category, color = "Good", "#00e400"
    elif aqi <= 100:
        category, color = "Satisfactory", "#ffff00"
    elif aqi <= 200:
        category, color = "Moderate", "#ff7e00"
    elif aqi <= 300:
        category, color = "Poor", "#ff0000"
    else:
        category, color = "Very Poor", "#8f3f97"
    
    return {
        'PM2.5': round(pm25, 1),
        'PM10': round(pm10, 1),
        'NO2': round(no2, 1),
        'SO2': round(so2, 1),
        'CO': round(co, 2),
        'O3': round(o3, 1),
        'AQI': round(aqi),
        'category': category,
        'color': color,
        'temperature': round(random.uniform(15, 35), 1),
        'humidity': round(random.uniform(30, 85), 0),
        'wind_speed': round(random.uniform(2, 20), 1),
        'pressure': round(random.uniform(995, 1025), 1),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generate_mock_forecast(city, hours):
    """Generate mock forecast data - safe version without numpy"""
    print(f"Creating mock forecast for {city}, {hours} hours")
    
    try:
        base_pollution = {
            'Mumbai': 80, 'Delhi': 150, 'Bangalore': 60,
            'Chennai': 70, 'Kolkata': 100, 'Hyderabad': 75
        }
        
        predictions = []
        current_time = datetime.now()
        base = base_pollution.get(city, 75)
        
        # Optimize for long durations
        if hours <= 48:
            step = 1  # Every hour
        elif hours <= 168:  # 1 week
            step = 2  # Every 2 hours
        else:
            step = 4  # Every 4 hours
        
        actual_hours = list(range(0, hours, step))
        print(f"Generating {len(actual_hours)} data points with step {step}")
        
        for i, hour in enumerate(actual_hours):
            timestamp = current_time + timedelta(hours=hour)
            
            # Add realistic patterns
            hour_of_day = timestamp.hour
            day_of_week = timestamp.weekday()
            day_of_year = timestamp.timetuple().tm_yday
            
            # Seasonal variations using math.sin instead of numpy
            seasonal_factor = 1 + 0.3 * math.sin(2 * math.pi * day_of_year / 365)
            
            # Weekly patterns (weekends vs weekdays)
            weekend_factor = 0.8 if day_of_week >= 5 else 1.0
            
            # Daily patterns (rush hours)
            if hour_of_day in [7, 8, 9, 18, 19, 20]:
                daily_factor = 1.4
            elif hour_of_day in [2, 3, 4, 5]:
                daily_factor = 0.7
            else:
                daily_factor = 1.0
            
            # Random variations
            random_factor = random.uniform(0.8, 1.3)
            
            # Combine all factors
            total_factor = seasonal_factor * weekend_factor * daily_factor * random_factor
            
            # Generate pollutant levels
            pm25 = max(5, base * 0.6 * total_factor + random.uniform(-15, 20))
            pm10 = pm25 * random.uniform(1.6, 2.2) + random.uniform(-10, 15)
            no2 = base * 0.4 * total_factor + random.uniform(-8, 12)
            so2 = base * 0.2 * total_factor + random.uniform(-5, 8)
            co = base * 0.08 * total_factor + random.uniform(-1, 3)
            
            # Ozone with daily pattern using math.sin
            o3 = 50 + 20 * math.sin(2 * math.pi * hour_of_day / 24) + random.uniform(-15, 25)
            
            # Calculate AQI
            aqi = max(pm25 * 2.2, pm10 * 1.1, no2 * 1.8, so2 * 1.5)
            
            # Determine category
            if aqi <= 50:
                category = "Good"
            elif aqi <= 100:
                category = "Satisfactory"
            elif aqi <= 200:
                category = "Moderate"
            elif aqi <= 300:
                category = "Poor"
            else:
                category = "Very Poor"
            
            prediction = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'hour': hour_of_day,
                'day': timestamp.strftime('%a'),
                'date': timestamp.strftime('%m/%d'),
                'PM2.5': round(pm25, 1),
                'PM10': round(pm10, 1),
                'NO2': round(no2, 1),
                'SO2': round(so2, 1),
                'CO': round(co, 2),
                'O3': round(o3, 1),
                'AQI': round(aqi),
                'category': category
            }
            
            predictions.append(prediction)
        
        print(f"Successfully generated {len(predictions)} predictions")
        return predictions
        
    except Exception as e:
        print(f"Error in generate_mock_forecast: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

def generate_historical_data(city, days):
    """Generate mock historical data"""
    base_pollution = {
        'Mumbai': 80, 'Delhi': 150, 'Bangalore': 60,
        'Chennai': 70, 'Kolkata': 100, 'Hyderabad': 75
    }
    
    historical = []
    base = base_pollution.get(city, 75)
    end_date = datetime.now()
    
    for day in range(days):
        date = end_date - timedelta(days=day)
        
        # Daily average with some variation
        daily_variation = random.uniform(0.6, 1.5)
        
        pm25 = max(15, base * daily_variation + random.uniform(-25, 30))
        pm10 = pm25 * random.uniform(1.6, 2.2) + random.uniform(-20, 25)
        no2 = base * 0.4 * daily_variation + random.uniform(-15, 18)
        
        aqi = max(pm25 * 2.2, pm10 * 1.1, no2 * 1.8)
        
        if aqi <= 50:
            category = "Good"
        elif aqi <= 100:
            category = "Satisfactory"
        elif aqi <= 200:
            category = "Moderate"
        elif aqi <= 300:
            category = "Poor"
        else:
            category = "Very Poor"
        
        historical.append({
            'date': date.strftime('%Y-%m-%d'),
            'PM2.5': round(pm25, 1),
            'PM10': round(pm10, 1),
            'NO2': round(no2, 1),
            'AQI': round(aqi),
            'category': category
        })
    
    return historical[::-1]  # Return in chronological order

def generate_health_recommendations(aqi):
    """Generate health recommendations based on AQI"""
    if aqi <= 50:
        return {
            'level': 'Good',
            'color': 'green',
            'message': 'Air quality is excellent. Perfect for all outdoor activities.',
            'activities': ['Running', 'Cycling', 'Outdoor Sports', 'Walking'],
            'precautions': []
        }
    elif aqi <= 100:
        return {
            'level': 'Satisfactory',
            'color': 'yellow',
            'message': 'Air quality is acceptable for most people.',
            'activities': ['Light Exercise', 'Walking', 'Outdoor Dining'],
            'precautions': ['Sensitive individuals should limit prolonged outdoor exposure']
        }
    elif aqi <= 200:
        return {
            'level': 'Moderate',
            'color': 'orange',
            'message': 'Air quality is unhealthy for sensitive groups.',
            'activities': ['Indoor Exercise', 'Short Walks', 'Avoid Strenuous Activity'],
            'precautions': ['Wear masks outdoors', 'Limit outdoor time', 'Keep windows closed']
        }
    else:
        return {
            'level': 'Unhealthy',
            'color': 'red',
            'message': 'Air quality is unhealthy for all people.',
            'activities': ['Stay Indoors', 'Use Air Purifiers', 'Avoid Outdoor Activities'],
            'precautions': ['Wear N95 masks if going outside', 'Consult doctor if breathing issues', 'Keep all windows closed']
        }

def get_mock_weather_conditions(city):
    """Generate mock weather conditions for ML model input"""
    # Seasonal adjustments based on current month
    current_month = datetime.now().month
    
    if current_month in [12, 1, 2]:  # Winter
        temp_base, humidity_base, season = 18, 70, 'Winter'
    elif current_month in [3, 4, 5]:  # Spring
        temp_base, humidity_base, season = 28, 55, 'Spring'
    elif current_month in [6, 7, 8, 9]:  # Monsoon
        temp_base, humidity_base, season = 30, 85, 'Monsoon'
    else:  # Summer
        temp_base, humidity_base, season = 35, 45, 'Summer'
    
    return {
        'temperature': temp_base + random.uniform(-5, 5),
        'humidity': max(30, min(90, humidity_base + random.uniform(-15, 15))),
        'wind_speed': max(1, random.exponential(8)),
        'pressure': 1013 + random.uniform(-20, 20),
        'weather_condition': random.choice(['Clear', 'Cloudy', 'Partly Cloudy']),
        'season': season
    }

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested resource was not found on this server.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500

@app.before_request
def initialize():
    """Initialize the application"""
    init_models()

if __name__ == '__main__':
    # Initialize models on startup
    init_models()
    
    print("🌍 Air Pollution Forecasting API Server")
    print("=" * 50)
    print("Server starting...")
    print("API endpoints:")
    print("  GET  /                     - Health check")
    print("  POST /api/current          - Current conditions")
    print("  POST /api/forecast         - Generate forecast")
    print("  GET  /api/cities           - Supported cities")
    print("  POST /api/historical       - Historical data")
    print("  POST /api/health-recommendations - Health advice")
    print("=" * 50)
    print("Frontend should be running on: http://localhost:3000")
    print("API server running on: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)