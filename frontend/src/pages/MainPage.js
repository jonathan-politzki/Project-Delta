// frontend/src/pages/MainPage.js

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { analyzeUrl } from '../services/api';  // Update this line



const MainPage = () => {
  const [url, setUrl] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const result = await analyzeUrl(url);
      if (result.status === "processing") {
        pollForResults(result.task_id);
      } else {
        setAnalysisResult(result);
      }
    } catch (err) {
      console.error('Error during analysis:', err);
      setError('An error occurred while analyzing the URL. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const pollForResults = async (taskId) => {
    const pollInterval = setInterval(async () => {
      try {
        const result = await getAnalysisStatus(taskId);
        if (result.status === "completed") {
          clearInterval(pollInterval);
          setAnalysisResult(result);
        }
      } catch (err) {
        console.error('Error polling for results:', err);
        clearInterval(pollInterval);
        setError('An error occurred while retrieving analysis results. Please try again.');
      }
    }, 5000); // Poll every 5 seconds
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
            disabled={isLoading}
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </form>
      
      <AnimatePresence>
        {analysisResult && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-4xl mt-8 bg-slate-800 rounded-lg p-6 overflow-hidden"
          >
            <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
            <p><strong>Insights:</strong> {analysisResult.insights}</p>
            <p><strong>Writing Style:</strong> {analysisResult.writing_style}</p>
            <p><strong>Key Themes:</strong> {analysisResult.key_themes.join(', ')}</p>
            <p><strong>Readability Score:</strong> {analysisResult.readability_score.toFixed(2)}</p>
            <p><strong>Sentiment:</strong> {analysisResult.sentiment}</p>
            <p><strong>Post Count:</strong> {analysisResult.post_count}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <p className="text-red-500 mt-4">{error}</p>
      )}
    </div>
  );
};

export default MainPage;