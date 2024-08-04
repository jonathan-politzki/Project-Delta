import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainPage from './pages/MainPage';
import NotFound from './pages/NotFound';
// import AboutPage from './components/AboutPage';  // Uncomment when you create this component

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        {/* <Route path="/about" element={<AboutPage />} /> */}  {/* Uncomment when you create this component */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;