import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, Wind, Droplets, Thermometer, Eye } from 'lucide-react';

const CurrentConditions = ({ data, city }) => {
  const getAQIColor = (aqi) => {
    if (aqi <= 50) return 'from-green-400 to-green-600';
    if (aqi <= 100) return 'from-yellow-400 to-yellow-600';
    if (aqi <= 200) return 'from-orange-400 to-orange-600';
    if (aqi <= 300) return 'from-red-400 to-red-600';
    return 'from-purple-400 to-purple-600';
  };

  const getAQITextColor = (aqi) => {
    if (aqi <= 50) return 'text-green-600';
    if (aqi <= 100) return 'text-yellow-600';
    if (aqi <= 200) return 'text-orange-600';
    if (aqi <= 300) return 'text-red-600';
    return 'text-purple-600';
  };

  const pollutants = [
    { name: 'PM2.5', value: data['PM2.5'], unit: 'μg/m³', icon: '🔴' },
    { name: 'PM10', value: data['PM10'], unit: 'μg/m³', icon: '🟠' },
    { name: 'NO2', value: data['NO2'], unit: 'μg/m³', icon: '🟡' },
    { name: 'SO2', value: data['SO2'], unit: 'μg/m³', icon: '🔵' },
    { name: 'CO', value: data['CO'], unit: 'mg/m³', icon: '🟣' },
    { name: 'O3', value: data['O3'], unit: 'μg/m³', icon: '🟢' },
  ];

  return (
    <div className="bg-white/70 backdrop-blur-md rounded-2xl p-8 shadow-glass">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Current Air Quality</h2>
          <p className="text-gray-600 flex items-center space-x-2">
            <span>{city}</span>
            <span>•</span>
            <span>{new Date(data.timestamp).toLocaleString()}</span>
          </p>
        </div>
        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <AlertCircle className="w-6 h-6 text-blue-500" />
        </motion.div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        
        {/* AQI Circle */}
        <div className="lg:col-span-1 flex flex-col items-center justify-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, type: "spring", stiffness: 200 }}
            className={`w-32 h-32 rounded-full bg-gradient-to-br ${getAQIColor(data.AQI)} flex items-center justify-center shadow-2xl mb-4`}
          >
            <div className="text-center">
              <div className="text-3xl font-bold text-white">{Math.round(data.AQI)}</div>
              <div className="text-xs text-white/80">AQI</div>
            </div>
          </motion.div>
          
          <div className="text-center">
            <div className={`text-xl font-semibold ${getAQITextColor(data.AQI)} mb-2`}>
              {data.category}
            </div>
            <div className="text-sm text-gray-500">
              Air Quality Index
            </div>
          </div>
        </div>

        {/* Pollutant Grid */}
        <div className="lg:col-span-2">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {pollutants.map((pollutant, index) => (
              <motion.div
                key={pollutant.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow duration-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl">{pollutant.icon}</span>
                  <span className="text-xs text-gray-500">{pollutant.unit}</span>
                </div>
                <div className="text-lg font-bold text-gray-800">
                  {pollutant.value?.toFixed(1)}
                </div>
                <div className="text-sm font-medium text-gray-600">
                  {pollutant.name}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Weather Conditions */}
      {data.temperature && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Weather Conditions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center space-x-3 bg-blue-50 rounded-lg p-3">
              <Thermometer className="w-5 h-5 text-blue-500" />
              <div>
                <div className="text-sm text-gray-600">Temperature</div>
                <div className="font-semibold">{data.temperature?.toFixed(1)}°C</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 bg-cyan-50 rounded-lg p-3">
              <Droplets className="w-5 h-5 text-cyan-500" />
              <div>
                <div className="text-sm text-gray-600">Humidity</div>
                <div className="font-semibold">{data.humidity?.toFixed(0)}%</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 bg-gray-50 rounded-lg p-3">
              <Wind className="w-5 h-5 text-gray-500" />
              <div>
                <div className="text-sm text-gray-600">Wind Speed</div>
                <div className="font-semibold">{data.wind_speed?.toFixed(1)} km/h</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 bg-indigo-50 rounded-lg p-3">
              <Eye className="w-5 h-5 text-indigo-500" />
              <div>
                <div className="text-sm text-gray-600">Visibility</div>
                <div className="font-semibold">Good</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CurrentConditions;