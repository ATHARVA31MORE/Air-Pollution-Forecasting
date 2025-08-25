import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, Clock, TrendingUp } from 'lucide-react';

const CitySelector = ({ 
  cities, 
  selectedCity, 
  onCityChange, 
  forecastHours, 
  onForecastHoursChange, 
  onLoadForecast, 
  loading 
}) => {
  return (
    <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 shadow-glass">
      <div className="grid md:grid-cols-3 gap-6 items-end">
        
        {/* City Selection */}
        <div className="space-y-3">
          <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
            <MapPin className="w-4 h-4" />
            <span>Select City</span>
          </label>
          <select
            value={selectedCity}
            onChange={(e) => onCityChange(e.target.value)}
            className="w-full px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
          >
            {cities.map((city) => (
              <option key={city.value} value={city.value}>
                {city.icon} {city.label}
              </option>
            ))}
          </select>
        </div>

        {/* Forecast Hours */}
        <div className="space-y-3">
          <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
            <Clock className="w-4 h-4" />
            <span>Forecast Duration</span>
          </label>
          <select
            value={forecastHours}
            onChange={(e) => onForecastHoursChange(parseInt(e.target.value))}
            className="w-full px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
          >
            <option value={12}>12 Hours</option>
            <option value={24}>24 Hours</option>
            <option value={48}>48 Hours</option>
            <option value={72}>72 Hours</option>
            <option value={168}>1 Week</option>
          </select>
        </div>

        {/* Generate Forecast Button */}
        <motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  onClick={() => {
    onLoadForecast();
    // Optional: Immediate scroll to show loading state
    setTimeout(() => {
      document.getElementById('forecast-section')?.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }, 50);
  }}
  disabled={loading}
  className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
>
  <TrendingUp className="w-4 h-4" />
  <span>{loading ? 'Generating...' : 'Generate Forecast'}</span>
</motion.button>
      </div>
    </div>
  );
};

export default CitySelector;