// frontend/src/App.js
import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import CitySelector from './components/CitySelector';
import CurrentConditions from './components/CurrentConditions';
import ForecastChart from './components/ForecastChart';
import HealthRecommendations from './components/HealthRecommendations';
import LoadingSpinner from './components/LoadingSpinner';
import { fetchCurrentConditions, fetchForecast } from './services/api';
import './App.css';

const useScrollToForecast = () => {
  const scrollToForecast = (elementRef) => {
    if (elementRef.current) {
      const yOffset = -20; // Offset from top
      const element = elementRef.current;
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;

      window.scrollTo({
        top: y,
        behavior: 'smooth'
      });
    }
  };

  return scrollToForecast;
};

function App() {
  const [selectedCity, setSelectedCity] = useState('Mumbai');
  const [currentConditions, setCurrentConditions] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [forecastHours, setForecastHours] = useState(24);
  const scrollToForecast = useScrollToForecast();
  const forecastSectionRef = useRef(null);

  const cities = [
    { value: 'Mumbai', label: 'Mumbai', icon: '🏙️' },
    { value: 'Delhi', label: 'Delhi', icon: '🏛️' },
    { value: 'Bangalore', label: 'Bangalore', icon: '🌆' },
    { value: 'Chennai', label: 'Chennai', icon: '🏖️' },
    { value: 'Kolkata', label: 'Kolkata', icon: '🌉' },
    { value: 'Hyderabad', label: 'Hyderabad', icon: '🏰' },
  ];
   

  useEffect(() => {
    loadCurrentConditions();
  }, [selectedCity]);

  const loadCurrentConditions = async () => {
    setLoading(true);
    try {
      const data = await fetchCurrentConditions(selectedCity);
      setCurrentConditions(data);
    } catch (error) {
      console.error('Error loading current conditions:', error);
    } finally {
      setLoading(false);
    }
  };

  // In your loadForecast function, add this:
const loadForecast = async () => {
    setLoading(true);
    try {
      const data = await fetchForecast(selectedCity, forecastHours);
      setForecastData(data);
      
      // Smooth scroll with custom offset
      setTimeout(() => {
        scrollToForecast(forecastSectionRef);
      }, 200);
      
    } catch (error) {
      console.error('Error loading forecast:', error);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <Header />

        {/* City Selector and Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8"
        >
          <CitySelector
            cities={cities}
            selectedCity={selectedCity}
            onCityChange={setSelectedCity}
            forecastHours={forecastHours}
            onForecastHoursChange={setForecastHours}
            onLoadForecast={loadForecast}
            loading={loading}
          />
        </motion.div>

        {/* Current Conditions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mb-8"
        >
          {loading && !currentConditions ? (
            <div className="bg-white/70 backdrop-blur-md rounded-2xl p-8 shadow-glass">
              <LoadingSpinner />
            </div>
          ) : currentConditions ? (
            <CurrentConditions data={currentConditions} city={selectedCity} />
          ) : null}
        </motion.div>

        {/* Health Recommendations */}
        {currentConditions && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="mb-8"
          >
            <HealthRecommendations aqi={currentConditions.AQI} category={currentConditions.category} />
          </motion.div>
        )}

        {/* Forecast Chart */}
        {forecastData && (
        <motion.div
          id="forecast-section"
          ref={forecastSectionRef} // ← Add this ref
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="mb-8"
        >
          <ForecastChart data={forecastData} city={selectedCity} />
        </motion.div>
      )}

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
          className="text-center py-8 text-gray-600"
        >
          <div className="bg-white/50 backdrop-blur-md rounded-xl p-6 shadow-air-card">
            <p className="text-sm mb-2">
              Built with ❤️ using React, Tailwind CSS, and Machine Learning
            </p>
            <p className="text-xs text-gray-500">
              Data updated every hour • Predictions powered by advanced ML algorithms
            </p>
          </div>
        </motion.footer>
      </div>
    </div>
  );
}

export default App;