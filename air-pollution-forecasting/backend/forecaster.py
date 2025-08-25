# Air Pollution Level Forecasting System
# A comprehensive system for predicting air quality using machine learning

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import requests
import sqlite3
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
import joblib
import warnings


warnings.filterwarnings('ignore')

class AirPollutionForecaster:
    def __init__(self, db_name='pollution_data.db'):
        """
        Initialize the Air Pollution Forecasting System
        """
        self.db_name = db_name
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.target_columns = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
        self.setup_database()
        
    def setup_database(self):
        """Setup SQLite database for storing pollution data"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create table for pollution data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pollution_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                city TEXT,
                pm25 REAL,
                pm10 REAL,
                no2 REAL,
                so2 REAL,
                co REAL,
                o3 REAL,
                temperature REAL,
                humidity REAL,
                wind_speed REAL,
                pressure REAL,
                weather_condition TEXT,
                season TEXT,
                hour INTEGER,
                day_of_week INTEGER,
                is_weekend INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database setup completed successfully!")
    
    def generate_synthetic_data(self, num_records=10000):
        """
        Generate synthetic pollution data for training
        In a real system, this would fetch from APIs like OpenWeatherMap, AirVisual, etc.
        """
        print("Generating synthetic training data...")
        
        np.random.seed(42)
        data = []
        
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad']
        seasons = ['Winter', 'Spring', 'Summer', 'Monsoon']
        weather_conditions = ['Clear', 'Cloudy', 'Rainy', 'Foggy', 'Stormy']
        
        start_date = datetime(2020, 1, 1)
        
        for i in range(num_records):
            # Generate timestamp
            timestamp = start_date + timedelta(hours=i)
            
            # Basic features
            city = np.random.choice(cities)
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Seasonal patterns
            month = timestamp.month
            if month in [12, 1, 2]:
                season = 'Winter'
                temp_base, humidity_base = 15, 70
            elif month in [3, 4, 5]:
                season = 'Spring'
                temp_base, humidity_base = 25, 60
            elif month in [6, 7, 8, 9]:
                season = 'Monsoon'
                temp_base, humidity_base = 28, 85
            else:
                season = 'Summer'
                temp_base, humidity_base = 35, 45
            
            # Weather features with realistic correlations
            temperature = temp_base + np.random.normal(0, 5)
            humidity = max(20, min(100, humidity_base + np.random.normal(0, 15)))
            wind_speed = max(0, np.random.exponential(8))
            pressure = 1013 + np.random.normal(0, 20)
            weather_condition = np.random.choice(weather_conditions)
            
            # Pollution levels with realistic patterns
            # Higher pollution in winter, rush hours, and certain cities
            base_pollution = {
                'Mumbai': 80, 'Delhi': 150, 'Bangalore': 60,
                'Chennai': 70, 'Kolkata': 100, 'Hyderabad': 75
            }[city]
            
            # Seasonal multiplier
            seasonal_mult = {'Winter': 1.5, 'Spring': 1.0, 'Summer': 1.2, 'Monsoon': 0.7}[season]
            
            # Rush hour effect (7-9 AM, 6-8 PM)
            rush_hour_mult = 1.3 if hour in [7, 8, 18, 19] else 1.0
            
            # Weekend effect (lower pollution)
            weekend_mult = 0.8 if is_weekend else 1.0
            
            # Weather effects
            weather_mult = {
                'Clear': 1.0, 'Cloudy': 1.1, 'Rainy': 0.6, 
                'Foggy': 1.4, 'Stormy': 0.7
            }[weather_condition]
            
            # Wind effect (higher wind = lower pollution)
            wind_mult = max(0.5, 1.2 - wind_speed/20)
            
            pollution_factor = base_pollution * seasonal_mult * rush_hour_mult * weekend_mult * weather_mult * wind_mult
            
            # Generate correlated pollutants
            pm25 = max(0, pollution_factor * 0.6 + np.random.normal(0, 15))
            pm10 = max(0, pm25 * 1.8 + np.random.normal(0, 20))
            no2 = max(0, pollution_factor * 0.4 + np.random.normal(0, 10))
            so2 = max(0, pollution_factor * 0.2 + np.random.normal(0, 8))
            co = max(0, pollution_factor * 0.1 + np.random.normal(0, 5))
            o3 = max(0, 60 + (temperature - 25) * 2 + np.random.normal(0, 15))
            
            data.append([
                timestamp, city, pm25, pm10, no2, so2, co, o3,
                temperature, humidity, wind_speed, pressure, 
                weather_condition, season, hour, day_of_week, is_weekend
            ])
        
        # Create DataFrame
        columns = ['timestamp', 'city', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3',
                  'temperature', 'humidity', 'wind_speed', 'pressure', 
                  'weather_condition', 'season', 'hour', 'day_of_week', 'is_weekend']
        
        df = pd.DataFrame(data, columns=columns)
        
        # Save to database
        conn = sqlite3.connect(self.db_name)
        df.to_sql('pollution_data', conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"Generated and saved {num_records} records to database!")
        return df
    
    def load_data(self):
        """Load data from database"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM pollution_data", conn)
        conn.close()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def preprocess_data(self, df):
        """Preprocess data for machine learning"""
        print("Preprocessing data...")
        
        # Handle missing values
        imputer_numeric = SimpleImputer(strategy='median')
        imputer_categorical = SimpleImputer(strategy='most_frequent')
        
        numeric_columns = ['temperature', 'humidity', 'wind_speed', 'pressure']
        categorical_columns = ['weather_condition', 'season', 'city']
        
        df[numeric_columns] = imputer_numeric.fit_transform(df[numeric_columns])
        df[categorical_columns] = imputer_categorical.fit_transform(df[categorical_columns])
        
        # Encode categorical variables
        le_weather = LabelEncoder()
        le_season = LabelEncoder()
        le_city = LabelEncoder()
        
        df['weather_encoded'] = le_weather.fit_transform(df['weather_condition'])
        df['season_encoded'] = le_season.fit_transform(df['season'])
        df['city_encoded'] = le_city.fit_transform(df['city'])
        
        # Create additional time-based features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['month'] = df['timestamp'].dt.month
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        
        # Create lag features (previous hour's pollution levels)
        for pollutant in self.target_columns:
            if pollutant in df.columns:
                df[f'{pollutant}_lag1'] = df[pollutant].shift(1)
                df[f'{pollutant}_lag24'] = df[pollutant].shift(24)  # Previous day same hour
        
        # Define feature columns
        self.feature_columns = [
            'temperature', 'humidity', 'wind_speed', 'pressure',
            'weather_encoded', 'season_encoded', 'city_encoded',
            'hour', 'day_of_week', 'is_weekend', 'month', 'day_of_year'
        ]
        
        # Add lag features to feature columns
        for pollutant in self.target_columns:
            if f'{pollutant}_lag1' in df.columns:
                self.feature_columns.extend([f'{pollutant}_lag1', f'{pollutant}_lag24'])
        
        # Remove rows with NaN values (due to lag features)
        df = df.dropna()
        
        print(f"Preprocessing completed! Features: {len(self.feature_columns)}")
        return df, (le_weather, le_season, le_city)
    
    def train_models(self, df, test_size=0.2):
        """Train multiple ML models for each pollutant"""
        print("Training machine learning models...")
        
        X = df[self.feature_columns]
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['main'] = scaler
        
        results = {}
        
        for pollutant in self.target_columns:
            if pollutant not in df.columns:
                continue
                
            print(f"Training models for {pollutant}...")
            
            y = df[pollutant]
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=42
            )
            
            # Train multiple models
            models = {
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'LinearRegression': LinearRegression()
            }
            
            pollutant_results = {}
            best_score = -np.inf
            best_model = None
            
            for model_name, model in models.items():
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                pollutant_results[model_name] = {
                    'model': model,
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2
                }
                
                print(f"  {model_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.3f}")
                
                # Track best model
                if r2 > best_score:
                    best_score = r2
                    best_model = model
            
            # Store best model
            self.models[pollutant] = best_model
            results[pollutant] = pollutant_results
            
            print(f"  Best model for {pollutant}: {type(best_model).__name__} (R² = {best_score:.3f})")
        
        # Save models
        self.save_models()
        
        return results
    
    def predict(self, input_data):
        """Make predictions for given input data"""
        if isinstance(input_data, dict):
            # Single prediction
            df_input = pd.DataFrame([input_data])
        else:
            df_input = input_data.copy()
        
        # Ensure all feature columns are present
        for col in self.feature_columns:
            if col not in df_input.columns:
                if 'lag' in col:
                    df_input[col] = 0  # Default lag values
                else:
                    df_input[col] = 0  # Default other values
        
        # Scale features
        X_scaled = self.scalers['main'].transform(df_input[self.feature_columns])
        
        predictions = {}
        for pollutant, model in self.models.items():
            pred = model.predict(X_scaled)
            predictions[pollutant] = pred[0] if len(pred) == 1 else pred
        
        return predictions
    
    def predict_future(self, hours_ahead=24, city='Mumbai', current_conditions=None):
        """Predict pollution levels for future hours"""
        if current_conditions is None:
            current_conditions = {
                'temperature': 25,
                'humidity': 60,
                'wind_speed': 10,
                'pressure': 1013,
                'weather_condition': 'Clear',
                'season': 'Winter'
            }
        
        predictions = []
        current_time = datetime.now()
        
        # Encode categorical variables (simplified)
        weather_map = {'Clear': 0, 'Cloudy': 1, 'Rainy': 2, 'Foggy': 3, 'Stormy': 4}
        season_map = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Monsoon': 3}
        city_map = {'Mumbai': 0, 'Delhi': 1, 'Bangalore': 2, 'Chennai': 3, 'Kolkata': 4, 'Hyderabad': 5}
        
        for hour in range(hours_ahead):
            future_time = current_time + timedelta(hours=hour)
            
            input_data = {
                'temperature': current_conditions['temperature'],
                'humidity': current_conditions['humidity'],
                'wind_speed': current_conditions['wind_speed'],
                'pressure': current_conditions['pressure'],
                'weather_encoded': weather_map.get(current_conditions['weather_condition'], 0),
                'season_encoded': season_map.get(current_conditions['season'], 0),
                'city_encoded': city_map.get(city, 0),
                'hour': future_time.hour,
                'day_of_week': future_time.weekday(),
                'is_weekend': 1 if future_time.weekday() >= 5 else 0,
                'month': future_time.month,
                'day_of_year': future_time.timetuple().tm_yday
            }
            
            # Add lag features (use previous predictions or defaults)
            for pollutant in self.target_columns:
                input_data[f'{pollutant}_lag1'] = 50  # Default lag values
                input_data[f'{pollutant}_lag24'] = 45
            
            pred = self.predict(input_data)
            pred['timestamp'] = future_time
            predictions.append(pred)
        
        return predictions
    
    def get_air_quality_index(self, pollutant_levels):
        """Calculate AQI based on pollutant levels"""
        # Simplified AQI calculation (Indian standards)
        aqi_breakpoints = {
            'PM2.5': [(0, 30, 0, 50), (30, 60, 51, 100), (60, 90, 101, 200), (90, 120, 201, 300), (120, 250, 301, 400)],
            'PM10': [(0, 50, 0, 50), (50, 100, 51, 100), (100, 250, 101, 200), (250, 350, 201, 300), (350, 430, 301, 400)],
            'NO2': [(0, 40, 0, 50), (40, 80, 51, 100), (80, 180, 101, 200), (180, 280, 201, 300), (280, 400, 301, 400)],
        }
        
        max_aqi = 0
        dominant_pollutant = None
        
        for pollutant, level in pollutant_levels.items():
            if pollutant in aqi_breakpoints:
                for bp_lo, bp_hi, aqi_lo, aqi_hi in aqi_breakpoints[pollutant]:
                    if bp_lo <= level <= bp_hi:
                        aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (level - bp_lo) + aqi_lo
                        if aqi > max_aqi:
                            max_aqi = aqi
                            dominant_pollutant = pollutant
                        break
        
        # AQI categories
        if max_aqi <= 50:
            category = "Good"
            color = "green"
        elif max_aqi <= 100:
            category = "Satisfactory"
            color = "yellow"
        elif max_aqi <= 200:
            category = "Moderate"
            color = "orange"
        elif max_aqi <= 300:
            category = "Poor"
            color = "red"
        else:
            category = "Very Poor"
            color = "maroon"
        
        return {
            'aqi': round(max_aqi),
            'category': category,
            'color': color,
            'dominant_pollutant': dominant_pollutant
        }
    
    def visualize_predictions(self, predictions, save_path='pollution_forecast.png'):
        """Create visualization of predictions"""
        df_pred = pd.DataFrame(predictions)
        df_pred['timestamp'] = pd.to_datetime(df_pred['timestamp'])
        
        plt.figure(figsize=(15, 10))
        
        # Plot each pollutant
        for i, pollutant in enumerate(['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'], 1):
            if pollutant in df_pred.columns:
                plt.subplot(2, 3, i)
                plt.plot(df_pred['timestamp'], df_pred[pollutant], marker='o', linewidth=2)
                plt.title(f'{pollutant} Forecast')
                plt.xlabel('Time')
                plt.ylabel(f'{pollutant} (μg/m³)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Forecast visualization saved as {save_path}")
    
    def save_models(self):
        """Save trained models and scalers"""
        joblib.dump(self.models, 'pollution_models.pkl')
        joblib.dump(self.scalers, 'pollution_scalers.pkl')
        print("Models and scalers saved successfully!")
    
    def load_models(self):
        """Load trained models and scalers"""
        try:
            self.models = joblib.load('pollution_models.pkl')
            self.scalers = joblib.load('pollution_scalers.pkl')
            print("Models and scalers loaded successfully!")
            return True
        except FileNotFoundError:
            print("No saved models found. Please train models first.")
            return False
    
    def generate_report(self, city='Mumbai', hours_ahead=24):
        """Generate a comprehensive pollution forecast report"""
        print(f"\n=== AIR POLLUTION FORECAST REPORT ===")
        print(f"City: {city}")
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Forecast period: Next {hours_ahead} hours")
        print("=" * 50)
        
        # Get predictions
        predictions = self.predict_future(hours_ahead=hours_ahead, city=city)
        
        # Current conditions (first prediction)
        current = predictions[0]
        aqi_info = self.get_air_quality_index(current)
        
        print(f"\nCURRENT CONDITIONS:")
        print(f"AQI: {aqi_info['aqi']} ({aqi_info['category']})")
        print(f"Dominant Pollutant: {aqi_info['dominant_pollutant']}")
        
        print(f"\nPOLLUTANT LEVELS:")
        for pollutant in self.target_columns:
            if pollutant in current:
                print(f"  {pollutant}: {current[pollutant]:.1f} μg/m³")
        
        # Find peak pollution hours
        max_aqi = 0
        peak_hour = None
        for i, pred in enumerate(predictions):
            aqi = self.get_air_quality_index(pred)['aqi']
            if aqi > max_aqi:
                max_aqi = aqi
                peak_hour = i
        
        print(f"\nFORECAST HIGHLIGHTS:")
        print(f"Peak pollution expected in {peak_hour} hours (AQI: {max_aqi})")
        
        # Health recommendations
        print(f"\nHEALTH RECOMMENDATIONS:")
        if aqi_info['aqi'] <= 50:
            print("- Air quality is good. Enjoy outdoor activities!")
        elif aqi_info['aqi'] <= 100:
            print("- Air quality is satisfactory. Sensitive individuals should limit outdoor exposure.")
        elif aqi_info['aqi'] <= 200:
            print("- Air quality is moderate. Consider reducing outdoor activities.")
        else:
            print("- Air quality is poor. Avoid outdoor activities. Use air purifiers indoors.")
        
        # Create visualization
        self.visualize_predictions(predictions)
        
        return predictions

def main():
    """Main function to demonstrate the Air Pollution Forecasting System"""
    print("🌍 Air Pollution Level Forecasting System")
    print("=" * 50)
    
    # Initialize the system
    forecaster = AirPollutionForecaster()
    
    # Try to load existing models
    if not forecaster.load_models():
        # Generate synthetic data and train models
        print("No existing models found. Training new models...")
        
        # Generate synthetic data
        df = forecaster.generate_synthetic_data(num_records=15000)
        
        # Preprocess data
        df_processed, encoders = forecaster.preprocess_data(df)
        
        # Train models
        results = forecaster.train_models(df_processed)
        
        print("\n📊 MODEL TRAINING RESULTS:")
        for pollutant, models in results.items():
            print(f"\n{pollutant}:")
            for model_name, metrics in models.items():
                print(f"  {model_name}: R² = {metrics['r2']:.3f}, RMSE = {metrics['rmse']:.2f}")
    
    # Generate forecast report
    print("\n🔮 GENERATING FORECAST...")
    predictions = forecaster.generate_report(city='Delhi', hours_ahead=24)
    
    # Example of single prediction
    print("\n🎯 SINGLE PREDICTION EXAMPLE:")
    test_conditions = {
        'temperature': 30,
        'humidity': 70,
        'wind_speed': 5,
        'pressure': 1010,
        'weather_condition': 'Cloudy',
        'season': 'Summer'
    }
    
    single_pred = forecaster.predict_future(hours_ahead=1, city='Mumbai', 
                                           current_conditions=test_conditions)
    current_pred = single_pred[0]
    aqi = forecaster.get_air_quality_index(current_pred)
    
    print(f"Predicted AQI for Mumbai: {aqi['aqi']} ({aqi['category']})")
    for pollutant in forecaster.target_columns:
        if pollutant in current_pred:
            print(f"  {pollutant}: {current_pred[pollutant]:.1f} μg/m³")
    
    print("\n✅ System demonstration completed!")
    print("\nTo extend this system:")
    print("1. Integrate real weather APIs (OpenWeatherMap, etc.)")
    print("2. Add more sophisticated models (LSTM, Prophet)")
    print("3. Include satellite imagery data")
    print("4. Build a web dashboard with Flask/Django")
    print("5. Add alert system for high pollution events")
    print("6. Implement real-time data streaming")

if __name__ == "__main__":
    main()