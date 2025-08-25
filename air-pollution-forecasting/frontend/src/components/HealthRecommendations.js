import React from 'react';
import { motion } from 'framer-motion';
import { Heart, Shield, AlertTriangle, CheckCircle, XCircle, Activity } from 'lucide-react';

const HealthRecommendations = ({ aqi, category }) => {
  const getRecommendations = (aqi) => {
    if (aqi <= 50) {
      return {
        icon: CheckCircle,
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        title: 'Excellent Air Quality',
        recommendations: [
          'Perfect time for outdoor activities and exercise',
          'All outdoor sports and activities are recommended',
          'Great day for cycling, jogging, or walking',
          'Open windows to let fresh air circulate indoors'
        ],
        activities: ['🏃‍♂️ Running', '🚴‍♀️ Cycling', '⚽ Sports', '🧘‍♀️ Outdoor Yoga']
      };
    } else if (aqi <= 100) {
      return {
        icon: Shield,
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        title: 'Moderate Air Quality',
        recommendations: [
          'Generally safe for outdoor activities',
          'Sensitive individuals should consider limiting prolonged outdoor exposure',
          'Good time for most outdoor exercises',
          'Monitor air quality if you have respiratory conditions'
        ],
        activities: ['🚶‍♂️ Walking', '🏸 Badminton', '🎾 Tennis', '🏊‍♀️ Swimming']
      };
    } else if (aqi <= 200) {
      return {
        icon: AlertTriangle,
        color: 'text-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        title: 'Unhealthy for Sensitive Groups',
        recommendations: [
          'Limit outdoor activities, especially for children and elderly',
          'Consider wearing N95 masks when outdoors',
          'Avoid strenuous outdoor exercises',
          'Keep windows closed and use air purifiers indoors'
        ],
        activities: ['🏠 Indoor Gym', '🧘‍♀️ Indoor Yoga', '🏊‍♀️ Pool Swimming', '🎮 Indoor Games']
      };
    } else {
      return {
        icon: XCircle,
        color: 'text-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        title: 'Unhealthy Air Quality',
        recommendations: [
          'Avoid all outdoor activities',
          'Stay indoors with windows and doors closed',
          'Use air purifiers and avoid opening windows',
          'Wear N95 masks if you must go outside',
          'Consult doctor if you experience breathing issues'
        ],
        activities: ['🏠 Stay Indoors', '💻 Work from Home', '📚 Reading', '🎬 Indoor Entertainment']
      };
    }
  };

  const recommendations = getRecommendations(aqi);
  const IconComponent = recommendations.icon;

  return (
    <div className={`${recommendations.bgColor} ${recommendations.borderColor} border-2 rounded-2xl p-6 shadow-air-card`}>
      <div className="flex items-center space-x-3 mb-6">
        <div className={`p-2 ${recommendations.bgColor} rounded-full`}>
          <IconComponent className={`w-6 h-6 ${recommendations.color}`} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-800">Health Recommendations</h2>
          <p className={`text-sm font-medium ${recommendations.color}`}>
            {recommendations.title}
          </p>
        </div>
        <div className="ml-auto">
          <Heart className="w-6 h-6 text-red-500 animate-pulse" />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Recommendations List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>What to Do</span>
          </h3>
          <ul className="space-y-3">
            {recommendations.recommendations.map((rec, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-start space-x-3"
              >
                <div className={`w-2 h-2 ${recommendations.bgColor} ${recommendations.borderColor} border rounded-full mt-2 flex-shrink-0`} />
                <span className="text-gray-700 text-sm">{rec}</span>
              </motion.li>
            ))}
          </ul>
        </div>

        {/* Recommended Activities */}
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Recommended Activities</h3>
          <div className="grid grid-cols-2 gap-3">
            {recommendations.activities.map((activity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="bg-white/80 rounded-lg p-3 text-center shadow-sm hover:shadow-md transition-shadow duration-200"
              >
                <div className="text-sm font-medium text-gray-700">
                  {activity}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Health Tips */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="bg-white/60 rounded-lg p-4">
          <h4 className="font-semibold text-gray-700 mb-2">💡 Quick Health Tips</h4>
          <div className="text-sm text-gray-600 space-y-1">
            <p>• Stay hydrated and maintain a healthy diet rich in antioxidants</p>
            <p>• Consider indoor plants to naturally purify air</p>
            <p>• Regular health check-ups are important in polluted environments</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthRecommendations;