import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const MainPage = () => {
  const [url, setUrl] = useState('');
  const [showAnalysis, setShowAnalysis] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Submitted URL:', url);
    setShowAnalysis(true);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center">
      <nav className="absolute top-0 left-0 right-0 p-4">
        <ul className="flex space-x-4">
          <li><Link to="/" className="hover:text-gray-300">Home</Link></li>
          <li><Link to="/about" className="hover:text-gray-300">About</Link></li>
        </ul>
      </nav>
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">Writer Analysis Tool</h1>
        <p>Get insights into your writing style</p>
      </div>
      <form onSubmit={handleSubmit} className="w-full max-w-md">
        <div className="flex items-center border-b border-white py-2">
          <input
            className="appearance-none bg-transparent border-none w-full text-white mr-3 py-1 px-2 leading-tight focus:outline-none"
            type="text"
            placeholder="Enter your Substack or Medium URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button
            className="flex-shrink-0 bg-white hover:bg-gray-200 text-slate-900 font-bold py-2 px-4 rounded"
            type="submit"
          >
            Analyze
          </button>
        </div>
      </form>
      
      <AnimatePresence>
        {showAnalysis && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-4xl mt-8 bg-slate-800 rounded-lg p-6 overflow-hidden"
          >
            <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
            <p>This is where your analysis results and visualizations will appear.</p>
            {/* Add more analysis content here */}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MainPage;
