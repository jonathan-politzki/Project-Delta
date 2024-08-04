import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const MainPage = () => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would handle the URL submission
    console.log('Submitted URL:', url);
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
    </div>
  );
};

export default MainPage;
