// Update your ForecastChart.js component with this optimized version:

import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

const ForecastChart = ({ data, city }) => {
  const predictions = data.predictions || [];
  
  // Optimize chart data based on duration
  const optimizeChartData = (predictions) => {
    if (predictions.length <= 48) {
      // For 48 hours or less, show hourly data
      return predictions.map(pred => ({
        time: new Date(pred.timestamp).toLocaleTimeString([], { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        fullTime: pred.timestamp,
        'PM2.5': pred['PM2.5'],
        'PM10': pred['PM10'],
        'NO2': pred['NO2'],
        'AQI': pred.AQI,
        category: pred.category
      }));
    } else if (predictions.length <= 84) {
      // For 1 week, show day + time
      return predictions.map(pred => ({
        time: `${pred.day} ${new Date(pred.timestamp).toLocaleTimeString([], { 
          hour: '2-digit' 
        })}`,
        fullTime: pred.timestamp,
        'PM2.5': pred['PM2.5'],
        'PM10': pred['PM10'],
        'NO2': pred['NO2'],
        'AQI': pred.AQI,
        category: pred.category
      }));
    } else {
      // For longer periods, show dates
      return predictions.map(pred => ({
        time: pred.date || new Date(pred.timestamp).toLocaleDateString(),
        fullTime: pred.timestamp,
        'PM2.5': pred['PM2.5'],
        'PM10': pred['PM10'],
        'NO2': pred['NO2'],
        'AQI': pred.AQI,
        category: pred.category
      }));
    }
  };

  const chartData = optimizeChartData(predictions);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/95 backdrop-blur-sm p-4 rounded-lg shadow-lg border">
          <p className="font-semibold text-gray-800 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.dataKey}: {entry.value?.toFixed(1)}
              {entry.dataKey === 'AQI' ? '' : ' μg/m³'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Determine chart height based on data length
  const chartHeight = predictions.length > 84 ? 320 : 280;

  if (!predictions.length) {
    return (
      <div className="bg-white/70 backdrop-blur-md rounded-2xl p-8 shadow-glass">
        <div className="text-center py-8">
          <p className="text-gray-500 text-lg">No forecast data available</p>
          <p className="text-gray-400 text-sm mt-2">Click "Generate Forecast" to load predictions</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/70 backdrop-blur-md rounded-2xl p-8 shadow-glass">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Air Quality Forecast</h2>
          <p className="text-gray-600">
            {city} • Next {predictions.length} data points 
            {predictions.length > 48 ? ' (optimized view)' : ''}
          </p>
        </div>
        <div className="text-sm text-gray-500">
          <div>Updated {new Date().toLocaleTimeString()}</div>
          <div className="mt-1">
            Duration: {data.hours} hours
          </div>
        </div>
      </div>

      {/* Pollutants Chart */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Pollutant Levels</h3>
        <div style={{ height: chartHeight }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart 
              data={chartData} 
              margin={{ top: 5, right: 30, left: 20, bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="time" 
                stroke="#64748b"
                fontSize={12}
                angle={predictions.length > 48 ? -45 : 0}
                textAnchor={predictions.length > 48 ? 'end' : 'middle'}
                height={predictions.length > 48 ? 80 : 60}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="PM2.5" 
                stroke="#ef4444" 
                strokeWidth={2}
                dot={predictions.length <= 48 ? { fill: '#ef4444', strokeWidth: 2, r: 3 } : false}
                activeDot={{ r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="PM10" 
                stroke="#f97316" 
                strokeWidth={2}
                dot={predictions.length <= 48 ? { fill: '#f97316', strokeWidth: 2, r: 3 } : false}
                activeDot={{ r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="NO2" 
                stroke="#8b5cf6" 
                strokeWidth={2}
                dot={predictions.length <= 48 ? { fill: '#8b5cf6', strokeWidth: 2, r: 3 } : false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* AQI Chart */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Air Quality Index Trend</h3>
        <div style={{ height: 240 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart 
              data={chartData} 
              margin={{ top: 5, right: 30, left: 20, bottom: 60 }}
            >
              <defs>
                <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="time" 
                stroke="#64748b"
                fontSize={12}
                angle={predictions.length > 48 ? -45 : 0}
                textAnchor={predictions.length > 48 ? 'end' : 'middle'}
                height={predictions.length > 48 ? 80 : 60}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="AQI"
                stroke="#3b82f6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#aqiGradient)"
              />
              {/* AQI category reference lines */}
              <Line 
                type="monotone" 
                dataKey={() => 50} 
                stroke="#22c55e" 
                strokeWidth={1} 
                strokeDasharray="5,5" 
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey={() => 100} 
                stroke="#eab308" 
                strokeWidth={1} 
                strokeDasharray="5,5" 
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey={() => 200} 
                stroke="#f97316" 
                strokeWidth={1} 
                strokeDasharray="5,5" 
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* AQI Legend */}
        <div className="flex flex-wrap justify-center mt-4 gap-4 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-1 bg-green-500"></div>
            <span>Good (0-50)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-1 bg-yellow-500"></div>
            <span>Satisfactory (51-100)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-1 bg-orange-500"></div>
            <span>Moderate (101-200)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-1 bg-red-500"></div>
            <span>Poor (201+)</span>
          </div>
        </div>
      </motion.div>

      {/* Summary Stats for Long Duration */}
      {predictions.length > 48 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-8 pt-6 border-t border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Forecast Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['PM2.5', 'PM10', 'NO2', 'AQI'].map(pollutant => {
              const values = predictions.map(p => p[pollutant]).filter(v => v != null);
              const avg = values.reduce((a, b) => a + b, 0) / values.length;
              const max = Math.max(...values);
              const min = Math.min(...values);
              
              return (
                <div key={pollutant} className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm font-medium text-gray-700 mb-2">{pollutant}</div>
                  <div className="space-y-1 text-xs">
                    <div>Avg: {avg.toFixed(1)}</div>
                    <div>Max: {max.toFixed(1)}</div>
                    <div>Min: {min.toFixed(1)}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ForecastChart;