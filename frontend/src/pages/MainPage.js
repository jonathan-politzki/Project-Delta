import React, { useState, useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import ReactConfetti from 'react-confetti';
import { analyzeUrl, getAnalysisStatus } from '../services/api';

const LoadingBar = ({ progress }) => (
  <div className="w-full bg-gray-700 rounded-full h-2.5 mb-4">
    <div 
      className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out"
      style={{ width: `${progress}%` }}
    ></div>
  </div>
);

const MainPage = () => {
  const [url, setUrl] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [progress, setProgress] = useState(0);
  const [totalEssays, setTotalEssays] = useState(10);

  useEffect(() => {
    if (showConfetti) {
      const timer = setTimeout(() => setShowConfetti(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [showConfetti]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
    setProgress(0);

    try {
      const result = await analyzeUrl(url);
      console.log('Initial API response:', result);
      setTotalEssays(result.total_essays || 10);
      await pollForResults(result.task_id);
    } catch (err) {
      console.error('Error during analysis:', err);
      setError('An error occurred while analyzing the URL. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [url]);

  const pollForResults = useCallback(async (taskId) => {
    const pollInterval = 5000; // 5 seconds
    const maxAttempts = 60; // 5 minutes total
    let attempts = 0;

    const updateProgress = (current, total) => {
      const newProgress = Math.min(Math.round((current / total) * 100), 99);
      console.log(`Updating progress: ${current}/${total} = ${newProgress}%`);
      setProgress(newProgress);
    };

    while (attempts < maxAttempts) {
      try {
        const result = await getAnalysisStatus(taskId);
        console.log('Status update:', result);
        
        if (result.status === 'completed') {
          setAnalysisResult(result.result);
          setProgress(100);
          setShowConfetti(true);
          return;
        } else if (result.status === 'error') {
          throw new Error(result.message || 'An error occurred during analysis.');
        } else if (result.status === 'processing') {
          updateProgress(result.essays_analyzed || 0, totalEssays);
        }
        
        attempts++;
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      } catch (err) {
        console.error('Error in pollForResults:', err);
        setError(err.message);
        return;
      }
    }

    setError('Analysis timed out. Please try again later.');
  }, [totalEssays]);

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4">
      {showConfetti && <ReactConfetti />}
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
      <form onSubmit={handleSubmit} className="w-full max-w-md mb-4">
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
      
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="w-full max-w-md text-center"
        >
          <LoadingBar progress={progress} />
          <p className="text-gray-300 mt-2">
            Analysis in progress: {progress}% complete
          </p>
          <p className="text-gray-300 mt-2">
            This may take a few minutes...
          </p>
        </motion.div>
      )}

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