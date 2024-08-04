import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
      <p className="mb-4">The page you are looking for doesn't exist.</p>
      <Link to="/" className="text-blue-400 hover:text-blue-300">Go back to home</Link>
    </div>
  );
};

export default NotFound;
