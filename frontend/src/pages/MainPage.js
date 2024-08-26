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
  const [analysisState, setAnalysisState] = useState({
    result: null,
    isLoading: false,
    error: null,
    progress: 0,
    isComplete: false,
  });
  const [showConfetti, setShowConfetti] = useState(false);
  const resultsRef = useRef(null);

  const scrollToResults = useCallback((duration = 3500) => {
    setAnalysisState(prev => ({ ...prev, isComplete: true }));
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
  }, []);

  useEffect(() => {
    if (showConfetti) {
      const timer = setTimeout(() => setShowConfetti(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [showConfetti]);

  const pollForResults = useCallback(async (taskId) => {
    const maxAttempts = 60;
    const pollInterval = 3000;

    const poll = async (attempts) => {
      if (attempts >= maxAttempts) {
        setAnalysisState(prev => ({ 
          ...prev, 
          error: 'Analysis timed out. Please try again.', 
          isLoading: false,
          isComplete: true
        }));
        return;
      }

      try {
        const result = await getAnalysisStatus(taskId);
        console.log('Received analysis status update:', JSON.stringify(result, null, 2));
  
        switch (result.status) {
          case 'completed':
            console.log('Analysis completed, full result:', JSON.stringify(result, null, 2));
            setAnalysisState(prev => ({
              ...prev,
              result: result,
              isLoading: false,
              isComplete: true,
              progress: 100
            }));
            setShowConfetti(true);
            setTimeout(() => scrollToResults(3500), 1000);
            break;

          case 'error':
            throw new Error(result.message || 'An error occurred during analysis.');

          case 'processing':
            console.log('Processing update:', JSON.stringify(result, null, 2));
            setAnalysisState(prev => ({
              ...prev,
              progress: typeof result.progress === 'number' 
                ? result.progress 
                : Math.min(Math.round((attempts / maxAttempts) * 100), 99),
            }));
            setTimeout(() => poll(attempts + 1), pollInterval);
            break;

          default:
            console.warn('Unknown status received:', result.status);
            setTimeout(() => poll(attempts + 1), pollInterval);
        }
      } catch (err) {
        console.error('Error in pollForResults:', err);
        setAnalysisState(prev => ({ 
          ...prev, 
          error: `Error checking analysis status: ${err.message}`, 
          isLoading: false,
          isComplete: true
        }));
      }
    };

    poll(0);
  }, [scrollToResults, setAnalysisState, setShowConfetti]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setAnalysisState({
      result: null,
      isLoading: true,
      error: null,
      progress: 0,
      isComplete: false,
    });

    try {
      const result = await analyzeUrl(url);
      console.log('Initial API response:', JSON.stringify(result, null, 2));
      if (!result.task_id) {
        throw new Error('No task ID received from the server');
      }
      await pollForResults(result.task_id);
    } catch (err) {
      console.error('Error during analysis:', err);
      setAnalysisState(prev => ({ 
        ...prev, 
        error: `An error occurred while analyzing the URL: ${err.message}`, 
        isLoading: false,
        isComplete: true
      }));
    }
  }, [url, pollForResults]);

  const renderAnalysisResult = () => {
    console.log('Rendering analysis result, full state:', JSON.stringify(analysisState, null, 2));

    if (!analysisState.result || !analysisState.result.result) {
      console.error('No result in analysisState');
      return <p>No analysis result available.</p>;
    }

    const analysis = analysisState.result.result;

    console.log('Analysis data:', JSON.stringify(analysis, null, 2));

    if (!analysis || typeof analysis !== 'object') {
      return <p>Unable to process analysis data.</p>;
    }

    const renderSection = (title, content, color) => (
      <section className="bg-slate-800 rounded-lg p-4 shadow-md mt-4">
        <h3 className={`text-xl font-semibold ${color} mb-2`}>{title}</h3>
        {content}
      </section>
    );

    const renderBulletPoints = (items) => (
      <ul className="list-disc pl-5 space-y-1">
        {items.map((item, index) => (
          <li key={index} className="text-gray-300">{item}</li>
        ))}
      </ul>
    );

    // Extract detailed concepts from insights
    const detailedConcepts = analysis.insights
      ? analysis.insights
          .split('\n')
          .filter(line => line.includes('**') && !line.includes('###'))
          .map(line => line.replace(/\*\*/g, '').trim())
      : [];

    const writingFingerprint = [
      `Writing Style: ${analysis.writing_style}`,
      `Sentiment: ${analysis.sentiment}`,
      `Readability Score: ${analysis.readability_score.toFixed(2)}`,
      `Posts analyzed: ${analysis.post_count}`,
      `Key Themes: ${analysis.key_themes.join(', ')}`
    ];

    return (
      <div className="space-y-6">
        {renderSection("Detailed Insights", renderBulletPoints(detailedConcepts), "text-blue-400")}
        {renderSection("Writing Fingerprint", renderBulletPoints(writingFingerprint), "text-green-400")}
        {renderSection("Key Concepts", renderBulletPoints(analysis.key_themes), "text-indigo-400")}
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
          <h1 className="text-4xl font-bold mb-2">Content Analysis Tool</h1>
          <p>Discover the key concepts in your content</p>
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
              disabled={analysisState.isLoading}
            >
              {analysisState.isLoading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </form>
        
        {analysisState.isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full max-w-md text-center"
          >
            <LoadingBar progress={analysisState.progress} />
            <p className="text-gray-300 mt-2">
              Analysis in progress: {analysisState.progress}% complete
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
        animate={{ opacity: analysisState.isComplete ? 1 : 0 }}
        transition={{ duration: 0.5 }}
      >
        <AnimatePresence>
          {analysisState.result && (
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
        {!analysisState.result && analysisState.isComplete && (
          <p className="text-yellow-500 mt-4">Analysis completed, but no results available.</p>
        )}
        {analysisState.error && (
          <p className="text-red-500 mt-4">{analysisState.error}</p>
        )}
      </motion.div>
    </div>
  );
};

export default MainPage;