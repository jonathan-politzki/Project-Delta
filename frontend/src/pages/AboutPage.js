import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const AboutPage = () => {
  const [suggestion, setSuggestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would typically send this data to a server
    console.log('Suggestion submitted:', suggestion);
    // Clear the input after submission
    setSuggestion('');
    // You might want to show a success message to the user here
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="p-4">
        <ul className="flex space-x-4">
          <li><Link to="/" className="hover:text-gray-300">Home</Link></li>
          <li><Link to="/about" className="hover:text-gray-300">About</Link></li>
        </ul>
      </nav>
      
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">About Writer Analysis Tool</h1>
        
        {/* Project Delta Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Project Delta</h2>
          <p className="mb-4">
            Learn more about the inspiration behind this tool in the 
            <a href="https://jonathanpolitzki.substack.com/p/project-delta" 
               className="text-blue-400 hover:text-blue-300 ml-1" 
               target="_blank" 
               rel="noopener noreferrer">
              Project Delta write-up
            </a>.
          </p>
        </section>
        
        {/* Quote Section */}
        <section className="mb-12">
          <blockquote className="border-l-4 border-blue-500 pl-4 py-2 italic">
            "To know thyself is the beginning of wisdom." - Socrates
          </blockquote>
        </section>
        
        {/* About This Project Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">About This Project</h2>
          <p>
            We believe that writing is an intimate projection of an author's mind and that everyone has a unique "fingerprint". The Writer Analysis Tool is designed to provide insights into writing styles and an authors personality using advanced language processing techniques. 
            Our goal is to help writers understand their unique voice and compare it with others in the literary world. We also believe this technique can be used to understand how you are uniquely differentiated in the sea of other writers.
          </p>
        </section>
        
        {/* About the Creator Section */}
        <section className="mb-12">
            <h2 className="text-2xl font-semibold mb-4">About the Creator</h2>
            <p>
                My name is <a href="https://jonathanpolitzki.com" className="text-blue-400 hover:text-blue-300" target="_blank" rel="noopener noreferrer">Jonathan Politzki</a>. I love technology, writing, and I recently launched this project to help writers better understand themselves. Any feedback is much appreciated. I'd love to hear how I can make this tool better for you.
            </p>
        </section>

        {/* Suggestion Input Section */}
        <section className="mt-12">
          <h2 className="text-2xl font-semibold mb-4">Suggest a Feature</h2>
          <p className="mb-4">We value your input! What would you like this tool to tell you about yourself and your writing?</p>
          <form onSubmit={handleSubmit} className="max-w-lg">
            <textarea
              className="w-full p-2 text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="4"
              value={suggestion}
              onChange={(e) => setSuggestion(e.target.value)}
              placeholder="Enter your suggestion here..."
            ></textarea>
            <button
              type="submit"
              className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
            >
              Submit Suggestion
            </button>
          </form>
        </section>
      </div>
    </div>
  );
};

export default AboutPage;

