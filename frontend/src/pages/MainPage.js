// MainPage.js

import React, { useState, useCallback, useEffect, useRef } from 'react';
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
  const [isAnalysisComplete, setIsAnalysisComplete] = useState(false);
  const resultsRef = useRef(null);

  const scrollToResults = (duration = 3500) => {
    setIsAnalysisComplete(true);
    const start = window.pageYOffset;
    const end = resultsRef.current?.offsetTop ?? 0;
    const startTime = performance.now();

    const animateScroll = (currentTime) => {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      const easeProgress = 0.5 - Math.cos(progress * Math.PI) / 2;
      window.scrollTo(0, start + (end - start) * easeProgress);

      if (progress < 1) {
        requestAnimationFrame(animateScroll);
      }
    };

    requestAnimationFrame(animateScroll);
  };

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
    setIsAnalysisComplete(false);

    try {
      const result = await analyzeUrl(url);
      console.log('Initial API response:', result);
      if (!result.task_id) {
        throw new Error('No task ID received from the server');
      }
      await pollForResults(result.task_id);
    } catch (err) {
      console.error('Error during analysis:', err);
      setError(`An error occurred while analyzing the URL: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [url]);

  const pollForResults = useCallback(async (taskId) => {
    const pollInterval = 5000; // 5 seconds
    const maxAttempts = 60; // 5 minutes total
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const result = await getAnalysisStatus(taskId);
        console.log('Status update:', result);
        
        if (result.status === 'completed') {
          console.log('Analysis completed. Result:', result.result);
          setAnalysisResult(result.result);
          setProgress(100);
          setShowConfetti(true);
          setTimeout(() => {
            scrollToResults(3500); // Scroll duration set to 3.5 seconds
          }, 1000); // Delay scrolling to allow confetti to be visible
          return;
        } else if (result.status === 'error') {
          throw new Error(result.message || 'An error occurred during analysis.');
        } else if (result.status === 'processing') {
          if (typeof result.progress === 'number') {
            setProgress(result.progress);
          } else {
            // Fallback progress calculation
            setProgress(Math.min(Math.round((attempts / maxAttempts) * 100), 99));
          }
        } else {
          console.warn('Unknown status received:', result.status);
        }
        
        attempts++;
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      } catch (err) {
        console.error('Error in pollForResults:', err);
        setError(`Error checking analysis status: ${err.message}`);
        return;
      }
    }

    setError('Analysis timed out. Please try again later.');
  }, []);

  const renderAnalysisResult = () => {
    if (!analysisResult || !analysisResult.insights) return null;

    console.log('Rendering analysis result:', analysisResult);

    const { writing_style, key_themes, conclusion } = analysisResult.insights;

    return (
      <div className="space-y-6">
        <section>
          <h3 className="text-xl font-semibold text-blue-400">Writing Style</h3>
          <ul className="list-disc pl-5 space-y-2">
            {writing_style.map((point, index) => (
              <li key={index} className="text-gray-300">{point}</li>
            ))}
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-semibold text-green-400">Key Themes</h3>
          <ul className="list-disc pl-5 space-y-2">
            {key_themes.map((theme, index) => (
              <li key={index} className="text-gray-300">{theme}</li>
            ))}
          </ul>
        </section>

        {conclusion && (
          <section>
            <h3 className="text-xl font-semibold text-yellow-400">Conclusion</h3>
            <p className="text-gray-300">{conclusion}</p>
          </section>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white overflow-y-auto">
      {showConfetti && <ReactConfetti />}
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
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
      </div>

      <motion.div
        ref={resultsRef}
        className="min-h-screen flex flex-col items-center justify-start p-4 bg-slate-900 border-t-4 border-gray-300"
        initial={{ opacity: 0 }}
        animate={{ opacity: isAnalysisComplete ? 1 : 0 }}
        transition={{ duration: 0.5 }}
      >
        <AnimatePresence>
          {analysisResult && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="w-full max-w-6xl mt-8 bg-slate-800 rounded-lg p-6 overflow-hidden"
            >
              <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
              {renderAnalysisResult()}
            </motion.div>
          )}
        </AnimatePresence>

        {error && (
          <p className="text-red-500 mt-4">{error}</p>
        )}
      </motion.div>
    </div>
  );
};

export default MainPage;