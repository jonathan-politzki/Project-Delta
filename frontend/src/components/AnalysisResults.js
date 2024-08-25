// In frontend/src/components/AnalysisResults.js

import React from 'react';

const AnalysisResults = ({ results }) => {
  return (
    <div>
      <h2>Essay Similarity Graph</h2>
      <img src={results.essay_graph} alt="Essay Similarity Graph" />
      
      <h2>Individual Essay Concepts</h2>
      {results.individual_concepts.map((concepts, index) => (
        <div key={index}>
          <h3>Essay {index + 1}</h3>
          <ul>
            {concepts.map((concept, cIndex) => (
              <li key={cIndex}>{concept}</li>
            ))}
          </ul>
        </div>
      ))}
      
      <h2>Top 5 Aggregated Concepts</h2>
      <ul>
        {results.aggregated_concepts.map((item, index) => (
          <li key={index}>{item.concept} (Mentioned {item.count} times)</li>
        ))}
      </ul>
    </div>
  );
};

export default AnalysisResults;