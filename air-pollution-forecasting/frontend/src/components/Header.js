import React from 'react';
import { motion } from 'framer-motion';
import { Cloud, Wind, Thermometer } from 'lucide-react';

const Header = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="text-center mb-12"
    >
      <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 shadow-glass">
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
          className="inline-block mb-4"
        >
          <div className="text-6xl">🌍</div>
        </motion.div>
        
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
          Air Quality Forecaster
        </h1>
        
        <p className="text-lg md:text-xl text-gray-600 mb-6 max-w-2xl mx-auto">
          Real-time air quality monitoring and ML-powered predictions for better health decisions
        </p>
        
        <div className="flex justify-center space-x-8 text-sm text-gray-500">
          <div className="flex items-center space-x-2">
            <Wind className="w-4 h-4" />
            <span>Real-time Data</span>
          </div>
          <div className="flex items-center space-x-2">
            <Cloud className="w-4 h-4" />
            <span>ML Predictions</span>
          </div>
          <div className="flex items-center space-x-2">
            <Thermometer className="w-4 h-4" />
            <span>Health Insights</span>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;